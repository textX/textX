# textx command/tool

To check and visualize (meta)models from the command line.

---

!!! note
    textx command is moving to
    [textx-tools](https://github.com/igordejanovic/textx-tools) project from
    textX version 1.5. See the project for more details.

## Using the tool

To get basic help:

    $ textx --help
    usage: textx [-h] [-i] [-d] cmd metamodel [model]

    textX checker and visualizer

    positional arguments:
      cmd         Command - "check" or "visualize"
      metamodel   Meta-model file name
      model       Model file name

    optional arguments:
      -h, --help  show this help message and exit
      -i          case-insensitive parsing
      -d          run in debug mode


You can check and visualize (generate a .dot file) your meta-model or model using
this tool.

For example, to check and visualize a metamodel you could issue:


    $ textx visualize robot.tx
    Meta-model OK.
    Generating 'robot.tx.dot' file for meta-model.
    To convert to png run 'dot -Tpng -O robot.tx.dot'

Create an image from the .dot file:
  
    $ dot -Tpng -O robot.tx.dot

Or use some `dot` viewer. For example:

    $ xdot robot.tx.dot

Visualize model:

    $ textx visualize robot.tx program.rbt
    Meta-model OK.
    Model OK.
    Generating 'robot.tx.dot' file for meta-model.
    To convert to png run 'dot -Tpng -O robot.tx.dot'
    Generating 'program.rbt.dot' file for model.
    To convert to png run 'dot -Tpng -O program.rbt.dot'


To only check (meta)models use `check` command:

    $ textx check robot.tx program.rbt


If there is an error you will get a nice error report:


    $ textx check robot.tx program.rbt
    Meta-model OK.
    Error in model file.
    Expected 'initial' or 'up' or 'down' or 'left' or 
      'right' or 'end' at program.rbt:(3, 3) => 'al 3, 1   *gore 4    '.


