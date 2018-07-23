import textx
def test_issue78_obj_processors_base_attr_proc():
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

