from os.path import dirname, join

from memory_profiler import profile

from textx import metamodel_from_file


@profile
def memoization():
    mm = metamodel_from_file('rhapsody.tx', memoization=True)

    # Small file
    this_folder = dirname(__file__)
    mm.model_from_file(join(this_folder,
                            'test_inputs', 'LightSwitch.rpy'))

    # Large file
    mm.model_from_file(join(this_folder,
                            'test_inputs', 'LightSwitchDouble.rpy'))


if __name__ == '__main__':
    memoization()
