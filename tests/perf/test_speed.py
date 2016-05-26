#-*- coding: utf-8 -*-
#######################################################################
# Testing parsing speed. This is used for the purpose of testing
#   of performance gains/loses for various approaches.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2016 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from __future__ import print_function, unicode_literals

import time
from os.path import dirname, join, getsize
from textx.metamodel import metamodel_from_file

def timeit(file_name, message, **kwargs):
    print(message, 'File:', file_name)
    file_name = join(dirname(__file__), 'test_inputs', file_name)
    file_size = getsize(file_name)
    print('File size: {:.2f}'.format(file_size/1000), 'KB')

    mm = metamodel_from_file('rhapsody.tx', **kwargs)

    t_start = time.time()
    mm.model_from_file(file_name)
    t_end = time.time()

    print('Elapsed time: {:.2f}'.format(t_end - t_start), 'sec')
    print('Speed = {:.2f}'.format(file_size/1000/(t_end - t_start)), 'KB/sec\n')


def main():


    # Small file
    file_name_small = 'LightSwitch.rpy'
    # Large file
    file_name_large = 'LightSwitchDouble.rpy'

    # No memoization
    print('\n*** No memoization\n')
    for i in range(3):
        timeit(file_name_small,
               '{}. Small file, no memoization.'.format(i + 1))
        timeit(file_name_large,
               '{}. Large file, no memoization.'.format(i + 1))

    print('\n*** Memoization\n')
    for i in range(3):
        timeit(file_name_small,
               '{}. Small file, with memoization.'.format(i + 1),
               memoization=True)
        timeit(file_name_large,
               '{}. Large file, with memoization.'.format(i + 1),
               memoization=True)

if __name__ == '__main__':
    main()
