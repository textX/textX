import textx


def test_issue78_obj_processors_base_attr_proc():
    """
    Test works in 1.6.1 (rev 84bfd8748554237dd2a0919c45e761523a4e2712)
    Test fails in e1981fb74397dc53580e19919bdec95a5e55c7ee (1.7++)
    """
    mm = textx.metamodel_from_str(
        """
        Model: base+=Base;
        Special1: '1' name=ID;
        Special2: '2' name=ID test=TestObj;
        Base: Special1|Special2;
        TestObj: name=ID;
    """
    )
    test_list = []
    mm.register_obj_processors(
        {
            "TestObj": lambda o: test_list.append(o.name),
        }
    )
    mm.model_from_str(
        """
    1 S1a
    1 S1b
    2 S2a t2a
    2 S2b t2b
    """
    )
    assert test_list == ["t2a", "t2b"]


def test_issue78_obj_processors_order_of_eval():
    """
    Test shows that different processors can be assigned to Base and
    Specialized classes (in case of ABSTRACT_RULE)
    """
    mm = textx.metamodel_from_str(
        """
        Model: base+=Base;
        Special1: '1' name=ID;
        Special2: '2' name=ID;
        Base: Special1|Special2;
    """
    )
    test_list = []
    mm.register_obj_processors(
        {
            "Base": lambda o: test_list.append("Base_" + o.name),
            "Special1": lambda o: test_list.append("Special_" + o.name),
        }
    )
    mm.model_from_str(
        """
    1 S1
    2 S2
    """
    )
    assert test_list == ["Special_S1", "Base_S1", "Base_S2"]


def test_issue78_obj_processors_replacement1_base():
    """
    Test shows that different processors can be assigned to Base and
    Specialized classes (in case of ABSTRACT_RULE)
    """
    mm = textx.metamodel_from_str(
        """
        Model: base+=Base;
        Special1: '1' name=ID;
        Special2: '2' name=ID;
        Base: Special1|Special2;
    """
    )
    test_list = []
    mm.register_obj_processors(
        {
            "Base": lambda o: "Base_" + o.name,
            "Special1": lambda o: test_list.append("Special_" + o.name),
        }
    )
    m = mm.model_from_str(
        """
    1 S1
    2 S2
    """
    )
    assert test_list == ["Special_S1"]
    assert m.base == ["Base_S1", "Base_S2"]


def test_issue78_obj_processors_replacement2_specialized():
    """
    Test shows that different processors can be assigned to Base and
    Specialized classes (in case of ABSTRACT_RULE)
    """
    mm = textx.metamodel_from_str(
        """
        Model: base+=Base;
        Special1: '1' name=ID;
        Special2: '2' name=ID;
        Base: Special1|Special2;
    """
    )
    test_list = []
    mm.register_obj_processors(
        {
            "Base": lambda o: test_list.append("Base_" + o.name),
            "Special1": lambda o: "Special_" + o.name,
        }
    )
    m = mm.model_from_str(
        """
    1 S1
    2 S2
    """
    )
    assert test_list == ["Base_S1", "Base_S2"]
    assert m.base[0] == "Special_S1"
    assert m.base[0].__class__.__name__ != "Special1"  # it is a str now...
    assert m.base[1].__class__.__name__ == "Special2"  # this one is unchanged


def test_issue78_obj_processors_replacement_domination_of_specialized():
    """
    Test shows that different processors can be assigned to Base and
    Specialized classes (in case of ABSTRACT_RULE)
    """
    mm = textx.metamodel_from_str(
        """
        Model: base+=Base;
        Special1: '1' name=ID;
        Special2: '2' name=ID;
        Base: Special1|Special2;
    """
    )
    mm.register_obj_processors(
        {
            "Base": lambda o: "Base_" + o.name,
            "Special1": lambda o: "Special_" + o.name,
        }
    )
    m = mm.model_from_str(
        """
    1 S1
    2 S2
    """
    )
    assert m.base == ["Special_S1", "Base_S2"]


def test_issue78_quickcheck_no_obj_processors_called_for_references():
    """
    This test represents just a plausibility check.
    """
    grammarA = """
    Model: a+=A | b+=B;
    A:'A' name=ID;
    B:'B' name=ID '->' a=[A];
    """

    mm = textx.metamodel_from_str(grammarA)

    import textx.scoping.providers as scoping_providers

    global_repo_provider = scoping_providers.PlainNameGlobalRepo()
    mm.register_scope_providers({"*.*": global_repo_provider})

    test_list = []
    mm.register_obj_processors(
        {
            "A": lambda o: test_list.append(o.name),
        }
    )

    # no references to A: --> obj proc called
    m1 = mm.model_from_str(
        """
    A a1 A a2 A a3
    """
    )
    assert test_list == ["a1", "a2", "a3"]

    # only references to A: --> obj proc not called
    global_repo_provider.add_model(m1)
    mm.model_from_str(
        """
    B b1 -> a1 B b2 -> a2 B b3 -> a3
    """
    )
    assert test_list == ["a1", "a2", "a3"]  # unchanged...
