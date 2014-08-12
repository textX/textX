from textx import parser_from_file
from textx.export import metamodel_export

# Construct parser
parser = parser_from_file('hello.tx')

# Get model
hello_model = parser.get_model('example.hello')
# Get metamodel
hello_metamodel = parser.get_metamodel()
# Export metamodel to dot
metamodel_export(hello_metamodel, 'example_meta.dot')



