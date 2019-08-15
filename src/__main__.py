import logging
import io
import asyncio
import textwrap
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import Callable, Text

from config import __version__
from config.settings import DEBUG


logger = logging.getLogger(__name__)


def get_version() -> str:
    """
    Returns current software version.

    :return:
    """
    return str(__version__)


class Command(object):
    __epilog: str = '''
        | One app to rule them all.
    '''

    __usage: str = textwrap.dedent('''\
        __main__.py <command> [<args>]

        The most commonly used git commands are:
            devices    Utilities for handle your devices
            ui         Interface based in curses
    ''')

    def __init__(self):
        """

        """
        self.stdout = sys.stdout
        self._loop = asyncio.get_event_loop()

        if DEBUG:
            self.__debug()

        parser = self.create_parser()

        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command):
            parser.print_help()
            exit(1)

        # Use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def create_parser(self) -> ArgumentParser:
        """

        :return:
        """
        parser = ArgumentParser(
            formatter_class=RawDescriptionHelpFormatter,
            # description=textwrap.dedent(),
            usage=self.__usage,
            epilog=self.__epilog
        )

        parser.add_argument('--version', action='version', version=self.get_version())
        parser.add_argument('command', help='Subcommand to run')

        return parser

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> ArgumentParser:
        """

        :param parser:
        :return:
        """
        parser.add_argument(
            '--path', action='store_true', dest='device_config',
            help='Set a device configuration',
        )

        parser.add_argument(
            '--verbose', type=int,
            help="increase output verbosity"
        )
        parser.add_argument(
            '-v', '--verbosity', action='store', dest='verbosity', default=1,
            type=int, choices=[0, 1, 2, 3],
            help='Verbosity level; 0=minimal, 1=normal, 2=verbose, 3=very verbose',
        )

        return parser

    @staticmethod
    def get_version() -> str:
        """
        Return the current version, which should be correct for all built-in
        commands.
        """
        return get_version()

    def __debug(self) -> None:
        """

        :return:
        """
        logging.basicConfig(level=logging.DEBUG)

        self._loop.set_debug(True)
        self._loop.slow_callback_duration = 200

    def _redirect_output(self, func: Callable[[], None]) -> Text:
        """
        Redirect output value from function to any variable. For
        example:

            func = lambda: self._list()

        :param func:
        :return:
        """
        stdout = sys.stdout

        try:
            self.stdout = io.StringIO()
            func()

        finally:
            output = self.stdout.getvalue()
            self.stdout.close()
            self.stdout = stdout

        return output


if __name__ == '__main__':
    Command()
