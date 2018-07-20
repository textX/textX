import pytest  # noqa
import os
import os.path
from pytest import raises
from textx import metamodel_from_str, metamodel_from_file
import textx.scoping.providers as scoping_providers
import textx.scoping as scoping
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
