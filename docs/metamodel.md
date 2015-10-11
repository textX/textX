.. _metamodel:

# textX meta-models

textX meta-model is a Python object that knows about all classes that can be
instantiated while parsing input. A meta-model is built from the grammar by
the functions :code:`metamodel_from_file` or :code:`metamodel_from_str` in the
:code:`textx.metamodel` module::

  from textx.metamodel import metamodel_from_file
  my_metamodel = metamodel_from_file('my_grammar.tx')

Each rule from the grammar will result in a Python class kept in a meta-model.
Besides, meta-model knows how to parse input strings and convert them to
:ref:`model`.

Parsing input and creating model is done by :code:`model_from_file` and
:code:`model_from_str` methods of the meta-model object::

  my_model = my_metamodel.model_from_file('some_input.md')


.. _custom-classes:

## Custom classes

For each grammar rule a Python class with the same name is created dynamically.
These classes are instantiated during parsing of input string/file to create
a graph of python objects, a.k.a. :ref:`model` or Abstract-Syntax Tree (AST).

Most of the time dynamically created classes will be sufficient but sometimes
you will want to use your own classes instead.
To do so use parameter :code:`classes` during meta-model instantiation. This
parameter is a list of your classes that should be named the same as the rules
from the grammar which they represent::

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

Now :code:`entity_mm` can be used to parse input models where our :code:`Entity`
class will be instantiated to represent each :code:`Entity` rule from the
grammar.

.. note::
   Constructor of user classes should accept all attributes defined by the
   corresponding rule from the grammar. In the previous example we have provided
   :code:`name` and :code:`attributes` attributes from the :code:`Entity` rule.
   If the class is a child in parent-child relationship (see in the next
   section) then :code:`parent` constructor parameter should also be given.


## Parent-child relationships

There is often an intrinsic parent-child relationship between object in the
model. In the previous example each :code:`Attribute` instance will always be a
child of some :code:`Entity` object.

textX gives automatic support for these relationships by providing
:code:`parent` attribute on each child object.

When you navigate :ref:`model` each child instance will have a :code:`parent`
attribute.

.. note::
   Always provide parent parameter in user classes for each class that is a
   child in parent-child relationship.


.. _processors:

## Processors

To specify static semantics of the language textX uses a concept called
**processor**. Processors are python callable that can modify model elements
during model parsing/instantiation or do some additional checks that are not
possible to do by the grammar alone.

There are two types of processors:

- **model processors** - are callable that are called at the end of the parsing
  when the whole model is instantiated. These processors accepts meta-model and
  model as parameters.
- **object processors** - are registered for particular classes (grammar rules)
  and are called when the objects of the given class is instantiated.

Processors can modify model/objects or raise exception
(:code:`TextXSemanticError`) if some constraint is not met. User code that call
model instantiation/parsing can catch and handle those exception.

### Model processors

To register model processor call :code:`register_model_processor` on the
meta-model instance:

.. code-block:: python

  from textx.metamodel import metamodel_from_file

  # Model processor is a callable that will accept meta-model and model as its
  # parameters.
  def check_some_semantics(metamodel, model):
    ...
    ... Do some check on the model and raise TextXSemanticError if semantics
    ... rules are violated.

  my_metamodel = metamodel_from_file('mygrammar.tx')

  # Register model processor on meta-model instance
  my_metamodel.register_model_processor(check_some_semantics)

  # Parse model. check_some_semantics will be called automatically after
  # successful parse to do further checks. If the rules are not met
  # an instance of TextXSemanticError will be raised.
  my_metamodel.model_from_file('some_model.ext')


### Object processors

The purpose of object processors is the same as for model processors but they
are called as soon as the particular object is recognized in the input string.
They are registered per class/rule.

Let's do some additional checks for the above Entity DSL example:


