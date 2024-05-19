import asyncio

import aiohttp
from bs4 import BeautifulSoup

from utils import BoundedTaskGroup


class LogCollector:
    """Scraper for backloggd profile."""

    def __init__(self, username: str, session: aiohttp.ClientSession):
        self.USERNAME = username
        self.SESSION = session
        self.GAMES_URL = f'https://www.backloggd.com/u/{username}/games/'
        self.LOGS_URL = f'https://www.backloggd.com/u/{username}/logs/'
        self.logs: list[dict] = []

    async def collect(self) -> None:
        """Get and store all user logs."""
        last_page_num = await self._get_last_page()
        async with BoundedTaskGroup(max_concurrency=2) as page_tg:
            for page_num in range(1, last_page_num + 1):
                page_tg.create_task(self._fetch_info_per_page(page_num))
        async with BoundedTaskGroup(max_concurrency=4) as log_tg:
            for partial_log in self.logs:
                log_tg.create_task(self._fetch_log(partial_log))

    async def _get_last_page(self) -> int:
        """Get last page from paginated profile."""
        async with self.SESSION.get(self.GAMES_URL) as response:
            page = await response.text()
            soup = BeautifulSoup(page, 'lxml')
            last_page_num = int(soup.find_all('span', class_='page')[-2].text)
            return last_page_num

    async def _fetch_info_per_page(self, page_num: int) -> None:
        """Store games' ids and slugs for later use."""
        url = f'{self.GAMES_URL}?page={page_num}'
        async with self.SESSION.get(url) as response:
            page = await response.text()
            soup = BeautifulSoup(page, 'lxml')
            self._parse_games_info(soup)

    def _parse_games_info(self, soup: BeautifulSoup) -> None:
        """Parse page to get relevant info for each game on page."""
        games = soup.find_all('div', class_='rating-hover')
        for game in games:
            partial_log = {'username': self.USERNAME}
            game_id = int(game.find('div', class_='game-cover')['game_id'])
            partial_log['game_id'] = game_id
            partial_log['slug'] = game.a['href'].strip('/').split('/')[-1]
            rating = game.find('div', attrs={'data-rating': True})
            if rating:
                partial_log['user_rating'] = int(rating.get('data-rating'))
            self.logs.append(partial_log)

    async def _fetch_log(self, partial_log: dict) -> None:
        """Get complete log and update partial one."""
        url = self.LOGS_URL + partial_log['slug']
        async with self.SESSION.get(url) as response:
            status = response.status
            if status == 429:
                print(f'Превышен лимит, повторяем slug: {partial_log['slug']}')
                await asyncio.sleep(60)
                await self._fetch_log(partial_log)
            if status == 200:
                page = await response.text()
                soup = BeautifulSoup(page, 'lxml')
                self._parse_log(soup, partial_log)
                print(f'{partial_log['slug']}: success')
            await asyncio.sleep(1)

    @staticmethod
    def _time_to_float(time_played: str) -> float:
        """Convert time to hours float."""
        hours, minutes = time_played.split()
        full_hours = int(hours[:-1])
        fraction = int(minutes[:-1]) / 60
        hours_float = full_hours + fraction
        return round(hours_float, 2)

    def _parse_log(self, soup: BeautifulSoup, partial_log: dict) -> None:
        """Parse log page to get relevant info."""
        status = soup.select_one('div.current').get_text()
        partial_log['status'] = status.strip()
        time_played = soup.select_one('p:has(> i)').get_text()
        if time_played and 'h' in time_played:
            hours = self._time_to_float(time_played.strip())
            partial_log['hours_played'] = hours
        platforms = soup.select('div.col-auto:has(>.game-page-platform)')
        if platforms:
            partial_log['platforms_played'] = [
                plat.text.strip().split(' via ')[0] for plat in platforms
            ]
