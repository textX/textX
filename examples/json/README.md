# JSON example

This is an example of making language/parsing support for popular [JSON
data-interchange format](http://json.org/).

JSON grammar is given in `json.tx`. All examples are taken from [json.org
example page](http://json.org/example.html).

Test script `json.py` will instantiate JSON meta-model defined in `json.tx`
file, export it to dot file for visualization purposes and than instantiate all
examples. Each, JSON example file is also exported to dot. To run it use:

    $ python json.py

Checking and visualization can also be done using `textx` command line tool and
GraphViz dot tool.

For example:

```
$ textx generate json.tx --target dot 
Generating dot target from models:
/home/igor/repos/textX/textX/examples/json/json.tx
-> /home/igor/repos/textX/textX/examples/json/json.dot
   To convert to png run "dot -Tpng -O json.dot"

$ textx generate example1.json --grammar json.tx --target dot
Generating dot target from models:
/home/igor/repos/textX/textX/examples/json/example1.json
-> /home/igor/repos/textX/textX/examples/json/example1.dot
   To convert to png run "dot -Tpng -O example1.dot"

$ dot -Tpng -O example1.dot
```

**Note:** This is just an example that textX can be used to parse arbitrary
textual format/language not just to build DSLs. It is always better to use
specialized parsers if available. For the purpose of JSON parsing in Python use
`json` module. It is optimized for that purpose and thus performance will be
much better.
