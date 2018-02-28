from textx import metamodel_from_str


def test_comments_skipws_optimization():
    '''
    See https://github.com/igordejanovic/textX/issues/53
    '''

    grammar = r'''
    file:
        lines*=cascading
    ;

    Comment:
        /#.*$/
    ;

    space[noskipws]:
        /[ \t]*/
    ;

    cascading:
        group | line
    ;

    line[noskipws]:
    /\s*/-
    (modifier=ID space &ID)? keyword=ID
    /\s*/-
    ;

    group:
        keyword=ID '{' entries*=cascading '}'
    ;
    '''

    mm = metamodel_from_str(grammar)

    model_str = r'''
    group
    {
        ZERO # comment
        ONE
        TWO
    }
    '''

    model = mm.model_from_str(model_str)
    assert len(model.lines) == 1
    group = model.lines[0]
    assert len(group.entries) == 3
    assert group.entries[0].keyword == 'ZERO'
    assert group.entries[0].modifier == ''
    assert group.entries[1].keyword == 'ONE'
    assert group.entries[1].modifier == ''
    assert group.entries[2].keyword == 'TWO'
    assert group.entries[2].modifier == ''
