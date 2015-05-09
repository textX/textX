"""
An example how to generate java code from textX model using jinja2
template engine (http://jinja.pocoo.org/docs/dev/)
"""
import os
import jinja2
from entity_test import get_entity_mm, Entity

if __name__ == "__main__":

    entity_mm = get_entity_mm()

    # Build Person model from person.ent file
    person_model = entity_mm.model_from_file('person.ent')

    # Generate java code

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
    if not os.path.exists('srcgen'):
        os.mkdir('srcgen')

    # Initialize template engine.
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

    # Register filter for mapping Entity type names to Java type names.
    jinja_env.filters['javatype'] = javatype

    # Load Java template
    template = jinja_env.get_template('java.template')

    for entity in person_model.entities:
        # For each entity generate java file
        with open(os.path.join('srcgen',
                               "%s.java" % entity.name.capitalize()), 'w') as f:
            f.write(template.render(entity=entity))
