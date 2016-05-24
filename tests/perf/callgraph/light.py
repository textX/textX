from textx.metamodel import metamodel_from_file

mm = metamodel_from_file('rhapsody.tx')
model = mm.model_from_file('LightSwitch.rpy')
