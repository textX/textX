#######################################################################
# Name: scoping.__init__.py
# Purpose: Meta-model / scope providers.
# Author: Pierre Bayerl
# License: MIT License
#######################################################################

import glob
import os
import errno


class MetaModelProvider(object):
    """
    This class has the responsability to provide a meta model
    for a given file to be loaded.
    This is a global resource (no objects, just this class).

    You can register meta model instances for given file patterns.
    If no pattern matches, the same meta model as for the underlying
    model is utilized.

    Example:

        # create meta models

        mm_components   = metamodel_from_file('Components.tx')
        mm_users        = metamodel_from_file('Users.tx')

        # register meta models

        scoping.MetaModelProvider.add_metamodel("*.components", mm_components)
        scoping.MetaModelProvider.add_metamodel("*.users", mm_users)
    """
    _pattern_to_metamodel = {}  # pattern:metamodel

    @staticmethod
    def add_metamodel(pattern, the_metamodel):
        if MetaModelProvider.knows(pattern):
            raise Exception("pattern {} already registered".format(pattern))
        MetaModelProvider._pattern_to_metamodel[pattern] = the_metamodel

    @staticmethod
    def clear():
        MetaModelProvider._pattern_to_metamodel = {}

    @staticmethod
    def knows(pattern):
        return pattern in MetaModelProvider._pattern_to_metamodel.keys()

    @staticmethod
    def get_metamodel(parent_model, filename):
        from textx.model import get_metamodel
        import fnmatch
        for p, mm in MetaModelProvider._pattern_to_metamodel.items():
            if fnmatch.fnmatch(filename, p):
                # print("loading model {} with special mm".format(filename));
                return mm
        # print("loading model {} with present mm".format(filename))
        if parent_model:
            return get_metamodel(parent_model)
        else:
            raise Exception(
                "unexpected: no meta model found for {}".format(filename))


# -------------------------------------------------------------------------------------
# Scope helper classes:
# -------------------------------------------------------------------------------------

class Postponed(object):
    """
    return an object of this class to postpone a reference resolution.
    If you get circular dependencies in resolution logic, an error
    is raised.
    """

    def __init__(self):
        pass


class ModelRepository(object):
    """
    This class has the responsibility to
    hold a set of (model-identifiers, model) pairs
    as dictionary.
    In case of some scoping providers the model-identifier
    is the absolute filename of the model.
    """

    def __init__(self):
        self.filename_to_model = {}

    def has_model(self, filename):
        return filename in self.filename_to_model.keys()


class GlobalModelRepository(object):
    """
    This class has the responsability to
    hold two ModelRepository objects:
        * one for model-local visible models
        * one for all models (globally, starting from
          some root model).
    The second ModelRepository "all_models" is to cache already
    loaded models and to prevent to load one model
    twice.

    The class allows loading local models visible to
    the current model. The current model is the model
    which references this GlobalModelRepository as
    attribute _tx_model_repository

    When loading a new local model, the current
    GlobalModelRepository forwards the embedded ModelRepository
    "all_models" to the new GlobalModelRepository of the
    next model. This is done using the pre_ref_resolution_callback
    to set the neccesary information before resolving
    the references in the new loaded model.
    """

    def __init__(self, all_models=None):
        """
        create a new repo for a model
        Args:
            all_models: models to be added to this new repository.
        """
        self.local_models = ModelRepository()  # used for current model
        if all_models:
            self.all_models = all_models  # used to reuse already loaded models
        else:
            self.all_models = ModelRepository()

    def load_models_using_filepattern(
            self, filename_pattern, model, glob_args, is_main_model=False):
        """
        add a new model to all relevant objects

        Args:
            filename_pattern: models to be loaded
            model: model holding the loaded models in its _tx_model_repository
                   field (may be None).
            glob_args: arguments passed to the glob.glob function.

        Returns:
            the list of loaded models
        """
        from textx import get_metamodel
        if (model):
            self.update_model_in_repo_based_on_filename(model)
        filenames = glob.glob(filename_pattern, **glob_args)
        if len(filenames) == 0:
            raise IOError(
                errno.ENOENT, os.strerror(errno.ENOENT), filename_pattern)
        loaded_models = []
        for filename in filenames:
            the_metamodel = MetaModelProvider.get_metamodel(model, filename)
            loaded_models.append(
                self.load_model(the_metamodel, filename, is_main_model))
        return loaded_models

    def load_model(self, the_metamodel, filename, is_main_model):
        """
        load a single model

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
                    is_main_model=is_main_model)
                self.all_models.filename_to_model[filename] = new_model
            # print("ADDING {}".format(filename))
            self.local_models.filename_to_model[filename] = new_model
        return self.local_models.filename_to_model[filename]

    def update_model_in_repo_based_on_filename(self, model):
        # makes only sense if the correct model is used
        assert (model._tx_model_repository == self)
        myfilename = model._tx_filename
        if (myfilename and (not self.all_models.has_model(myfilename))):
            # make current model visible
            # print("INIT {}".format(myfilename))
            self.all_models.filename_to_model[myfilename] = model

    def pre_ref_resolution_callback(self, other_model):
        """
        (internal: used to store a model after parsing into the repository)

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

