from __future__ import unicode_literals
import os
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


def metamodel_for_language(language_name):
    """
    Load and return the meta-model for the given language.
    Cache it for further use.
    """
    if language_name not in metamodels:
        language = language_description(language_name)
        metamodels[language_name] = language.metamodel()
    return metamodels[language_name]


def metamodels_for_file_extension(file_extension):
    """
    Return meta-models registered for the given extension.
    """
    ext_metamodels = []
    for language in language_descriptions().values():
        if language.extension == file_extension:
            ext_metamodels.append(metamodel_for_language(language.name))
    return ext_metamodels


def metamodel_for_file_extension(file_extension):
    """
    Return a meta-model registered for the given extension or raise
    `TextXRegistrationError` if more than one is registered.
    """
    ext_metamodels = metamodels_for_file_extension(file_extension)
    if len(ext_metamodels) > 1:
        raise TextXRegistrationError('Multiple languages registered for "{}"'
                                     ' extension.'.format(file_extension))
    elif len(ext_metamodels) == 0:
        raise TextXRegistrationError('No language registered for "{}" '
                                     'extension.'.format(file_extension))
    else:
        return ext_metamodels[0]


def metamodels_for_file(file_name):
    """
    Return meta-models that can parse the given file.
    """
    _, file_extension = os.path.splitext(file_name)
    file_extension = file_extension.strip('.')
    return metamodels_for_file_extension(file_extension)


def metamodel_for_file(file_name):
    """
    Return a meta-model that can parse the given file or raise
    `TextXRegistrationError` if more than one is registered.
    """

    _, file_extension = os.path.splitext(file_name)
    file_extension = file_extension.strip('.')
    return metamodel_for_file_extension(file_extension)
