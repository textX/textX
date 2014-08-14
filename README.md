textX
=====

Meta-language in Arpeggio inspired by Xtext

textX follows closely the syntax and semantics of [Xtext](http://www.eclipse.org/Xtext/) but differs in some places and is implemented 100% in Python using Arpeggio parser. It is fully dynamic - no code generation at all!

Quick start
-----------

1. Write a language description in textX (file `hello.tx`):

  ```
  HelloWorldModel:
    'hello'  to_greet+={Who ','}
  ;

  Who:
    name = ID
  ;
  ```

2. Create some content (i.e. model) in your new language (`example.hello`):

  ```
  hello World, Solar System, Universe
  ```

3. Create meta-model from textX language description:

  ```python
  from textx.metamodel import metamodel_from_file
  hello_meta = metamodel_from_file('hello.tx')
  ```
4. Optionally export meta-model to dot (visualize your language abstract syntax):

  ```python
  from textx.export import metamodel_export
  metamodel_export(hello_meta, 'hello_meta.dot')
  ```

  ![](https://raw.githubusercontent.com/igordejanovic/textX/master/examples/hello_world/hello_metamodel.png)

5. Use meta-model to create models from textual description:

  ```python
  hello_model = hello_meta.model_from_file('example.hello')
  ```

6. Optionally export model to dot:

  ```python
  from textx.export import model_export
  model_export(hello_model, 'example.dot')
  ``` 

  ![](https://raw.githubusercontent.com/igordejanovic/textX/master/examples/hello_world/hello_model.png)

7. Use your model: interpret it, generate code ...



