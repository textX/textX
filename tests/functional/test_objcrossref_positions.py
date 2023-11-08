from os.path import abspath, dirname, join

import textx.scoping.providers as scoping_providers
from textx import metamodel_from_str

grammar = r"""
Model:
        imports*=Import
        packages*=Package
;
Package:
        'package' name=ID '{'
            objects*=Object
        '}'
;
Object:
    'object' name=ID ('ref' ref=[Object:FQN])?
;
FQN: ID+['.'];
FQNI: ID+['.']('.*')?;
Import: 'import' importURI=FQNI;
"""

model_b_file_name = join(abspath(dirname(__file__)), "test_objcrossref_positions_B.model")

model_b_str = """
import test_objcrossref_positions

package packageB {
    object A1 ref packageA1.A
    object A2 ref packageA2.A
}
"""

model_a_file_name = join(abspath(dirname(__file__)), "test_objcrossref_positions.model")

with open(model_a_file_name) as model_a_file:
    model_a_str = model_a_file.read()


def test_objcrossref_positions():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_str(grammar, textx_tools_support=True)

    def conv(i):
        return i.replace(".", "/") + ".model"

    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.FQNImportURI(importURI_converter=conv)}
    )

    #################################
    # MODEL PARSING
    #################################

    model_b = my_meta_model.model_from_str(model_b_str, file_name=model_b_file_name)
    model_a = my_meta_model.model_from_file(model_a_file_name)

    #################################
    # TEST CROSSREF BETWEEN MODELS
    #################################

    # def_pos
    rule_position = model_a_str.find("packageA1")  # look for object A in packageA1
    assert (
        model_a_str.find("object A", rule_position)
        == model_b._pos_crossref_list[0].def_pos_start
    )
    rule_position = model_a_str.find("packageA2")  # look for object A in packageA2
    assert (
        model_a_str.find("object A", rule_position)
        == model_b._pos_crossref_list[1].def_pos_start
    )

    # ref_pos
    assert model_b_str.find("packageA1.A") == model_b._pos_crossref_list[0].ref_pos_start
    assert model_b_str.find("packageA2.A") == model_b._pos_crossref_list[1].ref_pos_start

    # def_file_name
    assert model_a_file_name == model_b._pos_crossref_list[0].def_file_name
    assert model_a_file_name == model_b._pos_crossref_list[1].def_file_name

    #################################
    # TEST CROSSREF SAME MODELS
    #################################

    # def_pos
    rule_position = model_a_str.find("packageA1")  # look for object A in packageA1
    assert (
        model_a_str.find("object A", rule_position)
        == model_a._pos_crossref_list[0].def_pos_start
    )
    rule_position = model_a_str.find("packageA2")  # look for object A in packageA2
    assert (
        model_a_str.find("object A", rule_position)
        == model_a._pos_crossref_list[1].def_pos_start
    )

    # ref_pos
    assert model_a_str.find("packageA1.A") == model_a._pos_crossref_list[0].ref_pos_start
    rule_position = model_a_str.find("object B")  # look for object B crossref
    assert (
        model_a_str.find("A", rule_position)
        == model_a._pos_crossref_list[1].ref_pos_start
    )

    # def_file_name
    assert model_a_file_name == model_a._pos_crossref_list[0].def_file_name
    assert model_a_file_name == model_a._pos_crossref_list[1].def_file_name

    #################################
    # END
    #################################
