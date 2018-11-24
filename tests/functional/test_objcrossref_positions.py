from __future__ import unicode_literals
from textx import metamodel_from_str

grammar = """
Model:
    firsts*=First
    second=Second
;
First:
    'first' name=ID
;
Second:
    'second' ref_list+=[First][',']
;
"""

modelstr = """
first Test1
first Test2

second Test1, Test2
"""


def test_objcrossref_positions():
    # get positions from string
    # definition positions
    test1_def_pos = modelstr.find('first Test1')
    test2_def_pos = modelstr.find('first Test2')
    # reference positions ( skip 30 characters )
    second_rule_pos = modelstr.find('second')
    test1_ref_pos = modelstr.find('Test1', second_rule_pos)
    test2_ref_pos = modelstr.find('Test2', second_rule_pos)

    # textx_tools_support enabled
    mm = metamodel_from_str(grammar, textx_tools_support=True)
    model = mm.model_from_str(modelstr)

    # compare positions with crossref list items
    test1_crossref = model._pos_crossref_list[0]
    test2_crossref = model._pos_crossref_list[1]

    # test1
    assert test1_crossref.ref_pos_start == test1_ref_pos
    assert test1_crossref.def_pos_start == test1_def_pos

    # test2
    assert test2_crossref.ref_pos_start == test2_ref_pos
    assert test2_crossref.def_pos_start == test2_def_pos
