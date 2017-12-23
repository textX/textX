"""
An example how to generate c++ code from textX model using jinja2
template engine (http://jinja.pocoo.org/docs/dev/)
"""

from __future__ import unicode_literals
import custom_idl
from os import mkdir
from os.path import dirname, join, exists
import jinja2
from textx import children_of_type

def main(debug=False):

    this_folder = dirname(__file__)
    mm = custom_idl.get_meta_model()

    # Build Person model from person.ent file
    idl_model = mm.model_from_file(join(this_folder, 'example.myidl'))

    srcgen_folder = join(this_folder, 'srcgen')
    if not exists(srcgen_folder):
        mkdir(srcgen_folder)

    # Initialize template engine.
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(this_folder),
        trim_blocks=True,
        lstrip_blocks=True)

    # Load Java template
    template = jinja_env.get_template('cpp_header.template')

    def render_formula(obj):
        if type(obj).__name__ == "Factor":
            if obj.ref:
                return "FACTOR(ref:{})".format( render_formula(obj.ref) )
            elif obj.sum:
                return "FACTOR(sum:{})".format(render_formula(obj.sum))
            else:
                return "FACTOR(value:{})".format(obj.value)
        elif type(obj).__name__ == "Sum":
            return "SUM({})".format("+".join( map(lambda x:render_formula(x), obj.summands) ))
        elif type(obj).__name__ == "Mul":
            return "MUL({})".format("*".join(map(lambda x: render_formula(x), obj.factors)))
        elif type(obj).__name__ == "ScalarRef":
            name = ".".join(map(lambda x:x.name, filter(lambda x: x, [obj.ref0, obj.ref1, obj.ref2])))
            return "SCALARREF({})".format(name)
        else:
            raise Exception("unexpected formula component: {}".format(type(obj).__name__))

    for struct in children_of_type("Struct",idl_model):
        # For each entity generate java file
        with open(join(srcgen_folder,
                       "%s.h" % struct.name.capitalize()), 'w') as f:
            f.write(template.render(struct=struct, render_formula=render_formula))


if __name__ == "__main__":
    main()
