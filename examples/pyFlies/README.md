This is an example of a complex textX language for cognitive experiments
modeling.

For explanation and documentation see [the pyFlies
project](https://github.com/igordejanovic/pyflies).

Language meta-model is given in `pyflies.tx` file. An example experiment is given in
`experiment.pf` file.

To check and visualize meta-model and model issue command:

    $ textx visualize pyflies.tx experiment.pf

You will get following output:

    Meta-model OK.
    Model OK.
    Generating 'pyflies.tx.dot' file for meta-model.
    To convert to png run 'dot -Tpng -O pyflies.tx.dot'
    Generating 'experiment.pf.dot' file for model.
    To convert to png run 'dot -Tpng -O experiment.pf.dot'

Now, you can use some `dot` viewer to view meta-model and model diagrams.
Alternativelly, you can convert `dot` files to some other graphical format as
stated above. See `png` files from this folder.
