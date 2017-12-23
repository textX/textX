"""
An example how to generate java code from textX model using jinja2
template engine (http://jinja.pocoo.org/docs/dev/)
"""
from os import mkdir
from os.path import exists, dirname, join
import jinja2
from entity_test import get_entity_mm
import sys


def main(filename, debug=False):
    try:
        this_folder = dirname(__file__)

        entity_mm = get_entity_mm(debug)

        # Build Person model from person.ent file
        person_model = entity_mm.model_from_file(filename)

        def javatype(s):
            """
            Maps type names from PrimitiveType to Java.
            """
            return {
                    'integer': 'int',
                    'string': 'String'
            }.get(s.name, s.name)

        # Create output folder
        srcgen_folder = join(this_folder, 'srcgen')
        if not exists(srcgen_folder):
            mkdir(srcgen_folder)

        # Initialize template engine.
        jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(this_folder),
            trim_blocks=True,
            lstrip_blocks=True)

        # Register filter for mapping Entity type names to Java type names.
        jinja_env.filters['javatype'] = javatype

        # Load Java template
        template = jinja_env.get_template('java.template')

        for entity in person_model.entities:
            # For each entity generate java file
            with open(join(srcgen_folder,
                           "%s.java" % entity.name.capitalize()), 'w') as f:
                f.write(template.render(entity=entity))
        return 0 # no error
    except:
        e = sys.exc_info()[0]
        print("Error: {}".format(e))
        return 1


if __name__ == "__main__":
    if len(sys.argv)==1:
        this_folder = dirname(__file__)
        example = join(this_folder, 'example.myidl')
        exit(main(example))
    elif len(sys.argv)==2:
        exit(main(sys.argv[1]))
    else:
        print("usage: {} <model_file>".format(sys.argv[1])
        exit(1)
