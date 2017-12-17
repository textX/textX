#######################################################################
# Name: scoping.py
# Purpose: Meta-model / Model scoping support functions.
# Author: Pierre Bayerl
# License: MIT License
#######################################################################
from powerline.segments.vim import file_name

from textx.model import ObjCrossRef,model_root,children,metamodel
from textx.exceptions import TextXSemanticError
from os.path import dirname,abspath
import glob

"""
This module defines scope providers to be used in conjunctions with a textx.metamodel meta model.

Example grammar snippet:
    MyAttribute:
            ref=[MyInterface|FQN] name=ID ';'
    ;

The scope providers are python callables accepting obj,attr,obj_ref:
 * obj     : the object representing a rule (e.g. "MyAttribute" in the example above
 * attr    : a reference to the attribute "ref"
 * obj_ref : a textx.model.ObjCrossRef - the reference to be resolved

The scope provides return the referenced object (e.g. a "MyInterface" object in the example above 
(or raise an Error - e.g. using _raise_semantic_error).

The scope provides are registered to the metamodel:
 * e.g., my_meta_model.register_scope_provider({"*.*":scoping.scope_provider_fully_qualified_name})
 * or: my_meta_model.register_scope_provider({"MyAttribute.ref":scoping.scope_provider_fully_qualified_name})
 * or: my_meta_model.register_scope_provider({"*.ref":scoping.scope_provider_fully_qualified_name})
 * or: my_meta_model.register_scope_provider({"MyAttribute.*":scoping.scope_provider_fully_qualified_name})

Scope providers shall be stateless or have unmodifiable state after construction: this means they should 
allow to be reused for different models (created using the same meta model) without interacting with each other.
This means, they must save their state in the corresponding model, if they need to store data (e.g., if
they load additional models from files *during name resolution*, they are not allowed to store them inside
the scope provider. Note: scope providers as normal functions (def <name>(...):..., not accessing global 
data, are safe per se.
"""

def _find_obj_fqn(p, fqn_name):
    """
    find a named object based on a qualified name ("."-separated names) starting from object p.
    :param p: the container where to start the search
    :param fqn_name: the "."-separated name
    :return: the object or None
    """
    def find_obj(parent, name):
        for attr in [a for a in dir(parent) if not a.startswith('__')
                                               and not a.startswith('_tx_')
                                               and not callable(getattr(parent, a))]:
            obj = getattr(parent, attr)
            if isinstance(obj, (list, tuple)):
                for innerobj in obj:
                    if "name" in dir(innerobj) and innerobj.name == name: return innerobj;
            else:
                if "name" in dir(obj) and obj.name == name: return obj;
        return None

    for n in str.split(fqn_name,'.'):
        obj = find_obj(p,n)
        if obj:
            p = obj;
        else:
            return None;
    return p;

def _find_referenced_obj(p, name):
    """
    Search the fully qualified name starting at relative container p.
    If no result is found, the search is continued from p.parent until the model root is reached.
    :param m: parent object
    :param n: name to be found
    :return: None or the found object
    """
    ret = _find_obj_fqn(p, name)
    if ret: return ret;
    while hasattr(p, "parent"):
        p = p.parent
        ret = _find_obj_fqn(p, name)
        if ret: return ret;
    return None

def _scope_provider_fully_qualified_name(obj,attr,obj_ref):
    """
    find a fully qualified name.
    Use this callable as scope_provider in a meta-model:
      my_metamodel.register_scope_provider({"*.*":scoping.scope_provider_fully_qualified_name})
    :obj object corresponding a instance of an object (rule instance)
    :attr the referencing attribute
    :type obj_ref: ObjCrossRef to be resolved
    :returns None or the referenced object
    """
    assert type(obj_ref) is ObjCrossRef, type(obj_ref)
    cls, obj_name = obj_ref.cls, obj_ref.obj_name
    ret = _find_referenced_obj(obj, obj_name)
    return ret

def _raise_semantic_error(msg,obj,pos):
    parser = model_root(obj)._tx_metamodel.parser
    line, col = parser.pos_to_linecol(pos)
    raise TextXSemanticError(
        '{} at {}'
        .format(msg, (line, col)),
        line=line, col=col)

def scope_provider_fully_qualified_name(obj,attr,obj_ref):
    res = _scope_provider_fully_qualified_name(obj, attr, obj_ref)
    if res: return res
    _raise_semantic_error('Unknown object "{}"'.format(obj_ref.obj_name, obj_ref.cls.__name__), obj, obj_ref.position)


class ModelRepository:
    """
    This class has the responsibility to
    hold a set of (model-identifiers, model) pairs
    as dictionary.
    In case of some scoping providers the model-identifier
    is the absolute filename of the model.
    """
    def __init__(self):
        self.filename_to_model={}
    def has_model(self, filename):
        return filename in self.filename_to_model.keys()

