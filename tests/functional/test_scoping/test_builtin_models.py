from textx import metamodel_from_str, register_language
from textx.scoping import ModelRepository

types_mm = metamodel_from_str(
    r"""
Model: types+=BaseType;
BaseType: 'type' name=ID;
"""
)

entity_mm_str = r"""
reference builtin_types as t
Model: entities+=Entity;
Entity: 'entity' name=ID '{'
              properties*=Property
        '}'
;
Property: name=ID ':' type=[t.BaseType:ID|+m:types];
"""


def test_builtin_models_are_searched_by_rrel():
    register_language("builtin_types", "*.type", metamodel=types_mm)

    builtin_models = ModelRepository()
    builtin_models.add_model(types_mm.model_from_str("type int type bool"))

    mm = metamodel_from_str(entity_mm_str, builtin_models=builtin_models)

    model = mm.model_from_str(
        r"""
    entity First {
        first : bool
    }
    """
    )
    assert model.entities[0].properties[0].type.__class__.__name__ == "BaseType"
    assert model.entities[0].properties[0].type.name == "bool"
