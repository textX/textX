"""
An example how to generate c++ code from textX model using jinja2
template engine (http://jinja.pocoo.org/docs/dev/)
"""

from __future__ import unicode_literals
import custom_idl_metamodel
from os import mkdir,makedirs
from shutil import copyfile
from os.path import dirname, join, exists, expanduser
import jinja2
from textx import children_of_type
import custom_idl_cpptool as cpptool

def main(model_file=None, srcgen_folder=None, debug=False, generate_cpp=True, generate_python=True):

    this_folder = dirname(__file__)
    mm = custom_idl_metamodel.get_meta_model(generate_cpp=generate_cpp, generate_python=generate_python)

    if not model_file:
        model_file = join(this_folder, 'example.myidl')

    # Build Person model from person.ent file
    idl_model = mm.model_from_file(model_file)

    if not srcgen_folder:
        srcgen_folder = join(this_folder, 'srcgen')
        if not exists(srcgen_folder):
            mkdir(srcgen_folder)
    print("generating into {}".format(srcgen_folder))

    if generate_cpp:
        generate_cpp_code(idl_model, srcgen_folder, this_folder)
    if generate_python:
        generate_python_code(idl_model, srcgen_folder, this_folder)


def generate_cpp_code(idl_model, srcgen_folder, this_folder):
    # attributes helper
    attributes_folder = srcgen_folder + "/attributes"
    if not exists(attributes_folder):
        makedirs(attributes_folder)
    copyfile(this_folder + "/support/attributes.h", attributes_folder + "/attributes.h")
    copyfile(this_folder + "/support/tools.h", attributes_folder + "/tools.h")
    # Initialize template engine.
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(this_folder + "/templates"),
        trim_blocks=True,
        lstrip_blocks=True)
    # Load Java template
    template = jinja_env.get_template('cpp_header.template')
    for struct in children_of_type("Struct", idl_model):
        # For each entity generate java file
        struct_folder = join(srcgen_folder, cpptool.path_to_file_name(struct))
        if not exists(struct_folder):
            makedirs(struct_folder)
        with open(join(struct_folder,
                       "{}.h".format(struct.name)), 'w') as f:
            f.write(template.render(struct=struct,
                                    cpptool=cpptool
                                    ))


def generate_python_code(idl_model, srcgen_folder, this_folder):
    # Initialize template engine.
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(this_folder + "/templates"),
        trim_blocks=True,
        lstrip_blocks=True)
    # Load Java template
    template = jinja_env.get_template('python.template')
    for struct in children_of_type("Struct", idl_model):
        # For each entity generate java file
        struct_folder = join(srcgen_folder, cpptool.path_to_file_name(struct))
        if not exists(struct_folder):
            makedirs(struct_folder)
        with open(join(struct_folder,
                       "{}.py".format(struct.name)), 'w') as f:
            f.write(template.render(struct=struct,
                                    cpptool=cpptool
                                    ))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='generate code for the custom idl model.')
    parser.add_argument('model_file', metavar='model_file', type=str,
                        help='model filename')
    parser.add_argument('--src-gen-folder', dest='srcgen', default="srcgen", type=str,
                        help='folder where to generate the code')
    parser.add_argument('--generate-cpp', dest='generate_cpp', default=False,
                        action='store_true', help='generate C++ code')
    parser.add_argument('--generate-python', dest='generate_python', default=False,
                        action='store_true', help='generate python code')

    args = parser.parse_args()
    main(model_file=args.model_file, srcgen_folder=expanduser(args.srcgen),
         generate_cpp=args.generate_cpp, generate_python=args.generate_python)
