import pytest  # noqa
import os
import os.path
from pytest import raises
from textx import (
    get_location,
    metamodel_from_str,
    metamodel_for_language,
    register_language,
    clear_language_registrations,
)
import textx.scoping.providers as scoping_providers
import textx.scoping as scoping
import textx.exceptions


grammarA = """
Model: a+=A;
A:'A' name=ID;
"""
grammarB = """
reference A
Model: b+=B;
B:'B' name=ID '->' a=[A.A];
"""
grammarBWithImport = """
reference A as a
Model: imports+=Import b+=B;
B:'B' name=ID '->' a=[a.A];
Import: 'import' importURI=STRING;
"""


def register_languages():
    clear_language_registrations()

    global_repo = scoping.GlobalModelRepository()
    global_repo_provider = scoping_providers.PlainNameGlobalRepo()

    class A:
        def __init__(self, **kwargs):
            super().__init__()
            for k, v in kwargs.items():
                self.__dict__[k] = v

        def __setattr__(self, name, value):
            raise Exception("test: this is not allowed.")

    def get_A_mm():
        mm_A = metamodel_from_str(grammarA, global_repository=global_repo, classes=[A])
        mm_A.register_scope_providers({"*.*": global_repo_provider})
        return mm_A

    def get_B_mm():
        mm_B = metamodel_from_str(grammarB, global_repository=global_repo)
        mm_B.register_scope_providers({"*.*": global_repo_provider})
        return mm_B

    def get_BwithImport_mm():
        mm_B = metamodel_from_str(grammarBWithImport, global_repository=global_repo)

        # define a default scope provider supporting the importURI feature
        mm_B.register_scope_providers({"*.*": scoping_providers.FQNImportURI()})
        return mm_B

    register_language("A", pattern="*.a", metamodel=get_A_mm)
    register_language("B", pattern="*.b", metamodel=get_B_mm)

    register_language("BwithImport", pattern="*.b", metamodel=get_BwithImport_mm)

    return global_repo_provider


def test_multi_metamodel_references1():
    global_repo_provider = register_languages()

    mm_A = metamodel_for_language("A")
    mA = mm_A.model_from_str(
        """
    A a1 A a2 A a3
    """
    )
    global_repo_provider.add_model(mA)

    mm_B = metamodel_for_language("B")
    mm_B.model_from_str(
        """
    B b1 -> a1 B b2 -> a2 B b3 -> a3
    """
    )

    with raises(textx.exceptions.TextXSemanticError, match=r".*UNKNOWN.*"):
        mm_B.model_from_str(
            """
        B b1 -> a1 B b2 -> a2 B b3 -> UNKNOWN
        """
        )


def test_multi_metamodel_references2():
    mm_A = metamodel_from_str(grammarA)
    mm_B = metamodel_from_str(grammarB)

    global_repo_provider = scoping_providers.PlainNameGlobalRepo()
    mm_B.register_scope_providers({"*.*": global_repo_provider})

    mA = mm_A.model_from_str(
        """
    A a1 A a2 A a3
    """
    )
    global_repo_provider.add_model(mA)

    mm_B.model_from_str(
        """
    B b1 -> a1 B b2 -> a2 B b3 -> a3
    """
    )

    with raises(textx.exceptions.TextXSemanticError, match=r".*UNKNOWN.*"):
        mm_B.model_from_str(
            """
        B b1 -> a1 B b2 -> a2 B b3 -> UNKNOWN
        """
        )


