import os
from os.path import dirname, join
from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export, model_export


this_folder = dirname(__file__)


class PrimitiveType(object):
    """
    We are registering user PrimitiveType class to support
    primitive types (integer, string) in our entity models
    Thus, user doesn't need to provide integer and string
    types in the model but can reference them in attribute types nevertheless.
    """
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def __str__(self):
        return self.name


def get_entity_mm(debug=False):
    """
    Builds and returns a meta-model for Entity language.
    """
    # Built-in primitive types
    # Each model will have this primitive types during reference resolving but
    # these will not be a part of `types` list of EntityModel.
    type_builtins = {
            'integer': PrimitiveType(None, 'integer'),
            'string': PrimitiveType(None, 'string')
    }
    entity_mm = metamodel_from_file(join(this_folder, 'entity.tx'),
                                    classes=[PrimitiveType],
                                    builtins=type_builtins,
                                    debug=debug)

    return entity_mm


def main(debug=False):

    entity_mm = get_entity_mm(debug)

    # Export to .dot file for visualization
    os.mkdir(join(this_folder, 'dotexport'))
    metamodel_export(entity_mm, join(this_folder,
                                     'dotexport', 'entity_meta.dot'))

    # Build Person model from person.ent file
    person_model = entity_mm.model_from_file(join(this_folder, 'person.ent'))

    # Export to .dot file for visualization
    model_export(person_model, join(this_folder, 'dotexport', 'entity.dot'))


if __name__ == "__main__":
    main()