class GlobalModelRepository:
    """
    This class has the responsability to
    hold two ModelRepository objects:
    - one for model-local visible models
    - one for all models (globally, starting from
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
        :param model the model to be added to
        :param global_repo: the repo of another (parent) model
        """
        self.local_models = ModelRepository() # used for current model
        if all_models:
            self.all_models = all_models;     # used to reuse already loaded models
        else:
            self.all_models = ModelRepository()

    def load_model(self, filename_pattern, model):
        """
        add a new model to all releveant objects
        :param filename: the new model source
        :return: nothing
        """
        assert(model)
        self.update_model_in_repo_based_on_filename(model)
        for filename in glob.glob(filename_pattern, recursive=True):
            #print("REQUESTING {}".format("filename"))
            if not self.local_models.has_model(filename):
                if self.all_models.has_model(filename):
                    newmodel = self.all_models.filename_to_model[filename]
                else:
                    #print("LOADING {}".format(filename))
                    newmodel = metamodel(model).model_from_file(filename,
                                                                pre_ref_resolution_callback=lambda other_model:self.pre_ref_resolution_callback(other_model,filename))
                    self.all_models.filename_to_model[filename] = newmodel
                self.local_models.filename_to_model[filename] = newmodel

    def update_model_in_repo_based_on_filename(self, model):
        assert (model._tx_model_repository == self)  # makes only sense if the correct model is used
        myfilename = model._tx_filename
        if (myfilename and (not self.all_models.has_model(myfilename))):
            # make current model visible
            # print("INIT {}".format(myfilename))
            self.all_models.filename_to_model[myfilename] = model

    def pre_ref_resolution_callback(self,other_model,filename):
        print("PRE-CALLBACK{}".format(filename))
        other_model._tx_model_repository=GlobalModelRepository(self.all_models)
        self.all_models.filename_to_model[filename] = other_model

def scope_provider_fully_qualified_name_with_importURI(obj,attr,obj_ref):
    """
    like scope_provider_fully_qualified_name, but supporting Xtext-like
    importURI attributes (w/o URInamespace)
    :obj object corresponding a instance of an object (rule instance)
    :attr the referencing attribute
    :type obj_ref: ObjCrossRef to be resolved
    :returns None or the referenced object
    """
    def _load_referenced_models(model):
        visited=[]
        for obj in children(lambda x:hasattr(x,"importURI") and not x in visited,model):
            visited.append(obj)
            # TODO add multiple lookup rules for file search
            filename_pattern = abspath(dirname(model._tx_filename)+"/"+obj.importURI)
            model._tx_model_repository.load_model(filename_pattern, model=model)

    assert type(obj_ref) is ObjCrossRef, type(obj_ref)
    # 1) try to find object locally
    ret = _scope_provider_fully_qualified_name(obj,attr,obj_ref)
    if ret: return ret
    # 2) then lookup URIs...
    # TODO: raise error if lookup is not unique
    model = model_root(obj)
    # 2.1) do we already have loaded models (analysis)? No -> check/load them
    cls, obj_name = obj_ref.cls, obj_ref.obj_name
    if "_tx_model_repository" in dir(model):
        model_repository = model._tx_model_repository
    else:
        model_repository = GlobalModelRepository()
        model._tx_model_repository = model_repository
    _load_referenced_models(model)
    # 2.2) do we have loaded models?
    for m in model_repository.local_models.filename_to_model.values():
        ret = _find_referenced_obj(m, obj_name)
        if ret: return ret
    _raise_semantic_error('Unknown object "{}"'.format(obj_ref.obj_name, obj_ref.cls.__name__), obj, obj_ref.position)

class Scope_provider_fully_qualified_name_with_global_repo:
    """
    Scope provider that allows to populate the set of models used for lookup before parsing models.
    Usage:
      * create metamodel
      * create Scope_provider_fully_qualified_name_with_global_repo
      * register models used for lookup into the scope provider
    Then the scope provider is ready to be registered and used.
    """
    def __init__(self, filename_pattern=None):
        self.filename_pattern_list=[]
        if filename_pattern: self.register_models(filename_pattern)

    def register_models(self, filename_pattern):
        """
        register models into provider object - visible for all
        :param mymetamodel: the metamodel to be used to load the models
        :param filename_pattern: the pattern (e.g. file.myext or dir/**/*.myext)
        :return: nothing
        """
        self.filename_pattern_list.append(filename_pattern)

    def _load_referenced_models(self, model):
        for filename_pattern in self.filename_pattern_list:
            model._tx_model_repository.load_model(filename_pattern, model=model)

    def __call__(self, obj,attr,obj_ref):
        assert type(obj_ref) is ObjCrossRef, type(obj_ref)
        # 1) try to find object locally
        ret = _scope_provider_fully_qualified_name(obj, attr, obj_ref)
        if ret: return ret
        # 2) then lookup URIs...
        # TODO: raise error if lookup is not unique
        model = model_root(obj)
        # 2.1) do we already have loaded models (analysis)? No -> check/load them
        cls, obj_name = obj_ref.cls, obj_ref.obj_name
        if "_tx_model_repository" in dir(model):
            model_repository = model._tx_model_repository
        else:
            model_repository = GlobalModelRepository()
            model._tx_model_repository = model_repository
        self._load_referenced_models(model)
        # 2.2) do we have loaded models?
        for m in model_repository.local_models.filename_to_model.values():
            ret = _find_referenced_obj(m, obj_name)
            if ret: return ret
        _raise_semantic_error('Unknown object "{}"'.format(obj_ref.obj_name, obj_ref.cls.__name__), obj,
                              obj_ref.position)
