These are two examples of expression languages.

Both languages support variable assignment in the form:

    <variable_name> = <variable_value> ;

Where `variable_value` is arbitrary expression on the given language and
can reference previously defined variables.

After variable initialization you can write an expression which is evaluated
and returned as the value of the model.

`calc.py` is a language based on four basic arithmetic operations (+, -, *, /)
and values can be integers and floats.

An example input is:

    a = 6;
    b = 2 * a + 17.5;
    -(7/a+8.2)-b*45+13/3.45

`boolean.py` is a language based on three boolean operations (`and`, `or` and
`not`).

An example input is:

    a = true;
    b = not a;
    a and b or not false

Evaluation is done using [custom
classes](https://textx.github.io/textX/stable/metamodel/#custom-classes).
Provided classes have `value` property which will evaluate the result using
appropriate operations and values of referenced subexpressions.

In this examples, grammar is embedded inside Python string so `textx` command
cannot be used. Instead, meta-model and model are exported to dot if the
example is run in debug mode. Pass `debug=True` in the call to the `main`
function at the last line.

`calc.py` example has a few variants, each demostrates a different approach
for working with the model:

  1. `calc_processors.py` -- instead of the custom classes employs object
     processors for evaluation
  2. `calc_monkey.py` -- similar to original `calc.py`, but instead of defining
     the custom classes, patches the ones created by textx, adding the `value`
     property which will evaluate the result.
  3. `calc_isinstance.py` -- uses a single `evaluate` function that traverses
     the model; the function employs `textx_isinstance()` to tell apart between
     different object types in the model tree.

