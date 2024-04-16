# Registration and discovery

textX has an API for registration and discovery of languages and code
generators. This enable developing languages and generators for others to use by
simply installing from PyPI using `pip`.

textX utilizes a concept of [extension
point](https://packaging.python.org/en/latest/specifications/entry-points/) to
declaratively specify the registration of language or generator. Each Python
project/package may in its `pyproject.toml` declare this extensions. Once a
Python package which declare the extension is installed in the environment, the
extension can be dynamically found.

To make it easier to find languages and generators on PyPI we recommend the
following naming scheme for the Python packages that provide a single language
or generator:

- `textx-lang-<language name>` - for language package (e.g. `textx-lang-entity`)
- `textx-gen-<source language>-<target language>` - for generator package (e.g.
  `textx-gen-entity-java`)
  
With this scheme in place searching PyPI for all languages or generators can be
easily achieved by `pip search` command (e.g. `pip search textx-lang` to find
all languages).


## textX languages

textX language consists of a meta-model which holds information of all language
concepts and their relations (a.k.a. *Abstract syntax*) as well as a parser
which knows how to transform textual representation of a language (a.k.a.
*Concrete syntax*) to a *model* which conforms to the meta-model.

Also, each language has its unique name, a short one-line description and a file
name pattern for recognizing files that contains textual representation of its
models.
  

### Registering a new language

To register a new language first you have to create an instance of
`LanguageDesc` class (or its subclass) providing the name of the language, the
file pattern of files using the language (e.g. `*.ent`), the description of the
language and finally a callable that should be called to get the instance of the
language meta-model. Alternatively, you can provide the instance of the
meta-model instead of the callable.

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
to register our `entity_lang` object in the `pyproject.toml` entry point named
`textx_languages`.

```toml
[project.entry-points.textx_languages]
entity = "entity.metamodel:entity_lang"
```

In this example `entity.metamodel` is the Python module where `entity_lang` is defined.

When you install this project textX will discover your language and offer it
through [registration API](#registration-api) (see bellow).

As a convenience there is a `language` decorator that makes creating an instance
of `LanguageDesc` more convenient. Use it to decorate meta-model callable and
provide the name and the file pattern as parameters. Docstring of the decorated
function will be used as a language description.

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

The `pyproject.toml` entry point registration would be the same.


```admonish warning
Language name is its unique identifier. There *must not* exist two languages
with the same name. The name consists of alphanumerics, underscores (`_`) and
dashes (`-`). If you plan to publish your language on PyPI choose a name that is
higly unlikely to collide with other languages (e.g. by using some prefix,
`mycompanyname-entity` instead of just `entity`).
```



### Listing languages

textX provides a core command `list-languages` that lists all registered
languages in the current environment. We eat our own dog food so even `textX`
grammar language is registered as a language using the same mechanism.

```
$ textx list-languages
txcl (*.txcl)         textx-gen-coloring    A language for syntax highlight definition.
textX (*.tx)          textX                 A meta-language for language definition
types-dsl (*.etype)   types-dsl             An example DSL for simple types definition
data-dsl (*.edata)    data-dsl              An example DSL for data definition
flow-dsl (*.eflow)    flow-dsl              An example DSL for data flow processing definition
```

The first column gives the language unique name and filename pattern, the second
column is the Python project which registered the language and the third column
is a short description.

You can get a reference to a registered language meta-model in your programs by
using the [registration API] `metamodel_for_language` call. For example:

```python
from textx import metamodel_for_language
data_dsl_mm = metamodel_for_language('data-dsl')

model = data_dsl_mm.model_from_file('my_model.data')
```


## textX generators

textX generators are callables which can transform any textX model to an
arbitrary (usually textual) representation. Similarly to languages, generators
can be registered and discovered. They can also be called either
programmatically or from CLI using `textx` command.


### Registering a new generator


To register a new generator first you have to create an instance of
`GeneratorDesc` class (or its subclass) providing the name of the source
language, the name of the target language, a short one-line description of the
generator and finally a callable that should be called to perform code
generation. The callable is if the form:

```python
def generator(metamodel, model, output_path, overwrite, debug, **custom_args)
```

where:

- `metamodel` - is the meta-model of the source language
- `model` - is the model for which the code generating is started
- `output_path` - is the root folder path where the output should be stored
- `overwrite` - a bool flag that tells us should we overwrite the target files
  if they exist
- `debug` - a bool flag which tells us if we are running in debug mode and
  should we produce more output
- `**custom_args` - additional generator-specific arguments. When the generator
  is called from the CLI this parameter will hold all other switches that are
  not recognized
  
  
For example:


```python
from textx import GeneratorDesc

def entity_java_generator(metamodel, model, output_path, overwrite, debug, **custom_args)
    # Some code that perform generation

entity_java_generator = GeneratorDesc(
    language='entity',
    target='java'
    description='Entity-relationship to Java language generator',
    generator=entity_java_generator)
```

The next step is to make this generator discoverable by textX. To do this we
have to register our `entity_java_generator` object in the `pyproject.toml`
entry point named `textx_generators`.

```toml
[project.entry-points.textx_generators]
entity_java = "entity.generators:entity_java_generator"
```

```admonish tip
You can also register generator programmatically using [registration API]. But
if you want your generator to be available to `textx` command you should use
`pyproject.toml`.
```
    
    
    

In this example `entity.generators` is the Python module where `entity_java_generator` is defined.

When you install this project textX will discover your generator and offer it
through [registration API](#registration-api) (see bellow).

As a convenience there is a `generator` decorator that makes creating an
instance of `GeneratorDesc` more convenient. Use it to decorate generator
callable and provide the name and the source and target language as parameters.
Docstring of the decorated function will be used as a generator description.

The equivalent of the previous definition using the `generator` decorator would
be:

```python
from textx import generator

@generator('entity', 'java')
def entity_java_generator(metamodel, model, output_path, overwrite, debug, **custom_args)
    "Entity-relationship to Java language generator"
    # Some code that perform generation
```

The `pyproject.toml` would remain the same.


Here is an example of the generator of `dot` files from any textX model. This is
an actual code from textX.


```python
@generator('any', 'dot')
def model_generate_dot(metamodel, model, output_path, overwrite, debug):
    "Generating dot visualizations from arbitrary models"

    input_file = model._tx_filename
    base_dir = output_path if output_path else os.path.dirname(input_file)
    base_name, _ = os.path.splitext(os.path.basename(input_file))
    output_file = os.path.abspath(
        os.path.join(base_dir, "{}.{}".format(base_name, 'dot')))
    if overwrite or not os.path.exists(output_file):
        click.echo('-> {}'.format(output_file))
        model_export(model, output_file)
        click.echo('   To convert to png run "dot -Tpng -O {}"'
                   .format(os.path.basename(output_file)))
    else:
        click.echo('-- Skipping: {}'.format(output_file))
```


### Listing generators

textX provides a core command `list-generators` that lists all registered
generators in the current environment. 

```
$ textx list-generators
textX -> dot         textX               Generating dot visualizations from textX grammars
textX -> PlantUML    textX               Generating PlantUML visualizations from textX grammars
any -> dot           textX               Generating dot visualizations from arbitrary models
flow-dsl -> PlantUML flow-codegen        Generating PlantUML visualization from flow-dsl
```

The first column gives the generator identifier, the second column is the Python
project which registered the generator and the third column is a short
description.

Generators are identified by pair `(<source language name>, <target language
name>)`. The source language must be registered in the environment for the
generator to be able to parse the input. The target output is produced by the
generator itself so the target language doesn't have to registered.

```admonish
We eat our own dog food so even [`textX` visualization](visualization.md) is
done as using the generator mechanism.
```


### Calling a generator

You can get a reference to a generator by using the [registration API]. For
example `generator_for_language_target` call will return the generator for the
given source language name and target language name.


```python
from textx import generator_for_language_target
robot_to_java = generator_for_language_target('robot', 'java')

robot_to_java(robot_mm, my_model)
```

```admonish warning
If you are using `@generator` decorator and want to programmatically call the
generator do not call the decorated fuction as it is transformed to
`GeneratorDesc` instance. Instead, use `generator_for_language_target` call from
the [registration API] as described.
```

A more convenient way is to call the generator from the CLI. This is done using
the textX provided `generate` command.

To get a help on the command:

```
$ textx generate --help
Usage: textx generate [OPTIONS] MODEL_FILES...

  Run code generator on a provided model(s).

  For example::

  # Generate PlantUML output from .flow models
  textx generate mymodel.flow --target PlantUML

  # or with defined output folder
  textx generate mymodel.flow -o rendered_model/ --target PlantUML

  # To chose language by name and not by file pattern use --language
  textx generate *.flow --language flow --target PlantUML

  # Use --overwrite to overwrite target files
  textx generate mymodel.flow --target PlantUML --overwrite

  # In all above cases PlantUML generator must be registered, i.e.:
  $ textx list-generators
  flow-dsl -> PlantUML  Generating PlantUML visualization from flow-dsl

  # If the source language is not registered you can use the .tx grammar
  # file for parsing but the language name used will be `any`.
  textx generate --grammar Flow.tx --target dot mymodel.flow

Options:
  -o, --output-path PATH  The output to generate to. Default = same as input.
  --language TEXT         A name of the language model conforms to. Deduced
                          from file name if not given.
  --target TEXT           Target output format.  [required]
  --overwrite             Should overwrite output files if exist.
  --grammar TEXT          A file name of the grammar used as a meta-model.
  -i, --ignore-case       Case-insensitive model parsing. Used only if
                          "grammar" is provided.
  --help                  Show this message and exit.

```

You can pass arbitrary parameters to the `generate` command. These parameters
will get collected and will be made available as `kwargs` to the generator
function call.

For example:

    textx generate mymodel.flow --target mytarget --overwrite --meaning_of_life 42
    
Your generator function:

    @generator('flow', 'mytarget')
    def flow_mytarget_generator(metamodel, model, output_path, overwrite, debug, **kwargs):
        ... kwargs has meaning_of_life param
        
gets `meaning_of_life` param with value `42` in `kwargs`.

If you have [model parameters
defined](metamodel.md#optional-model-parameter-definitions) on a meta-model
then any parameter passed to the generator that is registered on the meta-model
will be available as `model._tx_model_params` and can be used e.g. in [model
processors](metamodel.md#model-processors).


## Registration API


### Language registration API

All classes and functions documented here are directly importable from `textx` module.

- `LanguageDesc` - a class used as a structure to hold language meta-data

    Attributes:

    - `name` - a unique language name
    - `pattern` - a file name pattern used to recognized files containing the language model
    - `description` - a short one-line description of the language
    - `metamodel` - callable that is called to get the meta-model or the instance
      of the meta-model

- `language_description(language_name)` - return an instance of `LanguageDesc`
  given the language name
- `language_descriptions()` - return a dict of `language name` -> `LanguageDesc` instances
- `register_language(language_desc_or_name, pattern=None, description='',
  metamodel=None)` - programmatically register language by either providing an
  instance of `LanguageDesc` as the first parameter or providing separate
  parameters
- `clear_language_registrations()` - deletes all languages registered
  programmatically. Note: languages registered through `pyproject.toml` won't be
  removed
- `metamodel_for_language(language_name, **kwargs)` - returns a meta-model for
  the given language name. `kwargs` are additional keyword arguments passed to
  meta-model factory callable, similarly to `metamodel_from_str/file`.
- `language_for_file(file_name_or_pattern)` - returns an instance of `LanguageDesc`
  for the given file name or file name pattern. Raises `TextXRegistrationError`
  if no language or multiple languages can parse the given file
- `languages_for_file(file_name_or_pattern)` - returns a list of `LanguageDesc`
  for the given file name or file name pattern
- `metamodel_for_file(file_name_or_pattern, **kwargs)` - returns a language
  meta-model for a language that can parse the given file name or file name
  pattern. `kwargs` are additional keyword arguments passed to meta-model
  factory callable, similarly to `metamodel_from_str/file`. Raises
  `TextXRegistrationError` if no language or multiple languages can parse the
  given file
- `metamodels_for_file(file_name_or_pattern)` - returns a list of meta-models
  for languages that can parse the given file name or file pattern
- `language` - a decorator used for [language registration](#registering-a-new-language)


```admonish warning
Meta-model instances are cached with a given `kwargs` so the same instance can
be retrieved in further calls without giving `kwargs`. Whenever `kwargs` is
given in `metamodel_for_file/language` call, a brand new meta-model will be
created and cached for further use.
```



### Generator registration API

- `GeneratorDesc` - a class used as a structure to hold generator meta-data

    Attributes:

    - `name` - a unique language name
    - `pattern` - a file name pattern used to recognized files containing the language model
    - `description` - a short one-line description of the language
    - `metamodel` - callable that is called to get the meta-model or the instance
      of the meta-model

- `generator_description(language_name, target_name, any_permitted=False)` -
  return an instance of `GeneratorDesc` with the given language and target. If
  `any_permitted` is `True` allow for returning generator for the same target
  and the source language `any` as a fallback. 
- `generator_descriptions()` - return a dict of dicts where the first key is the
  source language name in lowercase and the second key is the target language
  name in lowercase. Values are `GeneratorDesc` instances.
- `generator_for_language_target(language_name, target_name,
  any_permitted=False)` - returns generator callable for the given language
  source and target. If `any_permitted` is `True` allow for returning generator
  for the same target and the source language `any` as a fallback.
- `register_generator(generator_desc_or_language, target=None, description='',
  generator=None)` - programmatically register generator by either providing an
  instance of `GeneratorDesc` as the first parameter or providing separate
  parameters
- `clear_generator_registrations` - deletes all generators registered
  programmatically. Note: generators registered through `pyproject.toml` won't
  be removed
- `generator` - a decorator used for [generator
  registration](#registering-a-new-generator)



[registration API]: #registration-api
