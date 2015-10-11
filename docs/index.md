# textX

---

[textX](https://github.com/igordejanovic/textX) is a meta-language (i.e. a
language for language definition) for domain-specific language (DSL)
specification in Python.

From a single grammar description textX automatically builds a meta-model (in
the form of Python classes) and a parser for your language. Parser will parse
expressions on your language and automatically build a graph of Python objects
(i.e. the model) corresponding to the meta-model.

textX is inspired by [Xtext](http://www.eclipse.org/xtext/) - a Java based
language workbench for building DSLs with full tooling support (editors,
debuggers etc.) on Eclipse platform.  If you like Java and
[Eclipse](http://www.eclipse.org/) check it out. It is a great tool.

# Scope

Each language consists of:

* Abstract syntax
* One or more concrete syntaxes
* Semantics

The focus of textX is the definition of abstract and textual concrete syntax
using single textual description. The semantic is out of scope for this tool but
it is easy to do in a pragmatic way by writing an interpreter (see :ref:`basic
tutorial` ) or code generator using one of python's template engines.


