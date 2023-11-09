#######################################################################
# Testing parsing speed. This is used for the purpose of testing
#   of performance gains/loses for various approaches.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2016 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

import time
from os.path import dirname, getsize, join

from textx.metamodel import metamodel_from_file


def timeit(file_name, message, **kwargs):
    print(message, 'File:', file_name)
    file_name = join(dirname(__file__), 'test_inputs', file_name)
    file_size = getsize(file_name)
    print(f'File size: {file_size/1000:.2f}', 'KB')

    mm = metamodel_from_file('rhapsody.tx', **kwargs)

    t_start = time.time()
    mm.model_from_file(file_name)
    t_end = time.time()

    print(f'Elapsed time: {t_end - t_start:.2f}', 'sec')
    print(f'Speed = {file_size/1000/(t_end - t_start):.2f}', 'KB/sec\n')


def main():


    # Small file
    file_name_small = 'LightSwitch.rpy'
    # Large file
    file_name_large = 'LightSwitchDouble.rpy'

    # No memoization
    print('\n*** No memoization\n')
    for i in range(3):
        timeit(file_name_small,
               f'{i + 1}. Small file, no memoization.')
        timeit(file_name_large,
               f'{i + 1}. Large file, no memoization.')

    print('\n*** Memoization\n')
    for i in range(3):
        timeit(file_name_small,
               f'{i + 1}. Small file, with memoization.',
               memoization=True)
        timeit(file_name_large,
               f'{i + 1}. Large file, with memoization.',
               memoization=True)

if __name__ == '__main__':
    main()
