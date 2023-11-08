from textx import metamodel_from_str


def test_issue96_object_processor_on_match_rule_not_called():
    grammar = r"""
    Command:
        name=ID parameters=ParameterList
    ;

    ParameterList:
        '(' parameters*=Parameter ')'
    ;
    Parameter:
        ExplicitFloat
    ;
    ExplicitFloat:
        /-?\d+\.\d+/
    ;
    """

    code = """
    mycommand(0.1 1.1)
    """
    mm = metamodel_from_str(grammar)
    mm.register_obj_processors({"ExplicitFloat": lambda x: float(x)})

    mymodel = mm.model_from_str(code)

    first_param = mymodel.parameters.parameters[0]
    assert isinstance(first_param, float)


def test_issue96_object_processor_on_multiple_alternatives_not_called():
    grammar = r"""
    Command:
        name=ID parameters=ParameterList
    ;

    ParameterList:
        '(' parameters*=Parameter ')'
    ;

    Parameter:
        value=ExplicitFloat | value=INT
    ;

    ExplicitFloat:
        /-?\d+\.\d+/
    ;
    """

    code = """
    mycommand(0.1 1)
    """
    mm = metamodel_from_str(grammar)

    mm.register_obj_processors(
        {"Parameter": lambda x: x.value, "ExplicitFloat": lambda x: float(x)}
    )

    mymodel = mm.model_from_str(code)

    first_param = mymodel.parameters.parameters[0]

    assert isinstance(first_param, float)
