# textX grammar

Language syntax and meta-model are defined by textX grammar given as a set of
textX rules.

## Rules

The basic building blocks of the textX language are rules. Rule is written
in the following form:

    Hello:
      'hello' who=ID;
    ;

This rule is called `Hello`. After the name is a colon. Between the colon and
the semicolon at the end is a body of the rule given as textX expression. This
rule tells us that the pattern of `Hello` objects in the input string consists
of the word `hello` followed by the ID rule (here ID is a rule reference to the
builtin rule, more about this in a moment).

These are valid `Hello` objects:

    hello Alice
    hello Bob
    hello foo1234

Rule `Hello` at the same time defines a Python class `Hello`. When the rule is
recognized in the input stream an object of this class will get created and the
attribute `who` will be set to whatever the rule `ID` has matched after the word
`hello` (this is specified by the assignment `who=ID`).

Of course, there are many more rule expressions than shown in this small example.
In the next section a detailed description of each textX expression is given.

## textX base types

In the previous example you have seen an `ID` rule. This rule is a part of
built-in rules that form the base of textX type system. Base types/rules are
given in the following figure:

![base types](images/base_types.png)

* `ID` rule will match an common identifier consisting of letters, digits
  and underscores. The regex pattern that describe this rule is `'[^\d\W]\w*\b'`.
  This match will be converted to a python string.
* `INT` rule will match an integer number. This match will be converted to
  python `int` type.
* `FLOAT` rule will match a float number. This match will be converted to
  python `float` type.
* `BOOL` rule will match words `true` or `false`. This match
  will be converted to python `bool` type.
* `STRING` rule will match a quoted string. This match will be converted
  to python `str` type.

