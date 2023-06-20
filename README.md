#  Nodetella - Material Maker node statistics

[![Python 3.x](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/MischaU8/nodetella/blob/main/LICENSE)

Nodetella provides statistics for the [Material Maker](https://www.materialmaker.org/) materials from the public assets website.
The materials are inserted into a SQLite database and exposed via [Datasette](https://datasette.io/).

## Demo

An online demo is available on https://nodetella.spevktator.io/material_maker
Take a look at the example queries on the above page.

## Installation

To install and run nodetella locally, you need at least Python 3.x and a couple Python libraries which you can install with `pipenv`.

### Development build (cloning git main branch):

```bash
git clone https://github.com/MischaU8/nodetella.git
cd nodetella
pipenv install
pipenv run get_mats.py
pipenv run datasette data/
```

Recommended: Take a look at [pipenv](https://pipenv.pypa.io/). This tool provides isolated Python environments, which are more practical than installing packages systemwide. It also allows installing packages without administrator privileges.
