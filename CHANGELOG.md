# textX changelog

* 2018-02-13 (branch/scoping)
  - added new function textx.get_model.children to search arbritrary children using a lambda predicate.
  - remapped textx.model.get_children_of_type to the new children function (changed the logic, such that
    the root node is also checked to be model object).
  - added new metamodel function to register scope providers. Scope providers are callables, which return
    the referenced object.
    - added optional attribute "_tx_model_repository", see metamodel.py documentation
    - added attribute "scope_provider" like "obj_processors" to organize scope providers
    - added an optional argument to model_from_str and model_from_file: "pre_ref_resolution_callback": this
      is required internally to prepare the loading of other model files.
  - changed reference resolution in model.py
    - moved default resolution to textx.scoping.py
    - select the scope provider based on rule and rule-attribute (see scoping.py documentation)
    - added a Postponed type to postpone the resolution
    - introduced a multi-pass resolution (implemented at the end of parse_tree_to_objgraph; introduced new
      helper argument, e.g., a new optional argument "is_this_the_main_model" and "pre_ref_resolution_callback"
      (see metamodel.py above) to support reference resolution in the presence of different model files.
  - added a new module textx.scoping, to provide some scope providers (e.g. a fully qualified name provider) - see scoping.py:
    - full qualified names for reference names (e.g. package.package.class)
    - global scope (model distributed over different files - loaded globally)
    - import scope (model distributed over different files - loaded when imported)
    - relative scopes (e.g. instance.method where method is defined for the class of the instance in a model of classes, methods and instances)
    - selecting the metamodel based on a file pattern when loading models
  - added tests (mostly scope related - some of them also test other stuff, like buildins)
* 2017-11-22 Release 1.6.1
  - Fixing build for PyPI.

* 2017-11-18 Release 1.6
  - Fix class masking for split grammar and rule overriden. Thanks aranega@GitHub!
  - Simplifying metaclass handling. Using Python type system.
  - Fixing base namespace construction.
  - Rework of textX metaclass. Added a proper __repr__ for both instances and classes.
  - Introduced _tx_fqn class attribute.
  - Introduced six library to handle Py2/Py3 metaclass usage.
  - Simplification. Changed recursive instance resolving for an iterative.
    Thanks aranega@GitHub.
  - Cleanup. Refactorings and code reorganization.
  - textX api functions and classes are now available directly from `textx` module.

* 2017-11-17 Release 1.5.2
  - Fixing bug with assignments in repetition. Commit e918868.
  - Fix in resolving of attributes. Commit 8d18073.
  - More robust obj. processor call.

* 2017-06-14 Release 1.5.1
  - Fixed issue #34 triggered with multiple assignments with the different types
    leading to errors in reference resolving.
  - Fixed inheritance of base types.
  - Some fixes in the docs (thanks borismarin@github).

* 2017-05-15 Release 1.5
  - For a more detailed feature highlights overview for this release
    please see [what's new section in the docs](http://www.igordejanovic.net/textX/whatsnew/release_1_5).
  - fixed issue #27 Operator precendence. Note: backward incompatibility! Be
    sure to read
    [what's new section in the docs](http://www.igordejanovic.net/textX/whatsnew/release_1_5) before upgrade.
  - Issue #30 - match filters.
    See [the docs](http://www.igordejanovic.net/textX/metamodel/#match-filters).
  - Added support for unordered groups. See [the docs](http://www.igordejanovic.net/textX/grammar/#repetitions).
  - Added `_tx_metamodel` attribute on the model object for easy access to the
    language metamodel. See [the docs](http://www.igordejanovic.net/textX/model/#special-model-objects-attributes).
  - Fixed issue #33. Much more robust support for multiple assignments to the
    same attribute.
  - Fixes in namespace support. Import now works even for grammar defined as
    Python strings.
  - Added special attribute `_tx_position_end` on model objects with the
    information where the object ends in the input stream.
  - Added various handy functions for querying a model. See [the docs on model
    API](http://www.igordejanovic.net/textX/model/#model-api).
  - New examples and additions to the docs. Added [comparison to Xtext](http://www.igordejanovic.net/textX/about/comparison) for
    users with previous Xtext exposure. Added references to [ppci tutorial by
    Windel Bouwman](https://ppci.readthedocs.io/en/latest/howto/toy.html).
  - textX now have an [Emacs mode](https://github.com/novakboskov/textx-mode)!

* 2016-05-31 Release 1.4
  - Significant performance improvements done in Arpeggio (see issue #22).
  - Fixed wrong rule type detection and infinite recursion in dot export for 
    recursive match rules (issues #23 and #25).
  - Added new performance tests to keep track of both speed and memory
    consumption.
  - Memoization is disabled by default. Added `memoization` parameter to
    meta-model instantiation.
  - New example - IBM Rational Rhapsody format.

* 2016-05-17 Release 1.3.1
  - Fixing several bugs in special cases regarding abstract rule with a single
    rule reference and match suppression.
  - Improvements in docs, tutorials and examples.

* 2016-05-05 Release 1.3
  - Added support for syntactic predicates (`!` and `&`). A.K.A. negative and
    positive lookahead. Tests. Docs.
  - Added support for match suppression (operator `-`). Tests. Docs.
  - Added Entity tutorial + video.
  - Added StateMachine example from Martin Fowler's DSL book.
  - Various improvements in documentation and examples.

* 2016-04-28 Release 1.2
  - Reworked rule types detection and handling. Simplified textX grammar.
  - Performance improvements.
  - Updated docs to reflect changes.
  - Additional examples. Fixing and tidying up.
  - Various improvements in the dot rendering. Added * prefix for abstract classes.
  - Extended tests. Added test for all examples.
  - Improvements in textx command.

* 2016-04-01 Release 1.1.1
  - Bugfix release. Added missing commands package.

* 2016-04-01 Release 1.1
  - Metamodel API tiding. Some undocumented internally used attrs/methods made
    private.
  - textx command is console entry point now.
  - Some fixes and improvements in the docs and examples.

* 2016-03-03 Release 1.0
  - Migrated docs to MkDocs.
  - Docs improvement.
  - Fixed escaping of backslashes in the dot exporter.
  - Added `textx` command/script for (meta)model checking/visualization.

* 2015-08-27 Release 0.4.2
  - Added debug parameter to model_from_str.
  - All prints converted to DebugPrinter.
  - Fixed issue when object processor is applied to the list of BASETYPE
    elements.
  - Fix in model export to dot to render proper base python type values inside
    lists.

* 2015-08-08 Release 0.4.1
  - Fixed bug with multiple rule params.
  - Fixed ws rule loaded from file.
  - Fixed loading of README in setup.py to use utf-8 encoding always.
  - Added more tests.

* 2015-05-08 Release 0.4
  - Reworked meta-class/objects initialization.
  - Added _tx_ prefix to textX class and object special attributes to prevent
    name clashing with the user attributes.
  - Entity example.
  - More tests.
  - Documentation finished (except the advanced tutorial).

* 2015-04-04 Release 0.3.1
  - Bugfix: Boolean type matching for BASETYPE defined attributes.
  - More tests.

* 2015-02-10 Release 0.3
  - Refactoring textX grammar. Support for ordered choice of sequences. Tests.
  - Introduced new parameters to meta-model construction:

    - ignore-case - for case sensitive/insensitive matching.
    - autokwd - for matching on word boundaries for keyword-like matches.
    - skipws - for enabling/disabling automatic whitespace skipping.
    - ws - for redefinition of white-spaces.
    - auto_init_attributes - for auto initializing of model attributes
                             based on their types.

  - Object processor callbacks.
  - Support for user meta-classes.
  - Rule modifiers (ws, skipws, noskipws)
  - Grammar import.
  - Meta-model redesigned.
  - Support for unicode grammars.
  - Python 2/3 compatibility.
  - Documentation. Work in progress.
  - Travis integration.

* Release 0.2

  - Tests.
  - Started documentation writing.
  - A keyword-like string matches will be matched with the respect of word boundaries.
  - Grammar redesigned.
  - Introduced repetition operator modifiers (eolterm, separator).
  - Support for multiple attribute assignment in the same rule.
  - Position is now stored on model objects.
  - Support for model processor callbacks.
  - Filename is now accessible on model if the model is created from file.
  - Various bugfixes.

* Release 0.1.2

  - Bugfix in conversion of basetypes to python.

* Release 0.1.1

  - Bugfix release. Using relative imports.

* Release 0.1

  - Initial release. Most planed stuff in place.
  - XText-like language fully functional. Rules, match rules, abstract rule,
    list matches, string matches, regex matches...
  - Metamodel and model construction.
  - Export to dot.
