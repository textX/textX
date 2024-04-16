# Language modularization

** This is a draft **

Currently, textX has [import
statement](http://textx.github.io/textX/grammar/#grammar-modularization)
which enables one grammar to import rules form the other one. But for some more
complex use-cases (see [issue 26](https://github.com/textX/textX/issues/26))
this is not enough.


## Modularization at the grammar/meta-model level


Motivation example (see [issue 26](https://github.com/textX/textX/issues/26)).


    type_meta_def = '''
    TypeDef: 'typedef' name=ID type=[Type];
    Type: RangeType | SimpleType;
    SimpleTypeDecl: 'type' type=SimpleType;
    SimpleType: name=ID;
    RangeTypeDecl: 'type' type=RangeType;
    RangeType: base=[SimpleType] range=Range;
    Range:  '[' from=INT (':' to=INT)? ']';
    '''

    struct_meta_def = '''
    Model: elements+=Element;
    Element: Entity | TypeDef;
    ...
    '''

    type_meta = metamodel_from_str(type_meta_def)
    struct_meta = metamodel_from_str(struct_meta_def)


###  Problem

Structural meta-model references a rule/class from the type meta-model
(`Element` references `TypeDef`).


### Possible solution

Let the meta-model inherit other meta-models

    struct_meta = metamodel_from_str(struct_meta_def, inherits=[type_meta])

All referenced but the missing rules from the struct meta-model will be
searched in types meta-model. Currently, this is supported by the
grammar import but it should be supported at the API level so that grammars
could be defined as strings. To support multiple inheritance properly
investigate C3 linearization as a solution.


### Open questions

Should we override rules inside inherited grammars? For example, if we
override `Range` to specify some different syntax or meta-class attributes,
should the new definition be used from the `Type` rule in the `type_meta_def`
grammar?  If we instantiate model using `type_meta`, original `Range` will
be used but if we instantiate `TypeDef` using `struct_meta` our redefined
`Range` will be used. These will be objects of different `Range` classes.
Do we want it to work that way? IMHO we should use one `Range` class for
all our models.


### Possible solution

Maybe it would be best to make one integral meta-model with strict rules
for meta-class resolution but provide means to define the root rule for each
model parse.

For example:
  
    meta = metamodel_from_str(struct_meta_def, inherits=[type_meta])

We get a single integral meta-model. 

Imagine that we want to redefined ranges:

    new_range = '''
      Range:  '(' low=INT ('->' high=INT)? ')';
    '''

    new_range_meta = metamodel_from_str(new_range)

Now an integral meta-model could be built with:

    meta = metamodel_from_str(struct_meta_def, inherits=[new_range_meta, type_meta])


`Range` will be resolved from the first meta-model following the C3
linearization.  That will be `new_range_meta`, thus syntax and meta-class for
`Range` will be changed in all model parsings using the `meta` meta-model.

Parsing of models:

    # type_model will, in rule RangeType, use Range from new_range_meta
    type_model = meta.model_from_str(type_def, root_rule='TypeDef')
    struct_model = meta.model_from_str(struct_def, root_rule='Model',
                                        ref_models=[type_model])

`ref_models` is an iterable of models used for object reference resolving.
Each nameable from the reference models can be used in the link rule reference
resolving.

`type_model` model parse could use redefined `Range` from the integral
meta-model `meta`, thus, `struct_model` will reference right class instances.

This idea is compatible with the current usage of `import` keyword in the
meta-model definition. The semantics of import will change to use the same C3
linearization and inheritance semantics. Probably it would be best to
change `import` keyword to `inherits`.

In addition, a new function for composing the meta-model could be introduced:

    meta = compose_metamodels(struct_meta, new_range_meta, type_meta)

To support this kind of composition, meta-model loading should not fail in the
event of missing rule references. Meta-model might be constructed in the unresolved
phase. Composing it with other meta-models might resolve it fully or
partially. Only fully resolved meta-models can be used for model parsing.


## Modularization at the model level

This could be supported by the `ref_models` iterable explained in the previous
section.

Open questions are:
 - How to handle scoping?
 - How to support independent model reloading? Motivation would be reloading of
   a model on a file change. It would be nice to reload just a single model and
   relink it. Some form of a reference tracking might be implemented.


