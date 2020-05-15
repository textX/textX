from __future__ import unicode_literals
import os
import os.path
from textx import (metamodel_from_file,
                   register_language, clear_language_registrations)
import textx.scoping.providers as scoping_providers
import textx.scoping as scoping


class C1(object):
    def __init__(self, **kwargs):
        for k in kwargs.keys():
            setattr(self, k, kwargs[k])


def test_multi_metamodel_obj_proc():
    global_repo = scoping.GlobalModelRepository()
    repo = scoping_providers.PlainNameGlobalRepo()
    repo.register_models(os.path.dirname(__file__) + "/issue140/*.a")

    mm_A = metamodel_from_file(os.path.join(
        os.path.dirname(__file__),
        "issue140",
        "A.tx"
    ), global_repository=global_repo, classes=[C1])
    mm_B = metamodel_from_file(os.path.join(
        os.path.dirname(__file__),
        "issue140",
        "B.tx"
    ), global_repository=global_repo, classes=[C1])

    mm_B.register_scope_providers({"*.*": repo})

    def proc(a):
        print(a)

    mm_A.register_obj_processors({"C1": proc})
    mm_B.register_obj_processors({"C1": proc})

    clear_language_registrations()
    register_language(
        'a-dsl',
        pattern='*.a',
        description='Test Lang A',
        metamodel=mm_A)
    register_language(
        'b-dsl',
        pattern='*.b',
        description='Test Lang B',
        metamodel=mm_B)

    mm_B.model_from_file(os.path.join(
        os.path.dirname(__file__),
        "issue140",
        "b.b"
    ))
