# Error handling

textX will raise an error if a syntax or semantic error is detected during
meta-model or model parsing/construction.

For a syntax error `TextXSyntaxError` is raised. For a semantic error
`TextXSemanticError` is raised. Both exceptions inherit from `TextXError`. These
exceptions are located in `textx.exceptions` module.

All exceptions have `message` attribute with the error message, and `line` and
`col` attributes which represent line and column where the error was found.


!!! note

    You can also raise `TextXSemanticError` during semantic checks (e.g. in [object
    processors](metamodel.md#processors). These error classes accepts the message
    and location information (`line`, `col`, `filename`) which can be produced from
    any textX model object using `get_location`:

        from textx import get_location, TextXSemanticError
        ...
        def my_processor(entity):
            ... check something
            raise TextXSemanticError('Invalid entity', **get_location(entity))
        ...

!!! note
    See also [textx command/tool](textx_command.md) for (meta)model checking 
    from command line.