def test_multi_metamodel_references_with_importURI():
    # Use a global repo.
    # This is useful, especially with circular includes or diamond shaped
    # includes. Without such a repo, you might get double instantiations of
    # model elements.
    # However, if B includes A, but A not B, both meta models might have
    # global repos on their own (global between model files of the same
    # meta model --> global_repository=True). Circular dependencies
    # will require shared grammars, like in test_metamodel_provider3.py,
    # because it is not possible to share meta models for referencing, before
    # the meta model is constructed (like in our example, mm_A cannot
    # reference mm_B, if mm_B already references mm_A because one has to
    # constructed first).
    # Add a custom setattr for a rule used in the language with is imported
    # via the importURI feature. This should test that the attr
    # replacement also works for models not representing the "main outer
    # model" of a load_from_xxx-call.

    register_languages()

    # Create two meta models with the global repo.
    # The second meta model allows referencing the first one.
    mm_A = metamodel_for_language("A")
    mm_B = metamodel_for_language("BwithImport")

    modelA = mm_A.model_from_str(
        """
    A a1 A a2 A a3
    """
    )

    with raises(Exception, match=r".*test: this is not allowed.*"):
        modelA.a[0].x = 1

    # load a model from B which includes a model from A.
    current_dir = os.path.dirname(__file__)
    modelB = mm_B.model_from_file(
        os.path.join(current_dir, "multi_metamodel", "refs", "b.b")
    )

    # check that the classes from the correct meta model are used
    # (and that the model was loaded).
    assert modelB.b[0].__class__ == mm_B[modelB.b[0].__class__.__name__]
    assert modelB.b[0].a.__class__ == mm_A[modelB.b[0].a.__class__.__name__]

    with raises(Exception, match=r".*test: this is not allowed.*"):
        modelB.b[0].a.x = 1


# -------------------------------------


class LibTypes:
    """Library for Typedefs:
    type int
    type string
    """

    @staticmethod
    def get_metamodel():
        return metamodel_for_language("types")

    @staticmethod
    def library_init(repo_selector):
        if repo_selector == "no global scope":
            global_repo = False
        elif repo_selector == "global repo":
            global_repo = True
        else:
            raise Exception(f"unexpected parameter 'repo_selector={repo_selector}'")

        def get_metamodel():
            mm = metamodel_from_str(
                r"""
                    Model: types+=Type;
                    Type: 'type' name=ID;
                    Comment: /\/\/.*$/;
                """,
                global_repository=global_repo,
            )

            def check_type(t):
                if t.name[0].isupper():
                    raise textx.exceptions.TextXSyntaxError(
                        "types must be lowercase", **get_location(t)
                    )

            mm.register_obj_processors({"Type": check_type})

            return mm

        register_language("types", pattern="*.type", metamodel=get_metamodel)


class LibData:
    """Library for Datadefs:
    data Point { x: int y: int}
    data City { name: string }
    data Population { count: int}
    """

    @staticmethod
    def get_metamodel():
        return metamodel_for_language("data")

    @staticmethod
    def library_init(repo_selector):
        if repo_selector == "no global scope":
            global_repo = False
        elif repo_selector == "global repo":
            # get the global repo from the inherited meta model:
            global_repo = LibTypes.get_metamodel()._tx_model_repository
        else:
            raise Exception(f"unexpected parameter 'repo_selector={repo_selector}'")

        def get_metamodel():
            mm = metamodel_from_str(
                r"""
                    reference types as t
                    Model: includes*=Include data+=Data;
                    Data: 'data' name=ID '{'
                        attributes+=Attribute
                    '}';
                    Attribute: name=ID ':' type=[t.Type];
                    Include: '#include' importURI=STRING;
                    Comment: /\/\/.*$/;
                """,
                global_repository=global_repo,
            )

            mm.register_scope_providers({"*.*": scoping_providers.FQNImportURI()})

            return mm

        register_language("data", pattern="*.data", metamodel=get_metamodel)


class LibFlow:
    """Library for DataFlows
    algo A1 : Point -> City
    algo A2 : City -> Population
    connect A1 -> A2
    """

    @staticmethod
    def get_metamodel():
        return metamodel_for_language("flow")

    @staticmethod
    def library_init(repo_selector):
        if repo_selector == "no global scope":
            global_repo = False
        elif repo_selector == "global repo":
            # get the global repo from the inherited meta model:
            global_repo = LibData.get_metamodel()._tx_model_repository
        else:
            raise Exception(f"unexpected parameter 'repo_selector={repo_selector}'")

        def get_metamodel():
            mm = metamodel_from_str(
                r"""
                    reference data as d
                    Model: includes*=Include algos+=Algo flows+=Flow;
                    Algo: 'algo' name=ID ':' inp=[d.Data] '->' outp=[d.Data];
                    Flow: 'connect' algo1=[Algo] '->' algo2=[Algo] ;
                    Include: '#include' importURI=STRING;
                    Comment: /\/\/.*$/;
                """,
                global_repository=global_repo,
            )

            mm.register_scope_providers({"*.*": scoping_providers.FQNImportURI()})

            def check_flow(f):
                if f.algo1.outp != f.algo2.inp:
                    raise textx.exceptions.TextXSemanticError(
                        "algo data types must match", **get_location(f)
                    )

            mm.register_obj_processors({"Flow": check_flow})

            return mm

        register_language("flow", pattern="*.flow", metamodel=get_metamodel)


