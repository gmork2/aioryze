import sys
from argparse import ArgumentParser
from typing import Optional

from inputs import devices, InputDevice

from core.command import BaseCommandMixin, DEVICE_TEXT
from config.settings import SCAN_TIMER_RANGE
from devices.base import Device
from devices.config import Config
from .decorators import spin_animation


class CommandMixin(BaseCommandMixin):

    def __add_arguments(self, parser: ArgumentParser) -> None:
        """

        :param parser:
        :return:
        """
        parser.add_argument(
            '--list', action='store_true',
            help='Display a brief description for each device')

        parser.add_argument(
            '--configure', action='store_true',
            help='Scan your devices establishing the first issuer as default')

        self.add_arguments(parser)

    def __parse_arguments(self):
        """

        :return:
        """
        parser = self._create_parser()
        self.__add_arguments(parser)

        return parser.parse_args(sys.argv[2:])

    def __list(self, prefix: str = '') -> None:
        """

        :return:
        """
        stdout = getattr(self, 'stdout', sys.stdout)

        for i, dev in enumerate(devices.all_devices):
            name = prefix + DEVICE_TEXT.format(i, dev.name)
            stdout.write(name)

    def __select_device(self, msg: str) -> Optional[int]:
        """

        :return:
        """
        try:
            index = int(input(msg))
        except ValueError:
            return

        return self.__device(index)

    @spin_animation(message="Scanning device...", frequency=.1)
    def __scan(self, device: InputDevice = None) -> Device:
        """

        :return:
        """
        self.__config = Config(device=device)
        self.__config.scan(*SCAN_TIMER_RANGE)

        return self.__config.device

    @staticmethod
    def __device(index: int) -> Optional[InputDevice]:
        """

        :param index:
        :return:
        """
        try:
            return devices.all_devices[index]
        except IndexError:
            pass
