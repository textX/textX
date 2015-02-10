textX changelog
---------------

* Release 0.3
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
