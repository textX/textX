from os.path import dirname, join

from textx import metamodel_from_file
from textx.export import metamodel_export, model_export


def main(debug=False):

    this_folder = dirname(__file__)

    json_mm = metamodel_from_file(join(this_folder, 'json.tx'), debug=debug)
    metamodel_export(json_mm, join(this_folder, 'json.tx.dot'))

    model1 = json_mm.model_from_file(join(this_folder, 'example1.json'))
    model_export(model1, join(this_folder, 'example1.json.dot'))

    model2 = json_mm.model_from_file(join(this_folder, 'example2.json'))
    model_export(model2, join(this_folder, 'example2.json.dot'))

    model3 = json_mm.model_from_file(join(this_folder, 'example3.json'))
    model_export(model3, join(this_folder, 'example3.json.dot'))

    model4 = json_mm.model_from_file(join(this_folder, 'example4.json'))
    model_export(model4, join(this_folder, 'example4.json.dot'))

    model5 = json_mm.model_from_file(join(this_folder, 'example5.json'))
    model_export(model5, join(this_folder, 'example5.json.dot'))


if __name__ == '__main__':
    main()
