# Contributing

Contributions are welcome, and they are greatly appreciated!. You can contribute
code, documentation, tests, bug reports. Every little bit helps, and credit will
always be given. If you plan to make a significant contribution it would be
great if you first announce that in [the
Discussions](https://github.com/textX/textX/discussions).

You can contribute in many ways:


## Types of Contributions


### Report Bugs

Report bugs at https://github.com/textX/textX/issues.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.


### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.


### Implement Features

Look through the GitHub issues for features. Anything tagged with
"enhancement/feature" and "help wanted" is open to whoever wants to implement
it.


### Write Documentation

textX could always use more documentation, whether as part of the official textX
docs, in docstrings, or even on the web in blog posts, articles, and such.

#### How to Test the Documentation Locally

textX is currently using `mdbook` documentation generator, which generate HTML
from markdown files in the `docs/src` folder.

The always up-to-date docs are available at https://textx.github.io/textX/index.html

The easiest way to build and test docs locally is to use our mdbook-textx docker
image:

1. Install [docker](https://docs.docker.com/engine/install/).
2. From the project's root folder run:

    ```sh
    ./serve-docs.sh
    ```

This starts docker container which will watch to changes in the markdown docs
files and serve generated content on http://localhost:3000

To add a new page you must add the page to the TOC at `docs/src/SUMMARY.md`.

To learn more on mdbook you can visit [the project
documentation](https://rust-lang.github.io/mdBook/).

`mdbook` is based on a concept of `preprocessors` which are just binaries whose
name starts with `mdbook-` and which are called to preprocess md files.

Currently we are using the following preprocessors:

1. [mdbook-admonish](https://github.com/tommilligan/mdbook-admonish)
2. [mdbook-linkcheck](https://github.com/Michael-F-Bryan/mdbook-linkcheck)
3. [mdbook-theme](https://github.com/zjp-CN/mdbook-theme)
4. [mdbook-bib](https://github.com/francisco-perez-sorrosal/mdbook-bib)


### Submit Feedback

The best way to send feedback is to open a discussion at
https://github.com/textX/textX/discussions

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions are
  welcome :)


## Get Started!

Ready to contribute? Here's how to set up `textX` for local development.

1. Fork the `textX` repo on GitHub.
2. Clone your fork locally:

        $ git clone git@github.com:your_name_here/textX.git

3. Install your local copy into a virtualenv. This is how you set up your fork
   for local development:

        $ cd textX/
        $ python -m venv venv
        $ source venv/bin/activate
        $ ./install-dev.sh
        $ ./install-test.sh

    Previous stuff is needed only the first time. To continue working on textX
    later you just do:

        $ cd textX/
        $ source venv/bin/activate

    Note that on Windows sourcing syntax is a bit different. Check the docs for
    virtualenv.

    An excellent overview of available tools for Python environments management
    can be found
    [here](https://stackoverflow.com/questions/41573587/what-is-the-difference-between-venv-pyvenv-pyenv-virtualenv-virtualenvwrappe)

    To verify that everything is setup properly run tests:

        $ ./runtests.sh

4. Create a branch for local development::

        $ git checkout -b name-of-your-bugfix-or-feature-branch

   Now you can make your changes locally.

   Optionally, run `ruff format` over the files you are changing from time to
   time to be sure that you adhere to the formatting style best-practices.

        $ ruff format <path to file>

   Please do not reformat the code that you have not changed. If you notice that
   ruff has reformatted parts of the code that are not part of your change use
   git to revert those parts.

5. When you're done making changes, check that your changes pass linter, the
   tests, and have a look at the coverage:

        $ ruff check textx/ tests/ examples/
        $ pytest tests/functional/
        $ coverage run --source textx -m pytest tests/functional
        $ coverage report

   You can run all this at once with provided script `runtests.sh`

        $ ./runtests.sh

   In case you have doubts, have also a look at the html rendered version of
   the coverage results:

        $ coverage html

6. Commit your changes and push your branch to GitHub:

        $ git add .
        $ git commit -m "Your detailed description of your changes."
        $ git push origin name-of-your-bugfix-or-feature-branch

7. Submit a pull request through the GitHub website.


## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds/changes functionality, the docs should be updated.
3. The pull request should work for Python 3.8+. Check
   https://github.com/textX/textX/actions and make sure that the tests pass for
   all supported Python versions.


## Tips

To run a subset of tests:

```
$ pytest tests/functional/mytest.py
```

or a single test:

```
$ pytest tests/functional/mytest.py::some_test
```

## Credit

This guide is based on the guide generated by
[Cookiecutter](https://github.com/audreyr/cookiecutter) and
[cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
project template.
