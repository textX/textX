
Error handling
==============

textX will raise an error if syntax or semantic error is detected during
meta-model or model parsing/construction.

For syntax error :code:`TextXSyntaError` is raised. For semantic error
:code:`TextXSemanticError` is raised. Both exceptions inherits from
:code:`TextXError`. These exceptions are located in :code:`textx.exceptions`
module.

All exceptions have :code:`message` attribute with the error message and
:code:`line` and :code:`col` attributes with the line and column where the error
is found.


