"""
Management of parameters passed to model_from_str or model_from_file.
"""

from __future__ import annotations

from collections import namedtuple
from collections.abc import Hashable, Iterator, Mapping
from functools import reduce
from typing import Any, TypeVar

from textx.exceptions import TextXError

_KT = TypeVar("_KT", bound=Hashable)

ModelParamDefinition = namedtuple("ModelParamDefinition", ["name", "description"])


class ModelParams(Mapping[_KT, Any]):
    """A read only dictionary that protocols
    accessing the values.

    This way, it is possible to check after parsing a model
    if all parameters have been used by accessing the value
    directly.

    https://stackoverflow.com/questions/3387691/how-to-perfectly-override-a-dict
    https://docs.python.org/3/library/collections.abc.html
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.store: dict[_KT, Any] = dict(*args, **kwargs)
        self.used_keys: set[_KT] = set()

    def __getitem__(self, key: _KT) -> Any:
        self.used_keys.add(key)
        return self.store[self.__keytransform__(key)]

    def __iter__(self) -> Iterator[_KT]:
        return iter(self.store)

    def __len__(self) -> int:
        return len(self.store)

    def __keytransform__(self, key: _KT) -> _KT:
        return key

    def _have_all_parameters_been_used(self) -> bool:
        return reduce(lambda r, k: r and (k in self.used_keys), self.store.keys(), True)

    @property
    def all_used(self) -> bool:
        "returns if all parameters have been used by the meta model"
        return not (set(self.store.keys()) - set(self.used_keys))


class ModelParamDefinitions(Mapping[str, ModelParamDefinition]):
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

    def __init__(self) -> None:
        self.store: dict[str, ModelParamDefinition] = dict()

    def __getitem__(self, key: str) -> ModelParamDefinition:
        return self.store[self.__keytransform__(key)]

    def __iter__(self) -> Iterator[str]:
        return iter(self.store)

    def __len__(self) -> int:
        return len(self.store)

    def __keytransform__(self, key: str) -> str:
        return key

    def add(self, name: str, description: str) -> None:
        self.store[name] = ModelParamDefinition(name, description)

    def check_params(self, source: str, **kwargs: Any) -> None:
        for k in kwargs:
            if k not in self.store:
                raise TextXError(f"unknown parameter {k} ({source})")