def test_multi_metamodel_types_data_flow1():
    # this stuff normally happens in the python module directly of the
    # third party lib
    selector = "no global scope"
    clear_language_registrations()
    LibTypes.library_init(selector)
    LibData.library_init(selector)
    LibFlow.library_init(selector)

    current_dir = os.path.dirname(__file__)
    model1 = LibFlow.get_metamodel().model_from_file(
        os.path.join(current_dir, "multi_metamodel", "types_data_flow", "data_flow.flow")
    )

    # althought, types.type is included 2x, it is only present 1x
    # (scope providers share a common repo within on model and all
    #  loaded models in that model)
    assert len(model1._tx_model_repository.all_models) == 3

    # load the type model also used by model1
    model2 = LibData.get_metamodel().model_from_file(
        os.path.join(
            current_dir, "multi_metamodel", "types_data_flow", "data_structures.data"
        )
    )

    # load the type model also used by model1 and model2
    model3 = LibTypes.get_metamodel().model_from_file(
        os.path.join(current_dir, "multi_metamodel", "types_data_flow", "types.type")
    )

    # the types (reloaded by the second model)
    # are not shared with the first model
    # --> no global repo
    assert (
        model1.algos[0].inp.attributes[0].type
        not in model2.includes[0]._tx_loaded_models[0].types
    )
    assert model1.algos[0].inp.attributes[0].type not in model3.types


def test_multi_metamodel_types_data_flow2():
    # this stuff normally happens in the python module directly of the
    # third party lib
    selector = "global repo"
    clear_language_registrations()
    LibTypes.library_init(selector)
    LibData.library_init(selector)
    LibFlow.library_init(selector)

    current_dir = os.path.dirname(__file__)
    model1 = LibFlow.get_metamodel().model_from_file(
        os.path.join(current_dir, "multi_metamodel", "types_data_flow", "data_flow.flow")
    )
    # althought, types.type is included 2x, it is only present 1x
    assert len(model1._tx_model_repository.all_models) == 3

    # load the type model also used by model1
    model2 = LibData.get_metamodel().model_from_file(
        os.path.join(
            current_dir, "multi_metamodel", "types_data_flow", "data_structures.data"
        )
    )

    # load the type model also used by model1 and model2
    model3 = LibTypes.get_metamodel().model_from_file(
        os.path.join(current_dir, "multi_metamodel", "types_data_flow", "types.type")
    )

    # the types (reloaded by the second model)
    # are shared with the first model
    # --> global repo
    assert (
        model1.algos[0].inp.attributes[0].type
        in model2.includes[0]._tx_loaded_models[0].types
    )
    assert model1.algos[0].inp.attributes[0].type in model3.types


def test_multi_metamodel_types_data_flow_validation_error_in_types():
    selector = "no global scope"
    clear_language_registrations()
    LibTypes.library_init(selector)
    LibData.library_init(selector)
    LibFlow.library_init(selector)

    current_dir = os.path.dirname(__file__)

    with raises(textx.exceptions.TextXSyntaxError, match=r".*lowercase.*"):
        LibFlow.get_metamodel().model_from_file(
            os.path.join(
                current_dir,
                "multi_metamodel",
                "types_data_flow",
                "data_flow_including_error.flow",
            )
        )


def test_multi_metamodel_types_data_flow_validation_error_in_data_flow():
    selector = "no global scope"
    clear_language_registrations()
    LibTypes.library_init(selector)
    LibData.library_init(selector)
    LibFlow.library_init(selector)

    current_dir = os.path.dirname(__file__)

    with raises(textx.exceptions.TextXSemanticError, match=r".*data types must match.*"):
        LibFlow.get_metamodel().model_from_file(
            os.path.join(
                current_dir,
                "multi_metamodel",
                "types_data_flow",
                "data_flow_with_error.flow",
            )
        )
