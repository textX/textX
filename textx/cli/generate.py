import os

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
    generator_for_language_target,
    language_for_file,
    metamodel_for_file,
    metamodel_for_language,
    metamodel_from_file,
)


def generate(textx):
    @textx.command(context_settings=dict(ignore_unknown_options=True))
    @click.argument("model_files", type=click.Path(), required=True, nargs=-1)
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
        model_files,
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
        click.echo(f"Generating {target} target from models:")

        try:
            per_file_metamodel = False
            if grammar:
                metamodel = metamodel_from_file(
                    grammar, debug=debug, ignore_case=ignore_case
                )
                language = "any"
            elif language:
                metamodel = metamodel_for_language(language)
            else:
                per_file_metamodel = True

            # Find all custom arguments
            model_files = list(model_files)
            model_files_without_args = []
            custom_args = {}
            while model_files:
                m = model_files.pop(0)
                if m.startswith("--"):
                    arg_name = m[2:]
                    if not model_files or model_files[0].startswith("--"):
                        # Boolean argument
                        custom_args[arg_name] = True
                    else:
                        custom_args[arg_name] = model_files.pop(0).strip("\"'")
                else:
                    model_files_without_args.append(m)

            # Call generator for each model file
            for model_file in model_files_without_args:
                click.echo(os.path.abspath(model_file))

                if per_file_metamodel:
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
                generator = generator_for_language_target(
                    language, target, any_permitted=per_file_metamodel
                )

                generator(metamodel, model, output_path, overwrite, debug, **custom_args)

        except TextXRegistrationError as e:
            raise click.ClickException(e.message) from e

        except TextXError as e:
            raise click.ClickException(str(e)) from e
