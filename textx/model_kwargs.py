"""
Management of parameters passed to model_from_str or model_from_file.
"""

from collections.abc import Mapping


class ModelKwargs(Mapping):
    """A read only dictionary that protocols
    accessing the values.

    This way, it is possible to check after parsing a model
    if all parameters have been used by accessing the value
    directly.

    https://stackoverflow.com/questions/3387691/how-to-perfectly-override-a-dict
    https://docs.python.org/3/library/collections.abc.html
    """

    def __init__(self, *args, **kwargs):
        self.store = dict(*args, **kwargs)
        self.used_keys = set()

    def __getitem__(self, key):
        self.used_keys.add(key)
        return self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key
