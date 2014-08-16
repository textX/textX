textX
=====

Meta-language in [Arpeggio](https://github.com/igordejanovic/Arpeggio) inspired by [Xtext](http://www.eclipse.org/Xtext/)

textX follows closely the syntax and semantics of Xtext but differs in some places and is implemented 100% in Python using Arpeggio parser. It is fully dynamic - no code generation at all!

Installation
------------

```
pip install textX
```

Quick start
-----------

There is no docs at the moment but here is a quick introduction what can be done. For more see examples.

1. Write a language description in textX (file `hello.tx`):

  ```
  HelloWorldModel:
    'hello'  to_greet+={Who ','}
  ;

  Who:
    name = /[^,]*/
  ;
  ```

  Description consists of a set of parsing rules which at the same time describe Python classes that
  will be used to instantiate object of your model.

2. Create meta-model from textX language description:

  ```python
  from textx.metamodel import metamodel_from_file
  hello_meta = metamodel_from_file('hello.tx')
  ```

3. Optionally export meta-model to dot (visualize your language abstract syntax):

  ```python
  from textx.export import metamodel_export
  metamodel_export(hello_meta, 'hello_meta.dot')
  ```

  ![hello_meta.dot](https://raw.githubusercontent.com/igordejanovic/textX/master/examples/hello_world/hello_meta.dot.png)

  You can see that for each rule from language description an appropriate Python class has been created.

2. Create some content (i.e. model) in your new language (`example.hello`):

  ```
  hello World, Solar System, Universe
  ```

  Your language syntax is also described by the language rule from step 1.

5. Use meta-model to create models from textual description:

  ```python
  example_hello_model = hello_meta.model_from_file('example.hello')
  ```

  You get plain Python object graph. Object classes are those defined by the meta-model.

6. Optionally export model to dot to visualize it:

  ```python
  from textx.export import model_export
  model_export(example_hello_model, 'example.dot')
  ``` 

  ![example.dot](https://raw.githubusercontent.com/igordejanovic/textX/master/examples/hello_world/example.dot.png)

  This is an object graph.

7. Use your model: interpret it, generate code ... It is a plain Python graph of objects with plain attributes.




