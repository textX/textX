from textx import metamodel_from_str
from textx.export import metamodel_export_tofile, metamodel_export
import io


def test_issue275():
    grammar = '''

    Comment:
        "<:" ( !"*/" /./ )* ":>"
    ;

    EntityModel:
      entities+=Entity    // each model has one or more entities
    ;

    Entity:
      'entity' name=ID '{'
        attributes+=Attribute     // each entity has one or more attributes
      '}'
    ;

    Attribute:
      name=ID ':' type=[Entity]   // type is a reference to an entity. There are
                                  // built-in entities registered on the meta-model
                                  // for primitive types (integer, string)
    ;
    '''

    entity_mm = metamodel_from_str(grammar)

    out_file = io.StringIO()
    # export.model_export(
    #    None, "debug_test.dot", m._tx_model_repository.all_models )
    metamodel_export(entity_mm, "test.dot")
    metamodel_export_tofile(entity_mm, out_file)

    text = out_file.getvalue()
    print(text)
    assert text.__contains__("&lt;")
    assert text.__contains__("&gt;")
