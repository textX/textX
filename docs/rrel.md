# Reference resolving expression language (RREL)

RREL allows to specify scope provider (lookup) specification in the
grammar itself ([grammar example](tests/functional/test_scoping/components_model1/ComponentsRrel.tx) and 
an example [test](https://github.com/textX/textX/blob/master/tests/functional/examples/test_hierarchical_data_structures_referencing_attributes.py)).

The idea is to support all current builtin scoping providers (e.g., `FQN`,
`RelativeName` etc.; see [scoping](scoping.md)) while the user would have to
resort to Python only to support some very specific cases or referring to models
not handled by textX.

A RREL expression is written as a third part of the textX [link rule
reference](grammar.md#references).

For example:

```
Attribute: 'attr' ref=[Class:FQN|^packages*.classes] name=ID ';';
```

This grammar rule has a `ref` attribute which is a reference to the `Class`
rule. This is a link rule reference as it is enclosed inside of square brackets.
It consists of three parts where first two parts are separated by `:` while the
second and the third are separated by `|`. The first part defines the target
object type or its grammar rule. The second part defines what will parser match
at the place of the reference. It would be a fully qualified name of the target
object (thus `FQN`). The third part of the reference is RREL expression
(`^packages*.classes`). Second and third part of the reference are optional. If
second part is not given `ID` is assumed. If RREL expression is not given the
default resolver, which search the reference in the global scope, will be used.

Each reference in the model, by default, forms a dot separated name, which is
matched by the second part of the link rule reference in the grammar, where a
plain ID is just a special case. For example, a reference could be
`package1.component4` or just `component4`. We could further generalize this by
saying that a reference is a sequence of names where a plain ID is just a
sequence of length 1. It doesn't have to be dot separated. A user could provide
a custom match rule (like `FQN` in the above example) and a match processor to
convert the matched string to a sequence of names. There is also the possibility
to define the separator sequence (by default a dot), as demonstrated in
sub-section ["RREL reference name deduction"](#rrel-reference-name-deduction)
bellow. 

For reference resolving as an input we have:

- A dot separated name matched by the parser, where ID is a special case
- A RREL expression

We evaluate RREL expression using the name in the process and we yield referenced
object or an error.

## RREL operators

Reference resolving expression language (RREL) consists of several operators
(see [test](tests/functional/test_scoping/test_rrel.py)):

- `.` Dot navigation. Search for the attribute in the current AST context. Can
  be used for navigation up the parent chain, e.g. `.` is this object, `..` is
  parent, `...` is a parent of a parent. If the expression starts with a `.`
  than we have a relative path starting from the current AST context. Otherwise
  we have an absolute path starting from the root of the model unless `^` is
  used (see below). For example, `.a.b` means search for `a` attribute at the
  current level (`.`) and than search for `b` attribute. Expression `a.b` would
  search starting from the root of the model.
- `parent(TYPE)` - navigate up the parent chain until the exact type is found.
- `~` This is a marker applied to a path element to inform resolver that the
  current collection should not be searched by the current name part but that
  all elements should be processed. For example, to search for a method in the
  inheritance hierarchy one would write `~extends*.methods` which (due to `*`,
  see below) first searches `methods` collection of the current context object,
  if not found, all elements of the current `extends` collection are iterated in
  the order of defintion without consuming name part, and then name would be
  searched in the `methods` collection of each object from the `extends`
  collection. If not found `*` would expand `extends` to `extends.extends` if
  possible and the search would continue.
- `'name-value'~` The `~` operator takes an additional optional string to
  indicate that the part of the name is not consumed, but is expected to be the
  value indicated by the passed string: `'myname'~myattribute` means _follow
  attribute `myattribute`, if it is named `'myname'`_. 
  
    The following example sketches parts of a meta-model, where the lookup rules
    indicate a fallback to some `types_collection` entry with the name
    `'builtin'` (of course such an object must be present to successfully
    resolve such references, e.g., by adding a builtin model with that
    information (see [tests/test_scoping/test_rrel.py,
    test_rrel_with_fixed_string_in_navigation](https://github.com/textX/textX/blob/master/tests/functional/test_scoping/test_rrel.py)):

          Using: 'using' name=ID "=" type=[Type:ID|+m:
                ~active_types.types,                // "regular lookup"
                'builtin'~types_collection.types    // "default lookup" - name "builtin" 
                                                    // hard coded in grammar
            ];
        
- `*` - Repeat/expand. Used in expansion step to expand sub-expression by 0+
  times. First expansion tried will be 0, then once, then twice etc. For
  example, `~extends*.methods` would search in `methods` collection in the
  current context object for the current name part. If not found expansion of
  `*` would took place and we would search in `~extends.methods` by iterating
  over `extends` collection without consuming part name (due to `~`) and
  searching by ref. name part inside `methods` collection of each iterated
  object. The process would continue (i.e. `~extends.~extends.methods` ...)
  until no more expansion is possible as we reach the end of inheritance chain.
- `^` - Bottom-up search. This operator specifies that the given path should be
  expanded bottom-up, up the parent chain. The search should start at the
  current AST context and go up the parent chain for the number of components in
  the current expanded path. Then the match should be tried. See the components
  example above using `^` in `extends`. For example, `^a.b.c` would start from
  the current AST level and go to the parent of the parent, search there for
  `a`, then would search for `b` in the context of the previous AST search
  result, and finally would search for attribute `c`. `^` is a marker applied to
  path search subexpression, i.e. it doesn't apply to the whole sequence (see
  below).
- `,` - Defines a sequence, i.e. a sequence of RREL expressions which should
  tried in order.
  
Priorities from highest to lowest: `*`, `.`, `,`.

`~` and `^` are regarded as markers, not operators.

## RREL evaluation

Evaluation goes like this:

1. Expand the expression. Expand `*` starting from 0 times.
2. Match/navigate the expression (consume part names in the process)
3. Repeat

The process stops when either:

- all possibilities are exhausted and we haven't find anything -> error.
- in `*` we came to a situation where we consume all part names before we
  finished with the RREL expression -> error.
- We have consumed all path name elements, finished with RREL expression and
  found the object. If the type is not the same as the type given in the grammar
  reference we report an error, else we found our object.

## RREL reference name deduction

The name of a referenced object is transformed into a list of non-empty
name parts, which is processed by a RREL expression to navigate through the
model. Possible names are defined in the grammar, e.g. `FQN` in the
following example (used in rule `Attribute` to reference a model class:

    Model:     packages*=Package;
    Package:   'package' name=ID '{' classes*=Class '}';
    Class:     'class' name=ID '{' attributes*=Attribute '}';
    Attribute: 'attr' ref=[Class:FQN|^packages*.classes] name=ID ';';
    Comment:   /#.*/;
    FQN:       ID('.'ID)*;

The name of a reference (`Attribute.ref`) could then be,
e.g., `P1.Part1` (the package `P1` and the class `Part1`),
separated by a dot. The **dot is the default separator**
(if no other separator is specified).

    package P1 {
        class Part1 {
        }
    }
    package P2 {
        class Part2 {
            attr C2 rec;
        }
        class C2 {
            attr P1.Part1 p1;
            attr Part2 p2a;
            attr P2.Part2 p2b;
        }
    }

The match rule used to specify possible reference names (e.g., `FQN`)
can **specify a separator used to split the reference name into individual
name parts**. Use the rule parameter `split`, which must be a non-empty
string (e.g. `split='/'`; note that the match rule itself should produce
names, for which the given separator makes sense):

    Model:          packages*=Package;
    Package:        'package' name=ID '{' classes*=Class '}';
    Class:          'class' name=ID '{' attributes*=Attribute '}';
    Attribute:      'attr' ref=[Class:FQN|^packages*.classes] name=ID ';';
    Comment:        /#.*/;
    FQN[split='/']: ID('/'ID)*;  // separator split='/'

Then the RREL scope provider (using the match rule with the extra
rule parameter `split`) automatically uses the given split
character to process the name.

## RREL and multi files model

Use the prefix `+m:` for an RREL expression to activate a multi file model
scope provider. Then, in case of no match, other loaded models are searched.
When using this extra prefix the importURI feature is activated
(see [scoping](scoping.md) and
[grammar example](https://github.com/textX/textX/blob/master/tests/functional/registration/projects/data_dsl/data_dsl/Data.tx)).

## Accessing the RREL 'path' of a resolved reference

Use the prefix `+p:` for an RREL expression to access the complete
path of named elements for a resolved reference. For that, the
resolved reference is represented by a proxy which is transparent
to the user is terms of attribute access and `textx_instanceof`
semantics.

The proxy (`textx.scoping.rrel.ReferenceProxy`) provides two extra
fields: `_tx_obj` and `_tx_path`. `_tx_obj` represent the
 referenced object itself and `_tx_path` is a list with
 all named elements traversed during scope resolution. The last
 entry of the list is `_tx_obj`. 

The following model shows how to employ the `+p:` flag and
is used in the unittest referenced for the following use case:
```
Model:
    structs+=Struct
    instances+=Instance
    references+=Reference;
Struct:
    'struct' name=ID '{' vals+=Val '}';
Val:
    'val' name=ID (':' type=[Struct])?;
Instance:
    'instance' name=ID (':' type=[Struct])?;
Reference:
    'reference' ref=[Val:FQN|+p:instances.~type.vals.(~type.vals)*];
FQN: ID ('.' ID)*;
```

The **use case** for that feature is that you sometimes need
to access all model elements specified in a model reference. Consider
a reference to a hierarchically modelled data element  like in this
[unittest example](https://github.com/textX/textX/blob/master/tests/functional/examples/test_hierarchical_data_structures_referencing_attributes.py),
e.g. `reference d.c.b.a.x`:

```
struct A {
    val x
}
struct B {
    val a: A
}
struct C {
    val b: B
    val a: A
}
struct D {
    val c: C
    val b1: B
}
instance d: D
reference d.c.b.a.x
reference d.b1.a.x
```

In this example you need all referenced intermediate model elements to
accurately identify the modelled data for, e.g., code generation because
`reference d.c.b.a.x` is not distinguishable from
`reference d.b1.a.x` without the path
(both point to the field `x` in `A`).


## Using RREL from Python code

RREL expression could be used during registration in place of scoping provider.
For example:

```Python
my_meta_model.register_scope_providers({
        "*.*": scoping_providers.FQN(),
        "Connection.from_port": "from_inst.component.slots"  # RREL
        "Connection.to_port": "from_inst.component.slots"      # RREL
    })
```

## RREL processing (internal)

RREL expression are parsed when the grammar is loaded and transformed to AST
consisting of RREL operator nodes (each node could be an instance of `RREL`
prefixed class, e.g `RRELSequence`). The expressions ASTs are stateless and thus
it is an important possibility to define the same expression for multiple
attributes by using wildcard as the same expression tree would be used for the
evaluation.

In the process of evaluation the root of the expression tree is given the
sequence of part names and the current context which represent the parent object
of the reference in the model AST. The evaluation is then carried out by
recursive calls of the RREL AST nodes. Each node gets the AST context consisting
of a collection of objects from the model and a current unconsumed part names
collection, which are the result of the previous operation or, in the case of
the root expression AST node, an initial input. Each operator object should
return the next AST context and the unconsumed part of the name. At the end of
the successful search AST context should be a single object and the names parts
should be empty.
