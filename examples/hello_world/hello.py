#!/usr/bin/env python
from os.path import join, dirname
from textx import metamodel_from_file
from textx.export import metamodel_export, model_export


def main(debug=False):

    this_folder = dirname(__file__)

    # Get meta-model from language description
    hello_meta = metamodel_from_file(join(this_folder, 'hello.tx'),
                                     debug=debug)

    # Optionally export meta-model to dot
    metamodel_export(hello_meta, join(this_folder, 'hello_meta.dot'))

    # Instantiate model
    example_hello_model = hello_meta.model_from_file(
        join(this_folder, 'example.hello'))

    # Optionally export model to dot
    model_export(example_hello_model, join(this_folder, 'example.dot'))


if __name__ == '__main__':
    main()
