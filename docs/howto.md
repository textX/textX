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

## Modeling classes and objects: class inheritance

Inherited attributes or methods can be accumulated with the 
textx.scoping.providers.ExtRelativeName scope provider:

 * Unittest (classes with pseudo inherited methods)
   [tests/functional/test_scoping/test_metamodel_provider3.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_metamodel_provider3.py),
    * test_metamodel_provider_advanced_test3_inheritance2
    * test_metamodel_provider_advanced_test3_diamond

 * Unittest (components with inherited slots)
   [tests/functional/test_scoping/test_inheritance.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_inheritance.py),
