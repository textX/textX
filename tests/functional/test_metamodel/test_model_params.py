import os.path

from click.testing import CliRunner
from pytest import raises

from textx import (
    generator,
    language,
    metamodel_from_str,
    register_generator,
    register_language,
)
from textx.cli import textx
from textx.exceptions import TextXError
from textx.generators import gen_file, get_output_filename

grammar = r"""
Model: 'MyModel' name=ID;
"""

text = r"""
MyModel test1
"""


def test_model_params():
    mm = metamodel_from_str(grammar)
    mm.model_param_defs.add("parameter1", "an example param (1)")
    mm.model_param_defs.add("parameter2", "an example param (2)")

    m = mm.model_from_str(text, parameter1="P1", parameter2="P2")
    assert m.name == "test1"
    assert hasattr(m, "_tx_model_params")
    assert len(m._tx_model_params) == 2
    assert len(m._tx_model_params.used_keys) == 0

    assert not m._tx_model_params.all_used

    assert m._tx_model_params["parameter1"] == "P1"
    assert len(m._tx_model_params.used_keys) == 1
    assert "parameter1" in m._tx_model_params.used_keys
    assert "parameter2" not in m._tx_model_params.used_keys

    assert not m._tx_model_params.all_used

    assert m._tx_model_params["parameter2"] == "P2"
    assert len(m._tx_model_params.used_keys) == 2
    assert "parameter1" in m._tx_model_params.used_keys
    assert "parameter2" in m._tx_model_params.used_keys

    assert m._tx_model_params.all_used

    assert (
        m._tx_model_params.get("missing_params", default="default value")
        == "default value"
    )
    assert m._tx_model_params.get("parameter1", default="default value") == "P1"

    with raises(TextXError, match=".*unknown parameter myerror2.*"):
        mm.model_from_str(text, parameter1="P1", myerror2="P2")

    assert len(mm.model_param_defs) >= 2
    assert "parameter1" in mm.model_param_defs
    assert "parameter1" in mm.model_param_defs
    assert mm.model_param_defs["parameter1"].description == "an example param (1)"


def test_model_params_empty():
    mm = metamodel_from_str(grammar)
    mm.model_param_defs.add("parameter1", "an example param (1)")
    mm.model_param_defs.add("parameter2", "an example param (2)")

    m = mm.model_from_str(text)
    assert m.name == "test1"
    assert hasattr(m, "_tx_model_params")
    assert len(m._tx_model_params) == 0

    assert m._tx_model_params.all_used


def test_model_params_file_based():
    mm = metamodel_from_str(grammar)
    mm.model_param_defs.add("parameter1", "an example param (1)")
    mm.model_param_defs.add("parameter2", "an example param (2)")

    current_dir = os.path.dirname(__file__)
    m = mm.model_from_file(
        os.path.join(current_dir, "test_model_params", "model.txt"),
        parameter1="P1",
        parameter2="P2",
    )
    assert m.name == "file_based"
    assert hasattr(m, "_tx_model_params")
    assert len(m._tx_model_params) == 2


def test_model_params_generate_cli():
    """
    Test that model parameters are passed through generate cli command.
    """

    # register test language
    @language("testlang", "*.mpt")
    def model_param_test():
        def processor(model, metamodel):
            # Just to be sure that processor sees the model parameters
            model.model_params = model._tx_model_params

        mm = metamodel_from_str(grammar)
        mm.model_param_defs.add("meaning_of_life", "The Meaning of Life")
        mm.register_model_processor(processor)
        return mm

    register_language(model_param_test)

    # register language generator
    @generator("testlang", "testtarget")
    def mytarget_generator(
        metamodel, model, output_path, overwrite, debug=False, **custom_args
    ):
        # Dump custom args for testing
        txt = "\n".join(
            [f"{arg_name}={arg_value}" for arg_name, arg_value in custom_args.items()]
        )

        # Dump model params processed by model processor for testing
        txt += "\nModel params:"
        txt += "\n".join(
            [
                f"{param_name}={param_value}"
                for param_name, param_value in model.model_params.items()
            ]
        )

        output_file = get_output_filename(model._tx_filename, None, "testtarget")

        def gen_callback():
            with open(output_file, "w") as f:
                f.write(txt)

        gen_file(model._tx_filename, output_file, gen_callback, overwrite)

    register_generator(mytarget_generator)

    # Run generator from CLI
    this_folder = os.path.abspath(os.path.dirname(__file__))
    runner = CliRunner()
    model_file = os.path.join(this_folder, "model_param_generate_test.mpt")
    result = runner.invoke(
        textx,
        [
            "generate",
            "--language",
            "testlang",
            "--target",
            "testtarget",
            "--overwrite",
            model_file,
            "--meaning_of_life",
            "42",
            "--someparam",
            "somevalue",
        ],
    )

    assert result.exit_code == 0

    output_file = os.path.join(this_folder, "model_param_generate_test.testtarget")
    with open(output_file) as f:
        content = f.read()

    assert "someparam=somevalue" in content
    assert "Model params:meaning_of_life=42" in content
