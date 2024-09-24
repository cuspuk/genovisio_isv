# Genovisio ISV

[![Python version](https://img.shields.io/badge/python-3.12+-green.svg)](https://www.python.org/downloads/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)

CNV annotation and pathogenicity prediction tool.

## Installation

In python3.12 you can simply use pip to install ISV:

```bash
pip install git+https://github.com/cuspuk/genovisio_isv.git
```

Without python3.12, you can install isv using mamba:

```bash
mamba env create -f conda_isv.yaml
```

This gives you 3 entrypoints:

- `isv-annotate` - running ISV for only annotation of input CNV using genovisio DB
- `isv-predict` - running ISV for only prediction of annotated CNV
- `isv-run` - running ISV to both annotate and predict input CNV

## Running

To run ISV, running instance of mongo database is required. Mongo URI and database name can be supplied to the entrypoint commands, see `--help`. Default MongoDB URI is `mongodb://localhost:27017/` and the database name 'genovisio'.

To run ISV, call one of entrypoint commands (if installed using conda, activate it first).

To annotate and predict input CNV `chr15:41286147-41439352/gain` call:

```sh
isv-run chr15:41286147-41439352/gain --annotation_output annotation.json --prediction_output prediction.json
```

### Partial running

To annotate only the input CNV given as `chr1:16302-166909/gain` and print the annotation to stdout:

```shell
isv-annotate chr15:41286147-41439352/gain 2> log.err
```

To predict from the JSON-stored annotation called `annotation.json` (for example by redirecting `isv-annotate` stdout or using `--output` of the command):

```shell
isv-predict annotation.json 2> log.err
```

## Development

Poetry is used to package the application. It is required to run `poetry build` and `poetry install` to recreate the `poetry.lock` containing frozen versions of dependencies.
