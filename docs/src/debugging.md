# Debugging

textX supports debugging on the meta-model (grammar) and model levels. If
debugging is enabled, textX will print various debugging messages.

If the `debug` parameter of the meta-model construction is set to `True`, debug
messages during grammar parsing and meta-model construction will be printed.
Additionally, a parse tree created during the grammar parsing as well as
meta-model (if constructed successfully) dot files will be generated:

```python
form textx.metamodel import metamodel_from_file

robot_metamodel = metamodel_from_file('robot.tx', debug=True)
```

If `debug` is set in the `model_from_file/str` calls, various messages during
the model parsing and construction will be printed. Additionally, parse tree
created from the input as well as the model will be exported to dot files.

```python
  robot_program = robot_metamodel.model_from_file('program.rbt', debug=True)
```

Alternatively, you can use [textx check or generate command](textx_command.md)
in debug mode.

    $ textx --debug generate --grammar robot.tx program.rbt --target dot

    *** PARSING LANGUAGE DEFINITION ***
    New rule: grammar_to_import -> RegExMatch
    New rule: import_stm -> Sequence
    New rule: rule_name -> RegExMatch
    New rule: param_name -> RegExMatch
    New rule: string_value -> OrderedChoice
    New rule: rule_param -> Sequence
    Rule rule_param founded in cache.
    New rule: rule_params -> Sequence
    ...

    >> Matching rule textx_model=Sequence at position 0 => */* This ex
      >> Matching rule ZeroOrMore in textx_model at position 0 => */* This ex
          >> Matching rule import_stm=Sequence in textx_model at position 0 => */* This ex
            ?? Try match rule StrMatch(import) in import_stm at position 0 => */* This ex
            >> Matching rule comment=OrderedChoice in import_stm at position 0 => */* This ex
                ?? Try match rule comment_line=RegExMatch(//.*?$) in comment at position 0 => */* This ex
                -- NoMatch at 0
                ?? Try match rule comment_block=RegExMatch(/\*(.|\n)*?\*/) in comment at position 0 => */* This ex

    ...


    Generating 'robot.tx.dot' file for meta-model.
    To convert to png run 'dot -Tpng -O robot.tx.dot'
    Generating 'program.rbt.dot' file for model.
    To convert to png run 'dot -Tpng -O program.rbt.dot'

This command renders parse trees and parser models of both textX and your
language to dot files. Also, a meta-model and model of the language will be
rendered if parsed correctly.

```admonish
By default all debug messages will be printed to stdout. You can provide `file`
parameter to `metamodel_from_file/str` to specify file-like object where all
messages should go.
```

