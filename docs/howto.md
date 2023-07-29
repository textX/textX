# HowTos

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
   [tests/functional/examples/test_hierarchical_data_structures_referencing_attributes.py](https://github.com/textX/textX/blob/master/tests/functional/examples/test_hierarchical_data_structures_referencing_attributes.py)

## Modeling classes and objects: class inheritance

Inherited attributes or methods can be accumulated with the 
textx.scoping.providers.ExtRelativeName scope provider:

 * Unittest (classes with pseudo inherited methods)
   [tests/functional/test_scoping/test_metamodel_provider3.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_metamodel_provider3.py)
    * test_metamodel_provider_advanced_test3_inheritance2
    * test_metamodel_provider_advanced_test3_diamond

 * Unittest (components with inherited slots)
   [tests/functional/test_scoping/test_inheritance.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_inheritance.py)


## Modeling Wiki-like texts with references inside

The idea is to model a string with an arbitrary content and links to other
objects (the links are encoded with a special symbol, e.g. "[myref]" or - 
like in the exmample referenced below "@[myref]"):

    ENTRY Hello:    """a way to say hello\@mail (see @[Hi])"""
    ENTRY Hi:       """another way to say hello (see @[Hello])"""
    ENTRY Salut:    """french "hello" (@[Hello]@[Hi]@[Bonjour]@[Salut]@[Hallo])"""
    ENTRY Hallo:    """german way to say hello (see ""@[Hello]"")"""
    ENTRY Bonjour:  """another french "\@@[Hello]", see @[Salut]"""
    ENTRY NoLink:   """Just text"""
    ENTRY Empty:    """"""

 * Unittest
   [tests/functional/examples/test_free_text_with_references.py](https://github.com/textX/textX/blob/master/tests/functional/examples/test_free_text_with_references.py)


## Referencing a JSON database from within a textX model

Here, we link a textX model with a non textX database (could be any database
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


 * Unittest
   [tests/functional/test_scoping/test_reference_to_nontextx_attribute.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_reference_to_nontextx_attribute.py)

## Referencing global data using full qualified names

 * Example model:

        package P1 {
            class Part1 {
            }
        }
        package P2 {
            class Part2 {
                attr C2 rec;
            }
            class C2 {
                attr P1.Part1 p1;
                attr Part2 p2a;
                attr P2.Part2 p2b;
            }
        }

 * Unittest
   [tests/functional/test_scoping/test_full_qualified_name.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_full_qualified_name.py)


## Multi-file models

 * Unittest (global import)
   [tests/functional/test_scoping/test_global_import_modules.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_global_import_modules.py)

 * Unittest (explicit import, "importURI")
   [tests/functional/test_scoping/test_import_module.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_import_module.py)

 * Unittest (explicit import, "importURI" with custom search path)
   [tests/functional/test_scoping/test_import_module_search_path_issue66.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_import_module_search_path_issue66.py)


## Multi-metamodel multi-file models

Here, we focus on referencing model elements from models based on other textX 
meta models. These other meta models are typically imported from other python
modules (e.g. deployed separately).

In the example referenced below, we simulate three modules with three classes
in the unittest. Each class take the role of one module and defines one
concrete DSL. These DLS reference each other.

 * Model example (types.type) - "Type"-DSL

        type int
        type string 

 * Model example (data_structures.data) - "Data"-DSL

        #include "types.type"

        data Point { x: int y: int}
        data City { name: string }
        data Population { count: int}

 * Model example (data_flow.flow) - "Flow"-DSL

        #include "data_structures.data"
        #include "types.type" // double include, loaded 1x only
        
        algo A1 : Point -> City
        algo A2 : City -> Population
        connect A1 -> A2

 * Model example (data_flow.flow) - "Flow"-DSL with validation error

        #include "data_structures.data"
        
        algo A1 : Point -> City
        algo A2 : City -> Population
        connect A2 -> A1 // Error, must be A1 -> A2

 * Unittest
   [tests/functional/test_metamodel/test_multi_metamodel_refs.py](https://github.com/textX/textX/blob/master/tests/functional/test_metamodel/test_multi_metamodel_refs.py)

## Enable and distinguish float and int values for attributes

 * Model text:
 
        x1 = 1
        x2 = -1
        y1 = 1.0
        y2 = 1.1e-2
        y3 = -1.1e+2

 * Unittest 
   [tests/functional/examples/test_modeling_float_int_variables.py](https://github.com/textX/textX/blob/master/tests/functional/examples/test_modeling_float_int_variables.py)

## Parsing structures inside arbitrary surrounding text

See this [StackOverflow question](https://stackoverflow.com/questions/53379893/parsing-dhcpd-conf-with-textx).

## Optimizing grammar performance

When it comes to parsing very large files with textX, the performance issues
may arise. In certain cases, a good performance improvement can be achieved by
optimizing the grammar.

Investigating the grammar with the parse trace option enabled (`debug=true`) 
helps to reveal the excessive backtrackings (unsuccessful matches) that are 
essentially the wasted computations. By investigating these backtrackings,
valuable clues can be obtained regarding possible inefficiencies in the 
grammar design.

Known optimization techniques:

- Reorder OrderedChoice to put first those members that occur more often in 
  inputs.

- If a grammar has a hot path that is called out very often and this path
  contains negative assertions (see this
  [example](https://stackoverflow.com/a/68891730/598057)), these negative 
  assertions can be optimized by merging them all together in a single 
  regex. Regex engine is implemented in C and is much faster to handle the
  negative assertions in one go compared to when the negative matching is done
  by Arpeggio on the Python level.

## Caching parsed content to speed up processing

Parsing a single text file with textX can be fast. However, when dealing with
multiple files that need to be re-parsed every time a program is invoked, it is
worth considering the option of caching the parsed content.

One straightforward solution, using Python, involves utilizing Python's
[pickle](https://docs.python.org/3/library/pickle.html) module. After running a
textX job, a set of Python objects is created based on the textX grammar. The
Pickle module allows storing these objects in a file on the file system.
Consequently, when the program is executed again, instead of parsing the textX
grammar from scratch, the program can efficiently recreate the Python objects
from the cached file.

To ensure that the cache remains valid, the modification date of the original
text file can be compared with that of the cached file. If the cached file is
found to be older than the original text file, it indicates that the textX
parser needs to be called again to obtain the latest result and subsequently
update the cached file.
