# textX meta-models

textX meta-model is a Python object that knows about all classes that can be
instantiated while parsing the input. A meta-model is built from the grammar by
the functions `metamodel_from_file` or `metamodel_from_str` in the
`textx.metamodel` module.

    from textx import metamodel_from_file
    my_metamodel = metamodel_from_file('my_grammar.tx')

Each rule from the grammar will result in a Python class kept in the meta-model.
Besides, meta-model knows how to parse the input strings and convert them
to [model](model.md).

Parsing the input and creating the model is done by `model_from_file` and
`model_from_str` methods of the meta-model object:

    my_model = my_metamodel.model_from_file('some_input.md')

When parsing a model file or string a new parser is cloned for each model.
This parser can be accessed via the model attribute `_tx_parser`.


## Custom classes

For each grammar rule a Python class with the same name is created dynamically.
These classes are instantiated during the parsing of the input string/file to
create a graph of python objects, a.k.a. `model` or Abstract-Syntax Tree (AST).

Most of the time dynamically created classes will be sufficient, but sometimes
you will want to use your own classes instead. To do so use parameter `classes`
during the meta-model instantiation. This parameter is a list of your classes
that should be named the same as the rules from the grammar which they
represent.

    from textx import metamodel_from_str

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

    class Entity:
      def __init__(self, parent, name, attributes):
        self.parent = parent
        self.name = name
        self.attributes = attributes


    # Use our Entity class. "Attribute" class will be created dynamically.
    entity_mm = metamodel_from_str(grammar, classes=[Entity])

Now `entity_mm` can be used to parse the input models where our `Entity` class
will be instantiated to represent each `Entity` rule from the grammar.

