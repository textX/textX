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
    a = children(lambda x:hasattr(x,'name') and x.name=="socket", my_model._tx_model_repository.all_models.filename_to_model[abspath(dirname(__file__)) + "/interface_model1/model_b/base.if"])
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

def test_model_with_circular_imports():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/interface_model1/Interface.tx')
    my_meta_model.register_scope_provider({"*.*":scoping.scope_provider_fully_qualified_name_with_importURI})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/interface_model1/model_c/A.if")

    #################################
    # TEST MODEL
    #################################

    A = children(lambda x:hasattr(x,'name') and x.name=="A", my_model)
    assert(len(A)==1)
    A=A[0]
    assert( "Interface" == A.__class__.__name__ )

    A_self = children(lambda x:hasattr(x,'name') and x.name=="self", A)
    assert(len(A_self)==1)
    A_self=A_self[0]

    A_other = children(lambda x:hasattr(x,'name') and x.name=="other", A)
    assert(len(A_other)==1)
    A_other=A_other[0]

    A_other_self = children(lambda x:hasattr(x,'name') and x.name=="self", A_other.ref)
    assert(len(A_other_self)==1)
    A_other_self=A_other_self[0]

    A_other_other = children(lambda x:hasattr(x,'name') and x.name=="other", A_other.ref)
    assert(len(A_other_other)==1)
    A_other_other=A_other_other[0]

    assert(A_self.ref  == A_other_other.ref)
    assert(A_self.ref  != A_other.ref)
    assert(A_other.ref == A_other_self.ref)
    assert(A_other.ref != A_other_other.ref)

    #################################
    # END
    #################################


def test_model_with_globalimports1():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/interface_model2/Interface.tx')
    my_meta_model.register_scope_provider({"*.*":scoping.Scope_provider_fully_qualified_name_with_global_repo(my_meta_model, abspath(dirname(__file__)) + "/interface_model1/model_a/*.if")})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/interface_model1/model_a/all_in_one.if")

    #################################
    # TEST MODEL
    #################################

    # check that "socket" is an interface
    a = children(lambda x:hasattr(x,'name') and x.name=="socket", my_model._tx_model_repository.all_models.filename_to_model[abspath(dirname(__file__)) + "/interface_model1/model_b/base.if"])
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
