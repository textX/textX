# textX meta-models

textX meta-model is a Python object that knows about all classes that can be
instantiated while parsing the input. A meta-model is built from the grammar by
the functions `metamodel_from_file` or `metamodel_from_str` in the
`textx.metamodel` module.

    from textx.metamodel import metamodel_from_file
    my_metamodel = metamodel_from_file('my_grammar.tx')

Each rule from the grammar will result in a Python class kept in the meta-model.
Besides, meta-model knows how to parse the input strings and convert them to
[model](model.md).

Parsing the input and creating the model is done by `model_from_file` and
`model_from_str` methods of the meta-model object:

    my_model = my_metamodel.model_from_file('some_input.md')


## Custom classes

For each grammar rule a Python class with the same name is created dynamically.
These classes are instantiated during the parsing of the input string/file to create
a graph of python objects, a.k.a. `model` or Abstract-Syntax Tree (AST).

Most of the time dynamically created classes will be sufficient, but sometimes
you will want to use your own classes instead. To do so use parameter `classes`
during the meta-model instantiation. This parameter is a list of your classes that
should be named the same as the rules from the grammar which they represent.

    from textx.metamodel import metamodel_from_str

    grammar = '''
    EntityModel:
      entities+=Entity    // each model has one or more entities
    ;

    Entity:
      'entity' name=ID '{'
        attributes+=Attribute     // each entity has one or more attributes
      '}'
    ;

    Attribute:
      name=ID ':' type=[Entity]   // type is a reference to an entity. There are
                                  // built-in entities registered on the meta-model
                                  // for primitive types (integer, string)
    ;
    '''

    class Entity(object):
      def __init__(self, parent, name, attributes):
        self.parent = parent
        self.name = name
        self.attributes = attributes


    # Use our Entity class. "Attribute" class will be created dynamically.
    entity_mm = metamodel_from_str(grammar, classes=[Entity])

Now `entity_mm` can be used to parse the input models where our `Entity` class will
be instantiated to represent each `Entity` rule from the grammar.

!!! note
    Constructor of the user-defined classes should accept all attributes defined by the
    corresponding rule from the grammar. In the previous example, we have provided
    `name` and `attributes` attributes from the `Entity` rule.
    If the class is a child in a parent-child relationship (see the next
    section), then the `parent` constructor parameter should also be given.


## Parent-child relationships

There is often an intrinsic parent-child relationship between object in the
model. In the previous example, each `Attribute` instance will always be a child
of some `Entity` object.

textX gives automatic support for these relationships by providing the `parent`
attribute on each child object.

When you navigate [model](model.md) each child instance will have a `parent`
attribute.

!!! note
    Always provide the parent parameter in user-defined classes for each class that is a
    child in a parent-child relationship.


## Processors

To specify static semantics of the language textX uses a concept called
**processor**. Processors are python callables that can modify the model elements
during model parsing/instantiation or do some additional checks that are not
possible to do by the grammar alone.

There are two types of processors:

- **model processors** - are callables that are called at the end of the parsing
  when the whole model is instantiated. These processors accept the meta-model and
  model as parameters.
- **object processors** - are registered for particular classes (grammar rules)
  and are called when the objects of the given class is instantiated.

Processors can modify model/objects or raise exception (`TextXSemanticError`) if
some constraint is not met. User code that calls the model instantiation/parsing can
catch and handle this exception.

### Model processors

To register a model processor call `register_model_processor` on the meta-model
instance.

    from textx.metamodel import metamodel_from_file

    # Model processor is a callable that will accept meta-model and model as its
    # parameters.
    def check_some_semantics(metamodel, model):
      ...
      ... Do some check on the model and raise TextXSemanticError if the semantics
      ... rules are violated.

    my_metamodel = metamodel_from_file('mygrammar.tx')

    # Register model processor on the meta-model instance
    my_metamodel.register_model_processor(check_some_semantics)

    # Parse the model. check_some_semantics will be called automatically after
    # a successful parse to do further checks. If the rules are not met,
    # an instance of TextXSemanticError will be raised.
    my_metamodel.model_from_file('some_model.ext')


### Object processors

The purpose of the object processors is the same as of the model processors, but they
are called as soon as the particular object is recognized in the input string.
They are registered per class/rule.

Let's do some additional checks for the above Entity DSL example.

    def entity_obj_processor(entity):
      '''
      Check that Ethe ntity names are capitalized. This could also be specified
      in the grammar using regex match but we will do that check here just
      as an example.
      '''

      if entity.name != entity.name.capitalize():
        raise TextXSemanticError('Entity name "%s" must be capitalized.' %
                                entity.name)

    def attribute_obj_processor(attribute):
      '''
      Obj. processors can also introduce changes in the objects they process.
      Here we set "primitive" attribute based on the Entity they refer to.
      '''
      attribute.primitive = attribute.type.name in ['integer', 'string']


    # Object processors are registered by defining a map between a rule name
    # and the callable that will process the instances of that rule/class.
    obj_processors = {
        'Entity': entity_obj_processor,
        'Attribute': attribute_obj_processor,
        }

    # This map/dict is registered on a meta-model by the "register_obj_processors"
    # call.
    entity_mm.register_obj_processors(obj_processors)

    # Parse the model. At each successful parse of Entity or Attribute, the registered
    # processor will be called and the semantics error will be raised if the
    # check does not pass.
    entity_mm.model_from_file('my_entity_model.ent')


For another example of the usage of an object processor that modifies the objects, see object
processor `move_command_processor` [robot example](tutorials/robot.md).

## Built-in objects

Often, you will need objects that should be a part of each model and you do not
want users to specify them in every model they create. The most notable example are
primitive types (e.g. `integer`, `string`, `bool`).

