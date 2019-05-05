import os
from textx import metamodel_from_file, language, TextXSemanticError
import textx.scoping.tools as tools
import textx.scoping.providers as scoping_providers


@language('flow-dsl', '*.eflow')
def flow_dsl():
    """
    An example DSL for data flow processing definition
    """
    current_dir = os.path.dirname(__file__)
    p = os.path.join(current_dir, 'Flow.tx')
    flow_mm = metamodel_from_file(p, global_repository=True)

    flow_mm.register_scope_providers(
        {"*.*": scoping_providers.FQNImportURI()})

    def check_flow(f):
        if f.algo1.outp != f.algo2.inp:
            raise TextXSemanticError(
                "algo data types must match",
                **tools.get_location(f)
            )

    flow_mm.register_obj_processors({
        'Flow': check_flow
    })

    return flow_mm