When passing a list of classes (as shown in the example above), you need to have rules
for all of these classes in your grammar (else, you get an exception). Alternatively,
you can also pass a callable (instead of a list of classes) to return user classes
given a rule name. In that case, only rule names found in the grammar
are used to query user classes.
See [unittest](https://github.com/textX/textX/blob/master/tests/functional/test_user_classes_callable.py).

```admonish
Constructor of the user-defined classes should accept all attributes defined by
the corresponding rule from the grammar. In the previous example, we have
provided `name` and `attributes` attributes from the `Entity` rule. If the class
is a child in a parent-child relationship (see the next section), then the
`parent` constructor parameter should also be given.
```

Classes that use `__slots__` are supported. Also, initialization of custom
classes is postponed during model loading and done after reference resolving but
before object processors call (see [Using the scope provider to modify a
model](scoping.md##using-the-scope-provider-to-modify-a-model)) to ensure that
immutable objects (e.g. using [attr frozen
feature](https://www.attrs.org/en/stable/examples.html#immutability)), that
can't be changed after initialization, are also supported.


## Parent-child relationships

There is often an intrinsic parent-child relationship between object in the
model. In the previous example, each `Attribute` instance will always be a child
of some `Entity` object.

textX gives automatic support for these relationships by providing the `parent`
attribute on each child object.

When you navigate [model](model.md) each child instance will have a `parent`
attribute.

```admonish
Always provide the parent parameter in user-defined classes for each class that
is a child in a parent-child relationship.
```


## Processors

To specify static semantics of the language textX uses a concept called
**processor**. Processors are python callables that can modify the model
elements during model parsing/instantiation or do some additional checks that
are not possible to do by the grammar alone.

There are two types of processors:

- **model processors** - are callables that are called at the end of the parsing
  when the whole model is instantiated. These processors accept the model 
  and meta-model as parameters.
- **object processors** - are registered for particular classes (grammar rules)
  and are called when the objects of the given class is instantiated.

Processors can modify model/objects or raise exception (`TextXSemanticError`) if
some constraint is not met. User code that calls the model instantiation/parsing
can catch and handle this exception.

### Model processors

To register a model processor call `register_model_processor` on the meta-model
instance.

    from textx import metamodel_from_file

    # Model processor is a callable that will accept meta-model and model as its
    # parameters.
    def check_some_semantics(model, metamodel):
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

The purpose of the object processors is to validate or alter the object being
constructed. They are registered per class/rule.

Let's do some additional checks for the above Entity DSL example.

    def entity_obj_processor(entity):
      '''
      Check that Ethe ntity names are capitalized. This could also be specified
      in the grammar using regex match but we will do that check here just
      as an example.
      '''

      if entity.name != entity.name.capitalize():
        raise TextXSemanticError('Entity name "%s" must be capitalized.' %
                                entity.name, **get_location(entity))

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


For another example of the usage of an object processor that modifies the
objects, see object processor
`move_command_processor` [robot example](tutorials/robot.md).

If object processor returns a value that value will be used instead of the
original object. This can be used to implement e.g. expression evaluators or
on-the-fly model interpretation. For more information

```admonish
For more information please take a look at [the
tests](https://github.com/textX/textX/blob/master/tests/functional/test_processors.py).
```

Object processors decorated with `textx.textxerror_wrap` will transform
any exceptions not derived from `TextXError` to a `TextXError` (including
line/column and filename information). This can be useful, if
object processors transform values using non-textx libraries (like `datetime`)
and you wish to get the location in the model file, where errors occur
while transforming the data (see 
[these tests](https://github.com/textX/textX/blob/master/tests/functional/test_processors.py)).

## Built-in objects

Often, you will need objects that should be a part of each model and you do not
want users to specify them in every model they create. The most notable example
are primitive types (e.g. `integer`, `string`, `bool`).

Let's provide `integer` and `string` Entities to our `Entity` meta-model in
order to simplify the model creation so that the users can use the names of
these two entities as the `Attribute` types.

    class Entity:
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

Now an `integer` and `string` `Attribute` types can be used.
See [model](model.md)
and
[Entitiy](https://github.com/textX/textX/tree/master/examples/Entity)
example for more.


## Creating your own base type

[Match rules](grammar.md#rule-types) by default return Python `string` type.
Built-in match rules (i.e. `BASETYPEs`) on the other hand return Python base
types.

You can use object processors to create your type by specifying match rule in
the grammar and object processor for that rule that will create an object of a
proper Python type.

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
register object processor for `MyFloat` rule:

```
mm = metamodel_from_str(grammar)
mm.register_obj_processors({'MyFloat': lambda x: float(x)}))
```

Now, `MyFloat` will always be converted to Python `float` type.

Using match filters you can override built-in rule's conversions like this:

```
Model:
  some_float=INT
;
```

```
mm = metamodel_from_str(grammar)
mm.register_obj_processors({'INT': lambda x: float(x)}))
```

In this example we use built-in rule `INT` that returns Python `int` type.
Registering object processor with the key `INT` we can change default behaviour
and convert what is matched by this rule to some other object (`float` in this
case).


## Auto-initialization of the attributes

Each object that is recognized in the input string will be instantiated and its
attributes will be set to the values parsed from the input. In the event that a
defined attribute is optional, it will nevertheless be created on the instance
and set to the default value.

Here is a list of the default values for each base textX type:

 - ID - empty string - ''
 - INT - int - 0
 - FLOAT - float - 0.0 (also 0 is possible)
 - STRICTFLOAT - float - 0.0 (0. or .0 or 0e1, but not 0, which is an INT)
 - BOOL - bool - False
 - STRING - empty string - ''

Each attribute with zero or more multiplicity (`*=`) that does not match any
object from the input will be initialized to an empty list.

An attribute declared with one or more multiplicity (`+=`) must match at least
one object from the input and will therefore be transformed to python list
containing all matched objects.

The drawback of this auto-initialization system is that we can't be sure if the
attribute was missing from the input or was matched, but the given value was the
same as the default value.

In some applications it is important to distinguish between those two
situations. For that purpose, there is a parameter `auto_init_attributes` of the
meta-model constructor that is `True` by default, but can be set to `False` to
prevent auto-initialization from taking place.

If auto-initialization is disabled, then each optional attribute that was not
matched on the input will be set to `None`. This is true for the plain
assignments (`=`). An optional assignment (`?=`) will always be `False` if the
RHS object is not matched in the input. The multiplicity assignments (`*=` and
`+=`) will always be python lists.

## Optional model parameter definitions

A meta-model can define optional model parameters. Such definitions are stored
in `model_param_defs` and define optional parameters, which can be specified
while loading/creating a model through `model_from_str` or `model_from_file`.
Details: see [tx_model_params](model.md#_tx_model_params).

`metamodel.model_param_defs` can be queried (like a dict) to retrieve possible
extra parameters and their descriptions for a meta-model. It is also used to
restrict the additional parameters passed to `model_from_str` or
`model_from_file`.

Default parameters are:

 * `project_root`: this model parameter is used by the [`GlobalRepo`](http://localhost:8000/scoping/#scope-providers-defined-in-module-textxscopingproviders)
    to set a project directory, where all file patterns not referring to an
    absolute file position are looked up.
 
 
An example of a custom model parameter definition used to control the behavior
of an object processor is given in
[test_reference_to_nontextx_attribute.py](https://github.com/textX/textX/blob/master/tests/functional/registration/test_check.py),
(`test_object_processor_with_optional_parameter_*`; specifying a parameter
while loading) and
[test_reference_to_nontextx_attribute.py](https://github.com/textX/textX/blob/master/tests/functional/registration/projects/types_dsl/types_dsl/__init__.py)
(defining the parameter in the metamodel).
