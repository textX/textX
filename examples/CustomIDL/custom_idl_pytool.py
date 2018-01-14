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


def default_value_init_code(attribute, force=False):
    if attribute.default_value:
        return " = {}".format(attribute.default_value)
    else:
        if force:
            raise Exception("expected default value for attribute {}".format(attribute.name))
        else:
            return ""
