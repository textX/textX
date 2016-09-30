"""
API for accessing registered languages.
Languages are registered using setuptools entry_point 'textx_lang'.
"""
import pkg_resources
from textx.exceptions import TextXError


LANG_EP = 'textx_lang'


def iter_languages():
    """
    Iterates overs registered languages and returns setuptools EntryPoint
    instances.
    """
    for ep in pkg_resources.iter_entry_points(group=LANG_EP):
        yield ep


def get_language(language_name):
    """
    Returns a callable that instantiates meta-model for the given language.
    """

    langs = list(pkg_resources.iter_entry_points(group=LANG_EP,
                                                 name=language_name))

    if not langs:
        raise TextXError('Language "{}" is not registered.'
                         .format(language_name))

    if len(langs) > 1:
        # Multiple languages defined with the same name
        raise TextXError('Language "{}" registered multiple times:\n{}'
                         .format(language_name,
                                 "\n".join([l.dist for l in langs])))

    return langs[0].load()()
