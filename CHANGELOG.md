# textX changelog

All _notable_ changes to this project will be documented in this file.

The format is based on _[Keep a Changelog][keepachangelog]_, and this project
adheres to _[Semantic Versioning][semver]_.

Everything that is documented in the [official docs][textXDocs] is considered
the part of the public API.

Backward incompatible changes are marked with **(BIC)**. These changes are the
reason for the major version increase so when upgrading between major versions
please take a look at related PRs and issues and see if the change affects you.

## [Unreleased]

### Added

  - Adding examples and documentation related to scope providers (related to
    model modification through scope providers) ([#168])
  - metamodel export feature for [PlantUML] ([#165])
  - `textx_isinstance` from `textx.scoping.tools` made available in `textx`
    ([#164], [#157])
  - CLI extensibility ([#162], [#161])
  - An initial version of FAQ page ([#138]). Thanks Aluriak@GitHub
  - A version of `calc.py` exercises usage of
    `text.scoping.tools.textx_isinstance()` to inspect model objects types
    during traversal. ([#136], [#123]). Thanks dkrikun@GitHub
  - A version of `calc.py` in expression example that exercises dynamically adding
    properties to object classes ([#126]). Thanks dkrikun@GitHub
  - python like imports (named import rules, scope providers affected) ([#114])
  - Added `STRICTFLOAT` as buildin type to allow to distinguish ints from floats
    in `NUMBER`. Fixed docu link ([#98]). Possible **(BIC)**
  - Added [flake8] and [coverage] checking ([#92])

### Changed

  - Made scope provider implementation of `RelativeName` and `ExtRelativeName`
    more readable ([#186]). Minor functional changes, not very probable to have
    any impact (only affects model-paths containing a list not at the end of the
    path; see [#186]). Possible **(BIC)**.
  - Improved handling of abstract rules references. Improved the definition of
    rules for various cases. Docs + tests ([#185], [#166]) **(BIC)**
  - Changed the time of call of match rule object processors to be during the
    model construction. This enable proper override of base types processors and
    calls on nested match rules ([#183], [#182], [#96]). Possible **(BIC)**
  - CLI migrated to the [click] library ([#162])
  - Docs improvements ([#146], [#153], [#151]). Thanks simkimsia@GitHub.
  - `FQN` constuctor param `follow_loaded_models` removed and introduced
    callback `scope_rediction_logic` to implement arbitrary logic on FQN
    resolution ([#133], [#114], [#103]) **(BIC)**
  - Changed attribute name for the meta-model object (from `metamodel._parser`
    to `metamodel._parser_blueprint`). ([#93]) **(BIC)**
  - Started using _[Keep a Changelog][keepachangelog]_ ([#174])
  - Started using _[Semantic Versioning][semver]_ ([#174])
     
### Fixed

  - Calling of match rule object processors ([#183], [#182], [#96])
  - Circular rule references in grammars ([#173], [#159], [#155])
  - Assertion error while calling object processors with multi meta models
    (extended grammars) and custom types ([#141], [#140])
  - Using a sequence of matches and rule reference in an abstract rule choice
    alternative, and explicitly disallowing referencing more than one rule in an
    abstract rule choice alternative ([#134])
  - Unicode requirement for (meta)-model strings API parameters made strict.
    This should prevent common errors with Python 2.x. ([#120]) (related: [#99],
    [#105], [#117]). Possible **(BIC)**
  - OS incompatibility fixes (path separator). ([#114])
  - Object processors called twice for imported models ([#108], [#118])
  - Documentation and examples regarding `NUMBER` base type ([#97], [#100]).
    Thanks approxit@GitHub


## [v1.8.0] (released: 2018-10-06)

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
   - mkdocs documentation now uses [mike] for multiversion support.

## [v1.7.1] (released: 2018-07-02)

   - Fixed bug with obj. processor call.
     https://github.com/textX/textX/issues/72
   - Fixed bug with `pos_to_linecol` in the context of multi-file models.
     https://github.com/textX/textX/issues/67
   - More tests.
   - Thanks goto40@GitHub for the above fixes/tests.

## [v1.7.0] (released: 2018-05-31)

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


## [v1.6.1] (released: 2017-11-22)
  - Fixing build for PyPI.

## [v1.6] (released: 2017-11-18)

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

## [v1.5.2] (released:2017-11-17)

  - Fixing bug with assignments in repetition. Commit e918868.
  - Fix in resolving of attributes. Commit 8d18073.
  - More robust obj. processor call.

## [v1.5.1] (released: 2017-06-14)

  - Fixed issue #34 triggered with multiple assignments with the different types
    leading to errors in reference resolving.
  - Fixed inheritance of base types.
  - Some fixes in the docs (thanks borismarin@github).

## [v1.5] (released: 2017-05-15)

  - For a more detailed feature highlights overview for this release please see
    [what's new section in the
    docs](http://textx.github.io/textX/whatsnew/release_1_5).
  - fixed issue #27 Operator precedence. Note: backward incompatibility! Be
    sure to read [what's new section in the
    docs](http://textx.github.io/textX/whatsnew/release_1_5) before upgrade.
  - Issue #30 - match filters. See [the
    docs](http://textx.github.io/textX/metamodel/#match-filters).
  - Added support for unordered groups. See [the
    docs](http://textx.github.io/textX/grammar/#repetitions).
  - Added `_tx_metamodel` attribute on the model object for easy access to the
    language metamodel. See [the
    docs](http://textx.github.io/textX/model/#special-model-objects-attributes).
  - Fixed issue #33. Much more robust support for multiple assignments to the
    same attribute.
  - Fixes in namespace support. Import now works even for grammar defined as
    Python strings.
  - Added special attribute `_tx_position_end` on model objects with the
    information where the object ends in the input stream.
  - Added various handy functions for querying a model. See [the docs on model
    API](http://textx.github.io/textX/model/#model-api).
  - New examples and additions to the docs. Added [comparison to
    Xtext](http://textx.github.io/textX/about/comparison) for users with
    previous Xtext exposure. Added references to [ppci tutorial by Windel
    Bouwman](https://ppci.readthedocs.io/en/latest/howto/toy.html).
  - textX now have an [Emacs mode](https://github.com/novakboskov/textx-mode)!

## [v1.4] (released: 2016-05-31)

  - Significant performance improvements done in Arpeggio (see issue #22).
  - Fixed wrong rule type detection and infinite recursion in dot export for
    recursive match rules (issues #23 and #25).
  - Added new performance tests to keep track of both speed and memory
    consumption.
  - Memoization is disabled by default. Added `memoization` parameter to
    meta-model instantiation.
  - New example - IBM Rational Rhapsody format.

## [v1.3.1] (released: 2016-05-17)

  - Fixing several bugs in special cases regarding abstract rule with a single
    rule reference and match suppression.
  - Improvements in docs, tutorials and examples.

## [v1.3] (released: 2016-05-05)

  - Added support for syntactic predicates (`!` and `&`). A.K.A. negative and
    positive lookahead. Tests. Docs.
  - Added support for match suppression (operator `-`). Tests. Docs.
  - Added Entity tutorial + video.
  - Added StateMachine example from Martin Fowler's DSL book.
  - Various improvements in documentation and examples.

## [v1.2] (released: 2016-04-28)

  - Reworked rule types detection and handling. Simplified textX grammar.
  - Performance improvements.
  - Updated docs to reflect changes.
  - Additional examples. Fixing and tidying up.
  - Various improvements in the dot rendering. Added `*` prefix for abstract
    classes.
  - Extended tests. Added test for all examples.
  - Improvements in textx command.

## [v1.1.1] (released: 2016-04-01)

  - Added missing `commands` package.

## [v1.1] (released: 2016-04-01)

  - Metamodel API tiding. Some undocumented internally used attrs/methods made
    private.
  - textx command is console entry point now.
  - Some fixes and improvements in the docs and examples.

## [v1.0] (released: 2016-03-03)

  - Migrated docs to [MkDocs][MkDocs].
  - Docs improvement.
  - Fixed escaping of backslashes in the dot exporter.
  - Added `textx` command/script for (meta)model checking/visualization.

## [v0.4.2] (released: 2015-08-27)

  - Added debug parameter to `model_from_str`.
  - All prints converted to `DebugPrinter`.
  - Fixed issue when object processor is applied to the list of `BASETYPE`
    elements.
  - Fix in model export to `dot` to render proper base python type values inside
    lists.

## [v0.4.1] (released: 2015-08-08)

  - Fixed bug with multiple rule params.
  - Fixed ws rule loaded from file.
  - Fixed loading of README in setup.py to use utf-8 encoding always.
  - Added more tests.

## [v0.4] (released: 2015-05-08)

  - Reworked meta-class/objects initialization.
  - Added `_tx_` prefix to textX class and object special attributes to prevent
    name clashing with the user attributes.
  - Entity example.
  - More tests.
  - Documentation finished (except the advanced tutorial).

## [v0.3.1] (released: 2015-04-04)

  - Boolean type matching for `BASETYPE` defined attributes.
  - More tests.

## [v0.3] (released: 2015-02-10)

  - Refactoring textX grammar. Support for ordered choice of sequences. Tests.
  - Introduced new parameters to meta-model construction:

    - `ignore-case` - for case sensitive/insensitive matching.
    - `autokwd` - for matching on word boundaries for keyword-like matches.
    - `skipws` - for enabling/disabling automatic whitespace skipping.
    - `ws` - for redefinition of white-spaces.
    - `auto_init_attributes` - for auto initializing of model attributes based
      on their types.

  - Object processor callbacks.
  - Support for user meta-classes.
  - Rule modifiers (`ws`, `skipws`, `noskipws`)
  - Grammar import.
  - Meta-model redesigned.
  - Support for unicode grammars.
  - Python 2/3 compatibility.
  - Documentation. Work in progress.
  - Travis integration.

## [v0.2] (released: 2014-09-20)

  - Tests.
  - Started documentation writing.
  - A keyword-like string matches will be matched with the respect of word
    boundaries.
  - Grammar redesigned.
  - Introduced repetition operator modifiers (`eolterm`, `separator`).
  - Support for multiple attribute assignment in the same rule.
  - Position is now stored on model objects.
  - Support for model processor callbacks.
  - Filename is now accessible on model if the model is created from file.
  - Various bugfixes.

## [v0.1.2] (released: 2014-08-17)

  - Bugfix in conversion of basetypes to python.

## [v0.1.1] (released: 2014-08-17)

  - Using relative imports.

## [v0.1] (released: 2014-08-17)

  - Initial release. Most planed stuff in place.
  - XText-like language fully functional. Rules, match rules, abstract rule,
    list matches, string matches, regex matches...
  - Metamodel and model construction.
  - Export to dot.


[#185]: https://github.com/textX/textX/pull/185
[#183]: https://github.com/textX/textX/pull/183
[#182]: https://github.com/textX/textX/issues/182
[#174]: https://github.com/textX/textX/pull/174
[#173]: https://github.com/textX/textX/pull/173
[#168]: https://github.com/textX/textX/pull/168
[#166]: https://github.com/textX/textX/issues/166
[#165]: https://github.com/textX/textX/pull/165
[#164]: https://github.com/textX/textX/pull/164
[#162]: https://github.com/textX/textX/pull/162
[#161]: https://github.com/textX/textX/issues/161
[#159]: https://github.com/textX/textX/pull/159
[#157]: https://github.com/textX/textX/issues/157
[#155]: https://github.com/textX/textX/issues/155
[#153]: https://github.com/textX/textX/pull/153
[#151]: https://github.com/textX/textX/pull/151
[#146]: https://github.com/textX/textX/pull/146
[#141]: https://github.com/textX/textX/pull/141
[#140]: https://github.com/textX/textX/issues/140
[#138]: https://github.com/textX/textX/pull/138
[#136]: https://github.com/textX/textX/pull/136
[#134]: https://github.com/textX/textX/pull/134
[#133]: https://github.com/textX/textX/pull/133
[#126]: https://github.com/textX/textX/pull/126
[#123]: https://github.com/textX/textX/issues/123
[#120]: https://github.com/textX/textX/pull/120
[#118]: https://github.com/textX/textX/pull/118
[#117]: https://github.com/textX/textX/pull/117
[#114]: https://github.com/textX/textX/pull/114
[#108]: https://github.com/textX/textX/issues/108
[#105]: https://github.com/textX/textX/issues/105
[#103]: https://github.com/textX/textX/issues/103
[#100]: https://github.com/textX/textX/pull/100
[#99]: https://github.com/textX/textX/pull/99
[#98]: https://github.com/textX/textX/pull/98
[#97]: https://github.com/textX/textX/issues/97
[#96]: https://github.com/textX/textX/issues/96
[#93]: https://github.com/textX/textX/pull/93
[#92]: https://github.com/textX/textX/pull/92

[Unreleased]: https://github.com/textX/textX/compare/v1.8.0...HEAD
[v1.8.0]: https://github.com/textX/textX/compare/v1.7.1...v1.8.0
[v1.7.1]: https://github.com/textX/textX/compare/v1.7.0...v1.7.1
[v1.7.0]: https://github.com/textX/textX/compare/v1.6.1...v1.7.0
[v1.6.1]: https://github.com/textX/textX/compare/v1.6...v1.6.1
[v1.6]: https://github.com/textX/textX/compare/v1.5.2...v1.6
[v1.5.2]: https://github.com/textX/textX/compare/v1.5.1...v1.5.2
[v1.5.1]: https://github.com/textX/textX/compare/v1.5...v1.5.1
[v1.5]: https://github.com/textX/textX/compare/v1.4...v1.5
[v1.4]: https://github.com/textX/textX/compare/v1.3.1...v1.4
[v1.3.1]: https://github.com/textX/textX/compare/v1.3...v1.3.1
[v1.3]: https://github.com/textX/textX/compare/v1.2...v1.3
[v1.2]: https://github.com/textX/textX/compare/v1.1.1...v1.2
[v1.1.1]: https://github.com/textX/textX/compare/v1.1...v1.1.1
[v1.1]: https://github.com/textX/textX/compare/v1.0...v1.1
[v1.0]: https://github.com/textX/textX/compare/v0.4.2...v1.0
[v0.4.2]: https://github.com/textX/textX/compare/v0.4.1...v0.4.2
[v0.4.1]: https://github.com/textX/textX/compare/v0.4...v0.4.1
[v0.4]: https://github.com/textX/textX/compare/v0.3.1...v0.4
[v0.3.1]: https://github.com/textX/textX/compare/v0.3...v0.3.1
[v0.3]: https://github.com/textX/textX/compare/v0.2.1...v0.3
[v0.2.1]: https://github.com/textX/textX/compare/v0.2...v0.2.1
[v0.2]: https://github.com/textX/textX/compare/v0.1.2...v0.2
[v0.1.2]: https://github.com/textX/textX/compare/v0.1.1...v0.1.2
[v0.1.1]: https://github.com/textX/textX/compare/v0.1...v0.1.1
[v0.1]: https://github.com/textX/textX/compare/0f33ecb0016a8f527...v0.1


[click]: https://github.com/pallets/click
[coverage]: https://coverage.readthedocs.io/
[flake8]: http://flake8.pycqa.org/en/latest/
[keepachangelog]: https://keepachangelog.com/
[mike]: https://github.com/jimporter/mike
[MkDocs]: https://www.mkdocs.org/
[PlantUML]: http://plantuml.com/
[semver]: https://semver.org/spec/v2.0.0.html
[textXDocs]: http://textx.github.io/textX/latest/
