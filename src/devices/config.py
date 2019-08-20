from typing import List
import asyncio

from inputs import devices, InputDevice, InputEvent

from .base import Device
from utils import UniqueValueOrderedDict


SNES = (
    'up', 'down', 'left', 'right', 'select', 'start',
    'y', 'x', 'b', 'a', 'l', 'r'
)


class Config:
    def __init__(self, names: List[str] = SNES, device: Device = None):
        """

        :param names:
        :param device:
        """
        self._mapping: UniqueValueOrderedDict = None
        self._names = names

        self.device = device

    @property
    def devices(self) -> List[Device]:
        """

        :return:
        """
        return [Device(device=dev) for dev in devices]

    async def read(self, device: Device = None):
        """

        :param device:
        :return:
        """
        async for ev in device.async_read():
            if not self.device:
                self.device = device
            return ev

    async def read_all(self, criteria: str = asyncio.FIRST_COMPLETED):
        """

        :param criteria:
        :return:
        """
        futures = list()

        for dev in self.devices:
            task = asyncio.ensure_future(self.read(dev))
            futures.append(task)

        done, _ = await asyncio.wait(futures, return_when=criteria)
        return done

    def scan(self):
        """

        :return:
        """
        pass

    def load(self):
        """
        Get configuration by self._name from storage.

        :return:
        """
        pass

    def save(self):
        """

        :return:
        """
        pass

    @staticmethod
    def set_actions(attrs: set, device: InputDevice) -> UniqueValueOrderedDict:
        """

        :param attrs:
        :param device:
        :return:
        """
        mapping = UniqueValueOrderedDict()

        while attrs:
            attr = attrs.pop()
            mapping[attr] = device.read()

        return mapping

    def __setitem__(self, key: str, value: InputEvent):
        """

        :param key:
        :param value:
        :return:
        """
        if key in self._names:
            self._mapping[key] = value
        else:
            raise KeyError

    def __getitem__(self, key: str) -> InputEvent:
        """

        :param key:
        :return:
        """
        return self._mapping[key]
