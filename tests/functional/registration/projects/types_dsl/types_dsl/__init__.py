import os
import textx.scoping.tools as tools
from textx import metamodel_from_file, TextXSyntaxError, language
from textx import get_model


@language('types-dsl', '*.etype')
def types_dsl():
    """
    An example DSL for simple types definition
    """
    current_dir = os.path.dirname(__file__)
    p = os.path.join(current_dir, 'Types.tx')
    types_mm = metamodel_from_file(p, global_repository=True)
    types_mm._tx_model_param_definitions.add(
        'type_name_check',
        'enabled checks on the type name',
        possible_values=['on', 'off']
    )

    def check_type(t):
        type_name_check = get_model(t)._tx_model_params.get(
            'type_name_check', default='on'
        )
        if type_name_check == 'on':
            if t.name[0].isupper():
                raise TextXSyntaxError(
                    "types must be lowercase",
                    **tools.get_location(t)
                )

    types_mm.register_obj_processors({
        'Type': check_type
    })

    return types_mm
