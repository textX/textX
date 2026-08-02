# Error handling

textX will raise an error if a syntax or semantic error is detected during
meta-model or model parsing/construction.

For a syntax error `TextXSyntaxError` is raised. For a semantic error
`TextXSemanticError` is raised. Both exceptions inherit from `TextXError`. These
exceptions are located in `textx.exceptions` module.

All exceptions have `message` attribute with the error message, and `line`,
`col` and `nchar` attributes which represent line, column and substring length
where the error was found.

## Errors during meta-model construction

Besides syntax errors in the grammar, `TextXSemanticError` is also raised when
the grammar is semantically invalid, even though it is syntactically well
formed. The most notable case is a [non-consuming
repetition](grammar.md#non-consuming-repetitions): a repetition (`*`, `+`, `*=`,
`+=`) whose body can match the empty string. Such grammars would hang the
parser in an infinite loop and are rejected at meta-model construction time,
with the `line`/`col` pointing to the offending repetition in the grammar:

    Model: (A)*;
    A: 'x'?;

    <file>:2:8: Non-consuming match inside repetition in rule "Model". Body
    expression may succeed without consuming input, which would cause an
    infinite loop.


```admonish
- You can also raise `TextXSemanticError` during semantic checks (e.g. in [object
  processors](metamodel.md#processors). These error classes accepts the message
  and location information (`line`, `col`, `nchar`, `filename`) which can be
  produced from any textX model object using `get_location`:

  ```python
  from textx import get_location, TextXSemanticError
  ...
  def my_processor(entity):
      ... check something
      raise TextXSemanticError('Invalid entity', **get_location(entity))
  ...
  ```


```admonish
See also [textx command/tool](textx_command.md) for (meta)model checking from
command line.
```

