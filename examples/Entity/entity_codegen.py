"""
An example how to generate java code from textX model using jinja2
template engine (http://jinja.pocoo.org/docs/dev/)
"""
from os import mkdir
from os.path import exists, dirname, join
import jinja2
from entity_test import get_entity_mm, Entity


def main(debug=False):

    this_folder = dirname(__file__)

    entity_mm = get_entity_mm(debug)

    # Build Person model from person.ent file
    person_model = entity_mm.model_from_file(join(this_folder, 'person.ent'))

    def javatype(s):
        """
        Maps type names from Entity to Java.
        """
        if isinstance(s, Entity):
            s = s.name

        return {
                'integer': 'int',
                'string': 'String'
        }.get(s, s)

    # Create output folder
    if not exists('srcgen'):
        mkdir('srcgen')

    # Initialize template engine.
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(this_folder))

    # Register filter for mapping Entity type names to Java type names.
    jinja_env.filters['javatype'] = javatype

    # Load Java template
    template = jinja_env.get_template('java.template')

    for entity in person_model.entities:
        # For each entity generate java file
        with open(join('srcgen',
                       "%s.java" % entity.name.capitalize()), 'w') as f:
            f.write(template.render(entity=entity))


if __name__ == "__main__":
    main()
