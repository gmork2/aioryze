import logging

from config import __version__
from config.settings import DEBUG


logger = logging.getLogger(__name__)


def get_version() -> str:
    """
    Returns current software version.

    :return:
    """
    return str(__version__)


if __name__ == '__main__':
    if DEBUG:
        print(get_version())
