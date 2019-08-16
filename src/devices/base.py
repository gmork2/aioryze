from pprint import pprint

from inputs import devices


def display_devices() -> None:
    """
    Display info about all detected devices.

    :return:
    """
    for device in devices:
        print('\n{}'.format(device))
        pprint(device.__dict__, indent=4)
