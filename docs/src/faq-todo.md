# Frequently Asked Questions (to answer ASAP)
Follows some copy-paste of [questions found in the bug tracker](https://github.com/textX/textX/labels/question),
that should be at some point be integrated into the [FAQ page](faq.md), Q&A style.


## Meta-class attributes are not initialized to None for non-terminals

Consider the grammar below:

```
from textx import metamodel_from_str
grammar = """
  constant :
       float=FLOAT
     | integer=INT
     | true='true'
     | false='false'
     | string=STRING
     | string2=my_literal
  ;
my_literal : /\"(.*?)\"/ ;
"""

parser = metamodel_from_str(grammar)
ast = parser.model_from_str("true")
print("ast.float [%s]"%  str(ast.float))
print("ast.integer [%s]"%str(ast.integer))
print("ast.true [%s]"%   str(ast.true))
print("ast.false [%s]"%  str(ast.false))
print("ast.string [%s]"% str(ast.string))
print("ast.string2[%s]"% str(ast.string2))
```

producing this output:

```
ast.float [0.0]
ast.integer [0]
ast.true [true]
ast.false []
ast.string []
ast.string2[None]
```

You can see that integers initialize to 0, floats to 0.0 and other strings to
the empty string ('') while the none-terminal (string2) initializes to None.
<!-- I would argue that they should be consistent and all initialize to None
unless they parsed. Otherwise there is no reliable way to know which rule fired.
--> <!-- What if the user entered 0.0 or the empty string? -->

As documented
[here](http://textx.github.io/textX/stable/metamodel/#auto-initialization-of-the-attributes),
this behavior can be changed with `auto_init_attributes` param of meta-model
instanciation.

```admonish
Taken from [#135](https://github.com/textX/textX/issues/135).
```


## How to divide the model in two files ?

```admonish
Inspired by [#65](https://github.com/textX/textX/issues/65).
```

## How to reference non-TextX objects in the grammar ?
By providing the metamodel instanciation a function that returns the objects to
map, using `metamodel.register_scope_providers()` method.

See [this
example](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_reference_to_nontextx_attribute.py).

```admonish
Taken from [#51](https://github.com/textX/textX/issues/51).
```
