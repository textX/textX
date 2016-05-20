# IBM Rapsody example

See:
  - https://www.reddit.com/r/Python/comments/4k50gf/textx_13_a_libtool_for_building_dsls_and_parsers/
  - http://stackoverflow.com/questions/36524566/pyparsing-recursion-of-values-list-ibm-rhapsody

Example taken from https://github.com/mansam/exploring-rhapsody/blob/master/LightSwitch/LightSwitch.rpy


To check and visualize meta-model and test model:

    $ textx visualize ibm_rapsody.tx test.ibmr

Load from code:

    from textx.metamodel import metamodel_from_file

    meta = metamodel_from_file('ibm_raposody.tx')
    model = meta.model_from_file('test.ibmr')


`model` will be an instance of `IBMRapsodyModel` class described by the grammar.

    print(model.root.name)
    for key in model.root.keys:
      print(key.name, key.values)

