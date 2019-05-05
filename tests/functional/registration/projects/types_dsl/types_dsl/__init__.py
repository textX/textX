import os
import textx.scoping.tools as tools
from textx import metamodel_from_file, TextXSyntaxError, language


@language('types-dsl', '*.etype')
def types_dsl():
    """
    An example DSL for simple types definition
    """
    current_dir = os.path.dirname(__file__)
    p = os.path.join(current_dir, 'Types.tx')
    types_mm = metamodel_from_file(p, global_repository=True)

    def check_type(t):
        if t.name[0].isupper():
            raise TextXSyntaxError(
                "types must be lowercase",
                **tools.get_location(t)
            )

    types_mm.register_obj_processors({
        'Type': check_type
    })

    return types_mm
