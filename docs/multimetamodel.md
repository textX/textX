# Multi meta-model support

There are different ways to combine meta models: **(1)** a meta model can use
another meta model to compose its own structures (extending a meta model) or
**(2)** a meta model can reference elements from another meta model.

**Extending an existing meta model** can be realized in textX by defining a
grammar extending an existing grammar. All user classes, scope providers and
processors must be manually added to the new meta model. Such extended meta
models can also reference elements of models created with the original meta
model. Although the meta classes corresponding to inherited rules are redefined
by the extending meta model, scope providers match the object types correctly.
This is implemented by comparing the types by their name (see
textx.textx_isinstance). Simple examples: see
[tests/functional/test_scoping/test_metamodel_provider*.py](https://github.com/textX/textX/tree/master/tests/functional/test_scoping).


**Referencing elements from another meta model** can be achieved without having
the original grammar, nor any other details like scope providers, etc. Such
references can, thus, be enabled by using just a referenced language name in a
`reference` statement of referring grammar. Target language meta-model may
originate from a library installed on the system (without sources, like the
grammar). The referencing grammar can reference the types (rules) of the
referenced meta model. Rule lookup takes care of choosing the correct types.
Simple examples: see
[tests/functional/test_metamodel/test_multi_metamodel_refs.py](https://github.com/textX/textX/tree/master/tests/functional/test_metamodel/test_multi_metamodel_refs.py).

To identify a referenced grammar you need to register the grammar to be
referenced with the [registration API](registration.md).

!!! tip
    Thus, when designing a domain model (e.g., from the software test domain) to
    reference elements of another domain model (e.g., from the
    interface/communication domain), the second possibility (referencing) is
    probably a cleaner way to achieve the task than the first possibility
    (extending).


## Use Case: meta model referencing another meta model

!!! note
    The example in this section is based on the
    [tests/functional/test_metamodel/test_multi_metamodel_refs.py](https://github.com/textX/textX/tree/master/tests/functional/test_metamodel/test_multi_metamodel_refs.py).

We have two languages/grammars (grammar `A` and `B`). `grammarA` string defines
named elements of type `A`:

```nohighlight
Model: a+=A;
A:'A' name=ID;
```

`GrammarBWithImportURI` string defines named elements of type `B` referencing
elements of type `A` (from `grammarA`). This is achieved by using `reference`
statement with alias. It also allows importing other model files by using
`importURI`.

```nohighlight
reference A as a
Model: imports+=Import b+=B;
B:'B' name=ID '->' a=[a.A];
Import: 'import' importURI=STRING;
```


We now proceed by registering languages using [registration
API](registration.md):

```python
global_repo = scoping.GlobalModelRepository()
global_repo_provider = scoping_providers.PlainNameGlobalRepo()

def get_A_mm():
    mm_A = metamodel_from_str(grammarA, global_repository=global_repo)
    mm_A.register_scope_providers({"*.*": global_repo_provider})
    return mm_A

def get_BwithImport_mm():
    mm_B = metamodel_from_str(grammarBWithImport,
                              global_repository=global_repo)

    # define a default scope provider supporting the importURI feature
    mm_B.register_scope_providers(
        {"*.*": scoping_providers.FQNImportURI()})
    return mm_B

register_language('A',
                  pattern="*.a",
                  metamodel=get_A_mm)

register_language('BwithImport',
                  pattern="*.b",
                  metamodel=get_BwithImport_mm)
```

Note that we are using a global repository and `FQNImportURI` scoping provider
for `B` language to support importing of `A` models inside `B` models and
referencing its model objects.

!!! tip
    In practice we would usually register our languages using declarative
    extension points. See [the registration API docs](registration.md) for more
    information.

After the languages are registered we can access the meta-models of registered
languages using [the registration API](registration.md). Given the model in
language `A` in file `myA_model.a`:

```nohighlight
A a1 A a2 A a3
```

and model in language `B` (with support for `ImportURI`) in file `myB_model.b`:

```nohighlight
import 'myA_model.a'
B b1 -> a1 B b2 -> a2 B b3 -> a3
```

we can instantiate model `myB_model.b` like this:

```python
mm_B = metamodel_for_language('BwithImport')
model_file_name = os.path.join(os.path.dirname(__file__), 'myB_model.b')
model = mm_B.model_from_file(model_file_name)
```

In another way we could use global model repository directly to instantiate
models directly from Python code without resorting to `ImportURI` machinery. For
this we shall modify the grammar of language `B` to be:

```nohighlight
reference A
Model: b+=B;
B:'B' name=ID '->' a=[A.A];
```

Notice that we are not using the `ImportURI` functionality to load the 
referenced model here. Since both metamodels share the same global
repository, we can directly add a model object to the global_repo_provider 
(```add_model```) of language A. 
This model object will then be visible to the scope provider
of the second model and make the model object available.
We register this language as we did above. Now, the code can look like this:

```python
mm_A = metamodel_for_language('A')
mA = mm_A.model_from_str('''
A a1 A a2 A a3
''')
global_repo_provider.add_model(mA)

mm_B = metamodel_for_language('B')
mB = mm_B.model_from_str('''
B b1 -> a1 B b2 -> a2 B b3 -> a3
''')
```

See how we explicitly added model `mA` to the global repository. This enabled
model `mB` to find and resolve references to objects from `mA`.

!!! note
    It is crucial to use a scope provider which supports the global repository,
    such as the ImporUri or the GlobalRepo based providers, to allow the described
    mechanism to add a model object directly to a global repository.



## Use Case: Recipes and Ingredients with global model sharing

In this use case we define recipes (food preparation) including a list of
ingredients. The ingredients of a recipe model element are defined by:

 * a count (e.g. 100),
 * a unit (e.g. gram),
 * and an ingredient reference (e.g. sugar).

In a separate model the ingredients are defined: Here we can define multiple
units to be used for each ingerdient (e.g. `60 gram of sugar` or `1 cup of
sugar`). Moreover some ingredients may inherit features of other ingredients
(e.g. salt may have the same units as sugar).

Here, two meta models are defined to handle ingredient definitions (grammar
`Ingredient.tx` for e.g. `fruits.ingredient`) and recipes (grammar
`Recipe.tx`,for e.g. `fruit_salad.recipe`).

The [registration API](registration.md) is utilized to allocate the file
extensions to the meta models (see
[test_metamodel_provider2.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_metamodel_provider2.py)).
Importantly, a common model repository (`global_repo`) is defined to share all
model elements among both meta models:

    i_mm = get_meta_model(
        global_repo, join(this_folder, "metamodel_provider2", "Ingredient.tx"))
    r_mm = get_meta_model(
        global_repo, join(this_folder, "metamodel_provider2", "Recipe.tx"))

    clear_language_registrations()
    register_language(
        'recipe-dsl',
        pattern='*.recipe',
        description='demo',
        metamodel=r_mm
    )
    register_language(
        'ingredient-dsl',
        pattern='*.ingredient',
        description='demo',
        metamodel=i_mm
    )

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
[test_reference_to_buildin_attribute.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_reference_to_buildin_attribute.py))

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
[test_reference_to_nontextx_attribute.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_reference_to_nontextx_attribute.py) we
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
data structure. 
