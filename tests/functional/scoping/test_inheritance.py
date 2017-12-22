from __future__ import unicode_literals

from textx import metamodel_from_file
from textx import children_of_type
import textx.scoping as scoping
import textx.object_processors as processors

from os.path import dirname, abspath
import re

def test_inheritance_processor():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/components_model1/Components.tx')
    my_meta_model.register_scope_provider({
        "*.*": scoping.scope_provider_fully_qualified_names,
        "Connection.from_port": scoping.ScopeProviderForExtendableRelativeNamedLookups("from_inst.component","slots","extends"),
        "Connection.to_port": scoping.ScopeProviderForExtendableRelativeNamedLookups("to_inst.component","slots","extends"),
    })
    my_meta_model.register_obj_processors({
        "Component": processors.InheritanceProcessor("extends")
    })

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/components_model1/example_inherit3.components")

    #################################
    # TEST MODEL
    #################################

    components = children_of_type("Component", my_model)

    expected="""
        Start
        BaseProc
        ExtProc(BaseProc)
        Plus
        ExtProc2(Plus,ExtProc(BaseProc))
        End
        End2
    """

    def myformatter(compo):
        if len(compo._tx_base_entities)==0:
            return compo.name
        else:
            return compo.name+"("+",".join(map(lambda x:myformatter(x), compo._tx_base_entities))+")"

    res="\n\n"
    for c in components: # posisbly in future version, the order need to be normalized...
        res += myformatter(c)+"\n"

    print(res)
    assert re.sub(r'\s*',"",expected) == re.sub(r'\s*',"",res)

    #################################
    # END
    #################################