Built-in types are automatically converted to python types during object
instantiation. See
[auto-initialization](metamodel.md#auto-initialization-of-attributes) for more information.

## Rule expressions

Rule expressions is a body of the rule. It is specified using basic expressions
and operators.

The basic expressions are:

* Sequence
* Ordered choice (`|`)
* Optional (`?`)
* Repetitions
    * Zero or more (`*`)
    * One or more (`+`)

* Assignments
    * Plain (`=`)
    * Boolean (`?=`)
    * Zero or more (`*=`)
    * One or more (`+=`)

* Matches
    * String match (`'...'`)
    * Regex match (`/.../`)

* References
    * Match reference
    * Link reference (`[..]`)

### Sequence

Sequence is the simplest textX expression that is given by just writing
contained sub-expressions one after another. For example the following rule:

    Colors:
      "red" "green" "blue"
    ;

is defined as a sequence consisting of three string matches (`red`
`green` and `blue`). Contained expressions will be matched in the
exact order they are given. If some of the expressions does not match the
sequence as a whole will fail. The above rule defined by the sequence will match
only the following string:

    red green blue

!!! note
    If whitespace skipping is included (which is default) arbitrary whitespaces
    can occur between matched words.


### Ordered choice

Ordered choice is given as a set of expression separated by `|` operator.
This operator will try to match contained expression from left to right and the
first match that succeeds will be used.

Example:

    Color:
      "red" | "green" | "blue"
    ;

This will match either `red` or `green` or `blue` and the parser will try the
match in that order.

!!! note
    In most classic parsing technologies an unordered match (alternative) is used
    which may lead to ambiguous grammar where multiple parse tree may exist for
    the same input string.

Underlaying parsing technology of textX is 
[Arpeggio](https://github.com/igordejanovic/Arpeggio) which is parser based on
PEG grammars and thus the `|` operator directly translates to Arpeggio's
PEG ordered choice. Using ordered choice yield unambiguous parsing. If the text
parses there is only one parse tree possible.


### Optional

`Optional` is an expression that will match contained expression if it can but
will not failed otherwise. Thus, optional expression always succeeds.

Example:

    MoveUp:
      'up' INT?
    ;

`INT` match is optional in this example. This means that the `up` keyword is
required but afterwards and integer may be found but it doesn't have to.

Following lines will match:

    up 45
    up 1
    up

Optional expression can be more complex. For example:

    MoveUp:
      'up' ( INT | FLOAT )?

Now, an ordered choice in parentheses is optional.


### Repetitions

* **Zero or more** repetition is specified by `*` operator and will match
  the contained expression zero or more times. Here is an example:

        Colors:
          ("red"|"green"|"blue")*
        ;

    In this example *zero or more* repetition is applied on the *ordered choice*.
    In each repeated match one color will be matched trying out from left to
    right.  Thus, `Colors` rule will match color as many as possible but
    will not fail if no color exists in the input string. The following would be
    matched by `Colors` rule:

        red blue green

    but also:

        red blue blue red red green

    or empty string.


* **One or more** repetition is specified by `+` operator and will match the
  contained expression one or more times. Thus, everything that is written for
  **zero or more** applies here except that at least one match must be found for
  this expression to succeed. Here is an above example modified to match at
  least one color:

        Colors:
          ("red"|"green"|"blue")+
        ;

### Assignments

Assignment is used as a part of the meta-model deduction process. Each
assignment will result in an attribute of the meta-class created by the rule.

Each assignment consists of LHS (left-hand side) and RHS (right-hand side). The
LHS is always a name of the meta-class attribute while the RHS can be a
reference to other rule (either a match or link reference) or a simple match
(string or regex match). For example:

    Person:
      name=Name ',' surename=Surename ',' age=INT ',' height=INT ';'
    ;

The `Name` and `Surename` rules referenced in the RHS of the first two
assignments are not given in this example.

This example describes rule and meta-class `Person` that will parse and
instantiate `Person` objects with four attributes:

* `name` - which will use rule `Name` to match the input and the
  `name` will be a reference to the instance of `Name` class,
* `surename` - will use `Surename` rule to match the input,
* `age` - will use builtin type `INT` to match a number from the
  input string. `age` will be converted to python `int` type.
* `height` - the same as `age` but the matched number will be
  assigned to `height` attribute of the `Person` instance.

Notice the comma as the separator between matches and the semicolon match at the
end of the rule. Those matches must be found in the input but the matched
strings will be discarded. They represent a syntactic noise.

If the RHS is one of textX BASETYPEs than the matched string will be converted
to some of plain python types (e.g. `int`, `string`, `boolean`).

If RHS is string or regex match like in this example:

    Color:
      color=/\w+/
    ;

then the attribute given by LHS will be set to be the string matched by the RHS
regular expression or string.

If the RHS is a reference to other rule than the attribute given by the LHS will
be set to refer to the object created by the RHS rule.

Following strings are matched by the `Person` rule from above:

    Petar, Petrovic, 27, 185;
    John, Doe, 34, 178;


There are four types of assignments:

* **Plain assignment** (`=`) will match its RHS once and assign what is
  matched to the attribute given by LHS. The above example uses plain
  assignments.

    Examples:

        a=INT
        b=FLOAT
        c=/[a-Z0-9]+/
        dir=Direction

* **Boolean assignment** (`?=`) will set the attribute on `True` if
  the RHS match succeeds or `False` otherwise.

    Examples::

        cold ?= 'cold'
        number_given ?= INT

* **Zero or more assignment** (`*=`) - LHS attribute will be a
  `list`. This assignment will match RHS as long as match succeeds and
  each matched object will be appended to the attribute. If no match succeeds
  attribute will be an empty list.

    Examples::

        commands*=Command
        numbers*=INT

* **One or more assignment** (`+=`) - same as previous but must match RHS
  at least once. If no match succeeds this assignment does not succeeds.



### Matches

Match expression are, besides base type rules, the expression at the lowest
level. They are the basic building blocks for more complex expressions. These
expressions will consume input on success.

There are two types of match expressions:

* **String match** - is written as a single quoted string. It will match literal
  string on the input.

    Here are a few examples of string matches:

        'blue'
        'zero'
        'person'

* **Regex match** - uses regular expression defined inside `/ /` to match
  input. Therefore, it defines a whole class of strings that can be matched.
  Internally a python `re` module is used.

    Here are few example of regex matches:

        /\s*/
        /[-\w]*\b/
        /[^}]*/

### References

Rules can reference each other. References are usually used as a
RHS of the assignments. There are two types of rule references:

* **Match rule reference** - will *call* other rule. When instance of the called
  rule is created it will be assigned to the attribute on the LHS. We say that
  referred object is contained inside referring object (e.g. they form a
  [parent-child relationship](metamodel.md#parent-child-relationships).

    Example::

        Structure:
          'structure' '{'
            elements*=StructureElement
          '}'
        ;

    `StructureElement` will be matched zero or more times. With each match a new
    instance of `StructureElement` will be created and appended to `elements`
    python list. A `parent` attribute of each `StructureElement` will be set to
    the containing `Structure`.

* **Link rule reference** - will match an identifier of some class object at the
  given place and convert that identifier to python reference to target object.
  This reference resolving is done automatically by textX. By default a
  `name` attribute is used as an identifier of the object. Currently,
  there is no automatic support for name spaces in textX. All objects of the
  same class are in a single namespace.

    Example:

        ScreenType:
          'screen' name=ID "{"
          '}'
        ;

        ScreenInstance:
          'screen' type=[ScreenType]
        ;

    The `type` attribute is a link to `ScreenType` object. This is a valid
    usage:

        // This is definition of ScreenType object
        screen Introduction {

        }

        // And this is reference link to the above ScreenType object
        // ScreenInstance instance
        screen Introduction

    `Introduction` will be matched, the `ScreenType` object with that name will
    be found and `type` attribute of `ScreenInstance` instance will be set to
    it.

    `ID` rule is used by default to match link identifier. If you want to change
    that you can use the following syntax:

        ScreenInstance:
          'screen' type=[ScreenType|WORD]
        ;

    Here, instead of `ID` a `WORD` rule is used to match object identifier.


### Repetition modifiers

Repetition modifiers are used for the modification of repetition expressions
(`*`, `+`, `*=`, `+=`). They are specified in brackets `[  ]`. If there are more
modifiers they are separated by a comma.

Currently there are two modifiers defined:

* **Separator modifier** - is used to define separator on multiple matches.
  Separator is simple match (string match or regex match).

    Example:

        numbers*=INT[',']

    Here a separator string match is defined (`','`). This will match zero
    or more integers separated by commas.

        45, 47, 3, 78

    A regex can be specified as a separator.

        fields += ID[/;|,|:/]

    This will match IDs separated by either `;` or `,` or `:`.

        first, second; third, fourth: fifth

* **End-of-line terminate modifier** (`eolterm`) - used to terminate repetition
  on end-of-line. By default repetition match will span lines. When this
  modifier is specified repetition will work inside current line only.

    Example:

        STRING*[',', eolterm]

    Here we have separator as well as `eolterm` defined. This will match
    zero or more strings separated by commas inside one line.

        "first", "second", "third"
        "fourth"

    If we run example expression once on this string it will match first line only.
    `"fourth"` in the second line will not be matched.

!!! warning
    Be aware that when `eolterm` modifier is used its effect starts from
    previous match. For example:

        Conditions:
          'conditions' '{'
            varNames+=WORD[eolterm]    // match var names until end of line
          '}'

    In this example `varNames` must be matched in the same line with
    `conditions {` because `eolterm` effect start immediately.
    In this example we wanted to give user freedom to specify var names on
    the next line, even to put some empty lines if he/she wish. In order to do
    that we should modify example like this::

        Conditions:
          'conditions' '{'
            /\s*/
            varNames+=WORD[eolterm]    // match var names until end of line
          '}'

    Regex match `/\s*/` will collect whitespaces (spaces and new-lines)
    before `WORD` match begins. Afterwards, repeated matches will work
    inside one line only.



## Rule types

There are three kinds of rules in textX:

- Common rules (or just rules)
- Abstract rules
- Match rules

**Common rules** are rules that contains at least one assignment, i.e., they
have attributes defined. For example:

    InitialCommand:
      'initial' x=INT ',' y=INT
    ;

This rule have two attributes defined: `x` and `y`.
    
**Abstract rules** are rules given as an ordered choice of other rules. For
example:

    Command:
      MoveCommand | InitialCommand
    ;

At least one of the referenced rules must be the common rule. A meta-class of
this rule will never be instantiated. The purpose of this rule is to generalize
other rules and be used in match and link references.

For example:

    Program:
      'begin'
        commands*=Command
      'end'
    ;

Python objects in `commands` list will be either instances of `MoveCommand` or
`InitialCommand`.


**Match rule** is a rule that have no assignments either direct or indirect,
i.e. all referenced rules are match rules too. It is usually used to specify
enumerated values or some complex string matches.

Examples:

    Widget:
      "edit"|"combo"|"checkbox"|"togglebutton"
    ;

    Name:
      STRING|/(\w|\+|-)+/
    ;

    Value:
      /(\w|\+|-)+/ | FLOAT | INT
    ;

These rules can be used in match references only and they produce objects of
base python types (`str`, `int`, `bool`, `float`).


## Rule modifiers

Rule modifiers are used for  the modification of rules expression. They are
specified in brackets (`[  ]`) at the beginning of the rule definition after the
rule name. Currently, they are used to alter parser configuration for whitespace
handling on the rule level.

There are two rule modifier at the moment:

* **skipws, noskipws** - are used to enable/disable whitespace skipping during
  parsing. This will change global parser `skipws` setting given during
  meta-model instantiation.

    Example:

        Rule:
            'entity' name=ID /\s*/ call=Rule2;
        Rule2[noskipws]:
            'first' 'second';

    In this example `Rule` rule will use default parser behavior set during
    meta-model instantiation while `Rule2` rule will disable whitespace
    skipping. This will change `Rule2` to match the word `firstsecond` but not
    words `first second` with whitespaces in between.

    !!! note

        Remember that whitespace handling modification will start immediately
        after previous match. In the above example, additional `/\s*/` is given
        before `Rule2` call to consume all whitespaces before trying to match
        `Rule2`.

* **ws** - used to redefine what is considered to be a whitespaces on the rule
  level. textX by default treat space, tab and new-line as a whitespace
  characters. This can be changed globally during meta-model instantiation (see
  [Whitespace handling](metamodel.md#whitespace-handling)) or per rule using 
  this modifier.

    Example:

        Rule:
            'entity' name=ID /\s*/ call=Rule2;
        Rule2[ws='\n']:
            'first' 'second';

    In this example `Rule` will use default parser behavior but the
    `Rule2` will alter the white-space definition to be new-line only.
    This means that the words `first` and `second` will get matched
    only if they are on separate lines or in the same line but without other
    characters in between (even tabs and spaces).

    !!! note

        As in previous example the modification will start immediately so if you
        want to consume preceding spaces you must do that explicitely as given
        with `/\s*/` in the :`Rule`.


## Grammar comments

Syntax for comments inside grammar is `//` for line comments and
`/* ... */` for block comments.

## Language comments

To support comments in your DSL use a special grammar rule `Comment`.
textX will try to match this rule in between each other normal grammar match
(similar to whitespace matching).
If the match succeeds the matched content will be discarded.


For example, in the [robot language example](tutorials/robot.md) comments are
defined like this:

    Comment:
      /\/\/.*$/
    ;

Which states that everything starting with `//` and continuing until the
end of line is a comment.


## Grammar modularization

Grammars can be defined in multiple files and than imported. Rules used in
references are first searched in current file and than in imported files in the
order of import.

  Example:

    import scheme

    Library:
      'library' name=Name '{'
        attributes*=LibraryAttribute

        scheme=Scheme

      '}'
    ;

`Scheme` rule is defined in `scheme.tx` grammar file imported at the beginning.

Grammar files may be located in folders. In that case dot notation is used.

  Example:

    import component.types

`types.tx` grammar is located in `component` folder relatively from current
grammar file.

If you want to override default search order you can specify fully qualified
name of the rule using dot notation when giving the name of the referring
object.

  Example:

    import component.types

    MyRule:
      a = component.types.List
    ;

    List:
      '[' values+=BASETYPE[','] ']'
    ;

`List` from `component.types` is matched/instantiated and set to `a` attribute.

