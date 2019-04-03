#######################################################################
# Name: scoping.__init__.py
# Purpose: Meta-model / scope providers.
# Author: Pierre Bayerl
# License: MIT License
#######################################################################

import glob
import os
import errno
from os.path import join, exists


def metamodel_for_file_or_default_metamodel(filename, the_metamodel):
    from textx import metamodel_for_file
    from textx.exceptions import TextXRegistrationError
    try:
        return metamodel_for_file(filename)
    except TextXRegistrationError:
        return the_metamodel


# -----------------------------------------------------------------------------
# Scope helper classes:
# -----------------------------------------------------------------------------

class Postponed(object):
    """
    Return an object of this class to postpone a reference resolution.
    If you get circular dependencies in resolution logic, an error
    is raised.
    """


class ModelRepository(object):
    """
    This class has the responsibility to hold a set of (model-identifiers,
    model) pairs as dictionary.
    In case of some scoping providers the model-identifier is the absolute
    filename of the model.
    """

    def __init__(self):
        self.filename_to_model = {}

    def has_model(self, filename):
        return filename in self.filename_to_model


class GlobalModelRepository(object):
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

    def __init__(self, all_models=None):
        """
        Create a new repo for a model.

        Args:
            all_models: models to be added to this new repository.
        """
        self.local_models = ModelRepository()  # used for current model
        if all_models:
            self.all_models = all_models  # used to reuse already loaded models
        else:
            self.all_models = ModelRepository()

    def load_models_using_filepattern(
            self, filename_pattern, model, glob_args, is_main_model=False,
            encoding='utf-8', add_to_local_models=True):
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
            the_metamodel = get_metamodel(model)  # default metamodel
        else:
            the_metamodel = None
        filenames = glob.glob(filename_pattern, **glob_args)
        if len(filenames) == 0:
            raise IOError(
                errno.ENOENT, os.strerror(errno.ENOENT), filename_pattern)
        loaded_models = []
        for filename in filenames:
            the_metamodel = metamodel_for_file_or_default_metamodel(
                filename, the_metamodel)
            loaded_models.append(
                self.load_model(the_metamodel, filename, is_main_model,
                                encoding=encoding,
                                add_to_local_models=add_to_local_models))
        return loaded_models

    def load_model_using_search_path(
            self, filename, model, search_path, is_main_model=False,
            encoding='utf8', add_to_local_models=True):
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
            # print(full_filename)
            if exists(full_filename):
                if model is not None:
                    the_metamodel = get_metamodel(model)
                else:
                    the_metamodel = None
                the_metamodel = metamodel_for_file_or_default_metamodel(
                    filename, the_metamodel)
                return self.load_model(the_metamodel,
                                       full_filename,
                                       is_main_model,
                                       encoding=encoding,
                                       add_to_local_models=add_to_local_models)

        raise IOError(
            errno.ENOENT, os.strerror(errno.ENOENT), filename)

    def load_model(
            self, the_metamodel, filename, is_main_model, encoding='utf-8',
            add_to_local_models=True):
        """
        Load a single model

        Args:
            the_metamodel: the metamodel used to load the model
            filename: the model to be loaded (if not cached)

        Returns:
            the loaded/cached model
        """

        if not self.local_models.has_model(filename):
            if self.all_models.has_model(filename):
                new_model = self.all_models.filename_to_model[filename]
            else:
                # print("LOADING {}".format(filename))
                # all models loaded here get their references resolved from the
                # root model
                new_model = the_metamodel.internal_model_from_file(
                    filename, pre_ref_resolution_callback=lambda
                    other_model: self.pre_ref_resolution_callback(other_model),
                    is_main_model=is_main_model, encoding=encoding)
                self.all_models.filename_to_model[filename] = new_model
            # print("ADDING {}".format(filename))
            if add_to_local_models:
                self.local_models.filename_to_model[filename] = new_model
        assert self.all_models.has_model(filename)  # to be sure...
        return self.all_models.filename_to_model[filename]

    def _add_model(self, model):
        filename = self.update_model_in_repo_based_on_filename(model)
        self.local_models.filename_to_model[filename] = model

    def update_model_in_repo_based_on_filename(self, model):
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
            while self.all_models.has_model("anonymous{}".format(i)):
                i += 1
            myfilename = "anonymous{}".format(i)
            self.all_models.filename_to_model[myfilename] = model
        else:
            myfilename = model._tx_filename
            if (not self.all_models.has_model(myfilename)):
                self.all_models.filename_to_model[myfilename] = model
        return myfilename

    def pre_ref_resolution_callback(self, other_model):
        """
        internal: used to store a model after parsing into the repository

        Args:
            other_model: the parsed model

        Returns:
            nothing
        """
        # print("PRE-CALLBACK{}".format(filename))
        filename = other_model._tx_filename
        assert (filename)
        other_model._tx_model_repository = \
            GlobalModelRepository(self.all_models)
        self.all_models.filename_to_model[filename] = other_model


class ModelLoader(object):
    """
    This class is an interface to mark a scope provider as an additional model
    loader.
    """

    def __init__(self):
        pass

    def load_models(self, model):
        pass


def get_all_models_including_attached_models(model):
    """
    get a list of all models stored within a model
    (including the owning model).

    Args:
        model: the owning model

    Returns:
        a list of all models
    """
    if (hasattr(model, "_tx_model_repository")):
        models = list(
            model._tx_model_repository.all_models.filename_to_model.values())
        if model not in models:
            models.append(model)
    else:
        models = [model]
    return models
