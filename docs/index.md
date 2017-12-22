![textX logo](images/textX-logo.svg)

---

[textX](https://github.com/igordejanovic/textX) is a meta-language (i.e. a
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
modeling language is bellow.

<iframe width="560" height="315" src="https://www.youtube.com/embed/CN2IVtInapo" frameborder="0" allowfullscreen></iframe>

For a not-so-basic video tutorial check out [State Machine video
tutorial](tutorials/state_machine.md).


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


* **Meta-model/model visualization**

    Both meta-model and parsed models can be visulized using
    [GraphViz](http://graphviz.org/) software package. See
    [visualization](visualization.md) section.


## Installation

    $ pip install textX

Note: Previous command requires [pip](https://pypi.python.org/pypi/pip) to be
installed.

To verify that textX is properly installed run:

    $ textx

You should get output like this:

    error: the following arguments are required: cmd, metamodel
    usage: textx [-h] [-i] [-d] cmd metamodel [model]

    textX checker and visualizer

    ...

## Python versions

textX works with Python 2.7, 3.3+. Other versions might work but are not
tested.

## Getting started

See textX `Tutorials` to get you started:

- [Hello World](tutorials/hello_world.md)
- [Robot](tutorials/robot.md)
- [Entity](tutorials/entity.md)
- [State Machine](tutorials/state_machine.md) - video tutorial
- [Toy language compiler](tutorials/toylanguage.md)

For specific information read various `User Guide` sections.

Also, you can
check out [examples](https://github.com/igordejanovic/textX/tree/master/examples/).


## Discussion and help

For general discussion and help please
join
[the textX google group](https://groups.google.com/forum/#!forum/textx-talk).


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
    - [pyFlies](https://github.com/igordejanovic/pyFlies) - DSL for cognitive
      experiments modeling
    - [ppci](http://ppci.readthedocs.io/en/latest/index.html) - Pure python
      compiler infrastructure. 
    - [Expremigen](https://github.com/shimpe/expremigen) -  Expressive midi generation

* Commercial

    - textX is used as a part of [Typhoon-HIL's](https://www.typhoon-hil.com/?utm_campaign=1604_HIL402%20Campaign&utm_content=Igor_github&utm_source=email)
      schematic editor for the description of power electronic and DSP schemes and
      components.
    - [JournaKit Followship .ows](https://journakit.chirale.org/) - A new
      language for social media management with an interactive console to follow
      and discover Twitter users (code released under GNU GPL 3). Read an
      announcement
      at
      [author's blog post](https://chirale.org/2017/09/17/a-new-language-for-social-media-managers-on-twitter/).

If you are using textX to build some cool stuff drop me a line at igor dot
dejanovic at gmail. I would like to hear from you!

## Editor/IDE support

### Visual Studio Code support

There is currently an ongoing effort to build tooling support
around [Visual Studio Code](https://code.visualstudio.com/). The idea is to
auto-generate VCS plugin with syntax highlighting, outline, InteliSense,
navigation, visualization. The input for the generator would be your language
grammar and additional information specified using various DSLs.

You can follow the progress
at [the textX-tools GitHub organization](https://github.com/textX-tools).

Projects that are currently in progress are:
- [viewX](https://github.com/danielkupco/viewX-vscode) - creating visualizators
  for textX languages
- [textX-languageserver](https://github.com/textX-tools/textX-languageserver) -
  Language Server Protocol support for textX languages
- [textX-extensions](https://github.com/textX-tools/textX-extensions) - syntax
  highlighting, code outline

Stay tuned ;)


### Other editors

If you are a vim editor user check
out [support for vim](https://github.com/igordejanovic/textx.vim/).

For emacs there is [textx-mode](https://github.com/novakboskov/textx-mode) which
is also available in [MELPA](https://melpa.org/#/textx-mode).

You can also check
out [textX-ninja project](https://github.com/igordejanovic/textX-ninja). It is
currently unmaintained.


## Citing textX

If you are using textX in your research project we would be very grateful if you
cite our paper:

Dejanović I., Vaderna R., Milosavljević G., Vuković Ž. (2017).
TextX: A Python tool for Domain-Specific Languages implementation.
Knowledge-Based Systems, 115, 1-4.

```bibtex
@article{Dejanovic2017,
	author = {Dejanovi\'{c}, I. and Vaderna, R. and Milosavljevi\'{c}, G. and Vukovi\'{c}, \v{Z}.},
	doi = {10.1016/j.knosys.2016.10.023},
	issn = {0950-7051},
	journal = {Knowledge-Based Systems},
	keywords = {Domain-Specific Language; Meta-model; Model; Model-Driven software development; Parser; Python },
	note = {},
	pages = {1--4},
	title = {{TextX: A Python tool for Domain-Specific Languages implementation}},
	url = {http://www.sciencedirect.com/science/article/pii/S0950705116304178},
	volume = {115},
	year = {2017}
}
```




