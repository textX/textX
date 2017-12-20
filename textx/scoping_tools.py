def needs_to_be_resolved(parser, parent_obj,attr_name):
    for obj, attr, crossref in parser._crossrefs:
        if obj is parent_obj and attr_name==attr.name:
            return True
    return False


def get_referenced_object(prev_obj, obj, dot_separated_name, parser, desired_type=None):
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
    return next_obj
