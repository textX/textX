#!/usr/bin/env python
from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export, model_export

# Get meta-model from language description
hello_meta = metamodel_from_file('hello.tx')

# Optionally export meta-model to dot
metamodel_export(hello_meta, 'hello_meta.dot')

# Instantiate model
hello_model = hello_meta.model_from_file('example.hello')

# Optionally export model to dot
model_export(hello_model, 'example.dot')




