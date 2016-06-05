# Modularization

** This is a draft **

Currently, textX has [import
statement](http://igordejanovic.net/textX/grammar/#grammar-modularization)
which enables one grammar to import rules form the other. But for some more
complex use-cases (see [issue 26](https://github.com/igordejanovic/textX/issues/26))
it is not enough.


# Modularization at the grammar/meta-model level


For motivation see [issue #33]()


    type_meta_def = '''
    Range:  '[' from=INT ':' to=INT ']';
    Type: 'type' base=ID range=Range;
    TypeDef: 'typedef' name=ID type=Type;
    '''

    struct_meta_def = '''
    Model: elements+=Element;
    Element: Entity | TypeDef;
    ...
    '''

    type_meta = metamodel_from_str(type_meta_def)
    struct_meta = metamodel_from_str(struct_meta_def)

  * **Problem 1:**
    Structural meta-model references rule/class from the type meta-model
    (`TypeDef`).

    **Possible solution:**
    Let meta-model inherits other meta-models

        struct_meta = metamodel_from_str(struct_meta_def, inherits=[type_meta])

    All missing rules from the struct meta-model will be searched for in types
    meta-model. Currently, this is supported by the grammar import but it should
    be supported at the API level so that grammars could be defined as strings.

    *Open questions*
    Should we override rules inside inherited grammars? For example, if we
    override `Range` to specify some different syntax or meta-class attributes,
    should new definition be used from the `Type` rule in the `type_meta_def`
    grammar?  If we instantiate model using `type_meta`, original `Range` will
    be used but if we instantiate `TypeDef` using `struct_meta` our redefined
    `Range` will be used. These will be objects of a different `Range` classes.
    Do we want it to work that way? IMHO we should use one `Range` class for
    all our models.

    **Possible solution:**
    Maybe it would be best to make one integral meta-model with a strict rules
    for meta-class resolution but provide a means to define root rule for each
    model parse.

    For example:
      
        meta = metamodel_from_str(type_meta_def, struct_meta_def)

    or maybe:

        meta = metamodel_from_str(struct_meta_def, include=[type_meta_def])

    We get a single integral meta-model. Rules from meta-models that come later
    (in the first case) override existing rules with the same name.

    Parsing of model:

        type_model = meta.model_from_str(type_def, root_rule='TypeDef')
        struct_model = meta.model_from_str(struct_def, root_rule='Model',
                                           ref_models=[type_model])

    `ref_models` is an iterable of models used for object reference resolving.


# Modularization at the model level

* Models can be loaded independently using one of the meta-models.

* Model object can reference objects in other models. The meta-class must
  be of the proper kind which is defined by a [link rule reference]().


