# Generator framework based on Jinja template engine

!!! warning

    This framework is implemented in 
    [textX-jinja](https://github.com/textX/textX-jinja) project.
    You have to install it with `pip install textX-jinja` to be able to use it.


You can roll your own code generation approach with textX but sometimes it is
good to have a predefined framework which is easy to get started with and only
if you need something very specific later you can create your own code
generator.

Here, we describe a little framework based on
[Jinja](https://jinja.palletsprojects.com/) template engine. 

The idea is simple. If you want to generate a set of files from your textX
model(s) you create a folder which resembles the outline of the file tree you
want to generate. Each file in your template folder can be a Jinja template
(with `.jinja` extension, e.g. `index.html.jinja`), in which case target file
will be created by running the template through the Jinja engine. If the file
doesn't end with `.jinja` extension it is copied as is to the target folder.

To call Jinja generator you use `textx_jinja_generator` function:

```python
...
from textxjinja import textx_jinja_generator
...

@generator('mylang', 'mytarget')
def mygenerator(metamodel, model, output_path, overwrite, debug):
    "Generate MyTarget from MyLang model."
    
    # Prepare config dictionary
    config = {}
    config['some_param'] = "Some value"

    template_folder = os.path.join(THIS_FOLDER, 'template')

    # Run Jinja generator
    textx_jinja_generator(template_folder, output_path, config, overwrite)
```

In this example we have our templates stored in `template` folder.

You can use variables from `config` dict in your templates as usual, but also
you can use them in filenames. If file name has a variable name in the format
`__<variablename>__` it will be replaced by the value of the variable from the
`config` dict. If variable by the given name is not found the `variablename` is
treated as literal filename. For example
[\_\_package__](https://github.com/textX/textX-dev/tree/master/textxdev/scaffold/template)
in the template file names will be replaced by package name from `config` dict.

Boolean values in file names are treated specially. If the value is of a bool
type the file will be skipped entirely if the value is `False` but will be used
if the value is `True`. This makes it easy to provide templates/files which
should be generated only under certain conditions (for example see `__lang__`
and `__gen__` variable usage in [template
names](https://github.com/textX/textX-dev/tree/master/textxdev/scaffold/template))

!!! note

    It is planned to support iterable in `config` dict. If a variable is
    iterable then a file will be generated for each element of the iterable. This
    is still not implemented.

To see a full example of using `textX-jinja` you can take a look at the
implementation of `startproject` textX command in
[textX-dev](https://github.com/textX/textX-dev) project. This textX command will
run a questionnaire based on [the Questionnaire
DSL](https://github.com/textX/textx-lang-questionnaire) and with run a project
scaffolding generation by [calling
textx\_jinja\_generate](https://github.com/textX/textX-dev/blob/master/textxdev/scaffold/__init__.py#L46)
with [the templates for the
project](https://github.com/textX/textX-dev/tree/master/textxdev/scaffold/template).
