from __future__ import unicode_literals
import pytest
from arpeggio import ParserPython, NoMatch, EOF
from textx.rrel import rrel_expression
from textx import metamodel_from_str


def rrel(): return rrel_expression, EOF


@pytest.fixture(scope='session')
def parser():
    return ParserPython(rrel)


valid_rrels = [
    'first',
    'first.second',
    'first.second.third',
    '^first',
    '^first.second',
    '^first.~second',
    '^first.second*',
    '^first.second*.a',
    '^first.~second*.a',
    '^(first.second)*.a',
    '^first.second*.a',
    '^first.second*.a, a.b',
    '^first.second*.a, ^ab.b',
    '^first.second*.a, ^ab.b*',
    '^parent(SomeType).second*.a, ^ab.b*',
    '^first.parent(SomeType).second*.a, ^ab.b*',
]

invalid_rrels = [
    'first^',
    'first..second',
    '^first~.second',
    '^first.second~*',
    '^first.(second*',
    '^fi(rst.second)*',
    '^first.se cond*.a',
    '^prent(SomeType).second*.a',
]


@pytest.mark.parametrize('rrel', valid_rrels)
def test_rrel_parsing_valid(parser, rrel):
    """
    Test parsing of valid RREL expressions.
    """
    parser.parse(rrel)


@pytest.mark.parametrize('rrel', invalid_rrels)
def test_rrel_parsing_invalid(parser, rrel):
    """
    Test that parsing of invalid RREL expressions result in Arpeggio NoMatch
    exception.
    """

    with pytest.raises(NoMatch):
        parser.parse(rrel)


def test_rrel_simple_path():
    """
    Test simple path RREL expression.
    """

    grammar = r'''
    S: a+=A B+=B;
    B: 'b' ref=[A||parent.a];
    A: 'a' name=ID;
    '''

    metamodel_from_str(grammar)
