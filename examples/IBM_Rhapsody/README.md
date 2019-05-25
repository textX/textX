# IBM Rational Rhapsody example

See:
  - https://www.reddit.com/r/Python/comments/4k50gf/textx_13_a_libtool_for_building_dsls_and_parsers/
  - http://stackoverflow.com/questions/36524566/pyparsing-recursion-of-values-list-ibm-rhapsody

Example taken from https://github.com/mansam/exploring-rhapsody/blob/master/LightSwitch/LightSwitch.rpy


To check and visualize meta-model and test model:

    $ textx generate rhapsody.tx --target dot
    $ textx generate LightSwitch.rpy --grammar rhapsody.tx --target dot
    $ dot -Tpdf -O *dot

Load from code:

```python
from textx import metamodel_from_file

meta = metamodel_from_file('rhapsody.tx')
model = meta.model_from_file('LightSwitch.rpy')
```


`model` will be an instance of `RhapsodyModel` class described by the grammar.
Each object attribute will be of a proper class defined by the grammar.

```python
print(model.root.name)
for property in model.root.properties:
  print(property.name, property.values)
```

