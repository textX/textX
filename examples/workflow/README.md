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
$ textx generate workflow.tx --target dot
Generating dot target from models:
/home/igor/repos/textX/textX/examples/workflow/workflow.tx
-> /home/igor/repos/textX/textX/examples/workflow/workflow.dot
   To convert to png run "dot -Tpng -O workflow.dot"

$ textx generate example.wf --grammar workflow.tx --target dot
Generating dot target from models:
/home/igor/repos/textX/textX/examples/workflow/example.wf
-> /home/igor/repos/textX/textX/examples/workflow/example.dot
   To convert to png run "dot -Tpng -O example.dot"

$ dot -Tpng -O workflow.dot
$ dot -Tpng -O example.dot
```
