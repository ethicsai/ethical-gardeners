EthicalGardeners documentation
==============================

**EthicalGardeners** is a `PettingZoo`_ multi-agent environment for simulating
gardeners tending to a grid-world garden, including ethical considerations.

.. _PettingZoo: https://pettingzoo.farama.org/

The goal is to make agents learn an ethically-aligned behaviour that includes
and respects these considerations.

Installation
------------

Install the package with pip:

.. code-block:: bash

    pip install ethical-gardeners

For visualization support (pygame, opencv):

.. code-block:: bash

    pip install "ethical-gardeners[viz]"

For metrics tracking (wandb):

.. code-block:: bash

    pip install "ethical-gardeners[metrics]"

Quick Start
-----------

To run the simulation with the default configuration. After cloning the project, at the project root or after installing
the package using pypi, use the following command:

.. code-block:: bash

    python -m ethicalgardeners.main --config-name config

For customization options, see the :doc:`tutorials/launch` tutorial.


.. toctree::
   :maxdepth: 2
   :caption: Tutorials:

   tutorials/launch
   tutorials/config
   tutorials/extend
   tutorials/algorithms

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: API

   api