.. code-block:: python

  def entity_obj_processor(entity):
    '''
    Check that Entity names are capitalized. This could also be specified
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

  # Parse model. At each successful parse of Entity or Attribute the registered
  # processor will be called and the semantics error will be raised if the
  # check do not pass.
  entity_mm.model_from_file('my_entity_model.ent')


For another example usage of object processor that modify objects see object
processor :code:`move_command_processor` in :ref:`robot example
<move_command_processor>`


## Built-in objects

Often you will need objects that should be a part of each model and you do not
want users to specify them in every model they create. Most notable example is
primitive types (e.g. integer, string, bool).

Let's provide :code:`integer` and :code:`string` Entities to our :code:`Entity`
meta-model in order to simplify model creation so that user can use the names of
these two entities for :code:`Attribute` types::


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

Now an :code:`integer` and :code:`string` :code:`Attribute` type can be used.
See :ref:`model` and :code:`Entity` example for more.


## Auto-initialization of attributes

Each object that is recognized in the input string will be instantiated and
their attributes will be set to the values parsed from the input. In the event
that defined attribute is optional, it will nevertheless be created on the
instance and set to the default value.

Here is a list of default values for each base textX type:

 - ID - empty string - ''
 - INT - int - 0
 - FLOAT - float - 0.0
 - BOOL - bool - False
 - STRING - empty string - ''

Each attribute with zero or more multiplicity (:code:`*=`) that does not match
any object from the input will be initialized to an empty list.

Attribute declared with one or more multiplicity (:code:`+=`) must match at
least one object from the input and therefore will be transformed to python list
containing all matched objects.

The drawback of this auto-initialization system is that we can't be sure if
the attribute was missing from the input or was matched but the value was
default.

In some applications it is important to distinguish between those two
situations. For that purpose there is a parameter :code:`auto_init_attributes`
to the meta-model constructor that is by default :code:`True` but can be set to
:code:`False` to prevent auto-initialization to take place.

If auto-initialization is disabled than each optional attribute that was not
matched on the input will be set to :code:`None`.  This holds true for plain
assignments (:code:`=`). An optional assignment (:code:`?=`) will always
be :code:`False` if the RHS object is not matched in the input. Many
multiplicity assignments (:code:`*=` and :code:`+=`) will always be python
lists.


## Parser configuration

### Case sensitivity

Parser is by default case sensitive. For DSLs that should be case insensitive
use `ignore\_case` parameter to the meta-model constructor call::

  from textx.metamodel import metamodel_from_file

  my_metamodel = metamodel_from_file('mygrammar.tx', ignore_case=True)


### Whitespace handling

The parser will skip whitespaces by default. Whitespaces are spaces, tabs and
newlines by default. Skipping of whitespaces can be disabled by :code:`skipws`
bool parameter in constructor call. Also, what is a whitespace can be redefined
by :code:`ws` string parameter::

  from textx.metamodel import metamodel_from_file
  my_metamodel = metamodel_from_file('mygrammar.tx', skipws=False, ws='\s\n')

Whitespaces and whitespace skipping can be defined in the grammar on the level
of a single rule by :ref:`rule-modifiers`.


### Automatic keywords

When designing a DSL it is usually desirable to match keywords on word
boundaries.  For example, if we have Entity grammar from the above than a word
:code:`entity` will be considered a keyword and should be matched on word
boundaries only. If we have a word :code:`entity2` in the input string at the
place where :code:`entity` should be matched the match should not succeed.

We could achieve this by using regular expression match and word boundaries
regular expression rule for each keyword-like match::

  Enitity:
    /\bentity\b/ name=ID ...

But the grammar will be cumbersome to read.

textX can do automatic word boundary match for all keyword-like string matches.
To enable this feature set parameter :code:`autokwd` to :code:`True` in the
constructor call::

  from textx.metamodel import metamodel_from_file
  my_metamodel = metamodel_from_file('mygrammar.tx', autokwd=True)

A keyword is considered any simple match from the grammar that is matched by the
regular expression :code:`[^\d\W]\w*`.

