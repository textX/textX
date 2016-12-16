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

A model is created from the input string using the `model_from_file` and `model_from_str`
methods of the meta-model instance.

    from textx.metamodel import metamodel_from_file

    my_mm = metamodel_from_file('mygrammar.tx')

    # Create model
    my_model = my_mm.model_from_file('some_model.ext')


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

!!! note
    This is available in the development version.

Functions given in this section can be imported from `textx.model` module.

### `model_root(obj)`

`obj (model object)`

Finds the root of the model following `parent` references.


### `metamodel(obj)`

Returns metamodel for the model given `obj` belongs to.

### `parent_of_type(typ, obj)`

- `typ (str or class)`: the name of type of the type itself of the model object
searched for.
- `obj (model object)`: model object to start search from.

Finds first object up the parent chain of the given type. If no parent of the
given type exists `None` is returned.

### `children_of_type(typ, root)`

- `typ (str or python class)`: The type of the model object we are looking for.
- `root (model object)`: Python model object which is the start of the search
    process.

Returns a list of all model elements of type `typ` starting from model element
`root`. The search process will follow containment links only. Non-containing
references shall not be followed.

## Special model object's attributes

Beside attributes specified by the grammar, there are several special
attributes on model objects created by textX. All special attributes' names
start with prefix `_tx`.

These special attributes don't exist if the type of the resulting model object
don't allow dynamic attribute creation (e.g. for Python base builtin types -
str, int).

### _tx_position

`_tx_position` attribute holds the position in the input string where the
object has been matched by the parser. Each object from the model object graph
has this attribute.

This is an absolute position in the input stream. To convert it to line/column
format use `pos_to_linecol` method of the parser.

```python
line, col = entity_mm.parser.pos_to_linecol(
    person_model.entities[0]._tx_position)
```

Where `entity_mm` is a meta-model of the language.

Previous example will give the line/column position of the first entity.

### _tx_filename

This attribute exists only on the root of the model. If the model is loaded
from a file, this attribute will be the full path of the source file. If the
model is created from a string this attribute will be `None`.

### _tx_metamodel

This attribute exists only on the root of the model. It is a reference to the
meta-model object used for creating the model.

This attribute can be useful to access the parser given the reference to the
model.

```python
parser = model._tx_metamodel.parser
line, col = parser.pos_to_linecol(some_model_object)
```


