# Test separator change in link rule references
# https://github.com/textX/textX/issues/384
from textx import metamodel_from_str


def test_ref_with_separator():
    grammar = r"""
    Model: objs+=Obj objrefs+=[Obj:ID];
    Obj: 'obj' name=ID;
    """
    mm = metamodel_from_str(grammar)
    model = mm.model_from_str(
        """
    obj first
    obj second

    first second
    """
    )

    assert len(model.objrefs) == 2
    assert model.objrefs[0].name == "first"


def test_ref_with_separator_and_rrel():
    grammar = r"""
    Model: objs+=Obj objrefs+=[Obj:Name|referenced] referenced+=Obj;
    Obj: 'obj' name=Name val=INT;
    Name: !'obj' ID;
    """
    mm = metamodel_from_str(grammar)
    model = mm.model_from_str(
        """
    obj first 1
    obj second 2

    first second

    obj first 3
    obj second 4
    """
    )

    assert len(model.objrefs) == 2
    assert model.objrefs[0].name == "first" and model.objrefs[0].val == 3


def test_ref_with_separator_backward():
    """
    Same as above but with "|" as separator.
    TODO: Remove in version 4.0.
    """
    grammar = r"""
    Model: objs+=Obj objrefs+=[Obj|ID];
    Obj: 'obj' name=ID;
    """
    mm = metamodel_from_str(grammar)
    model = mm.model_from_str(
        """
    obj first
    obj second

    first second
    """
    )

    assert len(model.objrefs) == 2
    assert model.objrefs[0].name == "first"


def test_ref_with_separator_and_rrel_backward():
    """
    Same as above but with "|" as separator.
    TODO: Remove in version 4.0.
    """
    grammar = r"""
    Model: objs+=Obj objrefs+=[Obj|Name|referenced] referenced+=Obj;
    Obj: 'obj' name=Name val=INT;
    Name: !'obj' ID;
    """
    mm = metamodel_from_str(grammar)
    model = mm.model_from_str(
        """
    obj first 1
    obj second 2

    first second

    obj first 3
    obj second 4
    """
    )

    assert len(model.objrefs) == 2
    assert model.objrefs[0].name == "first" and model.objrefs[0].val == 3
