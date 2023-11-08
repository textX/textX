import io

import html5lib

from textx import metamodel_from_str
from textx.export import DotRenderer, metamodel_export_tofile


def test_issue275():
    grammar = r"""

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
    """

    entity_mm = metamodel_from_str(grammar)

    out_file = io.StringIO()
    # metamodel_export(entity_mm, "test.dot")
    renderer = DotRenderer()
    metamodel_export_tofile(entity_mm, out_file, renderer)

    text = out_file.getvalue()
    assert text.__contains__("&lt;")
    assert text.__contains__("&gt;")

    table = renderer.get_match_rules_table()
    html5parser = html5lib.HTMLParser(strict=True)
    html5parser.parseFragment(table)
