Feature highlights
##################

Meta-model/parser from a single description
-------------------------------------------

A single description is used to define both language concrete syntax and its
meta-model (a.k.a. abstract syntax). See the description of :ref:`metamodel`.


Automatic model (AST) construction
----------------------------------

Parse tree will be automatically transformed to a graph of python objects
(a.k.a. the model). See the :ref:`model` section.

Python classes will be created by textX but if needed a user supplied classes
may be used. See :ref:`custom-classes`.

Automatic linking
-----------------

You can have a references to other objects in your language and the textual
representation of the reference will be resolved to proper python reference
automatically.

Automatic parent-child relationships
------------------------------------

textX will maintain a parent-child relationships imposed by the grammar.
See :ref:`parent-child`.

Parser control
--------------

Parser can be configured with regard to case handling, whitespace handling,
keyword handling etc. See :ref:`parser-config`.


Model/object post-processing
----------------------------

A callbacks (so called processors) can be registered for models and individual
classes.  This enables model/object postprocessing (validation, additional
changes etc.).  See the :ref:`processors` section.


Grammar modularization - imports
--------------------------------

Grammar can be split out in multiple files and than files/grammars can be
imported where needed. See :ref:`import` section.


Meta-model/model visualization
------------------------------

Both meta-model and parsed models can be visulized using `GraphViz`_ software
package.  See :ref:`visualization` section.


.. _GraphViz: http://graphviz.org/
