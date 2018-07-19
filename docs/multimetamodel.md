# Multi meta-model support

As a feature of some [scope providers](scoping.md), there is the possibility to
define a file extension based allocation of model files to meta models. This
global data is stored in the class `textx.scoping.MetaModelProvider`: Here, you
can register meta models associated to files patterns. Thus, you can control
which meta model to use when loading a file in a scope provider using the
`ImportURI`-feature (e.g., `FQNImportURI`) or with global scope providers (e.g.,
`PlainNameGlobalRepo`). If no file pattern matches, the meta model of the current
model is utilized.


There are different ways to combine meta models: **(1)** a meta model can use 
another meta model to compose its own structures (extending a meta model) 
or **(2)** a meta model can reference elements from another meta model.

**Extending an existing meta model** can be realized in TextX by defining 
a grammar extending an existing grammar. All user classes, scope providers 
and processors must be manually added to the new meta model. Such extended 
meta models can also reference elements of models created with the original 
meta model. Although the meta classes corresponding to inherited rules are 
redefined by the extending meta model, scope providers match the object 
types correctly. This is implemented by comparing the types by their name 
(see textx.scoping.tool.textx_isinstance). Simple examples: see 
[tests/test_scoping/test_metamodel_provider*.py](https://github.com/igordejanovic/textX/tree/master/tests/functional/test_scoping).


**Referencing elements from another meta model** can be achieved without 
having the original grammar, nor any other details like scope providers, etc. 
Such references can, thus, be enabled while having access only to the 
meta model object of the meta model to be referenced. This object may 
originate from a library installed on the system (without sources, like 
the grammar). The meta model to be referenced is passed to the referencing 
meta model while constructing it. The referencing grammar can then reference 
the types (rules) of the referenced meta model. Rule lookup takes care of 
choosing the correct types. Simple examples: see 
[tests/test_metamodel/test_multi_metamodel_refs.py](https://github.com/igordejanovic/textX/tree/master/tests/test_metamodel/test_multi_metamodel_refs.py).


Thus, when designing a domain model (e.g., from the software test domain) to 
reference elements of another domain model (e.g., from the 
interface/communication domain), the second possibility (referencing) 
is probably a cleaner way to achieve the task than the first possibility 
(extending).


## Use Case: meta model referencing another meta model

We have two grammars (grammar A nd B). "grammarA" defines named elements of 
type A:

    Model: a+=A;
    A:'A' name=ID;

"GrammarBWithImportURI" defines named elements of type B referencing elements
of type A (from "grammarA"). It also allows importing other model files.

    Model: imports+=Import b+=B;
    B:'B' name=ID '->' a=[A];
    Import: 'import' importURI=STRING;


In our case B models may include A models, but A models cannot include B
models. This, there is no need to have a shared repository between both meta 
models. A global repository within each meta model is enough 
(global_repository=True). Here, we create two meta models, where
the second meta model allows referencing the first one
(**referenced_metamodels=[mm_A]**).

    mm_A = metamodel_from_str(grammarA, global_repository=True)
    mm_B = metamodel_from_str(grammarBWithImport, global_repository=True,
                              referenced_metamodels=[mm_A])

Then we define a default scope provider supporting the importURI-feature:

    mm_B.register_scope_providers({"*.*": scoping_providers.FQNImportURI()})

and we map file endings to the meta models:

    scoping.MetaModelProvider.add_metamodel("*.a", mm_A)
    scoping.MetaModelProvider.add_metamodel("*.b", mm_B)

Full example: see 
[tests/test_metamodel/test_multi_metamodel_refs.py](https://github.com/igordejanovic/textX/tree/master/tests/test_metamodel/test_multi_metamodel_refs.py).


## Use Case: Recipes and Ingredients with global model sharing

In this use case we define recipes (food preparation) including a list of
ingredients. The ingredients of a recipe model element are defined by

 * a count (e.g. 100),
 * a unit (e.g. gram),
 * and an ingredient reference (e.g. sugar).

In a separate model the ingredients are defined: Here we can define multiple
units to be used for each ingerdient (e.g. `60 gram of sugar` or `1 cup of
sugar`). Moreover some ingredients may inherit features of other ingredients
(e.g. salt may have the same units as sugar).

Here, two meta models are defined to handle ingredient definitions (e.g.
`fruits.ingredient`) and recipes (e.g. `fruit_salad.recipe`).

The `MetaModelProvider` is utilized to allocate the file extensions to the meta
models
(see
[test_metamodel_provider2.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_metamodel_provider2.py)).
Importantly, a common model repository (`global_repo`) is defined to share all
model elements among both meta models:

    i_mm = get_meta_model(
        global_repo, this_folder + "/metamodel_provider2/Ingredient.tx")
    r_mm = get_meta_model(
        global_repo, this_folder + "/metamodel_provider2/Recipe.tx")

    scoping.MetaModelProvider.add_metamodel("*.recipe", r_mm)
    scoping.MetaModelProvider.add_metamodel("*.ingredient", i_mm)


## Use Case: meta model sharing with the ImportURI-feature

In this use case we have a given meta model to define components and instances
of components. A second model is added to define users to use instances of such
components defned in the first model.


The grammar for the user meta-model is given as follows (including the ability
to import a component model file).

    import Components

    Model:
        imports+=Import
        users+=User
    ;

    User:
        "user" name=ID "uses" instance=[Instance|FQN] // Instance, FQN from other grammar
    ;

    Import: 'import' importURI=STRING;


The global `MetaModelProvider` class is utilized to allocate the file extension to
the corresponding meta model:

        scoping.MetaModelProvider.add_metamodel("*.components", mm_components)
        scoping.MetaModelProvider.add_metamodel("*.users", mm_users)

With this construct we can define a user model referencing a component model:

    import "example.components"
    user pi uses usage.action1


## Use Case: referencing non-textx meta-models/models

You can reference an arbitrary python object using the `OBJECT` rule (see:
[test_reference_to_buildin_attribute.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_reference_to_buildin_attribute.py))

    Access:
        'access' name=ID pyobj=[OBJECT] ('.' pyattr=[OBJECT])?


In this case the referenced object is a python dictionary (`pyobj`) and the
entry of such a dictionary (`pyattr`). An example model will look like:

    access AccessName1 foreign_model.name_of_entry


A custom scope provider is used to achieve this mapping:

    def my_scope_provider(obj, attr, attr_ref):
        pyobj = obj.pyobj
        if attr_ref.obj_name in pyobj:
            return pyobj[attr_ref.obj_name]
        else:
            raise Exception("{} not found".format(attr_ref.obj_name))


The scope provider is linked to the `pyattr` attribute of the rule `Access`:

    my_metamodel.register_scope_providers({
        "Access.pyattr": my_scope_provider,
    })


With this, we can reference non-textx data elements from within our language.
This can be used to, e.g., use a non-textx AST object and reference it from a
textx model.


### Referencing non-textx meta-models/models with a json file

In
[test_reference_to_nontextx_attribute.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_reference_to_nontextx_attribute.py) we
also demonstrate how such an external model can be loaded with our own language
(using a json file as external model).

    import "test_reference_to_nontextx_attribute/othermodel.json" as data
    access A1 data.name
    access A2 data.gender

Where the json file `othermodel.json` consists of:

    {
      "name": "pierre",
      "gender": "male"
    }


## Conclusion

We provide a pragmatic way to define meta-models using other meta models.
Mostly, we focus on textx meta-models using other textx meta-models. But scope
providers may be used to also link a textx meta model to an arbitrary non-textx
data structure (see
[test_reference_to_nontextx_attribute.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_reference_to_nontextx_attribute.py)). 
