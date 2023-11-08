from os.path import abspath, dirname, join

import textx.scoping.providers as scoping_providers
from textx import (
    clear_language_registrations,
    get_children_of_type,
    metamodel_from_file,
    register_language,
)


def test_metamodel_provider_advanced_test():
    """
    Advanced test for ExtRelativeName and PlainNameGlobalRepo.

    Here we have a global model repository shared between
    different meta models.

    The meta models interact (refer to each other; one direction).
    """
    #################################
    # META MODEL DEF
    #################################
    this_folder = dirname(abspath(__file__))

    def get_meta_model(global_repo, grammar_file_name):
        mm = metamodel_from_file(join(this_folder, grammar_file_name), debug=False)
        mm.register_scope_providers(
            {
                "*.*": global_repo,
                "Ingredient.unit": scoping_providers.ExtRelativeName(
                    "type", "units", "extends"
                ),
            }
        )
        return mm

    global_repo = scoping_providers.PlainNameGlobalRepo()
    global_repo.register_models(join(this_folder, "metamodel_provider2", "*.recipe"))
    global_repo.register_models(join(this_folder, "metamodel_provider2", "*.ingredient"))

    i_mm = get_meta_model(
        global_repo, join(this_folder, "metamodel_provider2", "Ingredient.tx")
    )
    r_mm = get_meta_model(
        global_repo, join(this_folder, "metamodel_provider2", "Recipe.tx")
    )

    clear_language_registrations()
    register_language(
        "recipe-dsl",
        pattern="*.recipe",
        description="demo",
        metamodel=r_mm,  # or a factory
    )
    register_language(
        "ingredient-dsl",
        pattern="*.ingredient",
        description="demo",
        metamodel=i_mm,  # or a factory
    )

    #################################
    # MODEL PARSING
    #################################

    model_repo = global_repo.load_models_in_model_repo().all_models

    #################################
    # TEST MODEL
    #################################

    def get_all(model_repo, what):
        lst = []
        for m in model_repo:
            lst = lst + get_children_of_type(what, m)
        return lst

    lst_i = get_all(model_repo, "IngredientType")
    lst_r = get_all(model_repo, "Recipe")

    assert len(lst_i) == 2
    assert len(lst_r) == 2

    # check some references to be resolved (!=None)
    assert lst_r[0].ingredients[0].type
    assert lst_r[0].ingredients[0].unit

    #################################
    # END
    #################################
