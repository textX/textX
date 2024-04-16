"""
Languages and generators registration and discovery API.
"""
import fnmatch
import sys

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

from textx.exceptions import TextXRegistrationError


class LanguageDesc:
    """
    A class used in language registration/discovery.

    Attributes:
        name (str): the name/ID of the language (must be unique)
        pattern (str): filename pattern for models (e.g. "*.data")
        description (str): A short description of the language
        metamodel (callable): A callable that returns configured meta-model
            or the metamodel itself (if a single specific instance is
            desired)
        project_name (str): Read-only attribute available on registrations from
            `pyproject.toml`. Keeps the Python project name of the project that
            registered this language.
        project_version (str): Read-only attribute available on registrations
            from `pyproject.toml`. Keeps the Python project name of the project that
            registered this language.
    """

    def __init__(self, name, pattern=None, description="", metamodel=None):
        self.name = name
        self.pattern = pattern
        self.description = description
        self.metamodel = metamodel
        self.project_name = None
        self.project_version = None


class GeneratorDesc:
    """
    A class used in generators registration/discovery.

    Attributes:
        language (str): The name/ID of the language this generator is for.
                        If the generators is generic (applicable to any model)
                        use "any".
        target (str): A short name of the target stack/technology.
        description (str): A short description of the generator.
        generator (callable): A callable of the form:
                              def generator(metamodel, model, output_path,
                                            overwrite, debug, **custom_args)
        project_name (str): Read-only attribute available on registrations from
            `pyproject.toml`. Keeps the Python project name of the project that
            registered this generator.
        project_version (str): Read-only attribute available on registrations
            from `pyproject.toml`. Keeps the Python project name of the project that
            registered this language.
    """

    def __init__(self, language, target, description="", generator=None):
        self.language = language
        self.target = target
        self.description = description
        self.generator = generator
        self.project_name = None
        self.project_version = None


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
        for language in entry_points(group="textx_languages"):
            register_language_with_project(
                language.load(), language.dist.name, language.dist.version
            )
    return languages


def generator_descriptions():
    """
    Return a dict of `GeneratorDesc` instances keyed by language name.
    """
    global generators
    if generators is None:
        generators = {}
        for generator in entry_points(group="textx_generators"):
            register_generator_with_project(
                generator.load(), generator.dist.name, generator.dist.version
            )
    return generators


def language_description(language_name):
    """
    Return `LanguageDesc` for the given language name.
    """
    global languages
    language_name = language_name.lower()
    if languages is None:
        language_descriptions()
    try:
        return languages[language_name]
    except KeyError as e:
        raise TextXRegistrationError(f'Language "{language_name}" not registered.') from e


def generator_description(language_name, target_name, any_permitted=False):
    """
    Return `GeneratorDesc` instance for the given target and language name.
    If `any_permitted` is `True` return generator for language `any` if
    generator for the `language_name` doesn't exist.
    """
    global generators
    language_name = language_name.lower()
    target_name = target_name.lower()
    if generators is None:
        generator_descriptions()
    try:
        try:
            generators_for_language = generators[language_name]
            return generators_for_language[target_name]
        except KeyError:
            if not any_permitted:
                raise
            generators_for_language = generators["any"]
            return generators_for_language[target_name]
    except KeyError as e:
        raise TextXRegistrationError(
            "No generators registered for language "
            f'"{language_name}" and target "{target_name}".'
        ) from e


def generator_for_language_target(language_name, target_name, any_permitted=False):
    """
    Return generator callable for the given language name and target name.
    """
    generator_desc = generator_description(
        language_name, target_name, any_permitted=any_permitted
    )
    return generator_desc.generator


def register_language(
    language_desc_or_name, pattern=None, description="", metamodel=None
):
    """
    Programmatically register a language.

    Args:
        language_desc_or_name (LanguageDesc or str): If LanguageDesc is given
            other parameters are not used.
        For other parameters see `LanguageDesc`.
    """
    global languages
    if languages is None:
        language_descriptions()

    if not isinstance(language_desc_or_name, LanguageDesc):
        language_desc = LanguageDesc(
            name=language_desc_or_name,
            pattern=pattern,
            description=description,
            metamodel=metamodel,
        )
    else:
        language_desc = language_desc_or_name

    if language_desc.name.lower() in languages:
        raise TextXRegistrationError(
            f'Language "{language_desc.name}" already registered.'
        )
    languages[language_desc.name.lower()] = language_desc


