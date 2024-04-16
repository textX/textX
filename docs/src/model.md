# textX models

Model is a python object graph consisting of POPOs (Plain Old Python Objects)
constructed from the input string that conforms to your DSL defined by the
grammar and additional [model and object processors](metamodel.md#processors).

In a sense, this structure is an Abstract Syntax Tree (AST) known from classic
parsing theory, but it is actually a graph structure where each reference is
resolved to a proper python reference.

Each object is an instance of a class from the meta-model. Classes are created
on-the-fly from the grammar rules or are [supplied by the
user](metamodel.md#custom-classes).

A model is created from the input string using the `model_from_file` and 
`model_from_str` methods of the meta-model instance.

    from textx import metamodel_from_file

    my_mm = metamodel_from_file('mygrammar.tx')

    # Create model
    my_model = my_mm.model_from_file('some_model.ext')


```admonish
The `model_from_file` method takes an optional argument `encoding`
to control the input encoding of the model file to be loaded.
```
   

Let's take the Entity language used in [Custom
Classes](metamodel.md#custom-classes) section.

Content of `entity.tx` file:

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
                                  // for the primitive types (integer, string)
    ;


For the meta-model construction and built-in registration see [Custom
Classes](metamodel.md#custom-classes) and
[Builtins](metamodel.md#built-in-objects) sections.

Now, we can use the `entity_mm` meta-model to parse and create Entity models.

```python
person_model = entity_mm.model_from_file('person.ent')
```

Where `person.ent` file might contain this:

    entity Person {
      name : string
      address: Address
      age: integer
    }

    entity Address {
      street : string
      city : string
      country : string
    }

## Model API

Functions given in this section can be imported from `textx` module.

### `get_model(obj)`

`obj (model object)`

Finds the root of the model following `parent` references.


### `get_metamodel(obj)`

Returns meta-model the model given with `obj` conforms to.

### `get_parent_of_type(typ, obj)`

- `typ (str or class)`: the name of type of the type itself of the model object
searched for.
- `obj (model object)`: model object to start search from.

Finds first object up the parent chain of the given type. If no parent of the
given type exists `None` is returned.

### `get_children_of_type(typ, root, children_first=False, should_follow=lambda obj: True)`

- `typ (str or python class)`: The type of the model object we are looking for.
- `root (model object)`: Python model object which is the start of the search
    process.
- `children_first (bool)`: indicates if children should be returned before their
  parents.
- `should_follow (callable)`: a predicate used to decide if the object should be
  traversed.

Returns a list of all model elements of type `typ` starting from model element
`root`. The search process will follow containment links only. Non-containing
references shall not be followed.

### `get_children(selector, root, children_first=False, should_follow=lambda obj: True)`

- `selector (callable)`: a predicate returning True if the object is of interest.
- `root (model object)`: Python model object which is the start of the search
    process.
- `children_first (bool)`: indicates if children should be returned before their
  parents.
- `should_follow (callable)`: a predicate used to decide if the object should be
  traversed.

Returns a list of all selected model elements starting from model element
`root`. The search process will follow containment links only. Non-containing
references shall not be followed.

### `get_location(obj)`

Returns the location of the textX model object in the form of a dict with
`line/col/nchar/filename` keys. `nchar` is a substring length of the `obj` in
the input string. Filename can be `None` if the model is loaded from a string.
Return value is convenient for use in TextX exceptions (e.g. `raise
TextXSemanticError('Some message', **get_location(model_obj))`)

### `textx_isinstance(obj, cls)`

Return `True` if `obj` is instance of `cls` taking into account textX rule/class
hierarchy. For textX created classes you can get a reference to a class from
meta-model by keying into it using the class name `metamodel['SomeRule']`.

## Special model object's attributes

Beside attributes specified by the grammar, there are several special
attributes on model objects created by textX. All special attributes' names
start with prefix `_tx`.

These special attributes don't exist if the type of the resulting model object
don't allow dynamic attribute creation (e.g. for Python base builtin types -
str, int).

### _tx_position and _tx_position_end

`_tx_position` attribute holds the position in the input string where the
object has been matched by the parser. Each object from the model object graph
has this attribute.

This is an absolute position in the input stream. To convert it to line/column
format use `pos_to_linecol` method of the parser.

```python
line, col = entity_model._tx_parser.pos_to_linecol(
    person_model.entities[0]._tx_position)
```

Where `entity_model` is a model constructed by textX.

Previous example will give the line/column position of the first entity.

`_tx_position_end` is the position in the input stream where the object ends.
This position is one char past the last char belonging to the object. Thus,
`_tx_position_end - _tx_position == length of the object str representation`.

If you need line, column and filename of a textX object (e.g. for raising
`TextXSemanticError`) see [get_location above](#get_locationobj).


### _tx_filename

This attribute exists only on the root of the model. If the model is loaded
from a file, this attribute will be the full path of the source file. If the
model is created from a string this attribute will be `None`.

### _tx_parser

This attribute represents the concrete parser instance used for the model
(the attribute `_parser` of the `_tx_metamodel` is only a blueprint for the
parser of each model instance and cannot be used, e.g., to determine model
element positions in a file. Use the `_tx_parser` attribute of the model
instead).

### _tx_metamodel

This attribute exists only on the root of the model. It is a reference to the
meta-model object used for creating the model.


### _tx_fqn

Is the fully qualified name of the grammar rule/Python class in regard to the
import path of the grammar file where the rule is defined. This attribute is
used in `__repr__` of auto-generated Python classes.

### _tx_model_repository

The model may have a model repository (initiated by some scope provider or by
the metamodel). This object is responsible to provide and cache other model
instances (see textx.scoping.providers).

### _tx_model_params

This attribute always exists. It holds all additional parameters passed to
`model_from_str` or `model_from_file` of a metamodel. These parameters are
restricted by the `metamodel.model_param_defs` object ([model and object
processors](metamodel.md#optional-model-parameter-definitions)), which is
controlled by the metamodel designer.
