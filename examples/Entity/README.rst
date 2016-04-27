This is an example of a simple Entity DSL.

File :code:`entity.tx` contains a grammar of the language.  Each entity DSL
model consists of zero or more primitive types definitions and one or more
:code:`Entity` instances.  Each :code:`Entity` instance contains one or more
:code:`Attribute` instance.  Each :code:`Attribute` has a name conforming to
built-in :code:`ID` rule and a type which can be a reference to either
:code:`PrimitiveType` or :code:`Entity` from the model or one of two built-in
primitive types representing basic types (:code:`integer` and :code:`string`,
see file :code:`entity_test.py`).

Example model is given in the file :code:`person.ent`.

A program :code:`entity_test.py` will instantiate meta-model from the grammar,
register built-in primitive types :code:`integer` and :code:`string` and
register user class :code:`PrimitiveType` so that built-in types can be
instantiated from the code. A person example model is than parsed/instantiated
by the meta-model and both meta-model and model are exported to .dot files in
the folder :code:`dotexport`.

An example of code generation is presented in the program
:code:`entity_codegen.py`. The code is generated in the :code:`srcgen` subfolder
using `jinja2 <http://jinja.pocoo.org/docs/dev/>`_ template engine and the
template :code:`java.template`. For each Entity instance one java file is
generated.

**Note:** Meta-model/grammar can be checked/visualized by :code:`textx` command
line tool but model can't because it depends of two built-in primitive types
(:code:`integer` and :code:`string`).

