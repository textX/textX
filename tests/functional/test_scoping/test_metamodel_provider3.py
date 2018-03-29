from __future__ import unicode_literals
from textx import metamodel_from_file, get_children_of_type
import textx.scoping.providers as scoping_providers
import textx.scoping as scoping
from os.path import dirname, abspath, join
from textx.scoping.tools import get_unique_named_object_in_all_models
from pytest import raises


def test_metamodel_provider_advanced_test3_global():
    """
    Advanced test for ExtRelativeName and PlainNameGlobalRepo.

    Here we have a global model repository shared between
    different meta models.

    The meta models interact (refer to each other, different directions).
    """
    #################################
    # META MODEL DEF
    #################################
    this_folder = dirname(abspath(__file__))

    def get_meta_model(global_repo, grammar_file_name):
        mm = metamodel_from_file(join(this_folder, grammar_file_name),
                                 debug=False)
        mm.register_scope_providers({
            "*.*": global_repo,
        })
        return mm

    global_repo_provider = scoping_providers.PlainNameGlobalRepo()
    global_repo_provider.register_models(
        this_folder + "/metamodel_provider3/circular/*.a")
    global_repo_provider.register_models(
        this_folder + "/metamodel_provider3/circular/*.b")
    global_repo_provider.register_models(
        this_folder + "/metamodel_provider3/circular/*.c")

    a_mm = get_meta_model(
        global_repo_provider, this_folder + "/metamodel_provider3/A.tx")
    b_mm = get_meta_model(
        global_repo_provider, this_folder + "/metamodel_provider3/B.tx")
    c_mm = get_meta_model(
        global_repo_provider, this_folder + "/metamodel_provider3/C.tx")

    scoping.MetaModelProvider.clear()
    scoping.MetaModelProvider.add_metamodel("*.a", a_mm)
    scoping.MetaModelProvider.add_metamodel("*.b", b_mm)
    scoping.MetaModelProvider.add_metamodel("*.c", c_mm)

    #################################
    # MODEL PARSING
    #################################

    model_repo = global_repo_provider.load_models_in_model_repo().all_models

    #################################
    # TEST MODEL
    #################################

    def get_all(model_repo, what):
        lst = []
        for m in model_repo.filename_to_model.values():
            lst = lst + get_children_of_type(what, m)
        return lst

    lst = get_all(model_repo, "Obj")
    # print(lst)
    assert len(lst) == 3

    # check some references to be resolved (!=None)
    for a in lst:
        assert a.ref

    #################################
    # END
    #################################
    scoping.MetaModelProvider.clear()


def test_metamodel_provider_advanced_test3_import():
    """
    Advanced test for ExtRelativeName and PlainNameImportURI.

    Here we have a global model repository shared between
    different meta models.

    The meta models interact (refer to each other, different directions).
    """
    #################################
    # META MODEL DEF
    #################################
    this_folder = dirname(abspath(__file__))

    def get_meta_model(provider, grammar_file_name):
        mm = metamodel_from_file(join(this_folder, grammar_file_name),
                                 debug=False)
        mm.register_scope_providers({
            "*.*": provider,
        })
        return mm

    import_lookup_provider = scoping_providers.PlainNameImportURI()

    a_mm = get_meta_model(
        import_lookup_provider, this_folder + "/metamodel_provider3/A.tx")
    b_mm = get_meta_model(
        import_lookup_provider, this_folder + "/metamodel_provider3/B.tx")
    c_mm = get_meta_model(
        import_lookup_provider, this_folder + "/metamodel_provider3/C.tx")

    scoping.MetaModelProvider.clear()
    scoping.MetaModelProvider.add_metamodel("*.a", a_mm)
    scoping.MetaModelProvider.add_metamodel("*.b", b_mm)
    scoping.MetaModelProvider.add_metamodel("*.c", c_mm)

    #################################
    # MODEL PARSING
    #################################

    m = a_mm.model_from_file(
        this_folder + "/metamodel_provider3/circular/model_a.a")
    model_repo = m._tx_model_repository.all_models

    #################################
    # TEST MODEL
    #################################

    def get_all(model_repo, what):
        lst = []
        for m in model_repo.filename_to_model.values():
            lst = lst + get_children_of_type(what, m)
        return lst

    lst = get_all(model_repo, "Obj")
    # print(lst)
    assert len(lst) == 3

    # check all references to be resolved (!=None)
    for a in lst:
        assert a.ref

    #################################
    # END
    #################################
    scoping.MetaModelProvider.clear()


def test_metamodel_provider_advanced_test3_inheritance():
    """
    Advanced test for ExtRelativeName and FQNImportURI.

    Here we have a global model repository shared between
    different meta models.

    The meta models interact (refer to each other, different directions,
    A inherits from B, the B from A, etc.).

    It is checked that all relevant references are resolved.
    """
    #################################
    # META MODEL DEF
    #################################
    this_folder = dirname(abspath(__file__))

    def get_meta_model(provider, grammar_file_name):
        mm = metamodel_from_file(join(this_folder, grammar_file_name),
                                 debug=False)
        mm.register_scope_providers({
            "*.*": provider,
            "Call.method": scoping_providers.ExtRelativeName("obj.ref",
                                                             "methods",
                                                             "extends")
        })
        return mm

    import_lookup_provider = scoping_providers.FQNImportURI()

    a_mm = get_meta_model(
        import_lookup_provider, this_folder + "/metamodel_provider3/A.tx")
    b_mm = get_meta_model(
        import_lookup_provider, this_folder + "/metamodel_provider3/B.tx")
    c_mm = get_meta_model(
        import_lookup_provider, this_folder + "/metamodel_provider3/C.tx")

    scoping.MetaModelProvider.clear()
    scoping.MetaModelProvider.add_metamodel("*.a", a_mm)
    scoping.MetaModelProvider.add_metamodel("*.b", b_mm)
    scoping.MetaModelProvider.add_metamodel("*.c", c_mm)

    #################################
    # MODEL PARSING
    #################################

    m = a_mm.model_from_file(
        this_folder + "/metamodel_provider3/inheritance/model_a.a")
    model_repo = m._tx_model_repository.all_models

    #################################
    # TEST MODEL (dependencies from one file to the other and back again)
    # - checks all references are resolved
    #################################

    def get_all(model_repo, what):
        lst = []
        for m in model_repo.filename_to_model.values():
            lst = lst + get_children_of_type(what, m)
        return lst

    lst = get_all(model_repo, "Call")
    assert len(lst) > 0

    # check all references to be resolved (!=None)
    for a in lst:
        assert a.method

    #################################
    # END
    #################################
    scoping.MetaModelProvider.clear()


