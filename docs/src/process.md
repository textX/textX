# textX release process

```admonish
For the background see [here](https://github.com/textX/textX/issues/176).
```

- We are using semantic versioning and a standard format to keep changelogs (see
  [CHANGELOG.md](https://github.com/textX/textX/blob/master/CHANGELOG.md)).
- We develop features on feature branches. Feature branches are named
  `feature/<feature name>`.
- We fix bugs on bugfix branches named as `bugfix/<issue no>-<name>`
- We have a branch for the upcoming major release -- `next-release` (red in the
  picture bellow).
- If the feature is backward incompatible (BIC) the PR is made against the
  `next-release` branch (not against the `master` branch)
- If the feature is backward compatible PR is made against the `master`.
- Thus, `Unreleased` section in the changelog on the `master` branch will never
  have any BIC change. All BIC changes should go to the changelog on the
  `next-release` branch.
- We constantly merge `master` branch to `next-release` branch. Thus,
  `next-release` branch is the latest and greatest version with **all** finished
  features applied.
- When the time for minor release come we follow [textX release
  checklist](#textx-release-checklist) defined bellow.
- When the time for major release come we merge `next-release` branch to
  `master` and follow [textX release checklist](#textx-release-checklist)
  defined bellow.


![process](./images/process.png)

 
# textX release checklist

  1. Create a branch for the next release called `release/<version>` and switch
     to that branch.
  2. Update version in the `pyproject.toml`.
  3. Update CHANGELOG (create new section for the release, update github links,
     give credits to contributors). Do not forget link to changes at the bottom.
  4. Push release branch and create PR. Wait for tests to pass. Wait for the
     review process to complete.
  5. Delete all previous distributions in the `dist` folder.
      ```
      rm dist/*
      ```
  6. Create `whl/tar.gz` packages.

      ```
      flit build
      ```

  7. Release to PyPI testing.

      ```
      flit publish --repository testpypi
      ```
      - Check release at https://test.pypi.org/project/textX/#history

  8. Release to PyPI.

      ```
      flit publish
      ```
      - Check release at https://pypi.org/project/textX/#history

  9. In case of errors repeat steps 3-10.
  10. Create git tag in the form of `<version>` (e.g. `4.1.0`). Push the tag.
  11. Merge release branch in to `master`.
  12. Change the version in `pyproject.toml` to next minor version with `.dev0`
      addition (e.g. `4.2.0.dev0`).
  13. Merge `master` to `next-release` to keep it up-to-date.

```admonish
For supporting previous versions only bugfix releases will be made as necessary.
The process is similar. The difference would be that PR would be issued against
the `release` branch instead of the `master` branch as is done for regular
releases.
```


