import os

from textx import language, metamodel_from_file


@language("data-dsl", "*.edata")
def data_dsl():
    """
    An example DSL for data definition
    """
    current_dir = os.path.dirname(__file__)
    p = os.path.join(current_dir, "Data.tx")
    data_mm = metamodel_from_file(p, global_repository=True)

    return data_mm
