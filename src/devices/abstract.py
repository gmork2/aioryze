import asyncio
import time

from inputs import convert_timeval, InputEvent


def time_elapsed(timestamp: float) -> float:
    """
    Time elapsed since timestamp.

    :param timestamp:
    :return:
    """
    secs, msecs = convert_timeval(time.time())
    return secs + (msecs / 1000000) - timestamp


class BufferMixin:

    @property
    def buffer_qsize(self) -> int:
        """
        Number of items allowed in the buffer.

        :return:
        """
        return self._buffer.qsize()

    async def get(self) -> InputEvent:
        """
        Returns the next device event from buffer that has not
        exceeded the time limit.

        :return:
        """
        try:
            event = self._buffer.get_nowait()
            while time_elapsed(event.timestamp) > self._timeout / 100:
                event = self._buffer.get_nowait()

        except asyncio.QueueEmpty:
            event = await self._buffer.get()

        return event

    async def put(self, event: InputEvent) -> None:
        """
        Insert an event in the buffer with a timeout. If the
        timeout is exceeded the insertion task is canceled.

        :param event:
        :return:
        """
        try:
            await asyncio.wait_for(self._buffer.put(event), timeout=self._timeout)
        except asyncio.TimeoutError:
            pass
