import asyncio


# Found in https://bit.ly/2z573zm
class AsyncIteratorExecutor:
    """
    Converts a regular iterator into an asynchronous
    iterator, by executing the iterator in a thread.
    """
    def __init__(self, iterator, loop=None, executor=None):
        self.__iterator = iterator
        self.__loop = loop or asyncio.get_event_loop()
        self.__executor = executor

    def __aiter__(self):
        return self

    async def __anext__(self):
        value = await self.__loop.run_in_executor(
            self.__executor, next, self.__iterator, self)
        if value is self:
            raise StopAsyncIteration
        return value
