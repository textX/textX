# Multi meta-model support

There are different ways to combine meta models: **(1)** a meta model can use
another meta model to compose its own structures (extending a meta model) or
**(2)** a meta model can reference elements from another meta model. 
**(3)** Moreover, we also demonstrate, that we can combine textX metamodels 
with arbitrary non-textX metamodels/models available in python.

**(1) Extending an existing meta model** can be realized in textX by defining a
grammar extending an existing grammar. All user classes, scope providers and
processors must be manually added to the new meta model. Such extended meta
models can also reference elements of models created with the original meta
model. Although the meta classes corresponding to inherited rules are redefined
by the extending meta model, scope providers match the object types correctly.
This is implemented by comparing the types by their name (see
textx.textx_isinstance). Simple examples: see
[tests/functional/test_scoping/test_metamodel_provider*.py](https://github.com/textX/textX/tree/master/tests/functional/test_scoping).


**(2) Referencing elements from another meta model** can be achieved without having
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

```admonish tip
When designing a domain model (e.g., from the software test domain) to reference
elements of another domain model (e.g., from the interface/communication
domain), the second possibility (see **(2)** **referencing**) is probably a
**cleaner way** to achieve the task than the first possibility (see **(1)**
extending).
```

```admonish
A full example project that shows how multi-meta-modeling feature can be used is
also available in [a separate git
repository](https://github.com/textX/textx-multi-metamodel-example).
```


## Use Case: meta model referencing another meta model

```admonish
The example in this section is based on the
[tests/functional/test_metamodel/test_multi_metamodel_refs.py](https://github.com/textX/textX/tree/master/tests/functional/test_metamodel/test_multi_metamodel_refs.py).
```

We have two languages/grammars (grammar `A` and `B`). `grammarA` string defines
named elements of type `A`:

```textx
Model: a+=A;
A:'A' name=ID;
```

`GrammarBWithImportURI` string defines named elements of type `B` referencing
elements of type `A` (from `grammarA`). This is achieved by using `reference`
statement with alias. It also allows importing other model files by using
`importURI`.

```textx
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

```admonish tip
In practice we would usually register our languages using declarative extension
points. See [the registration API docs](registration.md) for more information.
```

After the languages are registered we can access the meta-models of registered
languages using [the registration API](registration.md). Given the model in
language `A` in file `myA_model.a`:

```
A a1 A a2 A a3
```

and model in language `B` (with support for `ImportURI`) in file `myB_model.b`:

```
import 'myA_model.a'
B b1 -> a1 B b2 -> a2 B b3 -> a3
```

we can instantiate model `myB_model.b` like this:

```python
mm_B = metamodel_for_language('BwithImport')
model_file_name = os.path.join(os.path.dirname(__file__), 'myB_model.b')
model = mm_B.model_from_file(model_file_name)
```

In another way we could use a global model repository directly to instantiate
models directly from Python code without resorting to `ImportURI` machinery.
For this we shall modify the grammar of language `B` to be:

```textx
reference A
Model: b+=B;
B:'B' name=ID '->' a=[A.A];
```

Notice that we are not using the `ImportURI` functionality to load the
referenced model here. Since both meta-models share the same global repository,
we can directly add a model object to the `global_repo_provider` (`add_model`)
of language A. This model object will then be visible to the scope provider of
the second model and make the model object available. We register this language
as we did above. Now, the code can look like this:

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

```admonish
It is crucial to use a scope provider which supports the global repository, such
as the `ImporUri` or the `GlobalRepo` based providers, to allow the described
mechanism to add a model object directly to a global repository.
```


## Use Case: Recipes and Ingredients with global model sharing

```admonish
The example in this section is based on the
[test_metamodel_provider2.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_metamodel_provider2.py).
```

In this use case we define recipes (food preparation) including a list of
ingredients. The ingredients of a recipe model element are defined by:

 * a count (e.g. 100),
 * a unit (e.g. gram),
 * and an ingredient reference (e.g. sugar).

In a separate model the ingredients are defined: Here we can define multiple
units to be used for each ingerdient (e.g. `60 gram of sugar` or 
`1 cup of sugar`). Moreover some ingredients may inherit features of other ingredients
(e.g. salt may have the same units as sugar).

Here, two meta-models are defined: 

 - `Ingredient.tx`, to handle ingredient definitions (e.g. `fruits.ingredient`
   model) and
 - `Recipe.tx`, for recipe definitions (e.g. `fruit_salad.recipe` model).

The [registration API](registration.md) is utilized to bind the file extensions
to the meta-models (see
[test_metamodel_provider2.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_metamodel_provider2.py)).
Importantly, a common model repository (`global_repo`) is defined to share all
model elements among both meta models:

```python
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
```

```admonish tip
In practice we would usually register our languages using declarative extension
points. See [the registration API docs](registration.md) for more information.
```


## Use Case: meta model sharing with the ImportURI-feature

```admonish
The example in this section is based on the
[test_metamodel_provider.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_metamodel_provider.py).
```

In this use case we have a given meta-model to define components and instances
of components. A second model is added to define users which use instances of
components defined in the first model.


The grammar for the user meta-model is given as follows (including the ability
to import a component model file).

```
import Components

Model:
    imports+=Import
    users+=User
;

User:
    "user" name=ID "uses" instance=[Instance:FQN] // Instance, FQN from other grammar
;

Import: 'import' importURI=STRING;
```

The [registration API](registration.md) is utilized to bind a file extension to
the corresponding meta-model:

    register_language(
        'components-dsl',
        pattern='*.components',
        description='demo',
        metamodel=mm_components  # or a factory
    )
    register_language(
        'users-dsl',
        pattern='*.users',
        description='demo',
        metamodel=mm_users  # or a factory
    )

With this construct we can define a user model referencing a component model:

```
import "example.components"
user pi uses usage.action1
```

```admonish tip
In practice we would usually register our languages using declarative extension
points. See [the registration API docs](registration.md) for more information.
```


## Use Case: referencing non-textX meta-models/models

```admonish
The example in this section is based on the
[test_reference_to_buildin_attribute.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_reference_to_buildin_attribute.py).
```


You can reference an arbitrary python object using the `OBJECT` rule (see:
[test_reference_to_buildin_attribute.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_reference_to_buildin_attribute.py))

```textx
Access:
    'access' name=ID pyobj=[OBJECT] ('.' pyattr=[OBJECT])?
```

In this case the referenced object will be a python dictionary referenced by
`pyobj` and the entry of such a dictionary will be referenced by `pyattr`. An
example model will look like:

```
access AccessName1 foreign_model.name_of_entry
```

`foreign_model` in this case is a plain Python dictionary provided as a [custom
built-in](metamodel.md#built-in-objects) and registered during meta-model
construction:

```python
foreign_model = {
    "name": "Test",
    "value": 3
}
my_metamodel = metamodel_from_str(metamodel_str,
                                  builtins={
                                      'foreign_model': foreign_model})
```

A custom scope provider is used to achieve mapping of `pyobj/pyattr` to the
entry in the `foreign_model` dict:

```python
def my_scope_provider(obj, attr, attr_ref):
    pyobj = obj.pyobj
    if attr_ref.obj_name in pyobj:
        return pyobj[attr_ref.obj_name]
    else:
        raise Exception("{} not found".format(attr_ref.obj_name))
```

The scope provider is linked to the `pyattr` attribute of the rule `Access`:

```python
my_metamodel.register_scope_providers({
    "Access.pyattr": my_scope_provider,
})
```


With this, we can reference non-texX data elements from within our language.
This can be used to, e.g., use a non-textX AST object and reference it from a
textX model.


## Use Case: referencing non-textX meta-models/models with a json file

```admonish
The example in this section is based on the
[test_reference_to_nontextx_attribute.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_reference_to_nontextx_attribute.py).
```

In
[test_reference_to_nontextx_attribute.py](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_reference_to_nontextx_attribute.py)
we also demonstrate how such an external model can be loaded with our own
language (using a json file as external model).

We want to access elements of JSON file from our model like this:

```
import "test_reference_to_nontextx_attribute/othermodel.json" as data
access A1 data.name
access A2 data.gender
```

Where the json file `othermodel.json` consists of:

```
{
  "name": "pierre",
  "gender": "male"
}
```
    
We start with the following meta-model:

```textx
Model:
    imports+=Json
    access+=Access
;
Access:
    'access' name=ID pyobj=[Json] '.' pyattr=[OBJECT]?
;

Json: 'import' filename=STRING 'as' name=ID;
Comment: /\/\/.*$/;

```

Now when resolving `pyobj/pyattr` combo of the `Access` rule we want to search
in the imported JSON file. To achieve this we will write and register a scope
provider that will load the referenced JSON file first time it is accessed and
that lookup for the `pyattr` key in that file:

```python
def generic_scope_provider(obj, attr, attr_ref):
    if not obj.pyobj:
        from textx.scoping import Postponed
        return Postponed()
    if not hasattr(obj.pyobj, "data"):
        import json
        obj.pyobj.data = json.load(open(
            join(abspath(dirname(__file__)), obj.pyobj.filename)))
    if attr_ref.obj_name in obj.pyobj.data:
        return obj.pyobj.data[attr_ref.obj_name]
    else:
        raise Exception("{} not found".format(attr_ref.obj_name))

# create meta model
my_metamodel = metamodel_from_str(metamodel_str)
my_metamodel.register_scope_providers({
    "Access.pyattr": generic_scope_provider,
})
```


## Conclusion

We provide a pragmatic way to define meta-models that use other meta-models.
Mostly, we focus on textX meta-models using other textX meta-models. But scope
providers may be used to also link a textX meta model to an arbitrary non-textX
data structure. 
