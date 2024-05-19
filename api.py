import asyncio
import logging
import os
from datetime import datetime as dt

from aiohttp import ClientSession
from dotenv import load_dotenv

from utils import BoundedTaskGroup


load_dotenv()
logger = logging.getLogger(__name__)


class IgdbInfoCollector:
    """Collector that gets and stores games' info using IGDB Api."""
    URL = 'https://api.igdb.com/v4/games'
    TOKEN = os.environ['TOKEN']
    CLIENT_ID = os.environ['CLIENT_ID']
    HEADERS = {'Authorization': TOKEN, 'Client-ID': CLIENT_ID}
    FIELDS = (
        'fields name,'
        'first_release_date,'
        'genres.name,'
        'collections.name,'
        'involved_companies.company.name,'
        'involved_companies.*,'
        'platforms.name;'
    )
    LIMIT = 500

    def __init__(self, game_ids: list[int], session: ClientSession):
        self.GAME_IDS = game_ids
        self.SESSION = session
        self.results: list[dict] = []

    async def collect(self) -> None:
        if len(self.GAME_IDS) > self.LIMIT:
            chunks = self._chunkify_list(self.GAME_IDS, self.LIMIT)
            async with BoundedTaskGroup(max_concurrency=3) as tg:
                [tg.create_task(self._fetch_info(chunk)) for chunk in chunks]
        else:
            await self._fetch_info(self.GAME_IDS)

    @staticmethod
    def _chunkify_list(game_ids: list[int], n: int) -> list[list[int]]:
        """
        Break a game_ids list into chunks of size n.
        Reason - IGDB API's maximum limit is set to 500 items/request.
        """
        return [game_ids[idx:idx + n] for idx in range(0, len(game_ids), n)]

    def _parse_game_data(self, data: list[dict]) -> None:
        """Get necessary information from IGDB API responce."""
        for obj in data:
            game = {}
            game['game_id'] = obj.get('id')
            game['title'] = obj.get('name')
            genres = obj.get('genres')
            release_date = obj.get('first_release_date')
            if release_date:
                game['release_year'] = dt.fromtimestamp(release_date).year
            if genres:
                game['genres'] = [genre['name'] for genre in genres]
            companies = obj.get('involved_companies')
            if companies:
                for company in companies:
                    company_name = company['company']['name']
                    if company['developer']:
                        game.setdefault('developers', []).append(company_name)
                    if company['publisher']:
                        game.setdefault('publishers', []).append(company_name)
            platforms = obj.get('platforms')
            if platforms:
                game['platforms'] = [plat['name'] for plat in platforms]
            series = obj.get('collections')
            if series:
                game['series'] = [serie['name'] for serie in series]
            self.results.append(game)

    async def _fetch_info(self, game_ids: list[int]) -> None:
        """Collect game info for up to 500 games using IGDB API."""

        WHERE_STATEMENT = f'where id = {*game_ids, };'
        BODY = self.FIELDS + WHERE_STATEMENT + f'limit {self.LIMIT};'

        KWARGS = dict(
            url=self.URL,
            headers=self.HEADERS,
            data=BODY
        )

        async with self.SESSION.post(**KWARGS) as responce:

            status = responce.status
            if status not in (200, 429):
                if status in (400, 401):
                    logger.critical(f'{await responce.json()}')
                else:
                    logger.critical(f'Something went wrong. Status: {status}')
                responce.raise_for_status()
            if status == 429:
                logger.error('Too many requests. Pause and repeat.')
                await asyncio.sleep(1)
                await self._fetch_info(self.SESSION, game_ids)
            else:
                data = await responce.json()
                if data:
                    logger.info(f'Success: {len(data)} results found.')
                    self._parse_game_data(data)
                else:
                    logger.warning('Nothing found. API returned empty list.')
