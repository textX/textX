# textX Scoping


## Motivation and Introduction to Scoping

Assume a grammar with references as in the following example (grammar snippet).

    MyAttribute:
            ref=[MyInterface|FQN] name=ID ';'
    ;

The scope provider is responsible for the reference resolution of such a
reference.

The default behavior (default scope provider) is looking for the referenced name
globally. Other scope providers will take namespaces into account, support
references to parts of the model stored in different files or even models
defined by other metamodels (imported into the current metamodel). Moreover,
scope providers exist allowing to reference model elements relative to other
referenced model elements: This can be a referenced method defined in a
referenced class of an instance (with a meta-model defining classes, methods and
instances of classes).


## Usage

The scope providers are registered to the metamodel and can be bound to specific
parts of rules:

 * e.g., `my_meta_model.register_scope_providers({"*.*": scoping.providers.FQN()})`
 * or: `my_meta_model.register_scope_providers({"MyAttribute.ref": scoping.providers.FQN()})`
 * or: `my_meta_model.register_scope_providers({"*.ref": scoping.providers.FQN()})`
 * or: `my_meta_model.register_scope_providers({"MyAttribute.*": scoping.providers.FQN()})`

Example (from [tests/test_scoping/test_local_scope.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_local_scope.py)):

    # Grammar snippet (Components.tx)
    Component:
        'component' name=ID ('extends' extends+=[Component|FQN][','])? '{'
            slots*=Slot
        '}'
    ;
    Slot: SlotIn|SlotOut;
    # ...
    Instance:
        'instance' name=ID ':' component=[Component|FQN] ;
    Connection:
        'connect'
          from_inst=[Instance|ID] '.' from_port=[SlotOut|ID]
        'to'
          to_inst=[Instance|ID] '.' to_port=[SlotIn|ID]
    ;

    # Python snippet
    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/components_model1/Components.tx')
    my_meta_model.register_scope_providers({
        "*.*": scoping_providers.FQN(),
        "Connection.from_port": scoping_providers.RelativeName("from_inst.component.slots"),
        "Connection.to_port": scoping_providers.RelativeName("to_inst.component.slots"),
    })


This example selects the fully qualified name provider as default provider
(`"*.*"`). Moreover, for special attributes of a `Connection` a relative name
lookup is specified: Here the `path` from the rule `Connection` containing the
attribute of interest (e.g. `Connection.from_port`) to the referenced element is
specified (the slot contained in `from_inst.component.slots`). Since this
attribute is a list, the list is searched to find the referenced name.

!!! note
    Special rule selections (e.g., `Connection.from_port`) are preferred
    to wildcard selection (e.e, `"*.*"`).


### Scope Providers defined in Module "textx.scoping.providers"

