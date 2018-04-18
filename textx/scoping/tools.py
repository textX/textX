#######################################################################
# Name: scoping.py
# Purpose: Helper module for scoping support functions.
# Author: Pierre Bayerl
# License: MIT License
#######################################################################
from textx import get_children, get_model
import re


def needs_to_be_resolved(parent_obj, attr_name):
    """
    This function determines, if a reference (CrossReference) needs to be
    resolved or not (while creating the model, while resolving references).

    Args:
        parent_obj: the object containing the attribute to be resolved.
        attr_name: the attribute identification object.

    Returns:
        True if the attribute needs to be resolved. Else False.
        In case of lists of references, this function return true if any of the
        references in the list needs to be resolved.
        Note: outside the model building process (from_file or from_str) this
        function always returns False.

    """
    if hasattr(get_model(parent_obj), "_tx_reference_resolver"):
        return get_model(parent_obj)._tx_reference_resolver. \
            has_unresolved_crossrefs(parent_obj, attr_name)
    else:
        return False


def textx_isinstance(obj, obj_cls):
    """
    This function determines, if a textx object is an instance of a
     textx class.
    Args:
        obj: the object to be analyzed
        obj_cls: the class to be checked

    Returns:
        True if obj is an instance of obj_cls.
    """
    if isinstance(obj, obj_cls):
        return True
    if hasattr(obj_cls, "_tx_fqn") and hasattr(obj, "_tx_fqn"):
        if getattr(obj_cls, "_tx_fqn") == getattr(obj_cls, "_tx_fqn"):
            return True
    if hasattr(obj_cls, "_tx_inh_by"):
        inh_by = getattr(obj_cls, "_tx_inh_by")
        for cls in inh_by:
            if (textx_isinstance(obj, cls)):
                return True
    return False


def get_list_of_concatenated_objects(obj, dot_separated_name,
                                     lst=None):
    """
    get a list of the objects consisting of
    - obj
    - obj+"."+dot_separated_name
    - (obj+"."+dot_separated_name)+"."+dot_separated_name (called ercursively)
    Note: lists are expanded

    Args:
        obj: the starting point
        dot_separated_name: "the search path" (applied recursively)
        lst: the initial list (e.g. [])

    Returns:
        the filled list (if one single object is requested, a list with one
        entry is returned).
    """
    from textx.scoping import Postponed
    if lst is None:
        lst = []
    if not obj:
        return lst
    if obj in lst:
        return lst
    lst.append(obj)
    if type(obj) is Postponed:
        return lst
    ret = get_referenced_object(None, obj, dot_separated_name)
    if type(ret) is list:
        for r in ret:
            lst = get_list_of_concatenated_objects(r, dot_separated_name, lst)
    else:
        lst = get_list_of_concatenated_objects(ret, dot_separated_name, lst)
    return lst


def get_location(model_obj):
    """
    Args:
        model_obj: the model object of interest

    Returns:
        the line, col and filename of the model element.
        The filename may be None.
        This function may be used to fill exceptions
    """
    the_model = get_model(model_obj)
    line, col = the_model._tx_parser.pos_to_linecol(
        model_obj._tx_position)
    return {"line": line, "col": col, "filename": the_model._tx_filename}


def get_parser(model_obj):
    """
    Args:
        model_obj: the model object of interest

    Returns:
        the parser associated with the element
    """
    the_model = get_model(model_obj)
    return the_model._tx_parser


def get_recursive_parent_with_typename(obj, desired_parent_typename):
    while type(obj).__name__ != desired_parent_typename and hasattr(obj,
                                                                    "parent"):
        obj = obj.parent
    if type(obj).__name__ != desired_parent_typename:
        return None
    else:
        return obj


