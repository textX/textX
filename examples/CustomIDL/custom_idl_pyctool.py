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
    return filename + "/Construct" + struct.name + ".py"


def the_package(struct):
    if struct.parent.target_namespace:
        return struct.parent.target_namespace.name + ".Construct" + struct.name
    else:
        return struct.name

def typename(thetype):
    if type(thetype) is RawType:
        return thetype.pythontype.type
    else:
        return the_package(thetype)+".format"
