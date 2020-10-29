from __future__ import unicode_literals

import concurrent.futures
import multiprocessing

from textx import metamodel_from_str


# Define custom classes because default classes provided by textX are not
# picklable:
# _pickle.PicklingError: Can't pickle <textx:Second class at 140337157533528>: attribute lookup TextXClass on textx.metamodel failed
class Main(object):
    def __init__(self, seconds):
        self.seconds = seconds


class Second(object):
    def __init__(self, parent, value):
        self.parent = parent
        self.value = value


grammar = """
Main:
    'first' seconds+=Second
;

Second:
    value=INT
;

"""


def parse_document_with_threads(n):
    meta_model = metamodel_from_str(grammar, classes=[Main, Second])

    document = meta_model.model_from_str('first 1 2 3 4')
    assert len(document.seconds) == 4

    return document


def parse_document_with_processes(n):
    meta_model = metamodel_from_str(grammar, classes=[Main, Second])

    document = meta_model.model_from_str('first 1 2 2 3')
    assert len(document.seconds) == 4

    # HACK:
    # ProcessPoolExecutor doesn't work because of non-picklable parts
    # of textx. The offending fields are stripped down because they
    # are not used anyway when writing using our generator.
    document._tx_attrs = None
    document._tx_parser = None
    document._tx_attrs = None
    document._tx_metamodel = None
    document._tx_model_params = None
    document._tx_peg_rule = None

    return document


# The test always fails here:
#             # If the the attributes to the class have been
#             # collected in _tx_obj_attrs we need to do a proper
#             # initialization at this point.
#             for obj in the_parser._user_class_inst:
#                 try:
#                     # Get the attributes which have been collected
#                     # in metamodel.obj and remove them from this dict.
#                     attrs = obj.__class__._tx_obj_attrs.pop(id(obj))
#                     KeyError: 4346391576
def test_parallelization_with_threads():
    # WIP: might be easier to debug this before the code gets threaded
    parse_document_with_processes(1)

    cpus = multiprocessing.cpu_count()
    with concurrent.futures.ThreadPoolExecutor(max_workers=cpus) as executor:
        for document in executor.map(parse_document_with_threads, range(1, 101)):
            assert len(document.seconds) == 4


def test_parallelization_with_processes():
    # WIP: might be easier to debug this before the code gets threaded
    parse_document_with_processes(1)

    cpus = multiprocessing.cpu_count()
    with concurrent.futures.ProcessPoolExecutor(max_workers=cpus) as executor:
        for document in executor.map(parse_document_with_processes, range(1, 101)):
            assert len(document.seconds) == 4
