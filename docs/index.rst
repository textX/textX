.. textX documentation master file, created by
   sphinx-quickstart on Thu Aug 28 12:08:46 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to textX's documentation!
=================================

`textX`_ is a meta-language (i.e. a language for language definition) for domain-specific language
(DSL) specification in Python.

From a single grammar description textX automatically builds a meta-model (in the form of Python classes)
and a parser for your language. Parser will parse expressions on your language and automatically build a
graph of Python objects (i.e. the model) corresponding to the meta-model.

textX is inspired by Xtext - a Java based language workbench for building DSLs with full
tooling support (editors, debuggers etc.) on Eclipse platform. If you like Java and Eclipse check it out.
It is a great tool.

.. _textX: https://github.com/igordejanovic/textX/
.. _Xtext: http://www.eclipse.org/xtext/
.. _Eclipse: http://www.eclipse.org/


Features
--------

.. toctree::
   :maxdepth: 2

   features

Getting started
---------------

.. toctree::
   :maxdepth: 2

   getting_started

.. _reference-docs:

Reference documentation
-----------------------

.. toctree::
   :maxdepth: 2

   language
   syntax_metamodels
   grammar
   metamodel
   model

.. _tutorials-docs:

Tutorials
---------

.. toctree::
   :maxdepth: 2

   tutorial_basic
   tutorial_advanced




