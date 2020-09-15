import os
from textx import metamodel_from_file, language


@language('data-dsl', '*.edata')
def data_dsl():
    """
    An example DSL for data definition
    """
    current_dir = os.path.dirname(__file__)
    p = os.path.join(current_dir, 'Data.tx')
    data_mm = metamodel_from_file(p, global_repository=True)

    return data_mm