def register_language_with_project(language_desc, project_name, project_version):
    """
    Register language with Python project name.
    """
    language_desc.project_name = project_name
    language_desc.project_version = project_version
    register_language(language_desc)


def clear_language_registrations():
    """
    Clear all registered languages.
    """
    global languages, metamodels
    languages = None
    metamodels = {}


def register_generator(
    generator_desc_or_language, target=None, description="", generator=None
):
    """
    Programmatically register a generator.

    Args:
        generator_desc_or_language (GeneratorDesc or str): If GeneratorDesc is
            given other parameters are not used.
        For other parameters see `GeneratorDesc`.
    """
    global generators
    if generators is None:
        generator_descriptions()

    if not isinstance(generator_desc_or_language, GeneratorDesc):
        generator_desc = GeneratorDesc(
            language=generator_desc_or_language,
            target=target,
            description=description,
            generator=generator,
        )
    else:
        generator_desc = generator_desc_or_language

    lang_gens = generators.setdefault(generator_desc.language.lower(), {})
    if generator_desc.target.lower() in lang_gens:
        raise TextXRegistrationError(
            f'Generator "{generator_desc.language}->'
            f'{generator_desc.target}" already registered.'
        )
    lang_gens[generator_desc.target.lower()] = generator_desc


def register_generator_with_project(generator_desc, project_name, project_version):
    """
    Register generator with Python project name.
    """
    generator_desc.project_name = project_name
    generator_desc.project_version = project_version
    register_generator(generator_desc)


def clear_generator_registrations():
    """
    Clear all registered generators.
    """
    global generators
    generators = None


def metamodel_for_language(language_name, **kwargs):
    """
    Load and return the meta-model for the given language.
    Cache it for further use.
    """
    language_name = language_name.lower()
    if language_name not in metamodels or kwargs:
        from textx.metamodel import TextXMetaMetaModel, TextXMetaModel

        language = language_description(language_name)
        if isinstance(language.metamodel, (TextXMetaModel, TextXMetaMetaModel)):
            metamodels[language_name] = language.metamodel
        else:
            metamodel = language.metamodel(**kwargs)
            if not (isinstance(metamodel, (TextXMetaModel, TextXMetaMetaModel))):
                raise TextXRegistrationError(
                    "Meta-model type for language "
                    f'"{language_name}" is "{metamodel.__class__.__name__}".'
                )
            metamodels[language_name] = metamodel
    return metamodels[language_name]


def languages_for_file(file_name_or_pattern):
    """
    Return a list of `LanguageDesc` registered for the given file pattern.
    """
    file_languages = []
    for language in language_descriptions().values():
        if file_name_or_pattern == language.pattern or fnmatch.fnmatch(
            file_name_or_pattern, language.pattern
        ):
            file_languages.append(language)
    return file_languages


def language_for_file(file_name_or_pattern):
    """
    Return an instance of `LanguageDesc` that can parse the given file or raise
    `TextXRegistrationError` if more than one is registered.
    """
    languages = languages_for_file(file_name_or_pattern)
    if len(languages) > 1:
        raise TextXRegistrationError(
            f'Multiple languages can parse "{file_name_or_pattern}".'
        )
    elif len(languages) == 0:
        raise TextXRegistrationError(
            "No language registered that can parse" f' "{file_name_or_pattern}".'
        )

    return languages[0]


def metamodels_for_file(file_name_or_pattern):
    """
    Return meta-models that can parse the given file .
    """
    return [
        metamodel_for_language(language.name)
        for language in languages_for_file(file_name_or_pattern)
    ]


def metamodel_for_file(file_name_or_pattern, **kwargs):
    """
    Return a meta-model that can parse the given file or raise
    `TextXRegistrationError` if more than one is registered.
    """
    return metamodel_for_language(language_for_file(file_name_or_pattern).name, **kwargs)


def generator(language, target):
    """
    Decorator factory used to create `GeneratorDesc` instances suitable for
    entry point registration.

    The target function docstring is used for the description.
    """

    def _generator(gen_f):
        return GeneratorDesc(
            language=language,
            target=target,
            description=gen_f.__doc__ if gen_f.__doc__ is not None else "",
            generator=gen_f,
        )

    return _generator


def language(name, pattern=None):
    """
    Decorator factory used to create `LanguageDesc` instances suitable for
    entry point registration.

    The target function docstring is used for the description.
    """

    def language(gen_f):
        return LanguageDesc(
            name=name,
            pattern=pattern,
            description=gen_f.__doc__.strip() if gen_f.__doc__ is not None else "",
            metamodel=gen_f,
        )

    return language
