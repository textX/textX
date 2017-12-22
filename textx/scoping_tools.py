#######################################################################
# Name: scoping.py
# Purpose: Helper module for scoping support functions.
# Author: Pierre Bayerl
# License: MIT License
#######################################################################
from textx import children

def needs_to_be_resolved(parser, parent_obj,attr_name):
    """
    This function determines, if a reference (CrossReference) needs to be
    resolved or not (while creating the model, while resolving references).
    :param parser: the parser which provides the information required for this function.
                   If it is None, False is returned.
    :param parent_obj: the object containing the attribute to be resolved.
    :param attr_name: the attribute identification object.
    :return: True if the attribute needs to be resolved. Else False.
             In case of lists of references, this function return true if any of the
             references in the list needs to be resolved.
    """
    if not parser: return False
    for obj, attr, crossref in parser._crossrefs:
        if obj is parent_obj and attr_name==attr.name:
            return True
    return False

def get_list_of_concatenated_objects(obj, dot_separated_name, parser=None, lst=None):
    """
    get a list of the objects consisting of
    - obj
    - obj+"."+dot_separated_name
    - (obj+"."+dot_separated_name)+"."+dot_separated_name (called ercursively)
    Note: lists are expanded
    :param obj: the starting point
    :param dot_separated_name: "the search path" (applied recursively)
    :param parser: the parser (req. to determine if an object is Postponed)
    :param lst: the initial list (e.g. [])
    :return: the filled list (if one single object is requested, a list with one entry is returned).
    """
    from textx.scoping import Postponed
    if lst is None: lst=[]
    if not obj: return lst
    if obj in lst: return lst
    lst.append(obj)
    if type(obj) is Postponed:
        return lst
    ret = get_referenced_object(None, obj, dot_separated_name, parser)
    if type(ret) is list:
        for r in ret:
            lst = get_list_of_concatenated_objects(r, dot_separated_name, parser, lst)
    else:
        lst = get_list_of_concatenated_objects(ret, dot_separated_name, parser, lst)
    return lst

def get_referenced_object(prev_obj, obj, dot_separated_name, parser=None, desired_type=None):
    """
    get objects based on a path
    :param prev_obj: the object containing obj (req. is obj is a list)
    :param obj: the current object
    :param dot_separated_name: the attribute name "a.b.c.d" starting from obj
    :param parser: the parser
    :param desired_type: (optional)
    :return: the object if found, None if not found or Postponed() if some postponed refs are found on the path
    """
    from textx.scoping import Postponed
    assert prev_obj or not type(obj) is list
    names = dot_separated_name.split(".")
    if type(obj) is list:
        next_obj = None
        for res in obj:
            if "name" in dir(res) and getattr(res, "name") == names[0]:
                if desired_type==None or isinstance(res, desired_type):
                    next_obj = res
                else:
                    raise TypeError("{} has type {} instead of {}.".format(name, type(res).__name__, desired_type.__name__))
        if not next_obj:
            #if prev_obj needs to be resolved: return Postponed.
            if needs_to_be_resolved(parser, prev_obj,names[0]):
                return Postponed()
            else:
                return None
    elif type(obj) is Postponed:
        return Postponed()
    else:
        next_obj = getattr(obj, names[0])
    if not next_obj:
        #if obj in in crossref return Postponed, else None
        if needs_to_be_resolved(parser, obj, names[0]):
            return Postponed()
        else:
            return None
    if len(names)>1:
        return get_referenced_object(obj, next_obj,".".join(names[1:]), parser, desired_type)
    if type(next_obj) is list and needs_to_be_resolved(parser, obj,names[0]):
        return Postponed()
    return next_obj


def get_unique_named_object(root, name):
    """
    retrieves a unqiue named object (no fully qualified name)
    :param root: start of search
    :param name: name of object
    :return: the object (if not unique, raises an error)
    """
    a = children(lambda x:hasattr(x,'name') and x.name==name, root)
    assert len(a)==1
    return a[0]


def check_unique_named_object_has_class(root, name, class_name):
    """
    checks the type (type name) of an unique named object (no fully qualified name)
    :param root: start of search
    :param name: name of object
    :param class_name: the name of the type to be checked
    :return: nothing (if not unique, raises an error)
    """
    assert class_name == get_unique_named_object(root, name).__class__.__name__
