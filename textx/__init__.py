# flake8: noqa
from textx.metamodel import metamodel_from_file, metamodel_from_str
from textx.model import (
    get_children_of_type,
    get_parent_of_type,
    get_model,
    get_metamodel,
    get_children,
    get_location,
    textx_isinstance,
    textxerror_wrap,
)
from textx.exceptions import (
    TextXError,
    TextXSyntaxError,
    TextXSemanticError,
    TextXRegistrationError,
)
from textx.registration import (
    LanguageDesc,
    GeneratorDesc,
    register_language,
    register_generator,
    language_descriptions,
    language_description,
    generator_descriptions,
    generator_description,
    clear_language_registrations,
    clear_generator_registrations,
    languages_for_file,
    language_for_file,
    metamodel_for_language,
    metamodel_for_file,
    metamodels_for_file,
    generator_for_language_target,
    generator,
    language,
)

try:
    from importlib.metadata import version
except ModuleNotFoundError:
    from importlib_metadata import version

__version__ = version("textx")
