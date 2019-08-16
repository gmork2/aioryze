from typing import List

from inputs import (
    devices, GamePad as _GamePad, Keyboard as _Keyboard,
    Mouse as _Mouse
)

from .base import Device


class GamePad(Device):

    @property
    def devices(self) -> List[_GamePad]:
        """
        Returns a list of GamePad devices.

        :return:
        """
        return devices.gamepads


class Mouse(Device):

    @property
    def devices(self) -> List[_Mouse]:
        """
        Returns a list of mouse devices.

        :return:
        """
        return devices.mice


class Keyboard(Device):

    @property
    def devices(self) -> List[_Keyboard]:
        """
        Returns a list of keyboard devices.

        :return:
        """
        return devices.keyboards
