from textx.scoping.rrel import rrel, parse
from arpeggio import ParserPython


def test_rrel_basic_parser1():
    parser = ParserPython(rrel)
    parse_tree = parser.parse("^pkg*.cls")
    assert len(parse_tree) == 2  # always true (one path, one EOF)

    parse_tree = parser.parse("obj.ref.~extension *.methods")
    assert len(parse_tree) == 2  # always true (one path, one EOF)

    parse_tree = parser.parse("instance.(type.vals)*")
    assert len(parse_tree) == 2  # always true (one path, one EOF)


def test_rrel_basic_parser2():
    tree = parse("^pkg*.cls", rule=rrel)
    tree = parse("obj.ref.~extension *.methods", rule=rrel)
    tree = parse("instance.(type.vals)*", rule=rrel)

