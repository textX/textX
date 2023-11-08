"""
Testing model and regexp with groups.
"""
import pytest  # noqa
from textx import metamodel_from_str

grammar = r'''
Model: entries += Entry;

// An entry must have a name, start with a '"""' and end with '"""'
// An entry may have links to other entries in the string with the
//    syntax '@[name]'
Entry:
    'ENTRY' name=ID ':' /\"{3}/ data*=FreeTextWithRefs datalast=LastFreeText
;

// A normal data fragment with text and a reference:
// - the text is anything which does contain '"""' and no '@'
//   (@ may be escaped)
// - the reference 'ref' is a normal textx reference
FreeTextWithRefs:
    text=/(?ms)((?:\\@|"\\@|""\\@|[^"@]|"[^"@]|""[^"@])*(?:"|"")?)@/
    '[' ref=[Entry] ']'
;

// The last text is a non-greedy "match anything" until '"""'
LastFreeText:
    text=/(?ms)(.*?)\"{3}/
;
'''


class Entry:
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def __str__(self):
        """returns the entry as model text"""
        text = ""
        for d in self.data:
            text += d.text
            text += f"@[{d.ref.name}]"
        text += self.datalast.text
        return text.replace(r"\@", "@")


def test_free_text_with_references():
    model_str = r'''
    ENTRY Hello:    """a way to say hello\@mail (see @[Hi])"""
    ENTRY Hi:       """another way to say hello (see @[Hello])"""
    ENTRY Salut:    """french "hello" (@[Hello]@[Hi]@[Bonjour]@[Salut]@[Hallo])"""
    ENTRY Hallo:    """german way to say hello (see ""@[Hello]"")"""
    ENTRY Bonjour:  """another french "\@@[Hello]", see @[Salut]"""
    ENTRY NoLink:   """Just text"""
    ENTRY Empty:    """"""
    '''  # noqa
    metamodel = metamodel_from_str(grammar, classes=[Entry], use_regexp_group=True)
    m = metamodel.model_from_str(model_str)

    assert len(m.entries[0].data) == 1
    assert len(m.entries[1].data) == 1
    assert len(m.entries[2].data) == 5
    assert len(m.entries[3].data) == 1
    assert len(m.entries[4].data) == 2
    assert len(m.entries[5].data) == 0
    assert len(m.entries[6].data) == 0

    assert m.entries[0].data[0].ref.name == "Hi"
    assert m.entries[1] == m.entries[0].data[0].ref

    assert str(m.entries[0]) == "a way to say hello@mail (see @[Hi])"
    assert str(m.entries[3]) == 'german way to say hello (see ""@[Hello]"")'
    assert str(m.entries[4]) == 'another french "@@[Hello]", see @[Salut]'
    assert str(m.entries[5]) == "Just text"
    assert str(m.entries[6]) == ""
