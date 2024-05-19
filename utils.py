import asyncio


class BoundedTaskGroup(asyncio.TaskGroup):
    """
    Asynchronous context manager that extends asyncio.Taskgroup
    to enable limiting max number of concurrent tasks.
    """
    def __init__(self, *args, max_concurrency=0, **kwargs):
        super().__init__(*args)
        if max_concurrency:
            self._sem = asyncio.Semaphore(max_concurrency)
        else:
            self._sem = None

    def create_task(self, coro, *args, **kwargs):
        if self._sem:
            async def _wrapped_coro(sem, coro):
                async with sem:
                    return await coro
            coro = _wrapped_coro(self._sem, coro)

        return super().create_task(coro, *args, **kwargs)
