![textX logo](images/textX-logo.svg)

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

See [Getting Started guide](getting_started.md) to get you going. Also, you can
check out [examples](https://github.com/igordejanovic/textX/tree/master/examples/).


## Feature highlights

* **Meta-model/parser from a single description**

    A single description is used to define both language concrete syntax and its
    meta-model (a.k.a. abstract syntax). See the description of
    [grammar](grammar.md) and [metamodel](metamodel.md).

* **Automatic model (AST) construction**

    Parse tree will be automatically transformed to a graph of python objects
    (a.k.a. the model). See the [model](model.md) section.

    Python classes will be created by textX but if needed a user supplied
    classes may be used. See [custom classes](metamodel.md#custom-classes).

* **Automatic linking**

    You can have a references to other objects in your language and the textual
    representation of the reference will be resolved to proper python reference
    automatically.

* **Automatic parent-child relationships**

    textX will maintain a parent-child relationships imposed by the grammar.
    See [parent-child relationships](metamodel.md#parent-child-relationships).

* **Parser control**

    Parser can be configured with regard to case handling, whitespace handling,
    keyword handling etc. See [parser
    configuration](metamodel.md#parser-configuration).


* **Model/object post-processing**

    A callbacks (so called processors) can be registered for models and
    individual classes.  This enables model/object postprocessing (validation,
    additional changes etc.).  See [processors](metamodel.md#processors) section.


* **Grammar modularization - imports**

    Grammar can be split out in multiple files and than files/grammars can be
    imported where needed. See [Grammar
    modularization](grammar.md#grammar-modularization).


* **Meta-model/model visualization**

    Both meta-model and parsed models can be visulized using
    [GraphViz](http://graphviz.org/) software package. See
    [visualization](visualization.md) section.


## Open-source projects using textX

- [applang](https://github.com/kosanmil/applang) - Textual DSL for generating mobile applications
- [pyTabs](https://github.com/E2Music/pyTabs) - A Domain-Specific Language (DSL) for simplified music notation
- [pyFlies](https://github.com/igordejanovic/pyFlies) - DSL for cognitive experiments modeling

## textX in the industry

[Typhoon HIL, Inc.](https://www.typhoon-hil.com/) is a technology leader for
ultra-high fidelity Hardware-in-the-Loop (HIL) real-time emulators for power
electronics.  textX is used as a part of Typhoon-HIL's schematic editor for the
description of power electronic and DSP schemes and components.

## Editor/IDE support

If you are a vim editor user check out [support for vim](https://github.com/igordejanovic/textx.vim/).

If you are more of an IDE type check out [textX-ninja project](https://github.com/igordejanovic/textX-ninja).

