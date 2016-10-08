from __future__ import unicode_literals
import os
from os.path import dirname, join
from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export, model_export


this_folder = dirname(__file__)


class SimpleType(object):
    """
    We are registering user SimpleType class to support
    simple types (integer, string) in our entity models
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
    # Built-in simple types
    # Each model will have this simple types during reference resolving but
    # these will not be a part of `types` list of EntityModel.
    type_builtins = {
            'integer': SimpleType(None, 'integer'),
            'string': SimpleType(None, 'string')
    }
    entity_mm = metamodel_from_file(join(this_folder, 'entity.tx'),
                                    classes=[SimpleType],
                                    builtins=type_builtins,
                                    debug=debug)

    return entity_mm


def main(debug=False):

    entity_mm = get_entity_mm(debug)

    # Export to .dot file for visualization
    dot_folder = join(this_folder, 'dotexport')
    if not os.path.exists(dot_folder):
        os.mkdir(dot_folder)
    metamodel_export(entity_mm, join(dot_folder, 'entity_meta.dot'))

    # Build Person model from person.ent file
    person_model = entity_mm.model_from_file(join(this_folder, 'person.ent'))

    # Export to .dot file for visualization
    model_export(person_model, join(dot_folder, 'person.dot'))


if __name__ == "__main__":
    main()
