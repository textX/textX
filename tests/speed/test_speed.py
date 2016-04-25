# -*- coding: utf-8 -*-
#######################################################################
# Name: test_speed
# Purpose: Basic performance test of textX to check for
#   performance differences of various approaches.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2016 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

from __future__ import unicode_literals
import timeit

if __name__ == "__main__":

# Setup code works for python 3 only. Haven't figured out yet how to
# from __future__ import unicode_literals  in the setup code
    setup = '''
import codecs
from textx.metamodel import metamodel_from_file

mm = metamodel_from_file('pyflies.tx')
# Preload file to eliminate I/O
with codecs.open("simon.pf", encoding="utf-8") as f:
    input = f.read()
    '''

    print(timeit.timeit("mm.model_from_str(input)", setup=setup, number=200))
    # 1.53 s
