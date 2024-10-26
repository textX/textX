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


## [4.1.0] (released: 2024-10-26)

### Added
- `nchar` attribute to `TextXError` class, which represents the substring length
  for the model object where the error was found. Also, this value is now
  returned by `get_location()`, so no changes are required in user code. See
  [420]. Thanks @davidchall.
- `linetype` parameter to PlantUML generator which controls line style. See the
  tip in [the visualization
  docs](https://textx.github.io/textX/visualization.html).

### Fixed
- Rendering of multiplicities of association in PlantUML generator.

### Changed
- Meta-model diagram export now raises attributes/references to abstract
  meta-classes along the inheritance chain. See [423].
- Documentation migrated to [mdbook](https://rust-lang.github.io/mdBook/) and
  GitHub Actions.
- The Python version limit "<3.13" has been removed from the pyproject.toml
  file. The library should run on all Python versions starting from 3.8. See
  [428].

[423]: https://github.com/textX/textX/issues/423
[420]: https://github.com/textX/textX/issues/420
[428]: https://github.com/textX/textX/issues/428


## [4.0.1] (released: 2023-11-12)

### Fixed

- Use flit-core for test projects. See [418]. Thanks @mgorny for reporting.

[418]: https://github.com/textX/textX/issues/418


## [4.0.0] (released: 2023-11-10)

### Fixed

- Removed word boundary from INT rule regex. Thanks @NevenaAl for reporting the
  issue and providing the test ([401]).
  
### Changed
- **(BIC)** Removed Python support for 3.6 and 3.7. The minimal supported
  version is 3.8.
- Migrated to pyproject.toml for project configuration. See ([416]).
- Migrated to importlib for language/generator registration/discovery as
  setuptools pkg_resources is deprecated and unsupported from Python 3.12. See
  [411]. Thanks @EmilyBourne and @nchammas for reporting. See ([416]).
- **(BIC)** Added dependency to `importlib-metadata` backward compatibility
  package for Python versions < 3.10. If Python is >=3.10 this library is not
  used. See ([416]).
- Use [ruff] instead of flake8 for linting. ruff can also be used for code
  formating. See ([416]).
- Relaxed dependency for click to accept 8.x. See [414]. Thanks @RootMeanSqr for
  reporting the issue. See ([416]).
- Use [flit] for package building and publishing.

[401]: https://github.com/textX/textX/pull/401
[416]: https://github.com/textX/textX/pull/416
[411]: https://github.com/textX/textX/issues/411
[414]: https://github.com/textX/textX/issues/414
[ruff]: https://github.com/astral-sh/ruff
[flit]: https://flit.pypa.io/


## [3.1.1] (released: 2023-02-10)

### Fixed

- Source distribution packaging issue ([392]). Thanks yurivict@GitHub.

[#392]: https://github.com/textX/textX/issues/392


## [3.1.0] (released: 2023-02-08)

### Fixed

- Fixed RREL lookup in case of multi-meta models (some special cases were not
  handled correctly; [#379]).
- Fixed test suite invocation to use `pytest` over `py.test` that stopped
  working in pytest-7.2.0. ([#389]). Thanks mgorny@GitHub.

### Changed

- Changed separator in obj. rule refs from `|` to `:`. Old separator
  will still be allowed until version 4.0. ([#385], [#384])
- Removed the dependency on `future` package ([#388]). Thanks mgorny@GitHub.
- Removed vendored `six` library. We don't need 2.x support anymore. Thanks
  davidchall@GitHub for reporting the issue ([#390]).

[#390]: https://github.com/textX/textX/issues/390
[#389]: https://github.com/textX/textX/pull/389
[#388]: https://github.com/textX/textX/pull/388
[#385]: https://github.com/textX/textX/pull/385
[#384]: https://github.com/textX/textX/issues/384
[#379]: https://github.com/textX/textX/pull/379


## [3.0.0] (released: 2022-03-20)

### Added

- Added RREL-'fixed name'-extension, allowing to follow model elements
  given a fixed name (e.g. an object defined in a builtin model).
  Details described in rrel.md ([#364]).
- Added ability to access the full path of named objects traversed while
  resolving a RREL expression ([#304]).
- Added decorator `textx.textxerror_wrap` for object processors to automatically
  transform non-TextXErrors to TextXErrors in order to indicate the filename and
  position of the element being processed ([#306]).

### Fixed

- `model_param_defs` on `TextXMetaMetaModel` ([#360]).
- Interpreting of backslash special chars (e.g. `\n`, `\t`) in grammar string
  matches ([#323]). Possible **(BIC)** - backslash chars were not interpreted in
  grammar files and raw Python strings prior to this fix.
- Exception/error messages ([#320])
- Relaxed assert in model creation enabling some model changes in user classes
  ([#311])
- Model export to dot in cases where textX object is replaced in the
  processor([#301])
- Do not allow "empty" RREL expressions (compare unittests in `test_rrel.py`; [#355])

### Changed

- Inheritance chain calculation. Possible **(BIC)** ([#369]).
- Added `def_file_name` attribute to `RefRulePosition` for storing the definition's
  model file name in case of cross-references between models. ([#313],[#277])
- Migrated from Travis CI to GitHub Actions ([#307])
- Dropped support for deprecated Python versions. The lowest supported version
  is 3.6. **(BIC)**

[#369]: https://github.com/textX/textX/pull/369
[#360]: https://github.com/textX/textX/issues/360
[#323]: https://github.com/textX/textX/issues/323
[#320]: https://github.com/textX/textX/pull/320
[#313]: https://github.com/textX/textX/pull/313
[#311]: https://github.com/textX/textX/pull/311
[#307]: https://github.com/textX/textX/issues/307
[#306]: https://github.com/textX/textX/pull/306
[#304]: https://github.com/textX/textX/pull/304
[#301]: https://github.com/textX/textX/issues/301
[#277]: https://github.com/textX/textX/issues/277


## [2.3.0] (released: 2020-11-01)

### Added
  - `textx generate`. Documented passing in arbitrary parameters which can be
    used in the generator function. Also, implemented passing of model
    parameters defined in the meta-model (`model_param_defs` and
    `_tx_model_params`) ([#299])
  - `get_location` function for producing `line/col/filename` from any textX
    object. ([#294])
  - `builtin_models` of type `ModelRepository` to meta-model constructor. Used
    to supply pre-loaded models for `ImportURI` based scoping providers as a
    fallback to search into. ([#284])
  - Initial implementation of TEP-001 ([#111]) allowing to specify scope
    provider behavior within the grammar itself. [#274] and [#287] introduce
    the RREL (reference resolving expression language) to define how
    references are resolved. Details see `rrel.md`.
  - Parameter `should_follow` of callable type to `get_children` and
    `get_children_of_type` model API calls to decide if the element should be
    traversed. ([#281])

### Fixed

  - Fixed bug with Falsy user classes in `get_children` ([#288])
  - Fixed bug with unhashable objects during dot export ([#283])
  - Fixed bug where (Ext)RelativeName scope providers accepted any referenced
    object that contained the lookup name in its name. Thanks ipa-mdl@GitHub
    ([#267])
  - Fixed bug in `flow_dsl` test project causing static files not being included
    in package build/installation. Thanks sebix@GitHub ([#272]).
  - Fixed bug, where user classes not used in the grammar caused exceptions
    ([#270]): now, when passing a list of user classes, you need to use them in
    your grammar. You can alternatively also pass a callable (see metamodel.md;
    [#273]). Also, using base classes for rules from imported grammars in
    conjunction with user classes is not allowed and results in an exception.
  - Fixed bug in `export.py` concerning html escaping in the dot export of a
    textx meta-model ([#276]).

### Changed

  - `_tx_model_param_definitions` deprecated in favor of `model_param_defs` ([#298]).
  - `click` is now an optional dependency, only when CLI is needed ([#292])
  - Make warning about not overwriting generated file more visible
    ([01341ec3](https://github.com/textX/textX/commit/01341ec381bfb4c8c27bcec5d2998a34d207f430))
  - Truncate long strings during dot export for better diagram readability ([#282]).
  - Changed `unhashable type` exception when a list is used for `name` attributes by
    raising a more informative exception and extending docs to document the issue
    and a proper way to solve it ([#40], [#266]).


## [v2.2.0] (released: 2020-08-03)

### Added

  - Initial docs for Jinja code generator support (from
    [textX-jinja](https://github.com/textX/textX-jinja)) ([#264]).
  - Analyzing grammars programmatically as plain textX models
    (`grammar_model_from_str/file`) ([#235])
  - Initial `startproject` scaffolding (from
    [textX-dev](https://github.com/textX/textX-dev)) docs ([#234])
  - Generator helper functions `get_output_filename` and `gen_file` ([#233])
  - `textx version` command ([#219])
  - Versions for languages/packages in `list-languages` and `list-generators`
    commands ([#228])
  - Added the ability to specify extra parameters during `model_from_file` or
    `model_from_str` and to define which extra parameters exist in the
    meta-model ([#243]).

### Fixed

  - Fixed several instances of invalid truthiness checking. Thanks
    markusschmaus@GitHub ([#250])
  - Fixed applying multiple grammar rule modifiers ([#246])
  - Fixed exception on calling `check` CLI command with relative path name.
  - Fixed return value of textx generate and check commands: we return a failure
    on error now ([#222])
  - Fixed type checking for references to builtin elements ([#218])

### Changed

  - User classes can now be immutable (e.g. `attr.frozen`) or can use
    `__slots__`. Thanks markusschmaus@GitHub ([#256, #260, #261])
  - Cleanup of setup configuration and install scripts [#231]
  - Dot/PlantUML rendering of meta-models: remove rendering of base types,
    improve rendering of required/optional, render match rules as a single
    table. ([#225])
  - Allow passing kwargs in `metamodel_for_file/language` registration API
    calls. ([#224])


## [v2.1.0] (released: 2019-10-12)

### Added

  - Added new function `textx.scoping.is_file_included` ([#197]).

### Changed

  - Allow passing kwargs (specially - file_name) argument when loading metamodel
    from string (needed for `textX-LS v0.1.0`) ([#211]).
  - Changed the parser rule for regex matches. Spaces are not stripped any more
    from the beginning and the end of the regexp-pattern. This could be possible
    **BIC** for some special cases [#208].
  - Changed function name `textx.scoping.get_all_models_including_attached_models`
    to `textx.scoping.get_included_models` (marked old function
    as deprecated) ([#197]).
  - Delete all models touched while loading a model, when an error occurs
    while loading in all repositories (strong exception safety guarantee) ([#200]).


## [v2.0.1] (released: 2019-05-20)

### Added

  - [Registration and discovery] of languages and generators ([#187])
  - New textx CLI commands for listing generators and languages
    (`list-generators`, `list-languages`) and calling a generator (`generate`) ([#187])
  - Meta-models may now [reference other registered meta-models] using the
    `reference` statement ([#187])
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

  - All textX commands implemented using textX CLI extensibility. `check`
    command reworked to support the new registration feature ([#187]) **(BIC)**
  - (Meta-)model visualization reworked as a set of textX generators ([#187]).
    **(BIC)**
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
  - Dropped support for Python 3.3

### Fixed

  - White-spaces in string matches were erroneously stripped ([#188])
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

[#364]: https://github.com/textX/textX/pull/364
[#355]: https://github.com/textX/textX/pull/355
[#299]: https://github.com/textX/textX/pull/299
[#298]: https://github.com/textX/textX/pull/298
[#294]: https://github.com/textX/textX/pull/294
[#292]: https://github.com/textX/textX/pull/292
[#288]: https://github.com/textX/textX/pull/288
[#287]: https://github.com/textX/textX/pull/287
[#284]: https://github.com/textX/textX/pull/284
[#283]: https://github.com/textX/textX/pull/283
[#282]: https://github.com/textX/textX/pull/282
[#281]: https://github.com/textX/textX/pull/281
[#276]: https://github.com/textX/textX/pull/276
[#274]: https://github.com/textX/textX/pull/274
[#273]: https://github.com/textX/textX/pull/273
[#270]: https://github.com/textX/textX/issues/270
[#272]: https://github.com/textX/textX/pull/272
[#267]: https://github.com/textX/textX/issues/267
[#266]: https://github.com/textX/textX/issues/266
[#264]: https://github.com/textX/textX/pull/264
[#261]: https://github.com/textX/textX/pull/261
[#260]: https://github.com/textX/textX/pull/260
[#256]: https://github.com/textX/textX/pull/256
[#250]: https://github.com/textX/textX/pull/250
[#246]: https://github.com/textX/textX/issues/246
[#243]: https://github.com/textX/textX/pull/243
[#235]: https://github.com/textX/textX/pull/235
[#234]: https://github.com/textX/textX/pull/234
[#233]: https://github.com/textX/textX/pull/233
[#231]: https://github.com/textX/textX/pull/231
[#228]: https://github.com/textX/textX/pull/228
[#225]: https://github.com/textX/textX/pull/225
[#224]: https://github.com/textX/textX/pull/224
[#222]: https://github.com/textX/textX/pull/222
[#219]: https://github.com/textX/textX/pull/219
[#218]: https://github.com/textX/textX/pull/218
[#211]: https://github.com/textX/textX/pull/211
[#208]: https://github.com/textX/textX/pull/208
[#200]: https://github.com/textX/textX/issues/200
[#197]: https://github.com/textX/textX/issues/197
[#188]: https://github.com/textX/textX/issues/188
[#187]: https://github.com/textX/textX/pull/187
[#186]: https://github.com/textX/textX/pull/186
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
[#111]: https://github.com/textX/textX/issues/111
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
[#40]: https://github.com/textX/textX/issues/40

[Unreleased]: https://github.com/textX/textX/compare/4.1.0...HEAD
[4.1.0]: https://github.com/textX/textX/compare/4.0.1...4.1.0
[4.0.1]: https://github.com/textX/textX/compare/4.0.0...4.0.1
[4.0.0]: https://github.com/textX/textX/compare/3.1.1...4.0.0
[3.1.1]: https://github.com/textX/textX/compare/3.1.0...3.1.1
[3.1.0]: https://github.com/textX/textX/compare/3.0.0...3.1.0
[3.0.0]: https://github.com/textX/textX/compare/2.3.0...3.0.0
[2.3.0]: https://github.com/textX/textX/compare/v2.2.0...2.3.0
[v2.2.0]: https://github.com/textX/textX/compare/v2.1.0...v2.2.0
[v2.1.0]: https://github.com/textX/textX/compare/v2.0.1...v2.1.0
[v2.0.1]: https://github.com/textX/textX/compare/v1.8.0...v2.0.1
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
[textXDocs]: http://textx.github.io/textX/
[Registration and discovery]: http://textx.github.io/textX/registration.html
[reference other registered meta-models]: http://textx.github.io/textX/multimetamodel.html#use-case-meta-model-referencing-another-meta-model
