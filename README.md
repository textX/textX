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

2. Create some test content in your new language (`example.hello`):

  ```
  hello World, Solar System, Universe
  ```

3. Create parser and model (python object graph based on your language description):

  ```python
  from textx import parser_from_file
  parser = parser_from_file('hello.tx')
  hello_model = parser.get_model('example.hello')
  ```

  Same parser may be used multiple times.

4. Use your model: interpret it or generate code.

5. Optionally export meta-model to dot (visualize your language abstract syntax):

  ```python
  from textx.export import metamodel_export 
  hello_metamodel = parser.get_metamodel()
  metamodel_export(hello_metamodel, 'example_meta.dot')
  ``` 

6. Optionally export your model to dot:

  ```python
  from textx.export import model_export
  model_export(hello_model, 'example.dot')
  ```


