from os.path import dirname, join

from textx import metamodel_from_file
from textx.export import metamodel_export, model_export


def main(debug=False):

    this_folder = dirname(__file__)

    # Create metamodel from textX description
    workflow_mm = metamodel_from_file(
        join(this_folder, 'workflow.tx'), debug=debug)

    # Export to dot
    # Create png image with: dot -Tpng -O workflow_meta.dot
    metamodel_export(workflow_mm, join(this_folder, 'workflow_meta.dot'))

    # Load example model
    example = workflow_mm.model_from_file(join(this_folder, 'example.wf'))

    # Export to dot
    # Create png image with: dot -Tpng -O example.dot
    model_export(example, join(this_folder, 'example.dot'))


if __name__ == '__main__':
    main()
