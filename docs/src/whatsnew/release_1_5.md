# What's new in textX 1.5

It's been quite a while since the last release of textX so this release brings a
lot of new features and fixes.

## Operator precedence change

Probably the most important/visible change is the change in the operator
precendence. In the previous version, sequence had lower precedence than
ordered choice which is counter-intuitive to the users that had previous
experience with other tools where this is not the case.

Ordered choice is now of lowest precedence which brings some backward
compatibility that should be addressed for migration to the new version.

For example, previously you would write:

    Rule:
        ('a'  'b') | ('c' 'd')
    ;
    
To match either `a b` or `c d`.

Now you can drop parentheses as the precedence of sequence is higher:

    Rule:
        'a'  'b' | 'c' 'd'
    ;
    
For the previous case there would be no problem in upgrade to 1.5 even if the
grammar is not changed. But consider this:

    Rule:
        'a' 'b' | 'c' 'd'
    ;
    
In the previous version this would match `a`, than `b` or `c`, and then `d` as
the `|` operator was of higher precedence than sequence.

For your grammar to match the same language you must now write:

    Rule:
      'a' ('b' | 'c') 'd'
    ;


## Unordered groups

There is often a need to specify several matches that should occur in an arbitrary
order. 

Read more [here](../grammar.md#repetitions)


## Match filters

Match rules always return Python strings. Built-in rules return proper Python
types. In order to change what is returned by match rules you can now register
python callables that can additionally process returned strings.

Read more [here](../metamodel.md#match-filters)


## Multiple assignments to the same attribute

textX had support for multiple assignments but it wasn't complete. When multiple
assignment is detected, in the previous version, textX will decide that the
multiplicity of the attribute is *many* but this lead to the problem if there is
no way for parser to collect more than one value even if there is multiple
assignments. For example, if all assignments belong to a different ordered
choice alternative (see issue #33).

In this version textX will correctly identify such cases. 

Read more [here](../grammar.md#multiple-assignment-to-the-same-attribute)

## Model API

There is now a set of handful functions for model querying.

Read more [here](../model.md#model-api).


## Additional special model attributes

In addition to `_tx_position` there is now `_tx_position_end` attribute on each
model object which has the value of the end of the match in the input stream.

In addition there is now `_tx_metamodel` attribute on the model which enables
easy access to the language meta-model.

Read more about it [here](../model.md#special-model-objects-attributes).

## textX Emacs mode

textX now has a [support for Emacs](https://github.com/novakboskov/textx-mode).
This package is also available in [MELPA](https://melpa.org/#/textx-mode).
