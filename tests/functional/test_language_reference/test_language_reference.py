"""
Testing `reference` grammar keyword.
"""
import os

import textx.scoping.providers as scoping_providers
from textx import language, metamodel_for_language, metamodel_from_str, register_language


def test_language_reference_keyword():
    @language("first-test-lang", "*.ftest")
    def first_language():
        return metamodel_from_str(
            r"""
            Model: firsts*=First;
            First: name=ID num=INT;
            """
        )

    register_language(first_language)

    @language("second-test-lang", "*.stest")
    def second_language():
        # We can reference here fist-test-lang since it is registered above
        mm = metamodel_from_str(
            r"""
            reference first-test-lang as f

            Model:
                includes*=Include
                refs+=Reference;
            Reference: 'ref' ref=[f.First];
            Include: 'include' importURI=STRING;
            """,
            global_repository=True,
        )
        mm.register_scope_providers({"*.*": scoping_providers.FQNImportURI()})
        return mm

    register_language(second_language)

    mm = metamodel_for_language("second-test-lang")

    current_dir = os.path.dirname(__file__)
    p = os.path.join(current_dir, "model.stest")
    model = mm.model_from_file(p)

    assert len(model.refs) == 2
    assert model.refs[0].ref.name == "first1"
    assert model.refs[0].ref.num == 42
