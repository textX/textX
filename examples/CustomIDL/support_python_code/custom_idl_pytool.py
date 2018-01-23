#from textx import model_root

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
    from custom_idl_metamodel import RawType
    if type(thetype) is RawType:
        if thetype.pythontype.fromlib:
            res = thetype.pythontype.fromlib+"."+thetype.pythontype.type
            #print("typename (rawtype) with lib: {}".format(res))
            return res
        else:
            res = thetype.pythontype.type
            #print("typename (rawtype) w/o lib: {}".format(res))
            return res
    else:
        res = the_package(thetype)+"."+thetype.name
        #print("typename (struct): {}".format(res))
        return res

def get_meta_info(attribute):
    from custom_idl_metamodel import RawType
    thetype = attribute.type
    if type(thetype) is RawType:
        return {"model_type_name":thetype.name, "format":thetype.pythontype.format}
    else:
        return {"model_type_name":thetype.name}

def default_value_init_code(attribute,fixed_read_only=False):
    from custom_idl_metamodel import Struct
    if attribute.default_value and not(type(attribute.type) is Struct):
        return "{}".format(attribute.default_value)
    else:
        if type(attribute.type) is Struct:
            if fixed_read_only:
                return "{}(True)".format(typename(attribute.type))
            else:
                return "{}(read_only)".format(typename(attribute.type))
        else:
            return "{}()".format(typename(attribute.type))