Let's provide `integer` and `string` Entities to our `Entity` meta-model in
order to simplify the model creation so that the users can use the names of these two
entities as the `Attribute` types.

    class Entity(object):
        def __init__(self, parent, name, attributes):
            self.parent = parent
            self.name = name
            self.attributes = attributes

    entity_builtins = {
            'integer': Entity(None, 'integer', []),
            'string': Entity(None, 'string', [])
    }
    entity_mm = metamodel_from_file(
      'entity.tx',
      classes=[Entity]            # Register Entity user class,
      builtins=entity_builtins    # Register integer and string built-in objs
    )

Now an `integer` and `string` `Attribute` types can be used.  See
[model](model.md) and [Entitiy](https://github.com/igordejanovic/textX/tree/master/examples/Entity) example for more.


## Match filters

!!! note
    Currently available in development version. It will be available in 1.5 stable
    version.

[Match rules](grammar.md#rule-types) by default return Python `string` type.
Built-in match rules (i.e. `BASETYPEs`) on the other hand return Python base
types.

Match filters are a dict of callables that is registered on metamodel and that
will get called with the string matched by the match rule. Whatever is returned
by the filter will be used of a matched string.

Example:

```
Model:
  'begin' some_number=MyFloat 'end'
;
MyFloat:
  /\d+\.(\d+)?/
;
```

In this example `MyFloat` rule is a match rule and by default will return Python
`string`, so attribute `some_number` will be of `string` type. To change that,
register match filter for `MyFloat` rule:

```
mm = metamodel_from_str(grammar, match_filters={'MyFloat': lambda x: float(x)})
```

Now, `MyFloat` will always be converted to Python `float` type.

Using match filters you can override built-in rule's conversions like this:

```
Model:
  some_float=INT
;
```

```
mm = metamodel_from_str(grammar, match_filters={'INT': lambda x: float(x)})
```

In this example we use built-in rule `INT` that returns Python `int` type.
Registering filter with the key `INT` we can change default behaviour and
convert what is matched by this rule to some other object (`float` in this
case).


## Auto-initialization of the attributes

Each object that is recognized in the input string will be instantiated and
its attributes will be set to the values parsed from the input. In the event
that a defined attribute is optional, it will nevertheless be created on the
instance and set to the default value.

Here is a list of the default values for each base textX type:

 - ID - empty string - ''
 - INT - int - 0
 - FLOAT - float - 0.0
 - BOOL - bool - False
 - STRING - empty string - ''

Each attribute with zero or more multiplicity (`*=`) that does not match any
object from the input will be initialized to an empty list.

An attribute declared with one or more multiplicity (`+=`) must match at least one
object from the input and will therefore be transformed to python list
containing all matched objects.

The drawback of this auto-initialization system is that we can't be sure if
the attribute was missing from the input or was matched, but the given value was
the same as the default value.

In some applications it is important to distinguish between those two
situations. For that purpose, there is a parameter `auto_init_attributes` of the
meta-model constructor that is `True` by default, but can be set to `False` to
prevent auto-initialization from taking place.

If auto-initialization is disabled, then each optional attribute that was not
matched on the input will be set to `None`.  This is true for the plain
assignments (`=`). An optional assignment (`?=`) will always be `False` if the
RHS object is not matched in the input. The multiplicity assignments (`*=` and
`+=`) will always be python lists.


## Parser configuration

### Case sensitivity

Parser is by default case sensitive. For DSLs that should be case insensitive
use `ignore_case` parameter of the meta-model constructor call.

```python
from textx.metamodel import metamodel_from_file

my_metamodel = metamodel_from_file('mygrammar.tx', ignore_case=True)
```


### Whitespace handling

The parser will skip whitespaces by default. Whitespaces are spaces, tabs and
newlines by default. Skipping of the whitespaces can be disabled by `skipws` bool
parameter in the constructor call. Also, what is a whitespace can be redefined by
the `ws` string parameter.

```python
from textx.metamodel import metamodel_from_file
my_metamodel = metamodel_from_file('mygrammar.tx', skipws=False, ws='\s\n')
```

Whitespaces and whitespace skipping can be defined in the grammar on the level
of a single rule by [rule modifiers](grammar.md#rule-modifiers).


### Automatic keywords

When designing a DSL, it is usually desirable to match keywords on word
boundaries.  For example, if we have Entity grammar from the above, then a word
`entity` will be considered a keyword and should be matched on word boundaries
only. If we have a word `entity2` in the input string at the place where
`entity` should be matched, the match should not succeed.

We could achieve this by using a regular expression match and the word boundaries
regular expression rule for each keyword-like match.

    Enitity:
      /\bentity\b/ name=ID ...

But the grammar will be cumbersome to read.

textX can do automatic word boundary match for all keyword-like string matches.
To enable this feature set parameter `autokwd` to `True` in the constructor
call.

```python
from textx.metamodel import metamodel_from_file
my_metamodel = metamodel_from_file('mygrammar.tx', autokwd=True)
```

Any simple match from the grammar that is matched by the
regular expression `[^\d\W]\w*` is considered to be a keyword.


### Memoization (a.k.a. packrat parsing)

This technique is based on memoizing result on each parsing expression rule.
For some grammars with a lot of backtracking this can yield a significant
speed increase at the expense of some memory used for the memoization cache.

Starting with textX 1.4 this feature is disabled by default. If you think that
parsing is slow, try to enable memoization by setting `memoization` parameter
to `True` during meta-model instantiation.

```python
from textx.metamodel import metamodel_from_file
my_metamodel = metamodel_from_file('mygrammar.tx', memoization=True)
```


