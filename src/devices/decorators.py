import threading
from functools import wraps
import itertools
import time
import sys
from typing import Callable, Tuple, Dict, Any, Optional
import asyncio

from inputs import InputDevice


Function = Callable[[Tuple[Any], Dict[str, Any]], InputDevice]


class Signal:
    """
    This class defines a simple mutable object with a go
    attribute we’ll use to control the thread from outside.
    """
    go: bool = True


class SpinDecorator(object):

    def __init__(self, message: str, frequency: float):
        """

        :param message:
        :param frequency:
        """
        self.signal = Signal()
        self.device: Optional[InputDevice] = None
        self.msg = message
        self.freq = frequency

    def __call__(self, func: Function):
        """

        :param func:
        :return:
        """
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[InputDevice]:

            # TODO: asyncio version
            spinner = threading.Thread(
                target=self.spin, args=(self.msg, self.signal, self.freq))
            spinner.start()

            try:
                self.device = func(*args, **kwargs)
            except asyncio.TimeoutError:
                pass

            # Change the state of the signal; this will terminate the
            # for loop inside the spin method.
            self.signal.go = False

            spinner.join()
            return self.device

        return wrapper

    @staticmethod
    def spin(msg: str, signal: Signal, freq: float) -> None:
        """
        This function will run in a separate thread. The signal
        argument is an instance of the Signal class just defined.

        :param msg:
        :param signal:
        :param freq:
        :return:
        """
        status = None
        write, flush = sys.stdout.write, sys.stdout.flush

        for char in itertools.cycle('|/-\\'):
            status = char + ' ' + msg
            write(status)
            flush()

            # Move the cursor back with backspace characters (\x08).
            write('\x08' * len(status))
            time.sleep(freq)

            if not signal.go:
                break

        # Clear the status line by overwriting with spaces and moving
        # the cursor back to the beginning.
        write(' ' * len(status) + '\x08' * len(status))


spin_animation = SpinDecorator
