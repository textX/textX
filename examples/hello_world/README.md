This is a very simple example textX language.

For a full explanation see
[tutorial](http://textx.github.io/textX/tutorials/hello_world/).

To run the example do the following:

- Verify that textX is installed. See documentation how to do that.

- From the `hello_world` example folder run

        $ python hello.py

- Previous command will generate dot files representing Hello language
  meta-model and example model. To render those files to PNG format do (you
  must have [GraphViz](http://graphviz.org/) installed):

        $ dot -Tpng -O *.dot

  You will get `hello_meta.dot.png` (Hello meta-model) and `example.dot.png`
  (example Hello model).
