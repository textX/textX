from custom_idl_metamodel import Struct, RawType
from textx import model_root

def path_to_file_name(struct):
    filename = ""
    if struct.parent.target_namespace:
        filename = "/".join(struct.parent.target_namespace.name.split("."))
    return filename


def full_path_to_file_name(struct):
    filename = ""
    if struct.parent.target_namespace:
        filename = "/".join(struct.parent.target_namespace.name.split("."))
    return filename + "/" + struct.name + ".py"


def the_package(struct):
    if struct.parent.target_namespace:
        return struct.parent.target_namespace.name + "." + struct.name
    else:
        return struct.name


def typename(thetype):
    if type(thetype) is RawType:
        if thetype.pythontype.fromlib:
            return thetype.pythontype.fromlib+"."+thetype.pythontype.type
        else:
            return thetype.pythontype.type
    else:
        return the_package(thetype)+"."+thetype.name

def default_value_init_code(attribute):
    if attribute.default_value:
        return "{}".format(attribute.default_value)
    else:
        return "{}()".format(typename(attribute.type))
