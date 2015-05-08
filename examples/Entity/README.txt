This is an implementation of simple Entity-Relationship DSL (entity DSL in the rest of this README)

File "entity.tx" contains a grammar of the language.
Each entity DSL model consists of one or more Entitity instances.
Each Entity instance contains one or more Attributes.
Each Attribute has a name conforming to built-in ID type and a type which can be a reference
to some existing Entity or a string for primitive types.

Example model is given in file "person.ent".

An example of code generation is presented in file ... using template ....
Java POJO code is generated.