We provide some standard scope providers:

 * `textx.scoping.providers.PlainName`: This is the **default provider** of
   textX.
 * `textx.scoping.providers.FQN`: This is a **provider similar to Java or Xtext
   name loopup**.
   Example: see [tests/test_scoping/test_full_qualified_name.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_full_qualified_name.py).
 * `textx.scoping.providers.ImportURI`: This a provider which **allows to load
   additional modules** for lookup.
   You need to define a rule with an attribute `importURI` as string (like in
   Xtext). This string is then used to load other models. Moreover, you need
   to provide another scope provider to manage the concrete lookup, e.g., the
   `scope_provider_plain_names` or the `scope_provider_fully_qualified_names`.
   Model objects formed by the rules with an `importURI` attribute get an
   additional attribute `_tx_loaded_models` which is a list of the loaded
   models by this rule instance.
   Example: see [tests/test_scoping/test_import_module.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_import_module.py).
    - `FQNImportURI` (decorated scope provider)
    - `PlainNameImportURI` (decorated scope provider)

   You can use ***globbing*** (import "*.data") with the ImportURI feature.
   This is implemented via the python "glob" module. Arguments can be passed to
   the glob.glob function (glob_args), e.g., to enable recursive globbing.
   Alternatively, you can also specify a list of ***search directories***.
   In this case globbing is not allowed and is disabled (reason: it is
   unclear if the user wants to glob over all search path entries or to stop
   after the first match).
   Example: see [tests/test_scoping/test_import_module_search_path_issue66.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_import_module_search_path_issue66.py).
 * `textx.scoping.providers.GlobalRepo`: This is a provider where **you initially
   need to specifiy the model files to be loaded and used for lookup**. Like
   for `ImportURI` you need to provide another scope provider for the concrete
   lookup.
   Example: see [tests/test_scoping/test_global_import_modules.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_global_import_modules.py).
    - `textx.scoping.providers.FQNGlobalRepo` (decorated scope provider)
    - `textx.scoping.providers.PlainNameGlobalRepo` (decorated scope provider)
 * `textx.scoping.providers.RelativeName`: This is a scope provider to **resolve
   relative lookups**: e.g., model-methods of a model-instance, defined by the
   class associated with the model-instance. Typically, another reference (the
   reference to the model-class of a model-instance) is used to determine the
   concrete referenced object (e.g. the model-method, owned by a model-class).
   Example: see [tests/test_scoping/test_local_scope.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_local_scope.py).

   The RelativeName scope provider expects a **path through your model as string**
   to resolve a given reference text (ref_name): the path "a.b.c" denotes 
   the path, starting form your current rule_object and yields
   rule_object.a.b.c (this means, rule_object must have an attribute a, which 
   in turn has an attribute b, and so on...). 
   The **last element of your path** must either be a **named
   object**, corresponding to your reference text (ref_name), or a **list of named
   objects** containing the named object to be resolved.

        grammar = '''
            Model:        kinds += GroupKind values += Ref;
            LiteralKind : name=ID;
            GroupKind:    kindName=ID name=ID "{"
                            vars *= LiteralKind
                          "}";
            Ref: ref0=[GroupKind] '.' ref1=[LiteralKind];
        '''
        mm = textx.metamodel_from_str(grammar)
        scope = textx.scoping.providers.RelativeName("ref0.vars")
        mm.register_scope_providers({"Ref.ref1": scope})

   
   Of course, you can use "parent" as part of your path string (but no indices
   or similar). The only special attribute is "parent(Type)", which follows
   the parent relationship until a given type is found. 

        grammar = '''
            Model:        kinds += GroupKind values+=Formula;
            LiteralKind : name=ID;
            GroupKind:    kindName=ID name=ID "{"
                            vars *= LiteralKind
                          "}";
            Formula:      formula=FormulaPlus;
            FormulaPlus:  sum+=FormulaMult['+'];
            FormulaMult:  mul+=FormulaVal['*'];
            FormulaVal:   (ref=Ref)|(val=NUMBER)|('(' rec=FormulaPlus ')');
            Ref: ref0=[GroupKind] '.' ref1=[LiteralKind];
        '''
        mm = textx.metamodel_from_str(grammar)
        mm.register_scope_providers({
            "Ref.ref0": RelativeName("parent(Model).kinds"),
            "Ref.ref1": RelativeName("ref0.vars")
            })


 * `textx.scoping.providers.ExtRelativeName`: The same as `RelativeName` **allowing
   to model inheritance or chained lookups**.
   Example: see [tests/test_scoping/test_local_scope.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_local_scope.py).


### Note on Uniqueness of Model Elements

Two different models created using one single meta model (not using a scope
provider like `GlobalRepo`, but by directly loading the models from file) have
different instances of the same model elements. If you need two such models to
share their model element instances, you can specify this, while creating the
meta model (`global_repository=True`). Then, the meta model will store an own
instance of a `GlobalModelRepository` as a base for all loaded models.

Model elements in models including other parts of the model (possibly circular)
have unique model elements (no double instances).

Examples see [tests/test_scoping/test_import_module.py](https://github.com/igordejanovic/textX/blob/master/tests/functional/test_scoping/test_import_module.py).


## Technical aspects and implementation details

The scope providers are python callables accepting `obj, attr, obj_ref`:

 * `obj`     : the object representing the start of the search (e.g., a rule
             (e.g. `MyAttribute` in the example above, or the model)
 * `attr`    : a reference to the attribute `ref`
 * `obj_ref` : a `textx.model.ObjCrossRef` - the reference to be resolved

The scope provider return the referenced object (e.g. a `MyInterface` object in
the example illustrated in the `Motivation and Introduction` above (or `None` if
nothing is found; or a `Postponed` object, see below).

The scope provider is responsible to check the type and throw a
TextXSemanticError if the type is not ok.

Scope providers shall be stateless or have unmodifiable state after
construction: this means they should allow to be reused for different models
(created using the same meta-model) without interacting with each other. This
means, they must save their state in the corresponding model, if they need to
store data (e.g., if they load additional models from files *during name
resolution*, they are not allowed to store them inside the scope provider.

Models with references being resolved have a temporary attribute
`_tx_reference_resolver` of type `ReferenceResolver`. This object can be used to
resolve the object. It contains information, such as the parser in charge for
the model (file) being processed.

!!! note
    Scope providers as normal functions (`def <name>(...):...`), not
    accessing global data, are safe per se. The reason to be stateless, is that
    no side effects (beside, e.g., loading other models) should influence the
    name lookup.

The state of model resolution should mainly consist of models already loaded.
These models are stored in a `GlobalModelRepository` class. This class (if
required) is stored in the model. An included model loaded from another
including model "inherits" the part of the `GlobalModelRepository` representing
all loaded models. This is done to (a) cache already loaded models and (b)
guarantee, that every referenced model element is instantiated exactly once.
Even in the case of circular inclusions.

Scope providers may return an object of type `Postponed`, if they depend on
another event to happen first. This event is typically the resolution of another
reference. The resolution process will repeat multiple times over all unresolved
references to be resolved until all references are resolved or no progress
regarding the resolution is observed. In the latter case an error is raised. The
control flow responsibility of the resolution process is allocated to the
`model.py` module.
