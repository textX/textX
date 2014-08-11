from textx import parser_from_file
from arpeggio.export import PTDOTExporter

# Construct parser
parser = parser_from_file('hello.tx', debug=True)

# Get model
hello_model = parser.get_model('example.hello')

PTDOTExporter().exportFile(parser.parse_tree, 'example_parse_tree.dot')

print(hello_model)

