"""
Ethical Gardeners: A simulation environment for ethical reinforcement learning.

The Ethical Gardeners package implements a simulation environment where agents
(gardeners) interact with a grid world, planting and harvesting flowers while
considering ethical considerations. This environment is designed to study and
promote ethical behaviors in reinforcement learning algorithms.

Main Components:
-----------------

* :py:class:`.WorldGrid`: The simulation grid representing the physical
  environment.
* :py:class:`.Agent`: The gardeners who act in the environment.
* :py:class:`.Flower`: Flowers that can be planted, grow, and reduce pollution.
* :py:func:`.create_action_enum`: Function that dynamically create an
  enumeration of actions for agents based on the number of flower types
  (:py:class:`._ActionEnum`).
* :py:class:`.ActionHandler`: Handles the execution of agent actions in the
  environment.
* :py:class:`.RewardFunctions`: Defines reward functions for agents based on
  their actions in the environment.
* :py:mod:`.observation`: Defines how agents perceive the environment (total or
  partial observation). Contains an interface for defining observation.
* :py:class:`.MetricsCollector`: Tracks and exports various performance
  metrics.
* :py:mod:`.renderer`: Display the environment state to the user.
* :py:class:`.GardenersEnv`: The main environment class that integrates all
  components and provides the interface for interaction with RL agents.

Usage Examples:
-----------------
.. code-block:: python

    import hydra
    from ethicalgardeners.gardenersenv import GardenersEnv


    @hydra.main(version_base=None, config_path="..", config_name="config")
    def main(config):
        # Initialise the environment with the provided configuration
        env = GardenersEnv(config)
        env.reset(seed=42)

        # Main loop for the environment
        for i, agent in enumerate(env.agent_iter()):
            observations, rewards, termination, truncation, infos = env.last()

            if termination or truncation:
                break
            else:
                # Here, add your agent's logic to choose an action
                action =

            env.step(action)

        # Close the environment
        env.close()

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
from ethicalgardeners.main import make_env
from ethicalgardeners.gardenersenv import GardenersEnv
