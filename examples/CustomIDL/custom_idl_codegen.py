"""
An example how to generate c++ code from textX model using jinja2
template engine (http://jinja.pocoo.org/docs/dev/)
"""

from __future__ import unicode_literals
import custom_idl
from os import mkdir,makedirs
from shutil import copyfile
from os.path import dirname, join, exists
import jinja2
from textx import children_of_type
import custom_idl_cpptool as cpptool

def main(debug=False):

    this_folder = dirname(__file__)
    mm = custom_idl.get_meta_model()

    # Build Person model from person.ent file
    idl_model = mm.model_from_file(join(this_folder, 'example.myidl'))

    srcgen_folder = join(this_folder, 'srcgen')
    if not exists(srcgen_folder):
        mkdir(srcgen_folder)

    # attributes helper
    attributes_folder = srcgen_folder+"/attributes"
    if not exists(attributes_folder):
        makedirs(attributes_folder)
    copyfile(this_folder+"/attributes.h",attributes_folder+"/attributes.h")

    # Initialize template engine.
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(this_folder),
        trim_blocks=True,
        lstrip_blocks=True)

    # Load Java template
    template = jinja_env.get_template('cpp_header.template')

    for struct in children_of_type("Struct",idl_model):
        # For each entity generate java file
        struct_folder = join(srcgen_folder, cpptool.path_to_file_name(struct))
        if not exists(struct_folder):
            makedirs(struct_folder)
        with open(join(struct_folder,
                       "{}.h".format(struct.name)), 'w') as f:
            f.write(template.render(struct=struct,
                                    cpptool = cpptool
                                    ))


if __name__ == "__main__":
    main()
