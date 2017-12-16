from textx.metamodel import metamodel_from_file
from textx.model import children
import textx.scoping as scoping
from os.path import dirname, abspath

def test_model_without_imports():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/interface_model1/Interface.tx')
    my_meta_model.register_scope_provider({"*.*":scoping.scope_provider_fully_qualified_name_with_importURI})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/interface_model1/model_a/all_in_one.if")

    #################################
    # TEST MODEL
    #################################

    # check that "socket" is an interface
    a = children(lambda x:hasattr(x,'name') and x.name=="socket", my_model)
    assert(len(a)==1)
    assert( "Interface" == a[0].__class__.__name__ )

    # check that "s.s1" is a reference to the socket interface
    b = children(lambda x:hasattr(x,'name') and x.name=="s", my_model)
    assert(len(b)==1)
    assert( "Interface" == b[0].ref.__class__.__name__ )
    s1 = children(lambda x:hasattr(x,'name') and x.name=="s1", b[0].ref)
    assert(len(s1)==1)
    assert( a[0] == s1[0].ref )

    #################################
    # END
    #################################

def test_model_with_imports():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/interface_model1/Interface.tx')
    my_meta_model.register_scope_provider({"*.*":scoping.scope_provider_fully_qualified_name_with_importURI})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/interface_model1/model_b/app.if")

    #################################
    # TEST MODEL
    #################################

    # check that "socket" is an interface
    a = children(lambda x:hasattr(x,'name') and x.name=="socket", my_model._tx_referenced_models[0])
    assert(len(a)==1)
    assert( "Interface" == a[0].__class__.__name__ )

    # check that "s.s1" is a reference to the socket interface
    b = children(lambda x:hasattr(x,'name') and x.name=="s", my_model)
    assert(len(b)==1)
    assert( "Interface" == b[0].ref.__class__.__name__ )
    s1 = children(lambda x:hasattr(x,'name') and x.name=="s1", b[0].ref)
    assert(len(s1)==1)
    assert( a[0] == s1[0].ref )

    #################################
    # END
    #################################

