import os

from textx import TextXSyntaxError, get_location, get_model, language, metamodel_from_file


@language("types-dsl", "*.etype")
def types_dsl():
    """
    An example DSL for simple types definition
    """
    current_dir = os.path.dirname(__file__)
    p = os.path.join(current_dir, "Types.tx")
    types_mm = metamodel_from_file(p, global_repository=True)
    types_mm.model_param_defs.add(
        "type_name_check", 'enables checks on the type name (default="on" or "off")'
    )

    def check_type(t):
        type_name_check = get_model(t)._tx_model_params.get(
            "type_name_check", default="on"
        )
        assert type_name_check in ["on", "off"]
        if type_name_check == "on" and t.name[0].isupper():
            raise TextXSyntaxError("types must be lowercase", **get_location(t))

    types_mm.register_obj_processors({"Type": check_type})

    return types_mm
