# LEIA Project Tools

This repository houses code written for the [Landscape, Encounters, and
Identity Archaeology (LEIA) Project](https://leiap.weebly.com).

## Installation

The package is not uploaded to PyPI yet, so to the easiest way to
install is to do so directly from the distribution file. Typically, if
you want to use a conda environment, you would use these steps:

1.  Download the files in the `dist` folder of the repository
2.  Activate the conda environment you want to use, e.g.,

```bash
$ source activate my_env
```

3.  Navigate to the location where you saved the `dist` files, e.g.,

```bash
$ cd /MyFiles/Downloads/
```

4.  `pip install` the package (see [Installing from local
    archives](https://packaging.python.org/tutorials/installing-packages/#installing-from-local-archives)
    for more info)

```bash
$ pip install ./dist/leiap-0.1.1.tar.gz
```

### Querying the database
In order to query the database, you will need the proper database login credentials. The `credentials.json` file in this repo is a dummy stand-in file. You will need to update it with the correct values or get a copy of the master file. You can then either: 

- Place it in the same directory as the script that runs the query.
 
 OR
 
- Specify its location as a keyword argument in the database query functions.

## Documentation
View the docs at [deppen8.github.io/leiap](https://deppen8.github.io/leiap/)

## License

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)