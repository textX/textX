from collections import namedtuple
import pkg_resources

from textx.exceptions import TextXRegistrationError

# A tuple used in language registration/discovery
LanguageDesc = namedtuple('LanguageDesc',
                          'name extension description metamodel')

# A tuple used in generators registration/discovery
# `generator` attribute is a callable of the form:
# def generator(model, output_folder)
GeneratorDesc = namedtuple('GeneratorDesc',
                           'language target description generator')

metamodels = {}
languages = None
generators = None


def get_language_descriptions():
    """
    Return a dict of LanguageDesc instances keyed by language name.
    """
    global languages
    if languages is None:
        languages = {}
        for language in pkg_resources.iter_entry_points(
                group='textx_languages'):
            if language.name in languages:
                raise TextXRegistrationError(
                    'Language "{}" already registered.'.format(language.name))
            languages[language.name] = language.load()
    return languages


def get_generator_descriptions():
    """
    Return a dict of GeneratorDesc instances keyed by language name.
    """
    global generators
    if generators is None:
        generators = {}
        for generator in pkg_resources.iter_entry_points(
                group='textx_generators'):
            lang_gens = generators.setdefault(generator.language, {})
            if generator.target in lang_gens:
                raise TextXRegistrationError(
                    'Generator "{}->{}" already registered.'.format(
                        generator.language, generator.target))
            lang_gens[generator.target] = generator.load()
    return generators


def get_language_description(language_name):
    global languages
    if languages is None:
        get_language_descriptions()
    return languages[language_name]


def get_generator_description(language_name, target_name):
    """
    For the given target and language name return GeneratorDesc instance.
    """
    global generators
    if generators in None:
        get_generator_descriptions()
    return generators[language_name][target_name]


def get_language_metamodel(language_name):
    """
    Load and return the meta-model for the given language.
    Cache it for further use.
    """
    if language_name not in metamodels:
        language = get_language_description(language_name)
        metamodels[language_name] = language.metamodel()
    return metamodels[language_name]
