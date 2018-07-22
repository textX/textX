import pytest  # noqa
import os
import os.path
from pytest import raises
from textx import metamodel_from_str, metamodel_from_file
import textx.scoping.providers as scoping_providers
import textx.scoping as scoping
import textx.scoping.tools as tools
import textx.exceptions

grammarA = """
Model: a+=A;
A:'A' name=ID;
"""
grammarB = """
Model: b+=B;
B:'B' name=ID '->' a=[A];
"""
grammarBWithImport = """
Model: imports+=Import b+=B;
B:'B' name=ID '->' a=[A];
Import: 'import' importURI=STRING;
"""


def test_multi_metamodel_references1():
    global_repo = scoping.GlobalModelRepository()
    mm_A = metamodel_from_str(grammarA, global_repository=global_repo)
    mm_B = metamodel_from_str(grammarB, global_repository=global_repo,
                              referenced_metamodels=[mm_A])

    global_repo_provider = scoping_providers.PlainNameGlobalRepo()
    mm_B.register_scope_providers({"*.*": global_repo_provider})
    mm_A.register_scope_providers({"*.*": global_repo_provider})

    mA = mm_A.model_from_str('''
    A a1 A a2 A a3
    ''')
    global_repo_provider.add_model(mA)

    _ = mm_B.model_from_str('''
    B b1 -> a1 B b2 -> a2 B b3 -> a3
    ''')

    with raises(textx.exceptions.TextXSemanticError,
                match=r'.*UNKNOWN.*'):
        _ = mm_B.model_from_str('''
        B b1 -> a1 B b2 -> a2 B b3 -> UNKNOWN
        ''')


def test_multi_metamodel_references2():
    mm_A = metamodel_from_str(grammarA)
    mm_B = metamodel_from_str(grammarB,
                              referenced_metamodels=[mm_A])

    global_repo_provider = scoping_providers.PlainNameGlobalRepo()
    mm_B.register_scope_providers({"*.*": global_repo_provider})

    mA = mm_A.model_from_str('''
    A a1 A a2 A a3
    ''')
    global_repo_provider.add_model(mA)

    _ = mm_B.model_from_str('''
    B b1 -> a1 B b2 -> a2 B b3 -> a3
    ''')

    with raises(textx.exceptions.TextXSemanticError,
                match=r'.*UNKNOWN.*'):
        _ = mm_B.model_from_str('''
        B b1 -> a1 B b2 -> a2 B b3 -> UNKNOWN
        ''')


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
    global_repo = scoping.GlobalModelRepository()

    # Create two meta models with the global repo.
    # The second meta model allows referencing the first one.
    mm_A = metamodel_from_str(grammarA, global_repository=global_repo)
    mm_B = metamodel_from_str(grammarBWithImport,
                              global_repository=global_repo,
                              referenced_metamodels=[mm_A])

    # define a default scope provider supporting the importURI feature
    mm_B.register_scope_providers({"*.*": scoping_providers.FQNImportURI()})

    # map file endings to the meta models
    scoping.MetaModelProvider.clear()
    scoping.MetaModelProvider.add_metamodel("*.a", mm_A)
    scoping.MetaModelProvider.add_metamodel("*.b", mm_B)

    # load a model from B which includes a model from A.
    current_dir = os.path.dirname(__file__)
    model = mm_B.model_from_file(os.path.join(current_dir, 'multi_metamodel',
                                              'refs', 'b.b'))

    # check that the classes from the correct meta model are used
    # (and that the model was loaded).
    assert model.b[0].__class__ == mm_B[model.b[0].__class__.__name__]
    assert model.b[0].a.__class__ == mm_A[model.b[0].a.__class__.__name__]

    # clean up
    scoping.MetaModelProvider.clear()

# -------------------------------------

class LibTypes:
    """ Library for Typedefs:
            type int
            type string
    """

    _mm = None

    @staticmethod
    def get_metamodel():
        return LibTypes._mm

    @staticmethod
    def library_init(repo_selector):
        if repo_selector=="no global scope":
            global_repo = False
        elif repo_selector=="global repo":
            global_repo = True
        else:
            raise Exception("unexpected parameter 'repo_selector={}'"
                            .format(repo_selector))
        LibTypes._mm = metamodel_from_str(
            '''
                Model: types+=Type;
                Type: 'type' name=ID;
                Comment: /\/\/.*$/;
            ''',
            global_repository=global_repo)
        textx.scoping.MetaModelProvider.add_metamodel("*.type",
                                                      LibTypes.get_metamodel())
        def check_type(t):
            if t.name[0].isupper():
                raise textx.exceptions.TextXSyntaxError(
                    "types must be lowercase",
                    **tools.get_location(t)
                )
        LibTypes._mm.register_obj_processors({
            'Type': check_type
        })

class LibData:
    """ Library for Datadefs:
            data Point { x: int y: int}
            data City { name: string }
            data Population { count: int}
    """

    _mm = None

    @staticmethod
    def get_metamodel():
        return LibData._mm

    @staticmethod
    def library_init(repo_selector):
        if repo_selector=="no global scope":
            global_repo = False
        elif repo_selector=="global repo":
            # get the global repo from the inherited meta model:
            global_repo = LibTypes.get_metamodel()._tx_model_repository
        else:
            raise Exception("unexpected parameter 'repo_selector={}'"
                            .format(repo_selector))
        LibData._mm = metamodel_from_str(
            '''
                Model: includes*=Include data+=Data;
                Data: 'data' name=ID '{'
                    attributes+=Attribute
                '}';
                Attribute: name=ID ':' type=[Type];
                Include: '#include' importURI=STRING;
                Comment: /\/\/.*$/;
            ''',
            global_repository=global_repo,
            referenced_metamodels=[LibTypes.get_metamodel()])
        LibData._mm.register_scope_providers(
            {"*.*": scoping_providers.FQNImportURI()})
        textx.scoping.MetaModelProvider.add_metamodel("*.data",
                                                      LibData.get_metamodel())

