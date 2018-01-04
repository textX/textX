from custom_idl_metamodel import Struct, RawType
from textx import model_root

def open_namespace(namespace):
    res = ""
    for n in namespace.target_namespace.name.split("."):
        res += "namespace {} {{\n".format(n)
    return res


def close_namespace(namespace):
    res = ""
    for n in namespace.target_namespace.name.split("."):
        res += "}} // namespace {}\n".format(n)
    return res


def path_to_file_name(struct):
    filename = ""
    if struct.parent.target_namespace:
        filename = "/".join(struct.parent.target_namespace.name.split("."))
    return filename


def full_path_to_file_name(struct):
    filename = ""
    if struct.parent.target_namespace:
        filename = "/".join(struct.parent.target_namespace.name.split("."))
    return filename + "/" + struct.name + ".h"


def fqn(t):
    if isinstance(t, Struct):
        struct = t
        fqn_result = ""
        if struct.parent.target_namespace:
            fqn_result = "::".join(struct.parent.target_namespace.name.split("."))
        return fqn_result + "::" + struct.name
    else:
        assert isinstance(t, RawType), "unexpected type found."
        cpptype = t.cpptype
        assert cpptype, "C++ type specification is required for {} in file {}".format(t.name, model_root(t)._tx_filename)
        return cpptype.type


def default_value_init_code(attribute, force=False):
    if attribute.default_value:
        return " = {}".format(attribute.default_value)
    else:
        if force:
            raise Exception("expected default value for attribute {}".format(attribute.name))
        else:
            return ""
