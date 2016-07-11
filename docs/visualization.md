# Visualization

A meta-model, model and parse-tree can be exported to dot files
([GraphViz](http://www.graphviz.org/)) for visualization. Module `textx.export`
contains functions `metamodel_export` and `model_export` that can export
meta-model and model to dot files respectively.

If [debugging](debugging.md) is enabled, meta-model, model and parse trees will
automatically get exported to dot.


## Meta-model visualization

To visualize a meta-model (see [Entity
example](https://github.com/igordejanovic/textX/tree/master/examples/Entity))
do:

```python
from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export

entity_mm = metamodel_from_file('entity.tx')

metamodel_export(entity_mm, 'entity.dot')
```

`entity.dot` file will be created. You can visualize this file by using
various dot viewers or convert it to various image formats using the 'dot'
tool.

    $ dot -Tpng -O entity.dot

The following image is generated:

![Entity meta-model](https://raw.githubusercontent.com/igordejanovic/textX/master/examples/Entity/dotexport/entity_meta.dot.png)


## Model visualization

Similarly to meta-model visualization, you can also visualize your models (see [Entity
example](https://github.com/igordejanovic/textX/tree/master/examples/Entity)).

```python
from textx.export import model_export

person_model = entity_mm.model_from_file('person.ent')

model_export(person_model, 'person.dot')
```


Convert this `dot` file to `png` with:

    $ dot -Tpng -O person.dot

The following image is generated:

![Person model](https://raw.githubusercontent.com/igordejanovic/textX/master/examples/Entity/dotexport/entity.dot.png)



!!! note
    Also, see [textx command/tool](textx_command.md) for model visualization
    from the command line.
