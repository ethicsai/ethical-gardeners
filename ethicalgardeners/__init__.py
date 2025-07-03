"""
Ethical Gardeners: A simulation environment for ethical reinforcement learning.

The Ethical Gardeners package implements a simulation environment where agents
(gardeners) interact with a grid world, planting and harvesting flowers while
considering ethical considerations. This environment is designed to study and
promote ethical behaviors in reinforcement learning algorithms.

Main Components:
-----------------
- :py:class:`.WorldGrid`: The simulation grid representing the physical
    environment
- :py:class:`.Agent`: The gardeners who act in the environment
- :py:class:`.Flower`: Flowers that can be planted, grow, and reduce pollution
- :py:class:`.Action`: Enumeration of possible actions (movement, planting,
    harvesting)

Usage Examples:
-----------------
.. code-block:: python

    # Create a grid world
    from ethicalgardeners import WorldGrid

    # Initialize a random grid
    grid = WorldGrid.init_random(width=10, height=10, obstacles_ratio=0.2,
                                nb_agent=2)

    # Or initialize from a configuration file
    grid = WorldGrid.init_from_file("config.txt")

    # Or initialize directly from code
    grid = WorldGrid.init_from_code(grid_config={
        'width': 10,
        'height': 10,
        'agents': [{'position': (0, 0), 'money': 10.0}]
    })

This package is designed to be used with reinforcement learning frameworks
such as Gymnasium or pettingzoo and follows the API conventions of these
frameworks.
"""
