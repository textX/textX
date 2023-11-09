from os.path import dirname, join

from textx import metamodel_from_file
from textx.export import metamodel_export, model_export


def main(debug=False):

    this_folder = dirname(__file__)

    pyflies_mm = metamodel_from_file(join(this_folder, 'pyflies.tx'),
                                     debug=debug)
    metamodel_export(pyflies_mm, join(this_folder, 'pyflies_meta.dot'))

    experiment = pyflies_mm.model_from_file(join(this_folder, 'experiment.pf'))
    model_export(experiment, join(this_folder, 'experiment.dot'))


if __name__ == '__main__':
    main()