def test_metamodel_provider_advanced_test3_inheritance2():
    """
    More complicated model (see test above). It is also checked that
    the parsers are correctly cloned.
    """
    #################################
    # META MODEL DEF
    #################################
    this_folder = dirname(abspath(__file__))

    def get_meta_model(provider, grammar_file_name):
        mm = metamodel_from_file(join(this_folder, grammar_file_name),
                                 debug=False)
        mm.register_scope_providers({
            "*.*": provider,
            "Call.method": scoping_providers.ExtRelativeName("obj.ref",
                                                             "methods",
                                                             "extends")
        })
        return mm

    import_lookup_provider = scoping_providers.FQNImportURI()

    a_mm = get_meta_model(
        import_lookup_provider, this_folder + "/metamodel_provider3/A.tx")
    b_mm = get_meta_model(
        import_lookup_provider, this_folder + "/metamodel_provider3/B.tx")
    c_mm = get_meta_model(
        import_lookup_provider, this_folder + "/metamodel_provider3/C.tx")

    scoping.MetaModelProvider.clear()
    scoping.MetaModelProvider.add_metamodel("*.a", a_mm)
    scoping.MetaModelProvider.add_metamodel("*.b", b_mm)
    scoping.MetaModelProvider.add_metamodel("*.c", c_mm)

    #################################
    # MODEL PARSING
    #################################

    m = a_mm.model_from_file(
        this_folder + "/metamodel_provider3/inheritance2/model_a.a")
    model_repo = m._tx_model_repository.all_models

    #################################
    # TEST MODEL (inheritance)
    # - check all references are resolved
    # - check all models have an own parser
    #################################

    def get_all(model_repo, what):
        lst = []
        for m in model_repo.filename_to_model.values():
            lst = lst + get_children_of_type(what, m)
        return lst

    lst = get_all(model_repo, "Call")
    assert len(lst) > 0

    # check all references to be resolved (!=None)
    for a in lst:
        assert a.method

    # check that all models have different parsers
    parsers = list(
        map(lambda x:x._tx_parser, model_repo.filename_to_model.values()))
    assert 4==len(parsers) #  4 files -> 4 parsers
    assert 4==len(set(parsers)) # 4 different parsers

    #################################
    # END
    #################################
    scoping.MetaModelProvider.clear()


def test_metamodel_provider_advanced_test3_diamond():
    """
    More complicated model (see test above): here we have a
    diamond shared dependency. It is also checked that
    the parsers are correctly cloned.
    """
    #################################
    # META MODEL DEF
    #################################
    this_folder = dirname(abspath(__file__))

    def get_meta_model(provider, grammar_file_name):
        mm = metamodel_from_file(join(this_folder, grammar_file_name),
                                 debug=False)
        mm.register_scope_providers({
            "*.*": provider,
            "Call.method": scoping_providers.ExtRelativeName("obj.ref",
                                                             "methods",
                                                             "extends")
        })
        return mm

    import_lookup_provider = scoping_providers.FQNImportURI()

    a_mm = get_meta_model(
        import_lookup_provider, this_folder + "/metamodel_provider3/A.tx")
    b_mm = get_meta_model(
        import_lookup_provider, this_folder + "/metamodel_provider3/B.tx")
    c_mm = get_meta_model(
        import_lookup_provider, this_folder + "/metamodel_provider3/C.tx")

    scoping.MetaModelProvider.clear()
    scoping.MetaModelProvider.add_metamodel("*.a", a_mm)
    scoping.MetaModelProvider.add_metamodel("*.b", b_mm)
    scoping.MetaModelProvider.add_metamodel("*.c", c_mm)

    #################################
    # MODEL PARSING
    #################################

    m = a_mm.model_from_file(
        this_folder + "/metamodel_provider3/diamond/A_includes_B_C.a")
    model_repo = m._tx_model_repository.all_models

    #################################
    # TEST MODEL (inheritance, diamond include structure)
    # - check all references are resolved
    # - check all models have an own parser
    #################################

    def get_all(model_repo, what):
        lst = []
        for m in model_repo.filename_to_model.values():
            lst = lst + get_children_of_type(what, m)
        return lst

    lst = get_all(model_repo, "Call")
    assert len(lst) > 0

    # check all references to be resolved (!=None)
    for a in lst:
        assert a.method

    # check that all models have different parsers
    parsers = list(
        map(lambda x:x._tx_parser, model_repo.filename_to_model.values()))
    assert 4==len(parsers) #  4 files -> 4 parsers
    assert 4==len(set(parsers)) # 4 different parsers

    #################################
    # END
    #################################
    scoping.MetaModelProvider.clear()
