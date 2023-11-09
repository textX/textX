from os.path import dirname, join

from textx import metamodel_from_file


def callgraph_memoization():
    mm = metamodel_from_file('rhapsody.tx', memoization=True)

    # Small file
    this_folder = dirname(__file__)
    mm.model_from_file(join(this_folder,
                            'test_inputs', 'LightSwitch.rpy'))


if __name__ == '__main__':
    callgraph_memoization()
