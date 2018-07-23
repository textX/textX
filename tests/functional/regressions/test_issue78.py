import textx
def test_issue78_obj_processors_base_attr_proc():
    """
    Test works in 1.6.1 (rev 84bfd8748554237dd2a0919c45e761523a4e2712)
    Test fails in e1981fb74397dc53580e19919bdec95a5e55c7ee (1.7++)
    """
    mm = textx.metamodel_from_str('''
        Model: base+=Base;
        Special1: '1' name=ID;
        Special2: '2' name=ID test=TestObj;
        Base: Special1|Special2;
        TestObj: name=ID;
    ''')
    test_list=[]
    mm.register_obj_processors({
        'TestObj': lambda o: test_list.append(o.name),
    })
    m = mm.model_from_str('''
    1 S1a
    1 S1b
    2 S2a t2a
    2 S2b t2b
    ''')
    assert ['t2a','t2b'] == test_list

