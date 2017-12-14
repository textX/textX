#######################################################################
# Name: scoping.py
# Purpose: Meta-model / Model scoping support functions.
# Author: Pierre Bayerl
# License: MIT License
#######################################################################
from textx.model import ObjCrossRef

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
    raise Exception("name '%s' not found.", name)

def scope_provider_fully_qualified_name(obj,attr,obj_ref):
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

