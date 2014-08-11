textX
=====

Meta-language in Arpeggio inspired by Xtext

textX follows closely the syntax and semantics of `Xtext`_ but differs in some places and is implemented 100%
in Python using Arpeggio parser. It is fully dynamic - no code generation at all!

_Xtext:: http://www.eclipse.org/Xtext/

Quick start
-----------

1. Write a language description in textX (file 'hello.tx')::

  HelloWorldModel:
    'hello'  to_greet={Who ','}
  ;

  Who:
    name = ID
  ;

2. Create some test content in your new language (file 'example.hello')::
  
  hello World, Solar System, Universe

3. Construct parser from language description::

  from textx import parser_from_file
  parser = parser_from_file('hello.tx')

4. Create model (python object graph based on your language description)::

  model = parser.get_model('example.hello')

5. Use your model: interpret it or generate code::

  print(model)




