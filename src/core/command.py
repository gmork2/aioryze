from argparse import ArgumentParser
from typing import ClassVar, Tuple, NoReturn, Text

COLORIZE_TEXT = '\33[32m{}\33[0m'
DEVICE_TEXT = '[{}] {}\n'


def mark_text(*args: Tuple[str]) -> Text:
    """

    :param args:
    :return:
    """
    if len(args) > 1:
        return ''.join(*args)
    else:
        return COLORIZE_TEXT.format(args[0])


class BaseCommandMixin(object):

    __description: ClassVar[str] = ''
    __help: ClassVar[str] = None

    def _create_parser(self) -> ArgumentParser:
        """

        :return:
        """
        parser = ArgumentParser(description=self.__description)
        return parser

    def add_arguments(self, parser: ArgumentParser) -> NoReturn:
        """

        :param parser:
        :return:
        """
        raise NotImplemented
