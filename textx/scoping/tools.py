#######################################################################
# Name: scoping.py
# Purpose: Helper module for scoping support functions.
# Author: Pierre Bayerl
# License: MIT License
#######################################################################
import re

from textx import get_children, get_model


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
        return get_model(parent_obj)._tx_reference_resolver.has_unresolved_crossrefs(
            parent_obj, attr_name
        )
    else:
        return False


def get_list_of_concatenated_objects(def_obj, path_to_extension):
    """
    get a list of the objects consisting of
    - obj
    - obj+"."+dot_separated_name
    - (obj+"."+dot_separated_name)+"."+dot_separated_name (called recursively)
    Note: lists are expanded
    Note: this function can be used to find a class-like object and
    all its base classes (if your DSL model class-like objects).

    Args:
        obj: the starting point
        dot_separated_name: "the search path" (applied recursively)
        lst: the initial list (e.g. [])

    Returns:
        the list of objects (if one single object is requested, a list with one
        entry is returned).
    """
    from textx.scoping import Postponed

    def_objs = []
    assert def_obj is not None

    def rec_walk(obj_or_list):
        if obj_or_list is not None:
            if not isinstance(obj_or_list, list):
                obj_or_list = [obj_or_list]
            for o in obj_or_list:
                def_objs.append(o)
            for o in obj_or_list:
                if type(o) is not Postponed:
                    rec_walk(resolve_model_path(o, path_to_extension))

    rec_walk(def_obj)
    return def_objs


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
    while type(obj).__name__ != desired_parent_typename and hasattr(obj, "parent"):
        obj = obj.parent
    if type(obj).__name__ != desired_parent_typename:
        return None
    else:
        return obj


def get_named_obj_in_list(obj_list, name):
    """
    get a named object from a list (of named objects)

    Args:
        obj_list: the list to be searched
        name: the name of the requeted object

    Returns:
        the object if found (unique name), or None.
    """
    lst = list(filter(lambda x: x.name == name, obj_list))
    if len(lst) == 1:
        return lst[0]
    else:
        return None


def resolve_model_path(obj, dot_separated_name, follow_named_element_in_lists=False):
    """
    Get a model object based on a model-path starting from some
    model object. It can be used in the same way you would
    navigate through a normal instance of a model object, except:
     - "parent(TYPE)" can be used to navigate to the parent of an
       element repeatedly, until a certain type is reached (see
       unittest).
     - lists of named objects (e.g. lists of named packages) can be
       traversed, as if the named objects were part of the model
       grammar (see unittest: Syntax,
       "name_of_model_list.name_of_named_obj_in_list").
     - None/Postponed values are intercepted and lead to an overall
       return value None/Postponed.
    A use case for this function is, when a model path needs to be
    stored and executed on a previously unknown object and/or the
    Postpone/None-logic is required.

    Args:
        obj: the current object
        dot_separated_name: the attribute name "a.b.c.d" starting from obj
           Note: the attribute "parent(TYPE)" is a shortcut to jump to the
           parent of type "TYPE" (exact match of type name).
        follow_named_element_in_lists: follow named elements in list if True
           override_unresolved_lists: try to follow unresolved lists, if True

    Returns:
        the object if found, or Postponed() if some postponed
        refs are found on the path / or obj is not found
    """
    from textx.scoping import Postponed

    names = dot_separated_name.split(".")
    match = re.match(r"parent\((\w+)\)", names[0])

    if obj is None or type(obj) is Postponed:
        return obj
    elif isinstance(obj, list):
        if follow_named_element_in_lists:
            next_obj = get_named_obj_in_list(obj, names[0])
        else:
            from textx.exceptions import TextXError

            raise TextXError("unexpected: got list in path for get_referenced_object")
    elif match:
        next_obj = obj
        desired_parent_typename = match.group(1)
        next_obj = get_recursive_parent_with_typename(next_obj, desired_parent_typename)
        if type(next_obj) is Postponed:
            return next_obj
        elif next_obj is not None:
            return resolve_model_path(
                next_obj, ".".join(names[1:]), follow_named_element_in_lists
            )
        else:
            return None
    else:
        next_obj = getattr(obj, names[0])
        if needs_to_be_resolved(obj, names[0]):
            return Postponed()
        elif next_obj is None:
            return None
    if len(names) > 1:
        return resolve_model_path(
            next_obj, ".".join(names[1:]), follow_named_element_in_lists
        )
    return next_obj


def get_unique_named_object_in_all_models(root, name):
    """
    retrieves a unique named object (no fully qualified name)

    Args:
        root: start of search (if root is a model all known models are searched
              as well)
        name: name of object

    Returns:
        the object (if not unique, raises an error)
    """
    if hasattr(root, "_tx_model_repository"):
        src = list(root._tx_model_repository.local_models)
        if root not in src:
            src.append(root)
    else:
        src = [root]

    a = []
    for m in src:
        # print("analyzing {}".format(m._tx_filename))
        a = a + get_children(lambda x: hasattr(x, "name") and x.name == name, m)

    assert len(a) == 1
    return a[0]


def get_unique_named_object(root, name):
    """
    retrieves a unique named object (no fully qualified name)

    Args:
        root: start of search
        name: name of object

    Returns:
        the object (if not unique, raises an error)
    """
    a = get_children(lambda x: hasattr(x, "name") and x.name == name, root)
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
