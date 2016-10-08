This is an example of a simple Entity DSL.

File `entity.tx` contains a grammar of the language.  Each entity DSL model
consists of zero or more simple types definitions and one or more `Entity`
instances.  Each `Entity` instance contains one or more `Property` instance.
Each `Property` has a name conforming to built-in `ID` rule and a type which
can be a reference to either `SimpleType` or `Entity` from the model or one of
two built-in simple types representing basic types (`integer` and `string`, see
file `entity_test.py`).

Example model is given in the file `person.ent`.

A program `entity_test.py` will instantiate meta-model from the grammar,
register built-in simple types `integer` and `string` and register user class
`SimpleType` so that built-in types can be instantiated from the code. A person
example model is than parsed/instantiated by the meta-model and both meta-model
and model are exported to .dot files in the folder `dotexport`.

An example of code generation is presented in the program `entity_codegen.py`.
The code is generated in the `srcgen` subfolder using
[jinja2](http://jinja.pocoo.org/docs/dev/) template engine and the template
`java.template`. For each Entity instance one java file is generated.

**Note:** Meta-model/grammar can be checked/visualized by `textx` command line
tool but model can't because it depends on two built-in simple types (`integer`
and `string`) which must be provided during meta-model instantiation (see
`entity_test.py` file).

To run the example do the following:

- Verify that textX is installed. See documentation how to do that.
- Install [Jinja2]() for code generation
    
        $ pip install Jinja2

- From the Entity example folder run

        $ python entity_test.py

- Previous command will generate dot files in `dotexport` folder. To convert 
  those files to PNG format do (you must have [GraphViz](http://graphviz.org/)
  installed):

        $ dot -Tpng -O dotexport/*.dot

  You will get `entity_meta.dot.png` (Entity meta-model) and `person.dot.png`
  (Person model) diagram.

- Run code generation:

        $ python entity_codegen.py

  This will produce Java files `Address.java` and `Person.java` in `srcgen`
  folder that corresponds to entities from the Person model.

