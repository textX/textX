# Parser configuration

## Case sensitivity

Parser is by default case sensitive. For DSLs that should be case insensitive
use `ignore_case` parameter of the meta-model constructor call.

```python
from textx import metamodel_from_file

my_metamodel = metamodel_from_file('mygrammar.tx', ignore_case=True)
```


## Whitespace handling

The parser will skip whitespaces by default. Whitespaces are spaces, tabs and
newlines by default. Skipping of the whitespaces can be disabled by `skipws` bool
parameter in the constructor call. Also, what is a whitespace can be redefined by
the `ws` string parameter.

```python
from textx import metamodel_from_file
my_metamodel = metamodel_from_file('mygrammar.tx', skipws=False, ws='\s\n')
```

Whitespaces and whitespace skipping can be defined in the grammar on the level
of a single rule by [rule modifiers](grammar.md#rule-modifiers).


## Automatic keywords

When designing a DSL, it is usually desirable to match keywords on word
boundaries. For example, if we have Entity grammar from the above, then a word
`entity` will be considered a keyword and should be matched on word boundaries
only. If we have a word `entity2` in the input string at the place where
`entity` should be matched, the match should not succeed.

We could achieve this by using a regular expression match and the word
boundaries regular expression rule for each keyword-like match.

    Enitity:
      /\bentity\b/ name=ID ...

But the grammar will be cumbersome to read.

textX can do automatic word boundary match for all keyword-like string matches.
To enable this feature set parameter `autokwd` to `True` in the constructor
call.

```python
from textx import metamodel_from_file
my_metamodel = metamodel_from_file('mygrammar.tx', autokwd=True)
```

Any simple match from the grammar that is matched by the
regular expression `[^\d\W]\w*` is considered to be a keyword.


## Memoization (a.k.a. packrat parsing)

This technique is based on memoizing result on each parsing expression rule. For
some grammars with a lot of backtracking this can yield a significant speed
increase at the expense of some memory used for the memoization cache.

Starting with textX 1.4 this feature is disabled by default. If you think that
parsing is slow, try to enable memoization by setting `memoization` parameter to
`True` during meta-model instantiation.

```python
from textx import metamodel_from_file
my_metamodel = metamodel_from_file('mygrammar.tx', memoization=True)
```

