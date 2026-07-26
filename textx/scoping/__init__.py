#######################################################################
# Name: scoping.__init__.py
# Purpose: Meta-model / scope providers.
# Author: Pierre Bayerl
# License: MIT License
#######################################################################

from __future__ import annotations

import errno
import glob
import os
from collections.abc import Iterator
from os.path import abspath, exists, join
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from textx.metamodel import TextXMetaMetaModel, TextXMetaModel


def metamodel_for_file_or_default_metamodel(
    filename: str,
    the_metamodel: TextXMetaModel | TextXMetaMetaModel | None,
) -> TextXMetaModel | TextXMetaMetaModel:
    from textx import metamodel_for_file
    from textx.exceptions import TextXRegistrationError

    try:
        return metamodel_for_file(filename)
    except TextXRegistrationError:
        assert the_metamodel is not None
        return the_metamodel


# -----------------------------------------------------------------------------
# Scope helper classes:
# -----------------------------------------------------------------------------


class Postponed:
    """
    Return an object of this class to postpone a reference resolution.
    If you get circular dependencies in resolution logic, an error
    is raised.
    """


class ModelRepository:
    """
    This class has the responsibility to hold a set of (model-identifiers,
    model) pairs as dictionary.
    In case of some scoping providers the model-identifier is the absolute
    filename of the model.
    """

    def __init__(self) -> None:
        self.name_idx: int = 1
        self.filename_to_model: dict[str, Any] = {}

    def has_model(self, filename: str) -> bool:
        return abspath(filename) in self.filename_to_model

    def add_model(self, model: Any) -> None:
        if model._tx_filename:
            filename = abspath(model._tx_filename)
        else:
            filename = f"builtin_model_{self.name_idx}"
            self.name_idx += 1
        self.filename_to_model[filename] = model

    def remove_model(self, model: Any) -> None:
        filename = None
        for f, m in self.filename_to_model.items():
            if m == model:
                filename = f
        if filename:
            del self.filename_to_model[filename]

    def __contains__(self, filename: str) -> bool:
        return self.has_model(filename)

    def __iter__(self) -> Iterator[Any]:
        return iter(self.filename_to_model.values())

    def __len__(self) -> int:
        return len(self.filename_to_model)

    def __getitem__(self, filename: str) -> Any:
        return self.filename_to_model[filename]

    def __setitem__(self, filename: str, model: Any) -> None:
        self.filename_to_model[filename] = model


