def get_referenced_object(obj, dot_separated_name, desired_type=None):
    from textx.scoping import Postponed
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
            raise LookupError("{} not found".format(names[0]))
    else:
        next_obj = getattr(obj, names[0])
    if not next_obj: return Postponed()
    if len(names)>1:
        return get_referenced_object(next_obj,".".join(names[1:]))
    return next_obj
