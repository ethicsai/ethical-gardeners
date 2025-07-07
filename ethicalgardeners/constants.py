"""Constant values used throughout the Ethical Gardeners simulation.
"""
DEFAULT_GRID_CONFIG = {
    'width': 10,
    'height': 10,
    'min_pollution': 0.0,
    'max_pollution': 100.0,
    'pollution_increment': 1.0,
    'num_seeds_returned': 1,
    'collisions_on': True,
    'flowers_data': {
        0: {"price": 10, "pollution_reduction": [0, 0, 0, 0, 5]},
        1: {"price": 5, "pollution_reduction": [0, 0, 1, 3]},
        2: {"price": 2, "pollution_reduction": [1]}
    },
    'cells': [
        {'position': (4, 4), 'type': 'OBSTACLE'},
        {'position': (5, 5), 'type': 'OBSTACLE'},
        {'position': (6, 6), 'type': 'OBSTACLE'}
    ],
    'agents': [
        {'position': (1, 1), 'money': 0.0, 'seeds': {0: 10, 1: 10, 2: 10}},
        {'position': (9, 9), 'money': 0.0, 'seeds': {0: 10, 1: 10, 2: 10}}
    ],
    'flowers': [
    ]
}
"""
Default configuration dictionary for grid initialization from code.

This dictionary provides a standard configuration when initializing a grid
using the :py:meth:`.WorldGrid.init_from_code` method without specifying a
custom configuration. It defines:

- Grid dimensions
- GridWorld properties (pollution levels, seed return policy, collision
    behavior)
- Flower data (prices and pollution reduction values)
- Special cell positions and types
- Initial agent positions and properties
- Initial flower placements (empty by default)
"""

MAX_PENALTY_TURNS = 10
"""
Maximum number of turns used to normalize the well-being penalty.

This constant defines the maximum number of turns without income after which
an agent receives the maximum well-being penalty (-1.0). It is used in the
`computeWellbeingReward` function to normalize the penalty given to agents
who haven't earned money, using the formula:
`-min(agent.turns_without_income / MAX_PENALTY_TURNS, 1.0)`

The higher this value, the more lenient the system is towards agents that go
for longer periods without harvesting and selling flowers.
"""
