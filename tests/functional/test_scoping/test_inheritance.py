import re
from os.path import abspath, dirname, join

import textx.scoping.providers as scoping_providers
from textx import get_children_of_type, metamodel_from_file


def test_inheritance_processor():
    """
    Basic test for ExtRelativeName (using an inheritance example)
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "components_model1", "Components.tx")
    )
    my_meta_model.register_scope_providers(
        {
            "*.*": scoping_providers.FQN(),
            "Connection.from_port": scoping_providers.ExtRelativeName(
                "from_inst.component", "slots", "extends"
            ),
            "Connection.to_port": scoping_providers.ExtRelativeName(
                "to_inst.component", "slots", "extends"
            ),
        }
    )

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        join(
            abspath(dirname(__file__)), "components_model1", "example_inherit3.components"
        )
    )

    #################################
    # TEST MODEL
    #################################

    components = get_children_of_type("Component", my_model)

    expected = """
        Start
        BaseProc
        ExtProc(BaseProc)
        Plus
        ExtProc2(Plus,ExtProc(BaseProc))
        End
        End2
    """

    def myformatter(compo):
        if len(compo.extends) == 0:
            return compo.name
        else:
            return (
                compo.name
                + "("
                + ",".join(map(lambda x: myformatter(x), compo.extends))
                + ")"
            )

    res = "\n\n"
    # possibly in future version, the order need to be normalized...
    for c in components:
        res += myformatter(c) + "\n"

    print(res)
    assert re.sub(r"\s*", "", expected) == re.sub(r"\s*", "", res)

    #################################
    # END
    #################################


def test_inheritance_processor_rrel():
    """
    Basic test for ExtRelativeName (using an inheritance example)
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "components_model1", "ComponentsRrel.tx")
    )

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        join(
            abspath(dirname(__file__)), "components_model1", "example_inherit3.components"
        )
    )

    #################################
    # TEST MODEL
    #################################

    components = get_children_of_type("Component", my_model)

    expected = """
        Start
        BaseProc
        ExtProc(BaseProc)
        Plus
        ExtProc2(Plus,ExtProc(BaseProc))
        End
        End2
    """

    def myformatter(compo):
        if len(compo.extends) == 0:
            return compo.name
        else:
            return (
                compo.name
                + "("
                + ",".join(map(lambda x: myformatter(x), compo.extends))
                + ")"
            )

    res = "\n\n"
    # possibly in future version, the order need to be normalized...
    for c in components:
        res += myformatter(c) + "\n"

    print(res)
    assert re.sub(r"\s*", "", expected) == re.sub(r"\s*", "", res)

    #################################
    # END
    #################################
