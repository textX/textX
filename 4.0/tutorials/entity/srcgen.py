from os import mkdir
from os.path import exists, dirname, join
import jinja2
from textx import metamodel_from_file

this_folder = dirname(__file__)


class SimpleType:
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def __str__(self):
        return self.name


def get_entity_mm():
    """
    Builds and returns a meta-model for Entity language.
    """
    type_builtins = {
        'integer': SimpleType(None, 'integer'),
        'string': SimpleType(None, 'string')
    }
    entity_mm = metamodel_from_file(join(this_folder, 'entity.tx'),
                                    classes=[SimpleType],
                                    builtins=type_builtins)

    return entity_mm


def main(debug=False):

    # Instantiate Entity meta-model
    entity_mm = get_entity_mm()

    def javatype(s):
        """
        Maps type names from SimpleType to Java.
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

    # Build Person model from person.ent file
    person_model = entity_mm.model_from_file(join(this_folder, 'person.ent'))

    # Generate Java code
    for entity in person_model.entities:
        # For each entity generate java file
        with open(join(srcgen_folder,
                       "%s.java" % entity.name.capitalize()), 'w') as f:
            f.write(template.render(entity=entity))


if __name__ == "__main__":
    main()
