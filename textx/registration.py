from collections import namedtuple

# A tuple used in language registration/discovery
LanguageDesc = namedtuple('LanguageDesc',
                          'name extension description metamodel')

# A tuple used in generators registration/discovery
# `generator` attribute is a callable of the form:
# def generator(model, output_folder)
GeneratorDesc = namedtuple('GeneratorDesc',
                           'language target description generator')
