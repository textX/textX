from textx import parser_from_file
from textx.export import metamodel_export, model_export

# Construct parser
parser = parser_from_file('hello.tx')

# Get model
hello_model = parser.get_model('example.hello')

# Export model to dot
model_export(hello_model, 'example.dot')

# Get meta-model
hello_metamodel = parser.get_metamodel()

# Export meta-model to dot
metamodel_export(hello_metamodel, 'example_meta.dot')



