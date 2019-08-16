import abc
import asyncio
import time
from typing import List

from inputs import convert_timeval, InputEvent, InputDevice


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


class AbstractDevice(abc.ABC, BufferMixin):
    def __init__(self, *, maxsize: int = 0, timeout: int = 100,
                 loop: asyncio.AbstractEventLoop = None, device=None):
        """

        :param maxsize:
        :param timeout:
        :param loop:
        """
        if loop is None:
            self._loop = asyncio.get_event_loop()
        else:
            self._loop = loop

        self._buffer = asyncio.Queue(maxsize, loop=self._loop)
        self._buffer_max_size = maxsize
        self._timeout = timeout

    @abc.abstractmethod
    def devices(self) -> List[InputDevice]:
        """
        Returns a list of available devices.

        :return:
        """

    @abc.abstractmethod
    async def get_device(self, index: int = 0) -> InputDevice:
        """
        Get device from the list of available devices using
        an index.

        :param index:
        :return:
        """

    @abc.abstractmethod
    async def read(self) -> None:
        """
        Read device events.

        :return:
        """

    @abc.abstractmethod
    async def start(self) -> None:
        """
        Simple supervisor as entry point.

        :return:
        """

    @abc.abstractmethod
    async def stop(self) -> None:
        """
        Stops the reading of device events.

        :return:
        """


