textX grammar
=============

Language syntax and meta-model are defined by textX grammar given as a set of
textX rules.

Rules
-----

The basic building blocks of the textX language are rules. Rule is written
in the following form::

  Hello:
    'hello' who=ID;
  ;

This rule is called `Hello`. After the name is a colon. Between the colon and
the semicolon at the end is a body of the rule given as textX expression. This
rule tells us that the pattern of `Hello` objects in the input string consists
of the word `hello` followed by the ID rule (here ID is a rule reference to the
builtin rule, more about this in a moment).

These are valid `Hello` objects::

  hello Alice
  hello Bob
  hello foo1234

Rule `Hello` at the same time defines a Python class `Hello`. When the rule is
recognized in the input stream an object of this class will get created and the
attribute `who` will be set to whatever the rule `ID` has matched after the word
`hello` (this is specified by the assignment `who=ID`).

Of course, there are many more rule expressions than shown in this small example.
In the next section a detailed description of each textX expression is given.

textX base types
~~~~~~~~~~~~~~~~

In the previous example you have seen an :code:`ID` rule. This rule is a part of
built-in rules that form the base of textX type system. Base types/rules are
given in the following figure:

.. image:

* :code:`ID` rule will match an common identifier consisting of letters, digits
  and underscores. The regex pattern that describe this rule is ... . This match
  will be converted to python string.
* :code:`INT` rule will match an integer number. This match will be converted to
  python :code:`int` type.
* :code:`FLOAT` rule will match a float number. This match will be converted to
  python :code:`float` type.
* :code:`BOOL` rule will match words :code:`true` or :code:`false`. This match
  will be converted to python :code:`bool` type.
* :code:`STRING` rule will match a quoted string. This match will be converted
  to python :code:`str` type.

Built-in types are automatically converted to python types during object
instantiation.

Rule expressions
~~~~~~~~~~~~~~~~

Rule expressions is a body of the rule. It is specified using basic expressions
and operators.

The basic expressions are:

* Sequence
* Ordered choice (|)
* Optional (?)
* Repetitions

  - Zero or more (*)
  - One or more (+)

* Assignments

  - Plain (=)
  - Boolean (?=)
  - Zero or more (\*=)
  - One or more (+=)

* Match

  - String match ('..')
  - Regex match (/../)

* References

  - Match reference
  - Link reference ([..])

Sequence
^^^^^^^^

Sequence is the simplest textX expression that is given by just writing
contained expression in a row. For example the following rule::

  Colors:
    "red" "green" "blue"
  ;

is defined as a sequence consisting of three string matches (:code:`red`
:code:`green` and :code:`blue`). Contained expression will be matched in the exact
order they are given. If some of the expression does not match the sequence
as a whole will fail. The above rule defined by sequence will match only the
following string::

  red green blue


Ordered choice
^^^^^^^^^^^^^^

Ordered choice is given as a set of expression separated by :code:`|` operator.
This operator will try to match contained expression from left to right and the
first match that succeeds will be used.

Example::

  Color:
    "red" | "green" | "blue"
  ;

Note that in most parsing technologies an unordered match (alternative) is used
which may lead to unabi

Underlaying parsing tehnology of textX is Arpeggio which is parser based on PEG
grammars and thus the :code:`|` operator directly translates to Arpeggio's PEG
ordered choice. Using ordered choice 


Optional
^^^^^^^^

Repetitions
^^^^^^^^^^^

* **Zero or more** repetition is specified by :code:`*` operator and will match
  the contained expression zero or more times. Here is an example::

    Colors:
      ("red"|"green"|"blue")*
    ;

  In this example *zero or more* repetition is applied on *ordered choice*. In
  each repeated match one color will be matched trying out from left to right.
  Thus, :code:`Colors` rule will match color as many as possible but will not
  fail if no color exists in the input string. The following would be matched by
  :code:`Colors` rule::

    red blue green

  but also::

    red blue blue red red green

  or empty string.


* *One or more* repetition is specified by :code:`+` operator and will match the
  contained expression one or more times. Thus, everything that is written for
  *zero or more* applies here except that at least one match must be performed
  for this expression to succeed. Here is an above example modified to match at
  least one color::

    Colors:
      ("red"|"green"|"blue")+
    ;

Assignments
^^^^^^^^^^^

Assignment is used for meta-model deduction. Each assignment will result in an
attribute of the meta-class created by the rule.

Each assignment consists of LHS (left-hand side) and RHS (right-hand side). The
LHS is always a name of the meta-class attribute while the RHS can be a
reference to other rule (either a match or link reference) or a direct match
(string or regex match). For example::

  Person:
    name=Name ',' surename=Surename ',' age=INT ',' height=INT ';'
  ;

The :code:`Name` and :code:`Surename` rules are not given in this example.

This example describes rule and meta-class :code:`Person` that will parse and
instantiate :code:`Person` objects with four attributes:

* :code:`name` - which will use rule `Name` to match the input and the
  :code:`name` will be a reference to the instance of :code:`Name` class,
* :code:`surename` - will use :code:`Surename` rule to match the input,
* :code:`age` - will use builtin type :code:`INT` to match a number from the
  input string. :code:`age` will be converted to python :code:`int` type.
* :code:`height` - the same as :code:`age` but the matched number will be
  assigned to :code:`height` attribute of the :code:`Person` instance.

Notice the comma as the separator between matches and the semicolon match at the
end of the rule.

If the RHS is textX one of BASETYPEs than the matched string will be converted
to some of plain python types (e.g. int, string, boolean).

If RHS is string or regex match like in this example::

  Color:
    color=/\w+/
  ;

than the attribute given by LHS will be set to be the matched string.

If the RHS is a reference to other rule than the attribute given by the LHS will
be set to refer to the object created by the RHS rule.

Following strings are matched by the :code:`Person` rule::

  Petar, Petrovic, 27, 185;
  John, Doe, 34, 178;


There are four types of assignments:

* **Plain** assignment will match its RHS once and assign what is matched to the
  attribute given by LHS. The above example uses plain assignments.

* **Boolean** assignment will 



Repetition modifiers
^^^^^^^^^^^^^^^^^^^^

Rule types
~~~~~~~~~~

There are three kinds of rules in textX:

- Common rules (or just rules)
- Abstract rules
- Match rules

Abstract and match rules are explained in the separate sections.


Grammar modularization
----------------------


