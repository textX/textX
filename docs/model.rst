.. _model:

textX models
============

Model is a python object graph (Plain Old Python Objects - POPO) constructed
from the input string that conforms to your DSL defined by the grammar and
additional :ref:`model and object processors <processors>`.

In a sense this structure is an Abstract Syntax Tree (AST) known from classic
parsing theory but it is actually a graph structure where each reference is
resolved to a proper python reference.

Each object is an instance of a class from meta-model. Classes are created
on-the-fly from grammar rules or are :ref:`supplied by the user
<custom-classes>`.

.. _linking:

Linking
-------


Builtin objects
~~~~~~~~~~~~~~~


Special attributes
------------------

Besides attributes specified by the grammar each model object has
:code:`_position` attribute that hold the position in the input string where
the object has been matched by the parser.