class GlobalModelRepository:
    """
    This class has the responsibility to hold two ModelRepository objects:

        - one for model-local visible models
        - one for all models (globally, starting from some root model).

    The second `ModelRepository` `all_models` is to cache already loaded models
    and to prevent to load one model twice.

    The class allows loading local models visible to the current model. The
    current model is the model which references this `GlobalModelRepository` as
    attribute `_tx_model_repository`

    When loading a new local model, the current `GlobalModelRepository`
    forwards the embedded `ModelRepository` `all_models` to the new
    `GlobalModelRepository` of the next model. This is done using the
    `pre_ref_resolution_callback` to set the necessary information before
    resolving the references in the new loaded model.

    """

    def __init__(self, all_models: ModelRepository | None = None) -> None:
        """
        Create a new repo for a model.

        Args:
            all_models: models to be added to this new repository.
        """
        self.local_models: ModelRepository = ModelRepository()
        if all_models is not None:
            self.all_models: ModelRepository = all_models
        else:
            self.all_models = ModelRepository()

    def remove_model(self, model: Any) -> None:
        self.all_models.remove_model(model)
        self.local_models.remove_model(model)

    def remove_models(self, models: list[Any]) -> None:
        for m in models:
            self.remove_model(m)

    def load_models_using_filepattern(
        self,
        filename_pattern: str,
        model: Any,
        glob_args: dict[str, Any],
        is_main_model: bool = False,
        encoding: str = "utf-8",
        add_to_local_models: bool = True,
        model_params: Any = None,
    ) -> list[Any]:
        """
        Add a new model to all relevant objects.

        Args:
            filename_pattern: models to be loaded
            model: model holding the loaded models in its _tx_model_repository
                   field (may be None).
            glob_args: arguments passed to the glob.glob function.

        Returns:
            the list of loaded models
        """
        from textx import get_metamodel

        if model is not None:
            self.update_model_in_repo_based_on_filename(model)
            the_metamodel: Any = get_metamodel(model)
        else:
            the_metamodel = None
        filenames = glob.glob(filename_pattern, **glob_args)
        if len(filenames) == 0:
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), filename_pattern)
        loaded_models: list[Any] = []
        for filename in filenames:
            the_metamodel = metamodel_for_file_or_default_metamodel(
                filename, the_metamodel
            )
            loaded_models.append(
                self.load_model(
                    the_metamodel,
                    filename,
                    is_main_model,
                    encoding=encoding,
                    add_to_local_models=add_to_local_models,
                    model_params=model_params,
                )
            )
        return loaded_models

    def load_model_using_search_path(
        self,
        filename: str,
        model: Any,
        search_path: list[str],
        is_main_model: bool = False,
        encoding: str = "utf8",
        add_to_local_models: bool = True,
        model_params: Any = None,
    ) -> Any:
        """
        Add a new model to all relevant objects

        Args:
            filename: models to be loaded
            model: model holding the loaded models in its _tx_model_repository
                   field (may be None).
            search_path: list of search directories.

        Returns:
            the loaded model
        """
        from textx import get_metamodel

        if model:
            self.update_model_in_repo_based_on_filename(model)
        for the_path in search_path:
            full_filename = join(the_path, filename)
            if exists(full_filename):
                the_metamodel: TextXMetaModel | TextXMetaMetaModel | None = (
                    get_metamodel(model) if model is not None else None
                )
                the_metamodel = metamodel_for_file_or_default_metamodel(
                    filename, the_metamodel
                )
                return self.load_model(
                    the_metamodel,
                    full_filename,
                    is_main_model,
                    encoding=encoding,
                    add_to_local_models=add_to_local_models,
                    model_params=model_params,
                )

        raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), filename)

    def load_model(
        self,
        the_metamodel: Any,
        filename: str,
        is_main_model: bool,
        encoding: str = "utf-8",
        add_to_local_models: bool = True,
        model_params: Any = None,
    ) -> Any:
        """
        Load a single model

        Args:
            the_metamodel: the metamodel used to load the model
            filename: the model to be loaded (if not cached)

        Returns:
            the loaded/cached model
        """
        assert model_params is not None, "model_params needs to be specified"

        filename = abspath(filename)
        if not self.local_models.has_model(filename):
            if self.all_models.has_model(filename):
                new_model = self.all_models[filename]
            else:
                # all models loaded here get their references resolved from the
                # root model
                new_model = the_metamodel.internal_model_from_file(
                    filename,
                    pre_ref_resolution_callback=lambda other_model: (
                        self.pre_ref_resolution_callback(other_model)
                    ),
                    is_main_model=is_main_model,
                    encoding=encoding,
                    model_params=model_params,
                )
                self.all_models[filename] = new_model
            if add_to_local_models:
                self.local_models[filename] = new_model
        else:
            pass

        assert filename in self.all_models  # to be sure...
        return self.all_models[filename]

    def _add_model(self, model: Any) -> None:
        filename = self.update_model_in_repo_based_on_filename(model)
        self.local_models[filename] = model

    def update_model_in_repo_based_on_filename(self, model: Any) -> str:
        """
        Adds a model to the repo (not initially visible)

        Args:
            model: the model to be added. If the model
            has no filename, a name is invented

        Returns:
            the filename of the model added to the repo
        """
        if model._tx_filename is None:
            for fn in self.all_models.filename_to_model:
                if self.all_models.filename_to_model[fn] == model:
                    return fn
            i = 0
            while self.all_models.has_model(f"anonymous{i}"):
                i += 1
            myfilename = f"anonymous{i}"
            self.all_models[myfilename] = model
        else:
            myfilename = abspath(model._tx_filename)
            if not self.all_models.has_model(myfilename):
                self.all_models[myfilename] = model
        return myfilename

    def pre_ref_resolution_callback(self, other_model: Any) -> None:
        """
        internal: used to store a model after parsing into the repository

        Args:
            other_model: the parsed model

        Returns:
            nothing
        """
        filename = other_model._tx_filename
        assert filename
        filename = abspath(filename)
        other_model._tx_model_repository = GlobalModelRepository(self.all_models)
        self.all_models[filename] = other_model


class ModelLoader:
    """
    This class is an interface to mark a scope provider as an additional model
    loader.
    """

    def __init__(self) -> None:
        pass

    def load_models(self, model: Any, encoding: str = "utf-8") -> None:
        pass


def get_all_models_including_attached_models(model: Any) -> list[Any]:
    """
    get a list of all models stored within a model
    (including the owning model).

    @deprecated (BIC): use model_object.get_included_models()

    Args:
        model: the owning model

    Returns:
        a list of all models
    """
    return get_included_models(model)


def get_included_models(model: Any) -> list[Any]:
    """
    get a list of all models stored within a model
    (including the owning model).

    Args:
        model: the owning model

    Returns:
        a list of all models
    """
    if hasattr(model, "_tx_model_repository"):
        models = list(model._tx_model_repository.all_models)
        if model not in models:
            models.append(model)
    else:
        models = [model]
    return models


def is_file_included(filename: str, model: Any) -> bool:
    """
    Determines if a file is included by a model. Also checks
    for indirect inclusions (files included by included files).

    Args:
        filename: the file to be checked (filename is normalized)
        model: the owning model

    Returns:
        True if the file is included, else False
        (Note: if no _tx_model_repository is present,
        the function always returns False)
    """
    if hasattr(model, "_tx_model_repository"):
        all_entries = model._tx_model_repository.all_models
        return all_entries.has_model(filename)
    else:
        return False


def remove_models_from_repositories(
    models: list[Any], models_to_be_removed: list[Any]
) -> None:
    """
    Remove models from all relevant repositories (_tx_model_repository
    of models and related metamodel(s), if applicable).

    Args:
        models: the list of models from
               which the models_to_be_removed have to be removed.
        models_to_be_removed: models to be removed

    Returns:
        None
    """
    assert isinstance(models, list)
    for model in models:
        if hasattr(model._tx_metamodel, "_tx_model_repository"):
            model._tx_metamodel._tx_model_repository.remove_models(models_to_be_removed)
        if hasattr(model, "_tx_model_repository"):
            model._tx_model_repository.remove_models(models_to_be_removed)
