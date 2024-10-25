![textX logo](images/textX-logo.png)

---

[textX](https://github.com/textX/textX) is a meta-language (i.e. a
language for language definition) for domain-specific language (DSL)
specification in Python.

In a nutshell, textX will help you build your textual language in an easy way.
You can invent your own language or build a support for an already existing
textual language or file format.

From a single grammar description, textX automatically builds a meta-model (in
the form of Python classes) and a parser for your language. The parser will
parse expressions of your language and automatically build a graph of Python
objects (i.e. the model) corresponding to the meta-model.

textX is inspired by [Xtext](http://www.eclipse.org/xtext/) - a Java based
language workbench for building DSLs with full tooling support (editors,
debuggers etc.) on the Eclipse platform.  If you like Java and
[Eclipse](http://www.eclipse.org/) check it out. It is a great tool.

A video tutorial for textX installation and implementation of a simple data
modeling language is below.

<iframe width="560" height="315" src="https://www.youtube.com/embed/CN2IVtInapo" frameborder="0" allowfullscreen></iframe>


For a not-so-basic video tutorial check out [State Machine video
tutorial](tutorials/state_machine.md).


For an introduction to DSLs in general here are some references:

- Federico Tomassetti: [The complete guide to (external) Domain Specific
  Languages](https://tomassetti.me/domain-specific-languages/).
- Pierre Bayerl: [self-dsl](https://goto40.github.io/self-dsl/).

For an in-depth coverage on the subject we recommend the following books:

- Voelter, Markus, et al. [DSL engineering: Designing, implementing and using domain-specific languages](http://dslbook.org). dslbook.org, 2013.
- Kelly, Steven, and Juha-Pekka Tolvanen. [Domain-specific modeling: enabling full code generation](http://dsmbook.com/). John Wiley & Sons, 2008.


## Feature highlights

* **Meta-model/parser from a single description**

    A single description is used to define both language concrete syntax and its
    meta-model (a.k.a. abstract syntax). See the description of
    [grammar](grammar.md) and [metamodel](metamodel.md).

* **Automatic model (AST) construction**

    Parse tree will automatically be transformed to a graph of python objects
    (a.k.a. the model). See the [model](model.md) section.

    Python classes will be created by textX but, if needed, user supplied
    classes may be used. See [custom classes](metamodel.md#custom-classes).

* **Automatic linking**

    You can have references to other objects in your language and the textual
    representation of the reference will be resolved to the proper python reference
    automatically.

* **Automatic parent-child relationships**

    textX will maintain a parent-child relationships imposed by the grammar.
    See [parent-child relationships](metamodel.md#parent-child-relationships).

* **Parser control**

    Parser can be configured with regard to case handling, whitespace handling,
    keyword handling etc. See [parser configuration](parser_config.md).


* **Model/object post-processing**

    A callbacks (so called processors) can be registered for models and
    individual classes.  This enables model/object postprocessing (validation,
    additional changes etc.).  See [processors](metamodel.md#processors) section.


* **Grammar modularization - imports**

    Grammar can be split into multiple files and then files/grammars can be
    imported where needed. See [Grammar
    modularization](grammar.md#grammar-modularization).

* **Scope Providers**

    Scope Providers allow different types of scoping. See [Scoping](scoping.md).

* **Multi-meta-model support**

    Different meta-models can be combined. Typically some of these meta-models
    extend other meta-models (grammar modularization) and reference each other.
    Special scope providers support file-extension-based allocation of model
    files to meta models. See [Multi meta-model support](multimetamodel.md)

* **Meta-model/model visualization**

    Both meta-model and parsed models can be visulized using
    [GraphViz](http://graphviz.org/) software package. See
    [visualization](visualization.md) section.


## Installation

    $ pip install textX[cli]


```admonish
Previous command requires [pip](https://pypi.python.org/pypi/pip) to be
installed.

Also, notice the use of `[cli]` which means that we would like to use CLI
`textx` command. If you just want to deploy your language most probably you
won't need CLI support.
```

To verify that textX is properly installed run:

    $ textx

You should get output like this:

```
Usage: textx [OPTIONS] COMMAND [ARGS]...

Options:
  --debug  Debug/trace output.
  --help   Show this message and exit.

Commands:
  check            Check/validate model given its file path.
  generate         Run code generator on a provided model(s).
  list-generators  List all registered generators
  list-languages   List all registered languages
  version          Print version info.

```


To install development (`master` branch) version:

    $ pip install --upgrade https://github.com/textX/textX/archive/master.zip


## Python versions

textX works with Python 3.8+. Other versions might work but are not tested.

## Getting started

See textX `Tutorials` to get you started:

- [Hello World](tutorials/hello_world.md)
- [Robot](tutorials/robot.md)
- [Entity](tutorials/entity.md)
- [State Machine](tutorials/state_machine.md) - video tutorial
- [Toy language compiler](tutorials/toylanguage.md)
- [self-dsl](tutorials/self-dsl.md)

For specific information read various `User Guide` sections.

You can also try textX in [our
playground](https://textx.github.io/textx-playground/). There is a dropdown with
several examples to get you started.

A full example project that shows how multi-meta-modeling feature can be used is
also available in [a separate git
repository](https://github.com/textX/textx-multi-metamodel-example).

To create the initial layout of your project quickly take a look at [project
scaffolding](scaffolding.md).


## Discussion and help

For general questions and help please use
[StackOverflow](https://stackoverflow.com/questions/tagged/textx). Just make
sure to tag your question with the `textx` tag.


For issues, suggestions and feature request please use 
[GitHub issue tracker](https://github.com/textX/textX/issues).


## Projects using textX

Here is a non-complete list of projects using textX.

* Open-source

    - [pyecore](https://github.com/pyecore/pyecore) - ECore implementation in
      Python. Vincent Aranega is doing a great work on integrating textX with
      pyecore. The idea is that the integration eventually gets merged to the
      main textX repo. For now, you can follow his
      work [on his fork of textX](https://github.com/aranega/textX).
    - [pyTabs](https://github.com/E2Music/pyTabs) - A Domain-Specific Language
      (DSL) for simplified music notation
    - [applang](https://github.com/kosanmil/applang) - Textual DSL for
      generating mobile applications
    - [pyFlies](https://github.com/pyflies/pyflies) - A DSL for designing
      experiments in psychology
    - [ppci](http://ppci.readthedocs.io/en/latest/index.html) - Pure python
      compiler infrastructure. 
    - [Expremigen](https://github.com/shimpe/expremigen) -  Expressive midi generation
    - [fanalyse](https://github.com/azag0/fanalyse) - Fortran code parser/analyser
    - [Silvera](https://gitlab.com/alensuljkanovic/silvera/-/wikis/home) - A DSL
      for microservice based software development
    - [cutevariant](https://github.com/labsquare/cutevariant) - A standalone and
      free application to explore genetics variations from VCF file. Developed
      by [labsquare](http://www.labsquare.org/) - A community for genomics
      software
    - [osxphotos](https://github.com/RhetTbull/osxphotos) - Python app to export
      pictures and associated metadata from Apple Photos on macOS.
    - [StrictDoc](https://github.com/strictdoc-project/strictdoc) - Software for
      technical documentation and requirements management. 

* Commercial

    - textX is used as a part of [Typhoon-HIL's](https://www.typhoon-hil.com/?utm_campaign=1604_HIL402%20Campaign&utm_content=Igor_github&utm_source=email)
      schematic editor for the description of power electronic and DSP schemes and
      components.

If you are using textX to build some cool stuff drop me a line at igor dot
dejanovic at gmail. I would like to hear from you!

## Editor/IDE support

### Visual Studio Code support

There is currently an ongoing effort to build tooling support
around [Visual Studio Code](https://code.visualstudio.com/). The idea is to
auto-generate VCS plugin with syntax highlighting, outline, InteliSense,
navigation, visualization. The input for the generator would be your language
grammar and additional information specified using various DSLs.

Projects that are currently in progress are:

- [textX-LS](https://github.com/textX/textX-LS) - support for Language Server
  Protocol and VS Code for any textX based language. 
  
- [textx-gen-coloring](https://github.com/danixeee/textx-gen-coloring) - a textX
  generator which generates syntax highlighting configuration for TextMate
  compatible editors (e.g. VSCode) from textX grammars.
  
- [textx-gen-vscode](https://github.com/danixeee/textx-gen-vscode) - a textX
  generator which generates VSCode extension from textX grammar.

- [viewX](https://github.com/danielkupco/viewX-vscode) - creating visualizers
  for textX languages

Stay tuned ;)


### Other editors

If you are a vim editor user check
out [support for vim](https://github.com/textX/textx.vim/).

For emacs there is [textx-mode](https://github.com/textX/textx-mode) which is
also available in [MELPA](https://melpa.org/#/textx-mode).

You can also check
out [textX-ninja project](https://github.com/textX/textX-ninja). It is
currently unmaintained.


## Citing textX

If you are using textX in your research project we would be very grateful if you
cite our paper @@Dejanovic2017.

```bibtex
{{#include ./references.bib:textx }}
```




