# textX changelog

* Next Release 1.?.?
   - https://github.com/textX/textX/pull/168
     - Adding examples and documentation related to scope providers
       (related to model modification through scope providers).
   - https://github.com/textX/textX/pull/165
     - Added metamodel export feature for PlantUML.
   - https://github.com/textX/textX/pull/134
     - Fixing bug when using a sequence of matches and rule reference in
       an abstract rule choice alternative.
     - Explicitly disallowing referencing more than one rule in an abstract
       rule choice alternative.
   - https://github.com/textX/textX/pull/114
     - python like imports (named import rules, scope providers affected)
     - OS incompatibility fixes (path separator).
   - https://github.com/textX/textX/pull/98
     - Added STRICTFLOAT as buildin type to allow to distinguish ints from
       floats in NUMBERs. Fixed docu link.
   - https://github.com/textX/textX/pull/93
     - Changed attribute name for the metamodel object (from 
       "metamodel._parser" to "metamodel._parser_blueprint").
   - https://github.com/textX/textX/pull/120
     Unicode requirement for (meta)-model strings API parameters made strict.
     This should prevent common errors with Python 2.x
     See:
     https://github.com/textX/textX/issues/105
     https://github.com/textX/textX/pull/99
     https://github.com/textX/textX/issues/117


* 2018-10-06 Release 1.8.0

   - https://github.com/textX/textX/pull/71
     - Regular expression with group support
     - See [the
       docs](http://textx.github.io/textX/development/grammar/#matches)
       for usage.
   - https://github.com/textX/textX/pull/69
     - Added search path feature (issue #66) - search path support for model 
       files (importURI scope providers; see docs/scoping.md).
   - https://github.com/textX/textX/pull/77
     - New multi meta model support for references-only for better meta model
       modularity (referencing models without having access to the grammar, 
       see docs/multimetamodel.md).
   - https://github.com/textX/textX/pull/79
     - Fixing obj_processors calling.
   - https://github.com/textX/textX/pull/84
     - New contribution guide.
   - https://github.com/textX/textX/pull/81
     - Bugfix: lost encoding for multi meta-model.
   - https://github.com/textX/textX/pull/68
     - changed parser access in metamodel (private attribute "_parser")
   - mkdocs documentation now uses [mike](https://github.com/jimporter/mike) for
     multiversion support.

* 2018-07-02 Release 1.7.1

   - Fixed bug with obj. processor call.
     https://github.com/textX/textX/issues/72
   - Fixed bug with `pos_to_linecol` in the context of multi-file models.
     https://github.com/textX/textX/issues/67
   - More tests.
   - Thanks goto40@GitHub for the above fixes/tests.

* 2018-05-31 Release 1.7.0

  - A major feature of this release is multi-(meta-)model support with
    configurable resolving techniques. Thanks Pierre Bayerl (goto40@GitHub)!

    The docs sections are [here](http://textx.github.io/textX/scoping/)
    and [here](http://textx.github.io/textX/multimetamodel/).

    Details follow:
    - added new function textx.get_model.children to search arbritrary children
      using a lambda predicate.
    - remapped textx.model.get_children_of_type to the new children function
    (changed the logic, such that the root node is also checked to be model
    object).
    - added new metamodel function to register scope providers. Scope providers
    are callables, which return the referenced object.
    - added optional attribute "_tx_model_repository", see metamodel.py
      documentation
    - added attribute "scope_provider" like "obj_processors" to organize scope
      providers
    - added an optional argument to model_from_str and model_from_file:
      "pre_ref_resolution_callback": this is required internally to prepare the
      loading of other model files.
    - changed reference resolution in model.py
      - moved default resolution to textx.scoping.py
      - select the scope provider based on rule and rule-attribute (see
        scoping.py documentation)
      - added a Postponed type to postpone the resolution
      - introduced a multi-pass resolution (implemented at the end of
        parse_tree_to_objgraph; introduced new helper argument, e.g., a new
        optional argument "is_this_the_main_model" and
        "pre_ref_resolution_callback" (see metamodel.py above) to support
        reference resolution in the presence of different model files.
    - added a new module textx.scoping, to provide some scope providers (e.g. a
      fully qualified name provider) - see scoping.py:
      - full qualified names for reference names (e.g. package.package.class)
      - global scope (model distributed over different files - loaded globally)
      - import scope (model distributed over different files - loaded when
        imported)
      - relative scopes (e.g. instance.method where method is defined for the
        class of the instance in a model of classes, methods and instances)
      - selecting the metamodel based on a file pattern when loading models
    - added tests (mostly scope related - some of them also test other stuff,
      like buildins)
    - exceptions where adapted to include a file name (makes errors more
      visible)
    - The metamodel now allows to specify a global model repository. With this
      you can now share models across metamodels (before you could only do this
      within one metamodel or language).
    - The metamodel clones the parser when parsing a model file. The meta model
      holds one parser, which is clone for every model to be parsed.

      Backward incompatible change: The metamodel.parser is only a blueprint 
      and cannot be used to, e.g., determine model element positions in the
      file. Use your_model._tx_parser instead, e.g., 
      textx.get_model(obj)._tx_parser).

    - TextXModelParser now has a clone method.
      (TBC: is the clone ok: see responsibility of the method)
    - model.py: the resolution loop logic now mostly moved to a separate object
      ReferenceResolver, which holds the parser.
      - The reference resolver are build from all model files affected (loaded).
        This may involve multiple meta models.
      - Then all references are resolved in one loop.
      - Finally the helper objects (ReferenceResolver) are purged.
    - The MetaModelProvider has a clear-method now (useful for tests).
    - Added tests.

  - Backward incompatible change: match filters and object processors unified.
    Now there are only object processors but they are called for any type of
    rule and the returned value if exists is used instead of the original
    object. See [the
    docs](http://textx.github.io/textX/metamodel/#object-processors). In
    order to migrate your match filters just register them as object processors.
    
  - Backward incompatible change: all methods of `textx.model` module get a
    `get_` prefix. See [this commit](https://github.com/textX/textX/commit/90667f29604f2e67c593e5a66de11ea286cf5be0) and [the
    docs](http://textx.github.io/textX/1.7/model/#model-api)

  - Fixing FLOAT regex. Thanks Boris Marin (borismarin@GitHub)!
  - Fixing position info on obj cross ref. Thanks Daniel Elero (danixeee@GitHub)!


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
    please see [what's new section in the docs](http://textx.github.io/textX/whatsnew/release_1_5).
  - fixed issue #27 Operator precendence. Note: backward incompatibility! Be
    sure to read
    [what's new section in the docs](http://textx.github.io/textX/whatsnew/release_1_5) before upgrade.
  - Issue #30 - match filters.
    See [the docs](http://textx.github.io/textX/metamodel/#match-filters).
  - Added support for unordered groups. See [the docs](http://textx.github.io/textX/grammar/#repetitions).
  - Added `_tx_metamodel` attribute on the model object for easy access to the
    language metamodel. See [the docs](http://textx.github.io/textX/model/#special-model-objects-attributes).
  - Fixed issue #33. Much more robust support for multiple assignments to the
    same attribute.
  - Fixes in namespace support. Import now works even for grammar defined as
    Python strings.
  - Added special attribute `_tx_position_end` on model objects with the
    information where the object ends in the input stream.
  - Added various handy functions for querying a model. See [the docs on model
    API](http://textx.github.io/textX/model/#model-api).
  - New examples and additions to the docs. Added [comparison to Xtext](http://textx.github.io/textX/about/comparison) for
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
