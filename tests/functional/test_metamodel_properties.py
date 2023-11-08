import textx


def test_metamodel_rule_properties():
    mm = textx.metamodel_from_str(
        r"""
        Model: 'value' a=C b=K c=N d=O e=P q=Q l=L;
        C: D|E;
        D: 'D';
        E: F;
        F: 'F';
        K: L|M;
        L: 'L' name=ID;
        M: 'M' name=ID;
        N: L|M|E;
        O: L|M|'test';
        P: '1'|'2'|'3';
        Q: '1'|'2'|'3' L;
        R: E L;
        S: E L | M;
        T: M;
    """
    )
    assert mm is not None
    all_rules = mm._current_namespace
    assert all_rules["C"]._tx_type == "match"
    assert all_rules["D"]._tx_type == "match"
    assert all_rules["E"]._tx_type == "match"
    assert all_rules["F"]._tx_type == "match"
    assert all_rules["K"]._tx_type == "abstract"
    assert all_rules["L"]._tx_type == "common"
    assert all_rules["M"]._tx_type == "common"
    assert all_rules["N"]._tx_type == "abstract"
    assert all_rules["O"]._tx_type == "abstract"
    assert all_rules["P"]._tx_type == "match"
    assert all_rules["Q"]._tx_type == "abstract"
    assert all_rules["R"]._tx_type == "abstract"
    assert all_rules["S"]._tx_type == "abstract"
    assert all_rules["T"]._tx_type == "abstract"


def test_metamodel_abstract_rule_detail1():
    mm = textx.metamodel_from_str(
        r"""
        Model: 'value' a=C b=K c=N d=O e=P q=Q l=L;
        C: D|E;
        D: 'D';
        E: F;
        F: 'F';
        K: L|M;
        L: 'L' name=ID;
        M: 'M' name=ID;
        N: L|M|E;
        O: L|M|'test';
        P: '1'|'2'|'3';
        Q: '1'|'2'|'3' L;
        R: E L;
        S: E L | M;
    """
    )
    assert mm is not None
    all_rules = mm._current_namespace
    assert all_rules["C"]._tx_type == "match"
    assert all_rules["D"]._tx_type == "match"
    assert all_rules["E"]._tx_type == "match"
    assert all_rules["F"]._tx_type == "match"
    assert all_rules["K"]._tx_type == "abstract"
    assert all_rules["L"]._tx_type == "common"
    assert all_rules["M"]._tx_type == "common"
    assert all_rules["N"]._tx_type == "abstract"
    assert all_rules["O"]._tx_type == "abstract"
    assert all_rules["P"]._tx_type == "match"
    assert all_rules["Q"]._tx_type == "abstract"
    assert all_rules["R"]._tx_type == "abstract"
    assert all_rules["S"]._tx_type == "abstract"


def test_metamodel_abstract_rule_detail2():
    # Example with "Base: Special1| (Special2 NotSpecial3)"
    # "If there are multiple common rules than the first will be used as a result and
    # the rest only for parsing" from http://textx.github.io/textX/stable/grammar/
    mm = textx.metamodel_from_str(
        r"""
        Model: 'value' x=Base;
        Base: S1 | S2 NotS3 // only use first rule (S2) as
                            // possible instance for each choice-option
            | (S4 | S5) S6; // Both S4 and S5 should be inheriting classes
                            // but not S6 as it comes second in sequence.
        S1: name=ID;
        S2: name=ID;
        NotS3: name=ID;
        S4: name=ID;
        S5: name=ID;
        S6: name=ID;
    """
    )
    assert mm is not None
    all_rules = mm._current_namespace
    assert all_rules["Base"]._tx_type == "abstract"
    assert textx.textx_isinstance(mm["S1"], mm["Base"])
    assert textx.textx_isinstance(mm["S2"], mm["Base"])
    assert not textx.textx_isinstance(mm["NotS3"], mm["Base"])  # problem

    assert set([c.__name__ for c in all_rules["Base"]._tx_inh_by]) == set(
        ["S1", "S2", "S4", "S5"]
    )
