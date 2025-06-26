# EthicalGardeners

**EthicalGardeners** is a [PettingZoo](https://pettingzoo.farama.org/)
multi-agent environment for simulating gardeners tending to a grid-world
garden, including ethical considerations.

The goal is to make agents learn an ethically-aligned behaviour that includes
and respects these considerations.


## How to

### Run tests

Tests must be placed in the `tests/` folder; files must follow the `test_*.py`
naming convention to be detected by unittest.

To run the tests, use the following command in a shell, with the current
working directory being the project root:

```sh
python -m unittest tests/test_*.py
```

### Build the docs

Documentation can be found in the `docs/` folder, and is built using Sphinx.
A quick command to build the documentation in the HTML format is:

```sh
cd docs/
make html
```

Then, open the `build/html/index.html` file in your favorite browser to read 
the rendered docs.

Documentation has its own requirements, which can be installed with

```sh
pip install -r docs/requirements.txt
```
