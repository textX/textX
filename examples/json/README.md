# JSON example

JSON grammar is given in `json.tx`.
It is a simplified version. Numbers and strings are parser by textX builtin
rules.

All examples are taken from [json.org example
page](http://json.org/example.html).

Visualization files are created using `textx` command line tool and GraphViz dot
tool.

For example:

```
$ textx visualize json.tx example1.json
$ dot -Tpng -O example1.json.dot
```
