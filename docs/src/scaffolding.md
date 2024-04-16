# textX projects scaffolding

```admonish warning
`startpoject` command is provided by
[textX-dev](https://github.com/textX/textX-dev) project. You have to either
install this project or install textX optional dev dependencies with `pip
install textX[dev]`.
```

In case you are developing many textX languages and generators and would like to
do some organization we have provided a textX command `startproject` that will
generate either a language or a generator project with all necessary project files
to get you started quickly.

To scaffold a project just run:

```
textx startproject <folder>
```

You will be asked several questions and then the project will be generated in
the given folder. After that you can:

```
pip install -e <folder>
```

to install your project in development mode.

Your language/generator will be registered in the project `setup.cfg` file and
visible to textX which you can verify with:

```
textx list-languages
```

for language project or

```
textx list-generators
```

for generator project.

Answers to questions are cached in your home folder so the next time you run
scaffolding you don't have to type all the answers. If the default provided
answer is OK just press Enter.

```admonish tip
Check the [textX registration and discovery](./registration.md) for details on
`list-generators` and `list-languages` commands and recommended naming for
language/generator textX projects.
```
