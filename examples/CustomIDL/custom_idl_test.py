from __future__ import unicode_literals
import os
from os.path import dirname, join
from textx import metamodel_from_file
from textx.export import metamodel_export, model_export
from custom_idl import get_meta_model

this_folder = dirname(__file__)

def main(debug=False):

    mm = get_meta_model(debug)

    # Export to .dot file for visualization
    dot_folder = join(this_folder, 'dotexport')
    if not os.path.exists(dot_folder):
        os.mkdir(dot_folder)
    metamodel_export(mm, join(dot_folder, 'CustomIDL_meta.dot'))

    # Build Person model from person.ent file
    model = mm.model_from_file(join(this_folder, 'example.myidl'))

    # Export to .dot file for visualization
    model_export(model, join(dot_folder, 'example.dot'))


if __name__ == "__main__":
    main()
