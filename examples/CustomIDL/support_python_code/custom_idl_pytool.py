from custom_idl_metamodel import Struct, RawType
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
    # TODO: unlcear why "is RawType" fails here on travis... locally it seems to import properly. Maybe double imports.
    print("typename ({}) with __name: '{}'".format(type(thetype),type(thetype).__name__))
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

def default_value_init_code(attribute,fixed_read_only=False):
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
