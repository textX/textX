textX language
==============

textX is inspired by the Xtext framework for domain-specific language engineering so all
the credits for the idea goes to the Xtext team.
If you have Xtext background than you will find yourself at home with textX.

The domain of textX language is language design. If resembles in a way a EBNF but
besides the language grammar definition defines a language meta-model
(i.e. its abstract syntax) at the same time.


Rules
-----

The basic building blocks of the textX language are rules. Rule is written in the following form::

  Hello:
    'hello' who=ID;
  ;

This rule is called `Hello`. After the name is a colon. Between the colon and the semicolon at the end
is a body of the rule. This rule tells us that the pattern of `Hello` objects in the input string consists
of the word `hello` followed by the ID rule (here ID is a rule reference to the builtin rule,more about
this in a moment).

These are valid `Hello` objects::

  hello Alice
  hello Bob
  hello foo1234

Rule `Hello` at the same time defines a Python class `Hello`. When the rule is recognized in the input stream
an object of this class will get created and the attribute `who` will be set to whatever the rule `ID` has matched
(this is specified by the assigment `who=ID`).

There are three kind of rules in textX:

- Common rules (or just rules)
- Abstract rules
- Match rules

Abstract and match rules are explained in the separate sections.

Matches
-------
Match is an element at the lowest level of the language. It does not have an internal structure.
In the parsing lingo *match* will result in creating a terminal during parsing.

textX has a two kind of match elements:

- string match
- regular expression match

String match are given in the form of the string and results in instruction to the parser to match
that string exacly as is given in the string match.
For example, in the `Hello` rule above `'hello'` is a string match that matches a word *hello* from the
input.

If you have a more complex string to match and you do know the pattern of that string but the string is not
fixed you can use a *regex match*.

Regex matches are regular expressions from standard python `re` module writen in between //.

For example, if we want to greet only those persons whose name includes only letters and the length
of their name is in between 5 and 10 characters we could write `Hello` rule like this::

  Hello:
    'hello' who=/\b[a-zA-Z]{5,10}\b/
  ;

Assignments
-----------

Lists
-----

Rule reference
--------------

Choice operator
---------------

Repetition operators
--------------------

Abstract rules
--------------

Match rules
-----------

