from textx.metamodel import metamodel_from_str

def test_issue188_skipws_1():
    mm = metamodel_from_str('''
        File: 'foo' /\s/ 'bar';
    ''', skipws=False)
    program = mm.model_from_str('foo bar')

def test_issue188_skipws_2():
    mm = metamodel_from_str('''
        File: 'foo' ' ' 'bar';
    ''', skipws=False)
    program = mm.model_from_str('foo bar')
