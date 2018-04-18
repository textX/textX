# Multi meta-model support

As a feature of some [scope providers](scoping.md),
there is the possibility to define a file extension based allocation of
model files to meta models. This global data is stored in the class
"textx.scoping.MetaModelProvider": Here, you can register meta models
associated to files patterns. Thus, you can control which meta model to use
when loading a file in a scope provider using the "ImportURI"-feature (e.g.,
FQNImportURI) or with global scope providers (e.g., PlainNameGlobalRepo).
If no file pattern matches, the meta model of the current model
is utilized.

Simple examples see tests/test_scoping/test_metamodel_provider*.py.

## Use Case: Recipes and Ingredients with global model sharing
In this use case we define recipes (food preparation) including a list of
ingredients. The ingredients of a recipe model element are defined by

 * a count (e.g. 100),
 * a unit (e.g. gram),
 * and an ingredient reference (e.g. sugar).

In a separate model the ingredients are defined: Here we can define multiple
units to be used for that ingerdient (e.g. "60 gram of sugar" or
"1 cup of sugar").
Moreover some ingredients may inherit feature of the ingredients (e.g.
salt may have the same units as sugar).

Here, two meta models are defined to handle ingredient definitions
(e.g. fruits.ingredient) and recipes (e.g. fruit_salad.recipe).

The MetaModelProvider is utilized to allocate the file extensions to
the meta models (see test_metamodel_provider2.py). Importantly, a common
model repository (global_repo) is defined to share all model elements
among both meta models:

    i_mm = get_meta_model(
        global_repo, this_folder + "/metamodel_provider2/Ingredient.tx")
    r_mm = get_meta_model(
        global_repo, this_folder + "/metamodel_provider2/Recipe.tx")

    scoping.MetaModelProvider.add_metamodel("*.recipe", r_mm)
    scoping.MetaModelProvider.add_metamodel("*.ingredient", i_mm)


## Use Case: meta model sharing with the ImportURI-feature
In this use case we have a given meta model to define components and instances
of components. A second model is added to define users to use instances of
such components defned in the first model.


The grammar for the user meta model is given as follows (including the
ability to import a component model file).

    import Components

    Model:
        imports+=Import+
        users+=User+
    ;

    User:
        "user" name=ID "uses" instance=[Instance|FQN]
    ;

    Import: 'import' importURI=STRING;


The MetaModelProvider utilized to allocate the file extension to the
corresponding meta model:

        scoping.MetaModelProvider.add_metamodel("*.components", mm_components)
        scoping.MetaModelProvider.add_metamodel("*.users", mm_users)

With this construct we can define a user model referencing a component
model:

    import "example.components"
    user pi uses usage.action1

## Concluding
