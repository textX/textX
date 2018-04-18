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
        "user" name=ID "uses" instance=[Instance|FQN] // Instance, FQN from other grammar
    ;

    Import: 'import' importURI=STRING;


The global MetaModelProvider class is utilized to allocate the file
extension to the corresponding meta model:

        scoping.MetaModelProvider.add_metamodel("*.components", mm_components)
        scoping.MetaModelProvider.add_metamodel("*.users", mm_users)

With this construct we can define a user model referencing a component
model:

    import "example.components"
    user pi uses usage.action1


## Use Case: referening non-textx meta-models/models

You can reference an arbitrary python object using the OBJECT rule (see:
test_reference_to_buildin_attribute.py)

    Access:
        'access' name=ID pyobj=[OBJECT] ('.' pyattr=[OBJECT])?


In this case the references objecct is a python dictionary (pyobj)
and the entry of such a dictionary (pyattr). A custom scope provider
is used to achive this mapping:

    def my_scope_provider(obj, attr, attr_ref):
        pyobj = obj.pyobj
        if attr_ref.obj_name in pyobj:
            return pyobj[attr_ref.obj_name]
        else:
            raise Exception("{} not found".format(attr_ref.obj_name))


The scope provider is linked to the "pyattr" attribute of the rule "Access":

    my_metamodel.register_scope_providers({
        "Access.pyattr": my_scope_provider,
    })


With this we can reference non textx data elements from within our language.
This can be used to, e.g., use a non-textx AST object and reference it from
a textx model.

## Conclusion

We provide a pragmatic way to define meta-models using other meta models.
Mostly, we focus on textx meta-models using other textx meta-models. But
scope providers may be used to also link a textx meta model to an arbitrary
non-textx data structure.
