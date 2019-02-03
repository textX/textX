# textx command/tool

To check and visualize (meta)models from the command line.

---

## Using the tool

To get basic help:

```sh
$ textx --help
Usage: textx [OPTIONS] COMMAND [ARGS]...

Options:
  --debug  Debug/trace output.
  --help   Show this message and exit.

Commands:
  check        Check validity of meta-model and optionally model.
  visualize    Generate .dot file(s) from meta-model and optionally model.
```
      

To get a help on a specific command:

```sh
$ textx check --help
Usage: textx check [OPTIONS] META_MODEL_FILE [MODEL_FILE]

  Check validity of meta-model and optionally model.

Options:
  -i, --ignore-case  case-insensitive parsing.
  --help             Show this message and exit.
```


You can check and visualize (generate a .dot file) your meta-model or model using
this tool.

For example, to check and visualize a metamodel you could issue:

```sh
$ textx visualize robot.tx
Meta-model OK.
Generating 'robot.tx.dot' file for meta-model.
To convert to png run 'dot -Tpng -O robot.tx.dot'
```


Create an image from the .dot file:

```sh
$ dot -Tpng -O robot.tx.dot
```


Or use some `dot` viewer. For example:

```sh
$ xdot robot.tx.dot
```


Visualize model:

```sh
$ textx visualize robot.tx program.rbt
Meta-model OK.
Model OK.
Generating 'robot.tx.dot' file for meta-model.
To convert to png run 'dot -Tpng -O robot.tx.dot'
Generating 'program.rbt.dot' file for model.
To convert to png run 'dot -Tpng -O program.rbt.dot'
```


To only check (meta)models use `check` command:

```sh
$ textx check robot.tx program.rbt
Meta-model OK.
Model OK.
```


If there is an error you will get a nice error report:

```sh
$ textx check robot.tx program.rbt
Meta-model OK.
Error in model file.
Expected 'initial' or 'up' or 'down' or 'left' or
  'right' or 'end' at program.rbt:(3, 3) => 'al 3, 1   *gore 4    '.
```


## Extending textx command

`textx` command can be extended from other installed Python packages using
[pkg_resources](https://setuptools.readthedocs.io/en/latest/pkg_resources.html)
extension points. Using command extension one can add new commands and command
groups to the `textx` command.

`textx` uses [click](https://github.com/pallets/click/) library for CLI commands
processing. That makes really easy to create new commands and command groups.

To create a new command you have to create a Python function decorated with
`click` decorators used for the definition of arguments and options. For more
information please see [click
documentation](https://click.palletsprojects.com/en/7.x/).

For example:

```python
import click

@click.argument('some_argument', type=click.Path())
@click.option('--some-option', default=False, is_flag=True,
              help="Testing option in custom command.")
def testcommand(some_argument, some_option):
    """
    This command will be found as a sub-command of `textx` command once this
    project is installed.
    """
    click.echo("Hello sub-command test!")
```

Register new command in your project's `setup.py` file under the entry point
`textx_commands` (we are assuming that `testcommand` function is in package
`cli`).

```python
setup(
    name='MyProject',
    packages=["cli"],
    entry_points={
        'textx_commands': [
            'testcommand = cli:testcommand'
        ],
    }
)
```

If you install now your project in the same Python environment where `textX` is
installed you will see that `textx` command now has your command registered.

```sh
$ textx
Usage: textx [OPTIONS] COMMAND [ARGS]...

Options:
  --debug  Debug/trace output.
  --help   Show this message and exit.

Commands:
  check        Check validity of meta-model and optionally model.
  testcommand  This command will be found as a sub-command of `textx`...
  visualize    Generate .dot file(s) from meta-model and optionally model.


$ textx testcommand some_argument
Hello sub-command test!
```

Similarly you can create new command groups. To do that create a function that
accepts `click` top-level group and registers new group on it with your group's
commands. You can have a group level options and a command level options and
arguments.

Here is a full example:

```python
import click

def create_testgroup(topgroup):
    @topgroup.group()
    @click.option('--group-option', default=False, is_flag=True,
                  help="Some group option.")
    def testgroup(group_option):
        """Here we write group explanation."""
        pass

    @testgroup.command()
    @click.argument('some_argument', type=click.Path())
    @click.option('--some-option', default=False, is_flag=True,
                  help="Testing option in custom command.")
    def groupcommand1(some_argument, some_option):
        """And here we write a doc for particular command."""
        click.echo("GroupCommand1: argument: {}, option:{}".format(
            some_argument, some_option))

    @testgroup.command()
    @click.argument('some_argument', type=click.Path())
    @click.option('--some-option', default=False, is_flag=True,
                  help="Testing option in custom command.")
    def groupcommand2(some_argument, some_option):
        """This is another command docs."""
        click.echo("GroupCommand2: argument: {}, option:{}".format(
            some_argument, some_option))
```

In this example we created a new group called `testgroup`. We use that group in
the rest of the code to decorate new commands belonging to the group.

We have to register our function in the extension point `textx_command_groups`:

```python
setup(
    name='MyProject',
    packages=["cli"],
    entry_points={
        ...
        'textx_command_groups': [
            'testgroup = cli:create_testgroup'
        ]
    }
    }
)
```

If `MyProject` is installed in the environment where `textX` is installed you'll
see that your command group is now accessible by the `textx` command:

```sh
$  textx
Usage: textx [OPTIONS] COMMAND [ARGS]...

Options:
  --debug  Debug/trace output.
  --help   Show this message and exit.

Commands:
  check        Check validity of meta-model and optionally model.
  testcommand  This command will be found as a sub-command of `textx`...
  testgroup    Here we write group explanation.
  visualize    Generate .dot file(s) from meta-model and optionally model.


$ textx testgroup
Usage: textx testgroup [OPTIONS] COMMAND [ARGS]...

  Here we write group explanation.

Options:
  --group-option  Some group option.
  --help          Show this message and exit.

Commands:
  groupcommand1  And here we write a doc for particular command.
  groupcommand2  This is another command docs.
  

$ textx testgroup groupcommand1 first_argument
GroupCommand1: argument: first_argument, option:False
```


For a full example please take a look at [this
test](https://github.com/textX/textX/blob/master/tests/functional/subcommands/test_subcommands.py) and this [example test
project](https://github.com/textX/textX/tree/master/tests/functional/subcommands/example_project).
