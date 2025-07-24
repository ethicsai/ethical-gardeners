"""
Ethical Gardeners: A simulation environment for ethical reinforcement learning.

The Ethical Gardeners package implements a simulation environment where agents
(gardeners) interact with a grid world, planting and harvesting flowers while
considering ethical considerations. This environment is designed to study and
promote ethical behaviors in reinforcement learning algorithms.

Main Components:
-----------------

* :py:class:`.GridWorld`: The simulation grid representing the physical
  environment. It contains cells (:py:class:`.Cell`) of different types
  (:py:class:`CellType`).
* :py:class:`.Agent`: The gardeners who act in the environment.
* :py:class:`.Flower`: Flowers that can be planted, grow, and reduce pollution.
* :py:func:`.create_action_enum`: Function that dynamically create an
  enumeration of actions for agents based on the number of flower types
  (:py:class:`._ActionEnum`).
* :py:class:`.ActionHandler`: Handles the execution of agent actions in the
  environment.
* :py:class:`.RewardFunctions`: Defines reward functions for agents based on
  their actions in the environment.
* :py:mod:`.observation`: Defines how agents perceive the environment.
* :py:class:`.MetricsCollector`: Tracks and exports various performance
  metrics.
* :py:mod:`.renderer`: Display the environment state to the user.
* :py:class:`.GardenersEnv`: The main environment class that integrates all
  components and provides the interface for interaction with RL agents.

Usage Examples:
-----------------
.. code-block:: python

    import hydra
    from ethicalgardeners import GardenersEnv, make_env
    from ethicalgardeners.main import make_agent_algorithm, run_simulation


    @hydra.main(version_base=None, config_path=os.getcwd())
    def main(config):
        # Initialise the environment with the provided configuration
        env = make_env(config)

        # Create an agent algorithm
        agent_algorithm = make_agent_algorithm()

        env.reset()

        # Main loop for the environment
        run_simulation(env)

Launch
------
To run the simulation with the default configuration. After cloning the
project, at the project root, use the following command:

.. code-block:: bash

    python ethicalgardeners.main --config-dir configs --config-name config

Configuration
------------

The environment can be customized using a YAML configuration file with Hydra.
The default configuration file is located at `configs/config.yaml`. You can
override the default configuration parameters by modifying the YAML file or
using command line arguments when running the script:

.. code-block:: bash

    python ethicalgardeners.main grid=from_file observation=total metrics=full


This package is designed to be used with reinforcement learning frameworks
such as Gymnasium or pettingzoo and follows the API conventions of these
frameworks.

For more information, see the complete documentation at the `Ethical Gardeners
documentation <https://ethicsai.github.io/ethical-gardeners/main/index.html>`_.
"""
# Some imports that simplify external use, e.g.:
# `from ethicalgardeners import make_env, GardenersEnv`
# We disable Flake8 linting to avoid them being raised as false positives.
from ethicalgardeners.main import make_env  # noqa: F401
from ethicalgardeners.gardenersenv import GardenersEnv  # noqa: F401
