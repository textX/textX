import textx


def test_issue89_get_obj_pos_in_text():
    mm = textx.metamodel_from_str(
        """
        Model: objs+=Obj;
        Obj: 'obj' name=ID;
    """
    )
    m = mm.model_from_str(
        """obj A
obj B
 obj C
         obj D
    """
    )
    assert textx.get_model(m.objs[0])._tx_parser.pos_to_linecol(
        m.objs[0]._tx_position
    ) == (1, 1)

    assert m._tx_parser.pos_to_linecol(m.objs[1]._tx_position) == (2, 1)
    assert m._tx_parser.pos_to_linecol(m.objs[2]._tx_position) == (3, 2)
    assert m._tx_parser.pos_to_linecol(m.objs[3]._tx_position) == (4, 10)
