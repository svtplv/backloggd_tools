import asyncio
from time import perf_counter

from aiohttp import ClientSession

from api import IgdbInfoCollector
from scraper import LogCollector
from savers import JsonSaver


async def main():
    async with ClientSession() as session:
        log_collector = LogCollector(input('Enter your username:\n'), session)
        await log_collector.collect()
        JsonSaver().save(f'{log_collector.USERNAME}_logs', log_collector.logs)
        game_ids = [log['game_id'] for log in log_collector.logs]
        game_collector = IgdbInfoCollector(game_ids, session)
        await game_collector.collect()
        JsonSaver().save(
            f'{log_collector.USERNAME}_games', game_collector.results
        )

if __name__ == '__main__':
    start = perf_counter()
    asyncio.run(main())
    print(perf_counter() - start)
