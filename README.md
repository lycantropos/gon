gon
===

[![](https://travis-ci.com/lycantropos/gon.svg?branch=master)](https://travis-ci.com/lycantropos/gon "Travis CI")
[![](https://dev.azure.com/lycantropos/gon/_apis/build/status/lycantropos.gon?branchName=master)](https://dev.azure.com/lycantropos/gon/_build/latest?branchName=master "Azure Pipelines")
[![](https://readthedocs.org/projects/gon/badge/?version=latest)](https://gon.readthedocs.io/en/latest "Documentation")
[![](https://codecov.io/gh/lycantropos/gon/branch/master/graph/badge.svg)](https://codecov.io/gh/lycantropos/gon "Codecov")
[![](https://img.shields.io/github/license/lycantropos/gon.svg)](https://github.com/lycantropos/gon/blob/master/LICENSE "License")
[![](https://badge.fury.io/py/gon.svg)](https://badge.fury.io/py/gon "PyPI")

In what follows
- `python` is an alias for `python3.5` or any later
version (`python3.6` and so on),
- `pypy` is an alias for `pypy3.5` or any later
version (`pypy3.6` and so on).

Installation
------------

Install the latest `pip` & `setuptools` packages versions:
- with `CPython`
  ```bash
  python -m pip install --upgrade pip setuptools
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --upgrade pip setuptools
  ```

### User

Download and install the latest stable version from `PyPI` repository:
- with `CPython`
  ```bash
  python -m pip install --upgrade gon
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --upgrade gon
  ```

### Developer

Download the latest version from `GitHub` repository
```bash
git clone https://github.com/lycantropos/gon.git
cd gon
```

Install dependencies:
- with `CPython`
  ```bash
  python -m pip install --force-reinstall -r requirements.txt
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --force-reinstall -r requirements.txt
  ```

Install:
- with `CPython`
  ```bash
  python setup.py install
  ```
- with `PyPy`
  ```bash
  pypy setup.py install
  ```

Usage
-----

```python
>>> from gon.shaped import Polygon
>>> raw_square = [(0, 0), (1, 0), (1, 1), (0, 1)], []
>>> square = Polygon.from_raw(raw_square)
>>> square.raw() == raw_square
True
>>> square == square
True
>>> square >= square
True
>>> square <= square
True
>>> square < square
False
>>> square > square
False
>>> from gon.primitive import Point
>>> Point(0, 0) in square
True
>>> len(square.border.vertices) == 4
True
>>> len(square.holes) == 0
True
>>> square.is_convex
True
>>> square.convex_hull == square
True
>>> square.area == 1
True
>>> square.perimeter == 4
True
>>> (square.triangulate()
...  == [Polygon.from_raw(([(0, 1), (1, 0), (1, 1)], [])), 
...      Polygon.from_raw(([(0, 0), (1, 0), (0, 1)], []))])
True

```

Development
-----------

### Bumping version

#### Preparation

Install
[bump2version](https://github.com/c4urself/bump2version#installation).

#### Pre-release

Choose which version number category to bump following [semver
specification](http://semver.org/).

Test bumping version
```bash
bump2version --dry-run --verbose $CATEGORY
```

where `$CATEGORY` is the target version number category name, possible
values are `patch`/`minor`/`major`.

Bump version
```bash
bump2version --verbose $CATEGORY
```

This will set version to `major.minor.patch-alpha`. 

#### Release

Test bumping version
```bash
bump2version --dry-run --verbose release
```

Bump version
```bash
bump2version --verbose release
```

This will set version to `major.minor.patch`.

### Running tests

Install dependencies:
- with `CPython`
  ```bash
  python -m pip install --force-reinstall -r requirements-tests.txt
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --force-reinstall -r requirements-tests.txt
  ```

Plain
```bash
pytest
```

Inside `Docker` container:
- with `CPython`
  ```bash
  docker-compose --file docker-compose.cpython.yml up
  ```
- with `PyPy`
  ```bash
  docker-compose --file docker-compose.pypy.yml up
  ```

`Bash` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```bash
  ./run-tests.sh
  ```
  or
  ```bash
  ./run-tests.sh cpython
  ```

- with `PyPy`
  ```bash
  ./run-tests.sh pypy
  ```

`PowerShell` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```powershell
  .\run-tests.ps1
  ```
  or
  ```powershell
  .\run-tests.ps1 cpython
  ```
- with `PyPy`
  ```powershell
  .\run-tests.ps1 pypy
  ```