class LibFlow:
    """ Library for DataFlows
            algo A1 : Point -> City
            algo A2 : City -> Population
            connect A1 -> A2
    """

    _mm = None

    @staticmethod
    def get_metamodel():
        return LibFlow._mm

    @staticmethod
    def library_init(repo_selector):
        if repo_selector=="no global scope":
            global_repo = False
        elif repo_selector=="global repo":
            # get the global repo from the inherited meta model:
            global_repo = LibData.get_metamodel()._tx_model_repository
        else:
            raise Exception("unexpected parameter 'repo_selector={}'"
                            .format(repo_selector))

        LibFlow._mm = metamodel_from_str(
            '''
                Model: includes*=Include algos+=Algo flows+=Flow;
                Algo: 'algo' name=ID ':' inp=[Data] '->' outp=[Data];
                Flow: 'connect' algo1=[Algo] '->' algo2=[Algo] ;
                Include: '#include' importURI=STRING;
                Comment: /\/\/.*$/;
            ''',
            global_repository = global_repo,
            referenced_metamodels=[LibData.get_metamodel()])
        LibFlow._mm.register_scope_providers(
            {"*.*": scoping_providers.FQNImportURI()})
        textx.scoping.MetaModelProvider.add_metamodel("*.flow",
                                                      LibFlow.get_metamodel())
        def check_flow(f):
            if f.algo1.outp != f.algo2.inp:
                raise textx.exceptions.TextXSemanticError(
                    "algo data types must match",
                    **tools.get_location(f)
                )
        LibFlow._mm.register_obj_processors({
            'Flow': check_flow
        })


def test_multi_metamodel_types_data_flow1():

    # this stuff normally happens in the python module directly of the
    # third party lib
    selector = "no global scope"
    textx.scoping.MetaModelProvider.clear()
    LibTypes.library_init(selector)
    LibData.library_init(selector)
    LibFlow.library_init(selector)

    current_dir = os.path.dirname(__file__)
    model1 = LibFlow.get_metamodel().model_from_file(
        os.path.join(current_dir, 'multi_metamodel','types_data_flow',
                     'data_flow.flow')
    )

    # althought, types.type is included 2x, it is only present 1x
    # (scope providers share a common repo within on model and all
    #  loaded models in that model)
    assert 3 == len(model1._tx_model_repository.all_models.filename_to_model)

    # load the type model also used by model1
    model2 = LibData.get_metamodel().model_from_file(
        os.path.join(current_dir, 'multi_metamodel','types_data_flow',
                     'data_structures.data')
    )

    # load the type model also used by model1 and model2
    model3 = LibTypes.get_metamodel().model_from_file(
        os.path.join(current_dir, 'multi_metamodel','types_data_flow',
                     'types.type')
    )

    # the types (reloaded by the second model)
    # are not shared with the first model
    # --> no global repo
    assert model1.algos[0].inp.attributes[0].type not in model2.includes[0]._tx_loaded_models[0].types
    assert model1.algos[0].inp.attributes[0].type not in model3.types


def test_multi_metamodel_types_data_flow2():

    # this stuff normally happens in the python module directly of the
    # third party lib
    selector = "global repo"
    textx.scoping.MetaModelProvider.clear()
    LibTypes.library_init(selector)
    LibData.library_init(selector)
    LibFlow.library_init(selector)

    current_dir = os.path.dirname(__file__)
    model1 = LibFlow.get_metamodel().model_from_file(
        os.path.join(current_dir, 'multi_metamodel','types_data_flow',
                     'data_flow.flow')
    )
    # althought, types.type is included 2x, it is only present 1x
    assert 3 == len(model1._tx_model_repository.all_models.filename_to_model)

    # load the type model also used by model1
    model2 = LibData.get_metamodel().model_from_file(
        os.path.join(current_dir, 'multi_metamodel','types_data_flow',
                     'data_structures.data')
    )

    # load the type model also used by model1 and model2
    model3 = LibTypes.get_metamodel().model_from_file(
        os.path.join(current_dir, 'multi_metamodel','types_data_flow',
                     'types.type')
    )

    # the types (reloaded by the second model)
    # are shared with the first model
    # --> global repo
    assert model1.algos[0].inp.attributes[0].type in model2.includes[0]._tx_loaded_models[0].types
    assert model1.algos[0].inp.attributes[0].type in model3.types


def test_multi_metamodel_types_data_flow_validation_error_in_types():

    selector = "no global scope"
    textx.scoping.MetaModelProvider.clear()
    LibTypes.library_init(selector)
    LibData.library_init(selector)
    LibFlow.library_init(selector)

    current_dir = os.path.dirname(__file__)

    with raises(textx.exceptions.TextXSyntaxError,
                match=r'.*lowercase.*'):
        _ = LibFlow.get_metamodel().model_from_file(
            os.path.join(current_dir, 'multi_metamodel','types_data_flow',
                         'data_flow_including_error.flow')
        )

def test_multi_metamodel_types_data_flow_validation_error_in_data_flow():

    selector = "no global scope"
    textx.scoping.MetaModelProvider.clear()
    LibTypes.library_init(selector)
    LibData.library_init(selector)
    LibFlow.library_init(selector)

    current_dir = os.path.dirname(__file__)

    with raises(textx.exceptions.TextXSemanticError,
                match=r'.*data types must match.*'):
        _ = LibFlow.get_metamodel().model_from_file(
            os.path.join(current_dir, 'multi_metamodel','types_data_flow',
                         'data_flow_with_error.flow')
        )

