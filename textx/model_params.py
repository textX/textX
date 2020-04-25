"""
Management of parameters passed to model_from_str or model_from_file.
"""

import sys
from functools import reduce
from collections import namedtuple
from textx.exceptions import TextXError

if sys.version < '3':
    from collections import Mapping
else:
    from collections.abc import Mapping


class ModelParams(Mapping):
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

    def have_all_parameters_been_used(self):
        return reduce(
            lambda r, k: r and (k in self.used_keys),
            self.store.keys(), True)


"""
Class describing a model parameter.
"""
ModelParamDefinition = namedtuple(
    'ModelKwargDefinition',
    ['name', 'description', 'possible_values'])


class ModelParamDefinitions(Mapping):
    """
    A class to hold possible model parameters
    together with a definition.

    This class can be used for an IDE/CLI integration.
    It is also used to check kwargs passed to the
    `model_from_str` or `model_from_file` functions.

    This check does not take place for models loaded
    from the model itself (multi meta model). In that
    case the "outer" metamodel is responsible to restrict
    the possible parameters.
    """
    def __init__(self):
        self.store = dict()

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key

    def add(self, name, description, possible_values=None):
        self.store[name] = ModelParamDefinition(name, description,
                                                possible_values)

    def check_params_and_raise_on_error(self, source, **kwargs):
        for k in kwargs.keys():
            if k not in self.store.keys():
                raise TextXError("unknown parameter {} ({})".format(k, source))
