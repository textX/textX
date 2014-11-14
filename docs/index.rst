.. textX documentation master file, created by
   sphinx-quickstart on Thu Aug 28 12:08:46 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to textX's documentation!
=================================

`textX`_ is a meta-language (i.e. a language for language definition)
for domain-specific language (DSL) specification in Python.

From a single grammar description textX automatically builds a meta-model
(in the form of Python classes) and a parser for your language. Parser will
parse expressions on your language and automatically build a graph of Python
objects (i.e. the model) corresponding to the meta-model.

textX is inspired by `Xtext`_ - a Java based language workbench for building
DSLs with full tooling support (editors, debuggers etc.) on Eclipse platform.
If you like Java and `Eclipse`_ check it out. It is a great tool.

Scope
-----

Each language consists of:

* Abstract syntax
* One or more concrete syntaxes
* Semantics

The focus of textX is the definition of abstract and textual concrete syntax using
single textual description. The semantic is out of scope for this tool but
it is easy to do in a pragmatic way by writing an interpreter (see :ref:`basic
tutorial` ) or code generator using one of python's template engines.

.. _textX: https://github.com/igordejanovic/textX/
.. _Xtext: http://www.eclipse.org/xtext/
.. _Eclipse: http://www.eclipse.org/

.. toctree::
   :maxdepth: 2

   features
   getting_started
   grammar
   metamodel
   model
   visualization
   tutorial_basic
   tutorial_advanced




