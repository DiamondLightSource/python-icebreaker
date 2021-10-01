## How to prepare a release

To prepare an Icebreaker EM release you need to install the package [bump2version](https://pypi.org/project/bump2version/):

```bash
pip install bump2version
```

and then, in the repository directory, run one of the following

```bash
# assuming current version is 1.2.3
bumpversion patch  # release version 1.2.4
bumpversion minor  # release version 1.3.0
bumpversion major  # release version 2.0.0
```

This automatically creates a release commit and a release tag.
You then need to push both to the Github repository:
```bash
git push  # pushes the release commit
git push origin v2.0.0  # pushes the release tag for version 2.0.0
```

Assuming the tests pass the release is then created by Azure and uploaded directly onto [pypi](https://pypi.org/project/icebreaker_em/).