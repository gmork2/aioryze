import asyncio
import select
from typing import List, Generator, AsyncIterable, Type
from pprint import pprint
import os

from inputs import InputDevice, InputEvent, devices, UnpluggedError

from .abstract import AbstractDevice


def display_devices() -> None:
    """
    Display info about all detected devices.

    :return:
    """
    for device in devices:
        print('\n{}'.format(device))
        pprint(device.__dict__, indent=4)


class IncompatibleDevice(Exception):
    pass


class ReadIterator(object):

    def __init__(self, device):
        self.current_batch = iter(())
        self.device = device

    def __iter__(self):
        return self

    def __next__(self):
        try:
            # Read from the previous batch of events.
            return next(self.current_batch)
        except StopIteration:
            r, w, x = select.select([self.device.fd], [], [])
            self.current_batch = self.device.read()
            return next(self.current_batch)

    def __aiter__(self):
        return self

    @asyncio.coroutine
    def __anext__(self):
        future = asyncio.Future()
        try:
            # Read from the previous batch of events.
            future.set_result(next(self.current_batch))
        except StopIteration:
            def next_batch_ready(batch):
                try:
                    self.current_batch = batch.result()
                    future.set_result(next(self.current_batch))
                except Exception as e:
                    future.set_exception(e)
            self.device.set_reader().add_done_callback(next_batch_ready)
        return future


class BaseDevice(AbstractDevice):

    def __init__(self, *, maxsize: int = 0, timeout: int = 100,
                 loop: asyncio.AbstractEventLoop = None, device: InputDevice):
        """
        Device base class that uses the 'inputs' package from
        (https://github.com/zeth/inputs).

        :param maxsize:
        :param timeout:
        :param loop:
        """
        super().__init__()

        self._device = device
        path: str = self._device.get_char_device_path()

        try:
            # Certain operations are possible only when the device is opened in
            # read-write mode.
            self.fd = os.open(path, os.O_RDWR | os.O_NONBLOCK)
        except OSError:
            self.fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)

        self.task_read: asyncio.Task = None
        self.reading = asyncio.Event()

    @property
    def devices(self) -> List[InputDevice]:
        """
        Returns a list of available devices.

        :return:
        """
        return devices

    def read(self) -> Generator[InputEvent, None, None]:
        """
        Read multiple input events from device. Return a generator object that
        yields :class:`InputEvent <evdev.events.InputEvent>` instances. Raises
        `BlockingIOError` if there are no available events at the moment.

        :return:
        """
        events = self._device.read()

        for event in events:
            yield event

    def set_reader(self) -> asyncio.Future:
        """
        Asyncio coroutine to read multiple input events from device. Return
        a generator object that yields :class:`InputEvent <evdev.events.InputEvent>`
        instances.
        """
        future = asyncio.Future()

        def ready():
            self._loop.remove_reader(self.fileno())
            try:
                future.set_result(self.read())
            except Exception as error:
                future.set_exception(error)

        self._loop.add_reader(self.fileno(), ready)

        return future

    def async_read(self) -> AsyncIterable[InputEvent]:
        """
        Return an iterator that yields input events. This iterator is
        compatible with the ''async for'' syntax.
        """
        return ReadIterator(self)

    async def on_read(self) -> None:
        """
        Read device events. This method waits 'self.reading'
        event object we'll use to control the reading from
        outside.

        :return:
        """
        await self.reading.wait()
        device = await self.get_device()

        # async for events in self.async_read():
        #     for ev in events:
        #         print("put event: ", ev)
        #         await self.put(ev)
        #         await asyncio.sleep(0)

    async def start(self) -> None:
        """
        Start the device reading task.

        :return:
        """
        self.reading.set()
        self.task_read = self._loop.create_task(self.on_read())

        while True:
            await asyncio.sleep(1)

    async def stop(self) -> None:
        """
        Stops the device reading task.

        :return:
        """
        self.reading.clear()
        self.task_read.cancel()

        try:
            await self.task_read
        except asyncio.CancelledError:
            pass

    async def get_device(self, index: int=0) -> InputDevice:
        """
        Returns device from available devices list.

        :param index:
        :return:
        """
        try:
            device = self._device or self.devices[index]
        except IndexError:
            raise UnpluggedError("No device found.")
        return device

    def set_device(self, device: InputDevice) -> None:
        """
        Set compatible device.

        :param device:
        :return:
        """
        if device not in self.devices:
            raise IncompatibleDevice("This device is not compatible.")
        self._device = device

    def fileno(self):
        """
        Returns the file descriptor to the open event device. This makes
        it possible to pass instances directly to 'select.select()'.
        """
        return self.fd

    def __repr__(self):
        return '<{}[{}] at {:#x} {}>'.format(
            type(self).__name__, self._device, id(self), self._buffer)

    def __str__(self):
        return '<{}[{}] {}>'.format(
            type(self).__name__, self._device, self._buffer)


class Device(BaseDevice):
    pass
