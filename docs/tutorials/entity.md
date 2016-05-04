# Entity tutorial

A tutorial for building ER-like language and generating Java code.

---

!!! note "Work in progress"
    Will be done soon. In the meantime see [Entity example](https://github.com/igordejanovic/textX/tree/master/examples/Entity).

## Entity language

In this example we will see how to make a simple language form data modeling.
We will use this language to generate Java source code (POJO classes).

Our main concept will be `Entity`. Each entity will have one or more
`properties`.  Each property is defined by its `name` and its `type`.

Let's sketch out a model on our language.

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


## The grammar

In our example we see that each entity starts with a keyword `entity`. After
that, we have a name that is identifier and open brace.
Inside braces we have properties. In textX this is written as:

    Entity:
        'entity' name=ID '{'
            properties+=Property
        '}'
    ;

We can see that the `Entity` rule references `Property` rule from the
assignment. Each property is defined by the `name`, semi-colon (`:`) and the
name of the type. This can be written as:


