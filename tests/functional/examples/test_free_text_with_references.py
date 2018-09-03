"""
Testing model and regexp with groups.
"""
from __future__ import unicode_literals
import pytest  # noqa
import sys
from textx import metamodel_from_str

if sys.version < '3':
    text = unicode  # noqa
else:
    text = str

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


class Entry(object):
    def __init__(self, **kwargs):
        for k in kwargs.keys():
            setattr(self, k, kwargs[k])

    def __str__(self):
        """returns the entry as model text"""
        text = ""
        for d in self.data:
            text += d.text
            text += "@[{}]".format(d.ref.name)
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
    metamodel = metamodel_from_str(grammar, classes=[Entry],
                                   use_regexp_group=True)
    m = metamodel.model_from_str(model_str)

    assert 1 == len(m.entries[0].data)
    assert 1 == len(m.entries[1].data)
    assert 5 == len(m.entries[2].data)
    assert 1 == len(m.entries[3].data)
    assert 2 == len(m.entries[4].data)
    assert 0 == len(m.entries[5].data)
    assert 0 == len(m.entries[6].data)

    assert 'Hi' == m.entries[0].data[0].ref.name
    assert m.entries[1] == m.entries[0].data[0].ref

    assert 'a way to say hello@mail (see @[Hi])' == str(m.entries[0])
    assert 'german way to say hello (see ""@[Hello]"")' == str(m.entries[3])
    assert 'another french "@@[Hello]", see @[Salut]' == str(m.entries[4])
    assert 'Just text' == str(m.entries[5])
    assert '' == str(m.entries[6])
