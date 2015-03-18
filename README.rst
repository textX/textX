.. image:: https://raw.githubusercontent.com/igordejanovic/textX/master/art/textX-logo.png

textX
=====

|build-status| |docs|

textX is a meta-language for building Domain-Specific Languages (DSLs) inspired
by `Xtext`_.  From a single language description (grammar) textX will build a
parser and a meta-model (a.k.a. abstract syntax) for the language.

textX follows the syntax and semantics of Xtext but differs in some places and is
implemented 100% in Python using `Arpeggio`_ parser.
It is fully dynamic - no code generation at all!

Installation
------------

::

    pip install textX

Quick start
-----------

1. Write a language description in textX (file ``hello.tx``):

::

  HelloWorldModel:
    'hello' to_greet+=Who[',']
  ;

  Who:
    name = /[^,]*/
  ;

Description consists of a set of parsing rules which at the same time
describe Python classes that will be used to instantiate object of your model.

2. Create meta-model from textX language description:

.. code:: python

  from textx.metamodel import metamodel_from_file
  hello_meta = metamodel_from_file('hello.tx')

3. Optionally export meta-model to dot (visualize your language abstract syntax):

.. code:: python

  from textx.export import metamodel_export
  metamodel_export(hello_meta, 'hello_meta.dot')

|hello_meta.dot|

You can see that for each rule from language description an appropriate
Python class has been created. A BASETYPE hierarchy is builtin. Each
meta-model has it.

4. Create some content (i.e. model) in your new language (``example.hello``):

::

  hello World, Solar System, Universe

Your language syntax is also described by language rules from step 1.

5. Use meta-model to create models from textual description:

.. code:: python

  example_hello_model = hello_meta.model_from_file('example.hello')

Textual model ‘example.hello’ will be parsed and transformed to a plain
Python object graph. Object classes are those defined by the meta-model.

6. Optionally export model to dot to visualize it:

.. code:: python

  from textx.export import model_export
  model_export(example_hello_model, 'example.dot')

|example.dot|

This is an object graph automatically constructed from ‘example.hello’
file.

7. Use your model: interpret it, generate code … It is a plain Python
   graph of objects with plain attributes!

.. _Arpeggio: https://github.com/igordejanovic/Arpeggio
.. _Xtext: http://www.eclipse.org/Xtext/

.. |hello_meta.dot| image:: https://raw.githubusercontent.com/igordejanovic/textX/master/examples/hello_world/hello_meta.dot.png
.. |example.dot| image:: https://raw.githubusercontent.com/igordejanovic/textX/master/examples/hello_world/example.dot.png


Learn more
----------

textX documentation is available `here <http://textx.readthedocs.org/en/latest/>`_.

Also, check out `examples <https://github.com/igordejanovic/textx/tree/master/examples>`_.

Open-source projects using textX
--------------------------------

- `applang`_ - Textual DSL for generating mobile applications
- `pyTabs`_ - A Domain-Specific Language (DSL) for simplified music notation
- `pyFlies`_ - DSL for cognitive experiments modeling

.. _applang: https://github.com/kosanmil/applang
.. _pyTabs: https://github.com/E2Music/pyTabs
.. _pyFlies: https://github.com/igordejanovic/pyFlies


Discuss, ask questions
----------------------
Please use `discussion forum`_ for general discussions, suggestions etc.

If you have some specific question on textX usage please use `stackoverflow`_.
Just make sure to tag your question with :code:`textx`.

Contribute
----------
textX is open for contributions. You can contribute code, documentation, tests, bug reports.
If you plan to make a contribution it would be great if you first announce that on the discussion forum.

For bug reports please use github `issue tracker`_.

For code/doc/test contributions do the following:

#. Fork the `project on github`_.
#. Clone your fork.
#. Make a branch for the new feature and switch to it.
#. Make one or more commits.
#. Push your branch to github.
#. Make a pull request. I will look at the changes and if everything is ok I will pull it in.

Note: For code contributions please try to adhere to the `PEP-8 guidelines`_. Although I am not strict in that regard it is useful to have a common ground for coding style. To make things easier use tools for code checking (PyLint, PyFlakes, pep8 etc.).


.. _discussion forum: https://groups.google.com/forum/?hl=en#!forum/textx-talk
.. _stackoverflow: http://stackoverflow.com/
.. _project on github: https://github.com/igordejanovic/textx/
.. _PEP-8 guidelines: http://legacy.python.org/dev/peps/pep-0008/
.. _issue tracker: https://github.com/igordejanovic/textx/issues/

.. |build-status| image:: https://travis-ci.org/igordejanovic/textX.svg?branch=master
   :target: https://travis-ci.org/igordejanovic/textX

.. |docs| image:: https://readthedocs.org/projects/textx/badge/?version=latest
   :target: https://readthedocs.org/projects/textx/?badge=latest
   :alt: Documentation Status


