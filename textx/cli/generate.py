import logging
import os
import sys

from textx.registration import generator_description

try:
    import click
except ImportError as e:
    raise Exception(
        "textX must be installed with CLI dependencies to use "
        "textx command.\npip install textX[cli]"
    ) from e
from textx import (
    TextXError,
    TextXRegistrationError,
    language_for_file,
    metamodel_for_file,
    metamodel_for_language,
    metamodel_from_file,
)

logger = logging.getLogger(__name__)


def generate(textx):
    @textx.command(context_settings=dict(ignore_unknown_options=True))
    @click.argument("arguments", type=click.Path(), required=True, nargs=-1)
    @click.option(
        "--output-path",
        "-o",
        type=click.Path(),
        default=None,
        help="The output to generate to. Default = same as input.",
    )
    @click.option(
        "--language",
        help="A name of the language model conforms to."
        " Deduced from file name if not given.",
    )
    @click.option("--target", help="Target output format.", required=True)
    @click.option(
        "--overwrite",
        is_flag=True,
        default=False,
        required=False,
        help="Should overwrite output files if exist.",
    )
    @click.option("--grammar", help="A file name of the grammar used as a meta-model.")
    @click.option(
        "--ignore-case/",
        "-i/",
        default=False,
        is_flag=True,
        help="Case-insensitive model parsing. " 'Used only if "grammar" is provided.',
    )
    @click.pass_context
    def generate(
        ctx,
        arguments,
        output_path,
        language,
        target,
        overwrite,
        grammar=None,
        ignore_case=False,
    ):
        """
        Run code generator on a provided model(s).

        For example::

        \b
        # Generate PlantUML output from .flow models
        textx generate mymodel.flow --target PlantUML

        \b
        # or with defined output folder
        textx generate mymodel.flow -o rendered_model/ --target PlantUML

        \b
        # To chose language by name and not by file pattern use --language
        textx generate *.flow --language flow --target PlantUML

        \b
        # Use --overwrite to overwrite target files
        textx generate mymodel.flow --target PlantUML --overwrite

        \b
        # In all above cases PlantUML generator must be registered, i.e.:
        $ textx list-generators
        flow-dsl -> PlantUML  Generating PlantUML visualization from flow-dsl

        \b
        # If the source language is not registered you can use the .tx grammar
        # file for parsing but the language name used will be `any`.
        textx generate --grammar Flow.tx --target dot mymodel.flow


        """

        debug = ctx.obj["debug"]
        logger.info("Generating %s target.", target)

        try:
            no_explicit_language = False
            if grammar:
                metamodel = metamodel_from_file(
                    grammar, debug=debug, ignore_case=ignore_case
                )
                language = "any"
            elif language:
                metamodel = metamodel_for_language(language)
            else:
                no_explicit_language = True

            # Find all custom arguments
            arguments = list(arguments)
            model_files_without_args = []
            # Custom language and generator arguments
            # These arguments can be defined on the metamodel level
            custom_args = {}
            while arguments:
                m = arguments.pop(0)
                if m.startswith("--"):
                    arg_name = m[2:]
                    if not arguments or arguments[0].startswith("--"):
                        # Boolean argument
                        custom_args[arg_name] = True
                    else:
                        custom_args[arg_name.replace("-", "_")] = arguments.pop(0).strip(
                            "\"'"
                        )
                else:
                    # If the argument is not switch treat it as the model file path.
                    model_files_without_args.append(m)

            def generate(language, target, any_permitted, metamodel, model, custom_args):
                # Check custom args
                given_args = set(custom_args.keys())
                generator = generator_description(language, target, any_permitted)

                generator_args = generator.custom_args
                if generator_args is not None:
                    for arg in generator_args:
                        if arg.mandatory and arg.name not in given_args:
                            raise TextXError(f"Parameter '{arg.name}' must be provided.")
                if given_args and generator_args:
                    generator_arg_names = set(a.name for a in generator_args)
                    for arg in given_args:
                        if arg not in generator_arg_names:
                            raise TextXError(
                                f"Parameter '{arg}' is not defined for this generator."
                            )

                assert generator.generator is not None
                generator.generator(
                    metamodel, model, output_path, overwrite, debug, **custom_args
                )

            if model_files_without_args:
                # Call generator for each model file
                for model_file in model_files_without_args:
                    logger.info(os.path.abspath(model_file))

                    if no_explicit_language:
                        language = language_for_file(model_file).name
                        metamodel = metamodel_for_file(model_file)

                    # Get custom args that match defined model parameters and pass
                    # them in to be available to model processors.
                    model_params = {
                        k: v
                        for k, v in custom_args.items()
                        if k in metamodel.model_param_defs
                    }

                    model = metamodel.model_from_file(model_file, **model_params)
                    generate(
                        language,
                        target,
                        no_explicit_language,
                        metamodel,
                        model,
                        custom_args,
                    )

            else:
                # If no model is given then the only input to the generator are
                # custom args
                if not custom_args:
                    raise TextXRegistrationError(
                        "No model nor custom arguments are given."
                    )

                # Here we run generator without the model as the generator can
                # be run for the metamodel only with custom args.
                if no_explicit_language:
                    language = "textx"
                metamodel = metamodel_for_language(language)
                generate(
                    language, target, no_explicit_language, metamodel, None, custom_args
                )

        except TextXRegistrationError as e:
            logger.error("ERROR: %s", str(e))
            sys.exit(1)

        except TextXError as e:
            logger.error("ERROR: %s", str(e))
            sys.exit(1)
