# textX models

Model is a python object graph consisting of POPOs (Plain Old Python Objects)
constructed from the input string that conforms to your DSL defined by the
grammar and additional [model and object processors](metamodel.md#processors).

In a sense this structure is an Abstract Syntax Tree (AST) known from classic
parsing theory but it is actually a graph structure where each reference is
resolved to a proper python reference.

Each object is an instance of a class from meta-model. Classes are created
on-the-fly from grammar rules or are [supplied by the
user](metamodel.md#custom-classes).

Model is created from input string using `model_from_file` and `model_from_str`
methods of meta-model instance.

    from textx.metamodel import metamodel_from_file

    my_mm = metamodel_from_file('mygrammar.tx')

    # Create model
    my_model = my_mm.model_from_file('some_model.ext')


Let's take a Entity language used in [Custom
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
                                  // for primitive types (integer, string)
    ;


For meta-model construction and built-in registration see [Custom
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


## Special attributes

Beside attributes specified by the grammar each model object has
`_tx_position` attribute that hold the position in the input string where
the object has been matched by the parser.

This is an absolute position in the input stream. To convert it to line/column
format use `pos_to_linecol` method of the parser.

```python
line, col = entity_mm.parser.pos_to_linecol(
    person_model.entities[0]._tx_position)
```

This will give the line/column position of the first entity.

