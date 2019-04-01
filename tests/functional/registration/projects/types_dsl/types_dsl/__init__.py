import os
import textx.scoping.tools as tools
from textx import metamodel_from_file, LanguageDesc, TextXSyntaxError


def types_metamodel():
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


types_dsl = LanguageDesc(
    name='types-dsl',
    pattern='*.etype',
    description='An example DSL for simple types definition',
    metamodel=types_metamodel)
