# Contributing

Contributions are welcome, and they are greatly appreciated!. You can contribute
code, documentation, tests, bug reports. Every little bit helps, and credit will
always be given. If you plan to make a significant contribution it would be
great if you first announce that in [the
Discussions](https://github.com/textX/textX/discussions).


## Legal Notice

When contributing to this project, you must agree that you have authored 100% of
the content, that you have the necessary rights to the content and that the
content you contribute may be provided under the project license.


## Guidelines for AI-assisted Contributions

AI tools are welcome as helpers, not authors. Keep these practices in mind:

- Stay accountable: only submit changes you understand and can justify; be ready
  to explain behavior, edge cases, and alignment with textX conventions. If an
  AI suggestion feels unclear, rewrite or drop it.
- Keep humans in the loop: discuss non-trivial ideas early via Issues or
  Discussions, especially when you are unsure about design or impact.
- Use AI for acceleration, then verify: treat AI output as a draft for code,
  tests, or docs; run linters/tests and review the logic yourself.
- Be transparent in PRs: note briefly if AI was used and for what (e.g., initial
  draft, test scaffolding), and call out any parts where you want extra review.
- Prefer focused patches over large dumps; if you cannot confidently explain an
  AI-produced change, open a well-described issue instead.


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

The easiest way to build and test docs locally is to do these steps:

1. Install [nix package manager](https://nixos.org/download/) with [flakes
   enabled](https://nixos.wiki/wiki/flakes).
2. From the project's root folder run:

    ```sh
    just docs
    ```

This will use a nix flake (defined in `docs/flake.nix`) to set up `mdbook` and
its preprocessors, serve the generated content on http://localhost:3000, and
automatically reload on changes.

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

3. Install [just](https://github.com/casey/just) and [uv](https://docs.astral.sh/uv/)
   and setup the development environment:

        $ cd textX/
        $ just dev

    To verify that everything is setup properly run check:

        $ just check

    Run `just` for options.

4. Create a branch for local development::

        $ git checkout -b name-of-your-bugfix-or-feature-branch

   Now you can make your changes locally.

   Optionally, run `ruff format` over the files you are changing from time to
   time to be sure that you adhere to the formatting style best-practices.

        $ ruff format <path to file>

   Please do not reformat the code that you have not changed. If you notice that
   ruff has reformatted parts of the code that are not part of your change use
   git to revert those parts.

   Please provide tests as a part of your change, if appropriate.

5. When you're done making changes, check that your changes pass linter, tests
   and coverage:

        $ just check

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
$ uv run pytest tests/functional/mytest.py
```

or a single test:

```
$ uv run pytest tests/functional/mytest.py::some_test
```

## Credit

This guide is based on the guide generated by
[Cookiecutter](https://github.com/audreyr/cookiecutter) and
[cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
project template.

Section on AI-assisted Contribution is taken and adapted from [Apache Kvrocks
project](https://kvrocks.apache.org/community/contributing/#guidelines-for-ai-assisted-contributions).
