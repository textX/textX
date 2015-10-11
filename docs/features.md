# Feature highlights

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
