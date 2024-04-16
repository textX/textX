# textx command/tool

Executing textX related CLI commands

---

textX has an extensible CLI tool which is a central hub for all textX CLI commands.

When you install textX with cli dependencies (`pip install textX[cli]`) you get
a CLI command `textx` which you call to execute any of the registered
sub-commands.

textX registers several sub-commands:

- `check` - used to check models and meta-models for syntax and semantic validity
- `generate` - used to call registered generators and transform given models to
  other target languages. This command is also used to visualize models and
  meta-models by generating visualizations. To see how to register your own
  generators head over to [registration/discover section](registration.md).
- `list-languages`/`list-generators` - used to list registered languages and
  generators (see the [registration/discover feature](registration.md) for more
  explanations)

```admonish tip
We eat our own dog food so all sub-commands are registered using the same
mechanism and there is no distinction between the core commands provided by the
textX itself and the commands provided by third-party Python packages.

Please, see [Extending textx command](#extending-textx-command) section bellow
on how to define your own sub-commands investigate `pyproject.toml` of the textX
project.

Some of development commands/tools are registered by
[textX-dev](https://github.com/textX/textX-dev) project which is an optional dev
dependency of textX. In order to have all these commands available you can
either install `textX-dev` project or install textX dev dependencies with `pip
install textX[dev]`.
```


## Using the tool


To see all available sub-commands just call the `textx`:

```sh
$ textx               
Usage: textx [OPTIONS] COMMAND [ARGS]...

Options:
  --debug  Debug/trace output.
  --help   Show this message and exit.

Commands:
  check            Check/validate model given its file path.
  generate         Run code generator on a provided model(s).
  list-generators  List all registered generators
  list-languages   List all registered languages
```
      

To get a help on a specific command:

```sh
$ textx check --help
Usage: textx check [OPTIONS] MODEL_FILES...

  Check/validate model given its file path. If grammar is given use it to
  construct the meta-model. If language is given use it to retrieve the
  registered meta-model.

  Examples:

  # textX language is built-in, so always registered:
  textx check entity.tx

  # If the language is not registered you must provide the grammar:
  textx check person.ent --grammar entity.tx

  # or if we have language registered (see: text list-languages) it's just:
  textx check person.ent

  # Use "--language" if meta-model can't be deduced by file extension:
  textx check person.txt --language entity

  # Or to check multiple model files and deduce meta-model by extension
  textx check *

Options:
  --language TEXT    A name of the language model conforms to.
  --grammar TEXT     A file name of the grammar used as a meta-model.
  -i, --ignore-case  Case-insensitive model parsing. Used only if "grammar" is
                     provided.
  --help             Show this message and exit.
```


## Extending textx command

`textx` command can be extended from other installed Python packages using
[entry
points](https://packaging.python.org/en/latest/specifications/entry-points/).
Using command extension one can add new commands and command groups to the
`textx` command.

`textx` uses [click](https://github.com/pallets/click/) library for CLI commands
processing. That makes really easy to create new commands and command groups.

To create a new command you need to provide a Python function accepting a
`click` command group (in this case a top level `textx` command) and use the
group to register additional commands using `click` decorators.

For example:

```python
import click

def testcommand(textx):
  @textx.command()
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

Register new command in your project's `pyproject.toml` file under the entry
point `textx_commands` (we are assuming that `testcommand` function is in
package `cli`).

```toml
[project.entry-points.textx_commands]
testcommand = "cli:testcommand"
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

Similarly you can create new command groups. You can have a group level options
and a command level options and arguments.

Here is a full example:

```python
import click

def create_testgroup(textx):
    @textx.group()
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

As usual, we have to register our function in the extension point
`textx_commands` inside `pyproject.toml`:

```toml
[project.entry-points.textx_commands]
testgroup = "cli:create_testgroup"
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

For more information please see [click
documentation](https://click.palletsprojects.com/en/7.x/).
