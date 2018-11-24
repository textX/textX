from __future__ import unicode_literals
import textx


def test_issue89_get_obj_pos_in_text():
    mm = textx.metamodel_from_str('''
        Model: objs+=Obj;
        Obj: 'obj' name=ID;
    ''')
    m = mm.model_from_str('''obj A
obj B
 obj C
         obj D
    ''')
    assert (1, 1) == textx.get_model(m.objs[0])._tx_parser.pos_to_linecol(
        m.objs[0]._tx_position)

    assert (2, 1) == m._tx_parser.pos_to_linecol(m.objs[1]._tx_position)
    assert (3, 2) == m._tx_parser.pos_to_linecol(m.objs[2]._tx_position)
    assert (4, 10) == m._tx_parser.pos_to_linecol(m.objs[3]._tx_position)
