This is an example of a complex textX language for cognitive experiments
modeling.

For explanation and documentation see [the pyFlies
project](https://github.com/igordejanovic/pyflies).

Language meta-model is given in `pyflies.tx` file. An example experiment is given in
`experiment.pf` file.

To check and visualize meta-model and model issue command:

    $ textx generate pyflies.tx --target dot
    Generating dot target from models:
    /home/igor/repos/textX/textX/examples/pyFlies/pyflies.tx
    -> /home/igor/repos/textX/textX/examples/pyFlies/pyflies.dot
      To convert to png run "dot -Tpng -O pyflies.dot"

    $ textx generate experiment.pf --grammar pyflies.tx --target dot
    Generating dot target from models:
    /home/igor/repos/textX/textX/examples/pyFlies/experiment.pf
    -> /home/igor/repos/textX/textX/examples/pyFlies/experiment.dot
      To convert to png run "dot -Tpng -O experiment.dot"

Now, you can use some `dot` viewer to view meta-model and model diagrams.
Alternativelly, you can convert `dot` files to some other graphical format as
stated above. See `png` files from this folder.

In `experiment.py` is the same thing done from code. To run it do:

    $ python experiment.py
