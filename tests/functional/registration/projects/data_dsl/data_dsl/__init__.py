import os
from textx import metamodel_from_file, LanguageDesc
import textx.scoping.providers as scoping_providers


def data_metamodel():
    current_dir = os.path.dirname(__file__)
    p = os.path.join(current_dir, 'Data.tx')
    data_mm = metamodel_from_file(p, global_repository=True)

    data_mm.register_scope_providers(
        {"*.*": scoping_providers.FQNImportURI()})

    return data_mm


data_dsl = LanguageDesc(
    name='data-dsl',
    pattern='*.edata',
    description='An example DSL for data definition',
    metamodel=data_metamodel)