def get_referenced_object(prev_obj, obj, dot_separated_name,
                          desired_type=None):
    """
    get objects based on a path

    Args:
        prev_obj: the object containing obj (req. is obj is a list)
        obj: the current object
        dot_separated_name: the attribute name "a.b.c.d" starting from obj
           Note: the attribute "parent(TYPE)" is a shortcut to jump to the
           parent of type "TYPE" (exact match of type name).
        desired_type: (optional)

    Returns:
        the object if found, None if not found or Postponed() if some postponed
        refs are found on the path
    """
    from textx.scoping import Postponed
    assert prev_obj or not type(obj) is list
    names = dot_separated_name.split(".")
    match = re.match(r'parent\((\w+)\)', names[0])
    if match:
        next_obj = obj
        desired_parent_typename = match.group(1)
        next_obj = get_recursive_parent_with_typename(next_obj,
                                                      desired_parent_typename)
        if next_obj:
            return get_referenced_object(None, next_obj, ".".join(names[1:]),
                                         desired_type)
        else:
            return None
    elif type(obj) is list:
        next_obj = None
        for res in obj:
            if hasattr(res, "name") and getattr(res, "name") == names[0]:
                if desired_type is None or textx_isinstance(res, desired_type):
                    next_obj = res
                else:
                    raise TypeError(
                        "{} has type {} instead of {}.".format(
                            names[0], type(res).__name__,
                            desired_type.__name__))
        if not next_obj:
            # if prev_obj needs to be resolved: return Postponed.
            if needs_to_be_resolved(prev_obj, names[0]):
                return Postponed()
            else:
                return None
    elif type(obj) is Postponed:
        return Postponed()
    else:
        next_obj = getattr(obj, names[0])
    if not next_obj:
        # if obj in in crossref return Postponed, else None
        if needs_to_be_resolved(obj, names[0]):
            return Postponed()
        else:
            return None
    if len(names) > 1:
        return get_referenced_object(obj, next_obj, ".".join(
            names[1:]), desired_type)
    if type(next_obj) is list and needs_to_be_resolved(obj, names[0]):
        return Postponed()
    return next_obj


def get_referenced_object_as_list(
        prev_obj, obj, dot_separated_name, desired_type=None):
    """
    same as get_referenced_object

    Args:
        prev_obj: see get_referenced_object
        obj: see get_referenced_object
        dot_separated_name: see get_referenced_object
        desired_type: see get_referenced_object

    Returns:
        same as get_referenced_object, but always returns a list
    """
    res = get_referenced_object(prev_obj, obj, dot_separated_name,
                                desired_type)
    if res is None:
        return []
    elif type(res) is list:
        return res
    else:
        return [res]


def get_unique_named_object_in_all_models(root, name):
    """
    retrieves a unqiue named object (no fully qualified name)

    Args:
        root: start of search (if root is a model all known models are searched
              as well)
        name: name of object

    Returns:
        the object (if not unique, raises an error)
    """
    if hasattr(root, '_tx_model_repository'):
        src = list(
            root._tx_model_repository.local_models.filename_to_model.values())
        if root not in src:
            src.append(root)
    else:
        src = [root]

    a = []
    for m in src:
        print("analyzing {}".format(m._tx_filename))
        a = a + get_children(
            lambda x: hasattr(x, 'name') and x.name == name, m)

    assert len(a) == 1
    return a[0]


def get_unique_named_object(root, name):
    """
    retrieves a unqiue named object (no fully qualified name)

    Args:
        root: start of search
        name: name of object

    Returns:
        the object (if not unique, raises an error)
    """
    a = get_children(lambda x: hasattr(x, 'name') and x.name == name, root)
    assert len(a) == 1
    return a[0]


def check_unique_named_object_has_class(root, name, class_name):
    """
    checks the type (type name) of an unique named object (no fully qualified
    name)

    Args:
        root: start of search
        name: name of object
        class_name: the name of the type to be checked

    Returns:
        nothing (if not unique, raises an error)
    """
    assert class_name == get_unique_named_object(root, name).__class__.__name__
