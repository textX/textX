from os.path import abspath, dirname, join

from pytest import raises

import textx.scoping.providers as scoping_providers
from textx import (
    clear_language_registrations,
    get_location,
    metamodel_from_file,
    register_language,
)


def test_exception_from_included_model():
    """
    This test checks that an error induced by an included model
    (thrown via an object processor) is (a) thrown and (b) indicates the
    correct model location (file, line and col).
    """
    #################################
    # META MODEL DEF
    #################################
    this_folder = dirname(abspath(__file__))

    def get_meta_model(provider, grammar_file_name):
        mm = metamodel_from_file(join(this_folder, grammar_file_name), debug=False)
        mm.register_scope_providers(
            {
                "*.*": provider,
                "Call.method": scoping_providers.ExtRelativeName(
                    "obj.ref", "methods", "extends"
                ),
            }
        )

        def my_processor(m):
            from textx.exceptions import TextXSemanticError

            if m.name == "d1":
                raise TextXSemanticError("d1 triggers artifical error", **get_location(m))

        mm.register_obj_processors({"Method": my_processor})
        return mm

    import_lookup_provider = scoping_providers.FQNImportURI()

    a_mm = get_meta_model(
        import_lookup_provider, join(this_folder, "metamodel_provider3", "A.tx")
    )
    b_mm = get_meta_model(
        import_lookup_provider, join(this_folder, "metamodel_provider3", "B.tx")
    )
    c_mm = get_meta_model(
        import_lookup_provider, join(this_folder, "metamodel_provider3", "C.tx")
    )

    clear_language_registrations()
    register_language("a-dsl", pattern="*.a", description="Test Lang A", metamodel=a_mm)
    register_language("b-dsl", pattern="*.b", description="Test Lang B", metamodel=b_mm)
    register_language("c-dsl", pattern="*.c", description="Test Lang C", metamodel=c_mm)

    #################################
    # MODEL PARSING / TEST
    #################################
    import textx.exceptions

    with raises(
        textx.exceptions.TextXSemanticError,
        match=r".*model_d\.b:5:3:.*d1 triggers artifical error",
    ) as excinfo:
        a_mm.model_from_file(
            join(this_folder, "metamodel_provider3", "inheritance2", "model_a.a")
        )

    assert excinfo.value.line == 5
    assert excinfo.value.col == 3
    assert excinfo.value.nchar == 9

    #################################
    # END
    #################################
    clear_language_registrations()
