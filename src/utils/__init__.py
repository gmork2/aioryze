from collections import OrderedDict

from inputs import InputEvent


class UniqueValueOrderedDict(OrderedDict):
    """
    Ordered dictionary variant that assigns an unique
    value for each key.
    """

    def __setitem__(self, key, value: InputEvent):
        if value in self.values():
            raise ValueError
        super().__setitem__(key, value)

