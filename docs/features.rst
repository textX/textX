Meta-model/grammar from single description
------------------------------------------

Single description is used to define both language syntax and its meta-model.
See the description of the textX meta-langage.


Automatic model (AST) construction
----------------------------------

Parse tree will be automatically transformed to the graph of python objects
(a.k.a. the model). See the `model`_ section.

Automatic linking
-----------------

You can have a references to other objects in your language and the textual
representation of the reference will be resolved to proper python reference
automatically.
See the `linking` section.


Model/object post-processing
----------------------------

A callbacks (so called processors) can be registered for models and individual classes.
This enables model/object postprocessing (validation, additional changes etc.).
See the `processors`_ section.


Grammar modularization - imports
--------------------------------

Grammar can be split out in multiple files and than files/grammars can be imported where
needed. See `import`_ section.


Meta-model/model visualization
------------------------------

Both meta-model and parsed models can be visulized using `GraphViz`_ software package.
See `visualization`_ section.


.. _GraphViz: http://
