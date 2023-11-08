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
import importlib


def test_examples():
    examples_pat = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "../../examples/*/*.py"
    )

    # Filter out __init__.py and files not eligible for test run
    examples = [
        f
        for f in sorted(glob.glob(examples_pat))
        if not any(f.endswith(a) for a in ["__init__.py", "render_all_grammars.py"])
    ]

    example_modules = []
    for e in examples:
        print("Running example:", e)
        example_dir = os.path.dirname(e)
        sys.path.insert(0, example_dir)

        (module_name, _) = os.path.splitext(os.path.basename(e))
        mod = importlib.import_module(module_name)

        if hasattr(mod, "main"):
            mod.main(debug=False)
            example_modules.append(mod)

    print("Tested examples:")
    for e in example_modules:
        print(e.__file__)
    assert len(example_modules) == 12
