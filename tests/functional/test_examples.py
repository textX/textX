# -*- coding: utf-8 -*-
#######################################################################
# Name: test_examples
# Purpose: Test that examples run without errors.
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright:
#    (c) 2014-2015 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
import pytest  # noqa
import os
import sys
import glob
import imp


def test_examples():

    examples_pat = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                '../../examples/*/*.py')

    # Filter out __init__.py and files not eligible for test run
    examples = [f for f in
                sorted(glob.glob(examples_pat))
                if not any(f.endswith(a)
                           for a in ['__init__.py', 'render_all_grammars.py'])]
    for e in examples:
        print("Running example:", e)
        example_dir = os.path.dirname(e)
        sys.path.insert(0, example_dir)
        (module_name, _) = os.path.splitext(os.path.basename(e))
        (module_file, module_path, desc) = \
            imp.find_module(module_name, [example_dir])

        m = imp.load_module(module_name, module_file, module_path, desc)

        if hasattr(m, 'main'):
            m.main(debug=False)
