from os.path import dirname, join
from textx import metamodel_from_file
import os
import textx.scoping as scoping

def get_meta_model():
    this_folder = dirname(__file__)
    mm = metamodel_from_file( os.path.join(os.path.abspath(this_folder),'CustomIDL.tx'))
    mm.register_scope_provider({
        "*.*": scoping.ScopeProviderFullyQualifiedNamesWithImportURI()
    })
    return mm
