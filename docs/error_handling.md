# Error handling

textX will raise an error if syntax or semantic error is detected during
meta-model or model parsing/construction.

For syntax error `TextXSyntaxError` is raised. For semantic error
`TextXSemanticError` is raised. Both exceptions inherits from `TextXError`.
These exceptions are located in `textx.exceptions` module.

All exceptions have `message` attribute with the error message and `line` and
`col` attributes with the line and column where the error is found.


