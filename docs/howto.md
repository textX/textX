# Howto

## Modeling hierarchical data structures: referencing attributes

The idea is to model a structure with attributes (which may again be 
structures).

    struct A {
        val x
    }
    struct B {
        val a: A
    }
    struct C {
        val b: B
        val a: A
    }
    struct D {
        val c: C
        val b1: B
        val a: A
    }
    
    instance d: D
    reference d.c.b.a.x
    reference d.b1.a.x

 * Unittest 
   [tests/functional/examples/test_hierarchical_data_structures_referencing_attributes.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/examples/test_hierarchical_data_structures_referencing_attributes.py),

## Modeling classes and objects: class inheritance

Inherited attributes or methods can be accumulated with the 
textx.scoping.providers.ExtRelativeName scope provider:

 * Unittest (classes with pseudo inherited methods)
   [tests/functional/test_scoping/test_metamodel_provider3.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_metamodel_provider3.py),
    * test_metamodel_provider_advanced_test3_inheritance2
    * test_metamodel_provider_advanced_test3_diamond

 * Unittest (components with inherited slots)
   [tests/functional/test_scoping/test_inheritance.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_inheritance.py),


## Modeling Wiki-like texts with references inside

The idea is to model a string with an arbitrary content and links to other
objects (the links are encoded with a special symbol, e.g. "[myref]" or - 
like in the exmample referenced below "@myref"):

    ENTRY Hello:    """a way to say hello\@mail (see @[Hi])"""
    ENTRY Hi:       """another way to say hello (see @[Hello])"""
    ENTRY Salut:    """french "hello" (@[Hello]@[Hi]@[Bonjour]@[Salut]@[Hallo])"""
    ENTRY Hallo:    """german way to say hello (see ""@[Hello]"")"""
    ENTRY Bonjour:  """another french "\@@[Hello]", see @[Salut]"""
    ENTRY NoLink:   """Just text"""
    ENTRY Empty:    """"""

 * Unittest (components with inherited slots)
   [tests/functional/examples/test_free_text_with_references.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/examples/test_free_text_with_references.py),


## Referncing a json database from within a textx model

Here, we link a textx model with a non textx database (could be any database
or data structure available in python). If you have, e.g., a DOORS binding,
you could also reference such information sources.

 * JSON-File "data.json":
 
        {
          "name": "pierre",
          "gender": "male"
        }
 
 * TextX-model:

        import "data.json" as data
        access A1 data.name
        access A2 data.gender


 * Unittest (components with inherited slots)
   [tests/functional/test_scoping/test_reference_to_nontextx_attribute.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_reference_to_nontextx_attribute.py),

