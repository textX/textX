import pytest  # noqa
import os
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

def test_multi_metamodel_references():

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

def test_multi_metamodel_references():

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
