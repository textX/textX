from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export, model_export


class Entity(object):
    """
    We are registering user Entity class to support
    primitive types (integer, string) in our entity models
    Thus, user does not need to provide integer and string
    Entities the model but can reference them in attribute types
    """
    def __init__(self, parent, name, attributes):
        self.parent = parent
        self.name = name
        self.attributes = attributes

    def __str__(self):
        return self.name


def get_entity_mm():
    """
    Builds and returns a meta-model for Entity language.
    """
    # Built-in primitive types
    # Each model will have this entities during reference resolving but
    # these entities will not be a part of `entities` list of EntityModel.
    entity_builtins = {
            'integer': Entity(None, 'integer', []),
            'string': Entity(None, 'string', [])
    }
    entity_mm = metamodel_from_file('entity.tx',
                                    classes=[Entity],  # Register Entity class
                                    builtins=entity_builtins,
                                    debug=False)

    return entity_mm

if __name__ == "__main__":

    entity_mm = get_entity_mm()

    # Export to .dot file for visualization
    metamodel_export(entity_mm, 'dotexport/entity_meta.dot')

    # Build Person model from person.ent file
    person_model = entity_mm.model_from_file('person.ent')

    # Export to .dot file for visualization
    model_export(person_model, 'dotexport/entity.dot')


