"""Default values used throughout the Ethical Gardeners simulation."""

STARTING_CELL_POLLUTION = 50
"""
Default initial pollution level for new cells.

This constant defines the default starting pollution value when a cell is created.
"""

STARTING_AGENT_MONEY = 0
"""
Default initial money for new agents.

This constant defines the default starting monetary wealth of agents when they
are created.
"""

STARTING_AGENT_SEEDS = [10, 10, 10]
"""
Default initial seed counts for new agents.

This list defines how many seeds of each flower type agents have at creation. 
Each position in the list corresponds to a flower type (0, 1, 2), with a value
of 10 seeds for each type by default.
"""

POLLUTION_INCREMENT = 1
"""
Default amount by which pollution increases each step on empty ground cells.

This constant determines how quickly ground cells become polluted when no
flowers are present by default.
"""

FLOWERS_DATA = {
    0: {"price": 10, "pollution_reduction": [0, 0, 0, 0, 5]},
    1: {"price": 5, "pollution_reduction": [0, 0, 1, 3]},
    2: {"price": 2, "pollution_reduction": [1]}
}
"""
Default configuration data for different flower types.

Dictionary mapping flower type IDs to their properties:
- price: The monetary value when harvested
- pollution_reduction: List of pollution reduction values for each growth stage
"""

DEFAULT_WIDTH = 10
"""
Default width of the grid world.

This constant defines the number of cells in the horizontal dimension when 
creating a new WorldGrid without specifying a custom width.
"""

DEFAULT_HEIGHT = 10
"""
Default height of the grid world.

This constant defines the number of cells in the vertical dimension when
creating a new WorldGrid without specifying a custom height.
"""

MIN_POLLUTION = 0
"""
Minimum allowed pollution level for any cell.

This constant defines the lower bound for pollution levels. Cells with flowers
will reduce pollution but never below this value.
"""

MAX_POLLUTION = 100
"""
Maximum allowed pollution level for any cell.

This constant defines the upper bound for pollution levels. Empty cells will
increase in pollution but never exceed this value.
"""

NUM_SEEDS_RETURNED = 1
"""
Default number of seeds returned when harvesting a flower.

This constant determines how many seeds agents receive when harvesting a fully
grown flower, allowing them to replant the same type of flower.
"""

COLLISIONS_ON = True
"""
Default setting for agent collision detection.

When True, agents cannot occupy the same cell simultaneously. When False,
multiple agents can occupy the same position in the grid.
"""