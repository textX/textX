#######################################################################
# Name: scoping.py
# Purpose: Meta-model / Model scoping support functions.
# Author: Pierre Bayerl
# License: MIT License
#######################################################################
from textx.model import ObjCrossRef,model_root,children,metamodel
from textx.exceptions import TextXSemanticError
from os.path import dirname,abspath

def find_obj_fqn(p, fqn_name):
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

def find_referenced_obj(p,name):
    """
    Search the fully qualified name starting at relative container p.
    If no result is found, the search is continued from p.parent until the model root is reached.
    :param m: parent object
    :param n: name to be found
    :return: None or the found object
    """
    ret = find_obj_fqn(p, name)
    if ret: return ret;
    while hasattr(p, "parent"):
        p = p.parent
        ret = find_obj_fqn(p, name)
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
    ret = find_referenced_obj(obj,obj_name)
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
        # TODO do not analyze/load imports from imported models!
        ret=[]
        visited=[]
        for obj in children(lambda x:hasattr(x,"importURI") and not x in visited,model):
            visited.append(obj)
            # TODO add multiple lookup rules for file search
            filename = abspath(dirname(model._tx_filename)+"/"+obj.importURI)
            imported_model = metamodel(model).model_from_file(filename)
            ret.append( imported_model )
        return ret
    assert type(obj_ref) is ObjCrossRef, type(obj_ref)
    # 1) try to find object locally
    ret = _scope_provider_fully_qualified_name(obj,attr,obj_ref)
    if ret: return ret
    # 2) then lookup URIs...
    model = model_root(obj)
    # 2.1) do we already have loaded models (analysis)? No -> check/load them
    cls, obj_name = obj_ref.cls, obj_ref.obj_name
    if not("_tx_referenced_models" in dir(model)):
        model._tx_referenced_models = _load_referenced_models(model)
    referenced_models = model._tx_referenced_models
    # 2.2) do we have loaded models?
    for m in referenced_models:
        ret = find_referenced_obj(m,obj_name)
        if ret: return ret
    _raise_semantic_error('Unknown object "{}"'.format(obj_ref.obj_name, obj_ref.cls.__name__), obj, obj_ref.position)

