.. _model:

textX models
============

Model is a python object graph consisting of POPOs (Plain Old Python Objects)
constructed from the input string that conforms to your DSL defined by the
grammar and additional :ref:`model and object processors <processors>`.

In a sense this structure is an Abstract Syntax Tree (AST) known from classic
parsing theory but it is actually a graph structure where each reference is
resolved to a proper python reference.

Each object is an instance of a class from meta-model. Classes are created
on-the-fly from grammar rules or are :ref:`supplied by the user
<custom-classes>`.

Model is created from input string using :code:`model_from_file` and
:code:`model_from_str` methods of meta-model instance::

  from textx.metamodel import metamodel_from_file

  my_mm = metamodel_from_file('mygrammar.tx')

  # Create model
  my_model = my_mm.model_from_file('some_model.ext')


Let's take a Entity language used in :ref:`custom-classes` section.

Content of :code:`entity.tx` file::

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


For meta-model construction and built-in registration see :ref:`custom-classes`
and :ref:`builtins` sections.

Now, we can use the :code:`entity_mm` meta-model to parse and create Entity
models::

  person_model = entity_mm.model_from_file('person.ent')

Where :code:`person.ent` file might contain this::

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


Special attributes
------------------

Beside attributes specified by the grammar each model object has
:code:`_position` attribute that hold the position in the input string where
the object has been matched by the parser.

This is an absolute position in the input stream. To convert it to line/column
format use :code:`pos_to_linecol` method of the parser::

  entity_mm.parser.pos_to_linecol(person_model.entities[0]._position)

This will give the line/column position tuple of the first entity.

