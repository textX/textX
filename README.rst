textX
=====

Meta-language in `Arpeggio`_ inspired by `Xtext`_

textX follows closely the syntax and semantics of Xtext but differs in
some places and is implemented 100% in Python using Arpeggio parser. It
is fully dynamic - no code generation at all!

Installation
------------

::

    pip install textX

Quick start
-----------

There is no docs at the moment but here is a quick introduction what can
be done. For more see examples.

#. Write a language description in textX (file ``hello.tx``): ::

  HelloWorldModel:
    ‘hello’ to\_greet+={Who ‘,’}
  ;

  Who:
    name = /[^,]\*/
  ;

Description consists of a set of parsing rules which at the same time
describe Python classes that will be used to instantiate object of your model.

#. Create meta-model from textX language description:

.. code:: python

  from textx.metamodel import metamodel_from_file
  hello_meta = metamodel_from_file('hello.tx')

#. Optionally export meta-model to dot (visualize your language abstract syntax):

.. code:: python

  from textx.export import metamodel_export
  metamodel_export(hello_meta, 'hello_meta.dot')

|hello\_meta.dot|

You can see that for each rule from language description an appropriate
Python class has been created. A BASETYPE hierarchy is builtin. Each
meta-model has it.

#. Create some content (i.e. model) in your new language (``example.hello``): ::

  hello World, Solar System, Universe

Your language syntax is also described by language rules from step 1.

#. Use meta-model to create models from textual description:

.. code:: python

  example_hello_model = hello_meta.model_from_file('example.hello')

Textual model ‘example.hello’ will be parsed and transformed to a plain
Python object graph. Object classes are those defined by the meta-model.

#. Optionally export model to dot to visualize it:

.. code:: python

  from textx.export import model_export
  model_export(example_hello_model, 'example.dot')

|example.dot|

This is an object graph automatically constructed from ‘example.hello’
file.

#. Use your model: interpret it, generate code … It is a plain Python
   graph of objects with plain attributes!

.. _Arpeggio: https://github.com/igordejanovic/Arpeggio
.. _Xtext: http://www.eclipse.org/Xtext/

.. |hello\_meta.dot| image:: https://raw.githubusercontent.com/igordejanovic/textX/master/examples/hello_world/hello_meta.dot.png
.. |example.dot| image:: https://raw.githubusercontent.com/igordejanovic/textX/master/examples/hello_world/example.dot.png

