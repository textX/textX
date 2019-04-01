from __future__ import unicode_literals
import fnmatch
import pkg_resources

from textx.exceptions import TextXRegistrationError


class LanguageDesc:
    """
    A class used in language registration/discovery.

    Attributes:
        name (str): the name/ID of the language (must be unique)
        pattern (str): filename pattern for models (e.g. "*.data")
        description (str): A short description of the language
        metamodel (callable): A callable that returns configured meta-model
    """

    def __init__(self, name, pattern=None, description='', metamodel=None):
        self.name = name
        self.pattern = pattern
        self.description = description
        self.metamodel = metamodel


class GeneratorDesc:
    """
    A class used in generators registration/discovery.

    Attributes:
        language (str): The name/ID of the language this generator is for.
                        If the generators is generic (applicable to any model)
                        use "*".
        target (str): A short name of the target stack/technology.
        description (str): A short description of the generator.
        generator (callable): A callable of the form:
                              def generator(model, output_folder)
    """
    def __init__(self, language, target, description='', generator=None):
        self.language = language
        self.target = target
        self.description = description
        self.generator = generator


metamodels = {}
languages = None
generators = None


def language_descriptions():
    """
    Return a dict of `LanguageDesc` instances keyed by language name.
    """
    global languages
    if languages is None:
        languages = {}
        for language in pkg_resources.iter_entry_points(
                group='textx_languages'):
            register_language(language.load())
    return languages


def generator_descriptions():
    """
    Return a dict of `GeneratorDesc` instances keyed by language name.
    """
    global generators
    if generators is None:
        generators = {}
        for generator in pkg_resources.iter_entry_points(
                group='textx_generators'):
            register_generator(generator.load())
    return generators


def language_description(language_name):
    """
    Return `LanguageDesc` for the given language name.
    """
    global languages
    if languages is None:
        language_descriptions()
    try:
        return languages[language_name]
    except KeyError:
        raise TextXRegistrationError('Language "{}" not registered.'
                                     .format(language_name))


def generator_description(language_name, target_name):
    """
    Return `GeneratorDesc` instance for the given target and language name.
    """
    global generators
    if generators in None:
        generator_descriptions()
    return generators[language_name][target_name]


def register_language(language_desc):
    """
    Programmatically register a language.
    """
    global languages
    if languages is None:
        language_descriptions()
    if language_desc.name in languages:
        raise TextXRegistrationError(
            'Language "{}" already registered.'.format(language_desc.name))
    languages[language_desc.name] = language_desc


def clear_language_registrations():
    """
    Clear all registered languages.
    """
    global languages, metamodels
    languages = None
    metamodels = {}


def register_generator(generator_desc):
    """
    Programmatically register a generator.
    """
    global generators
    if generators is None:
        generator_descriptions()
    lang_gens = generators.setdefault(generator_desc.language, {})
    if generator_desc.target in lang_gens:
        raise TextXRegistrationError(
            'Generator "{}->{}" already registered.'.format(
                generator_desc.language, generator_desc.target))
    lang_gens[generator_desc.target] = generator_desc


def clear_generator_registrations():
    """
    Clear all registered generators.
    """
    global generators
    generators = None


def metamodel_for_language(language_name):
    """
    Load and return the meta-model for the given language.
    Cache it for further use.
    """
    if language_name not in metamodels:
        from textx.metamodel import TextXMetaModel, TextXMetaMetaModel
        language = language_description(language_name)
        metamodel = language.metamodel()
        if not (isinstance(metamodel, TextXMetaModel) or
                isinstance(metamodel, TextXMetaMetaModel)):
            raise TextXRegistrationError(
                'Meta-model type for language "{}" is "{}".'
                .format(language_name, type(metamodel).__name__))
        metamodels[language_name] = language.metamodel()
    return metamodels[language_name]


def metamodels_for_pattern(pattern):
    """
    Return meta-models registered for the given file pattern.
    """
    ext_metamodels = []
    for language in language_descriptions().values():
        if language.pattern == pattern:
            ext_metamodels.append(metamodel_for_language(language.name))
    return ext_metamodels


def metamodel_for_pattern(pattern):
    """
    Return a meta-model registered for the given pattern or raise
    `TextXRegistrationError` if more than one is registered.
    """
    ext_metamodels = metamodels_for_pattern(pattern)
    if len(ext_metamodels) > 1:
        raise TextXRegistrationError('Multiple languages registered for "{}"'
                                     ' pattern.'.format(pattern))
    elif len(ext_metamodels) == 0:
        raise TextXRegistrationError('No language registered for "{}"'
                                     ' pattern.'.format(pattern))
    return ext_metamodels[0]


def metamodels_for_file(file_name):
    """
    Return meta-models that can parse the given file.
    """
    file_metamodels = []
    for language in language_descriptions().values():
        if fnmatch.fnmatch(file_name, language.pattern):
            file_metamodels.append(metamodel_for_language(language.name))
    return file_metamodels


def metamodel_for_file(file_name):
    """
    Return a meta-model that can parse the given file or raise
    `TextXRegistrationError` if more than one is registered.
    """
    file_metamodels = metamodels_for_file(file_name)
    if len(file_metamodels) > 1:
        raise TextXRegistrationError('Multiple languages can parse file "{}".'
                                     .format(file_name))
    elif len(file_metamodels) == 0:
        raise TextXRegistrationError('No language registered that can parse'
                                     ' file "{}".'.format(file_name))

    return file_metamodels[0]
