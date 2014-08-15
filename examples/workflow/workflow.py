from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export, model_export

# Create metamodel from textX description
workflow_mm = metamodel_from_file('workflow.tx')
# Export to dot
# Create png image with: dot -Tpng -O workflow_meta.dot
metamodel_export(workflow_mm, 'workflow_meta.dot')

# Load example model
example = workflow_mm.model_from_file('example.wf')
# Export to dot
# Create png image with: dot -Tpng -O example.dot
model_export(example, 'example.dot')

