This is an example of simple workflow language.

Meta-model is defined in `workflow.tx` file.  Each `Workflow` has a name,
optional description, reference to the initial task, zero or more task
definition and zero or more action definitions.

Each `Task` instance starts with a keyword `task`. All tasks have name, entry
action, leave action and one or more next tasks references separated by a comma.

Action starts with a keyword `action` after which is given the name.

An example of workflow is given in file `example.wf`.

Test script `workflow.py` will load meta-model and example model and
export them to dot files. To run it do:

    $ python workflow.py

Checking and exporting to dot can also be done with `textx` command line tool:

```
$ textx visualize workflow.tx example.wf
Meta-model OK.
Model OK.
Generating 'workflow.tx.dot' file for meta-model.
To convert to png run 'dot -Tpng -O workflow.tx.dot'
Generating 'example.wf.dot' file for model.
To convert to png run 'dot -Tpng -O example.wf.dot'

$ dot -Tpng -O workflow.tx.dot
$ dot -Tpng -O example.wf.dot
```
