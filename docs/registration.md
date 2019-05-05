# Registration and discovery

textX has an API for registration and discovery of languages and code
generators. This enable developing languages and generators for others to use by
simply installing from PyPI using `pip`.

textX utilizes `pkg_resources` module found in `setuptools` and its concept of
*extension point* to declaratively specify the registration of language or
generator. Each Python project/package may in its `setup.py` declare this
extensions. Once a Python package which declare the extension is installed in
the environment, the extension can be dynamically found.

To make it easier to find languages and generators on PyPI we recommend the
following naming scheme for the Python packages that provide a single language
or generator:

- `textx-lang-<language name>` - for language package (e.g. `textx-lang-entity`)
- `textx-gen-<source language>-<target language>` - for generator package (e.g.
  `textx-gen-entity-java`)
  
With this scheme in place searching PyPI for all languages or generators can be
easily achieved by `pip search` command (e.g. `pip search textx-lang` to find
all languages).
  

## Registering a new language

To register a new language first you have to create an instance of
`LanguageDesc` class providing the name of the language, the file pattern of
files using the language (e.g. `*.ent*`), the description of the language and
finally a callable that should be called to get the instance of the language
meta-model or the meta-model instance itself instead of callable.

For example:

```python
from textx import LanguageDesc

def entity_metamodel():
    # Some code that constructs and return the language meta-model
    # E.g. call to metamodel_from_file

entity_lang = LanguageDesc('entity',
                           pattern='*.ent',
                           description='Entity-relationship language',
                           metamodel=entity_metamodel)
```

The next step is to make this language discoverable by textX. To do this we have
to register our `entity_lang` object in the `setup.py` entry point named
`textx_languages`.

```python
setup(
    ...
    entry_points={
        'textx_languages': [
            'entity = entity.metamodel:entity_lang',
        ],
    },
```

In this example `entity.metamodel` is the python module where `entity_lang` is defined.

When you install this project textX will discover your language and offer it
through [registration API]() (see bellow).

As a convenience there is a `language` decorator that makes creating an instance
of `LanguageDesc` even easier. Use it on meta-model callable and provide the
name and the file pattern as parameters. Docstring of the decorated function
will be used as a language description.

The equivalent of the previous definition using the `language` decorator would
be:

```python
from textx import language

@language('entity', '*.ent')
def entity_lang():
    """
    Entity-relationship language
    """
    # Some code that constructs and return the language meta-model
    # E.g. call to metamodel_from_file
```

The `setup.py` entry point would be the same.

## Listing languages

textX provides a core command `list-languages` that lists all registered
languages in the current environment. We eat our own dog food so even `textX`
grammar language is registered as a language using the same mechanism.

```nohighlight
$ textx list-languages
txcl (*.txcl)                 A language for syntax highlight definition.
textX (*.tx)                  A meta-language for language definition
types-dsl (*.etype)           An example DSL for simple types definition
data-dsl (*.edata)            An example DSL for data definition
flow-dsl (*.eflow)            An example DSL for data flow processing definition
```

## Registering a new generator
## Listing generators
## Calling a generator
## Registration API
