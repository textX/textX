def test_textx_issue155():
    import textx

    METAMODEL = textx.metamodel_from_str(
        """
    Model: expression=Expr ;

    ParenExpr: '(' Expr ')';
    Expr: ParenExpr | BaseExpr;
    BaseExpr: left=Condition operations*=Operation;
    Operation:  op=BoolOperator remaining=Condition;

    Condition: ParenExpr | RawCondition;
    RawCondition: id=Identifier op=MathOperator val=INT;

    Identifier: id=/[a-zA-Z0-9_-]+/;
    MathOperator:  op=/=|>|</;
    BoolOperator:  op=/AND|OR/;
    """
    )

    from textx import textx_isinstance

    m1 = METAMODEL.model_from_str("(b=3 OR c=4)")
    assert textx_isinstance(m1.expression, METAMODEL["BaseExpr"])
    assert textx_isinstance(m1.expression.left, METAMODEL["RawCondition"])
    assert len(m1.expression.operations) == 1
    assert m1.expression.operations[0].op.op == "OR"
    assert textx_isinstance(
        m1.expression.operations[0].remaining, METAMODEL["RawCondition"]
    )

    m2 = METAMODEL.model_from_str("a=2 AND (b=3 OR c=4)")
    assert textx_isinstance(m2.expression, METAMODEL["BaseExpr"])
    assert textx_isinstance(m2.expression.left, METAMODEL["RawCondition"])
    assert len(m2.expression.operations) == 1
    assert m2.expression.operations[0].op.op == "AND"
    assert textx_isinstance(m2.expression.operations[0].remaining, METAMODEL["BaseExpr"])
    assert textx_isinstance(
        m2.expression.operations[0].remaining.left, METAMODEL["RawCondition"]
    )
    assert len(m2.expression.operations[0].remaining.operations) == 1
    assert m2.expression.operations[0].remaining.operations[0].op.op == "OR"
    assert textx_isinstance(
        m2.expression.operations[0].remaining.operations[0].remaining,
        METAMODEL["RawCondition"],
    )
