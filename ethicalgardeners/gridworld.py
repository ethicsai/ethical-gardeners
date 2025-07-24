"""
The gridworld module represents the physical environment simulation grid for
Ethical Gardeners.

This module defines the fundamental structures of the simulated environment
where agents (gardeners) interact with the world. The environment consists of:

1. A 2D grid of cells (:py:class:`Cell`) - Each cell represents a physical
location that can be of different types (:py:class:`CellType`). The cells
have a pollution level that evolves over time, depending on whether they
contain flowers or not.

2. Flowers (:py:class:`Flower`) - Plants that agents can grow in ground cells:

* Different types with unique growth patterns and properties
* Progress through growth stages over time
* Reduce pollution in their cell based on type and growth stage
* Can be harvested for monetary value when fully grown
* Return seeds when harvested that can be used to plant more flowers

3. Agents (:py:class:`.Agent`) - Gardeners that move through and interact with
the environment:

* Can move between cells
* Plant flowers using seeds from their inventory
* Harvest fully grown flowers for monetary value

The GridWorld provides methods to initialize the environment (from file,
randomly, or programmatically), place and manage agents and flowers,
update environmental conditions, and validate agent actions.
"""
from enum import Enum
import copy

import numpy as np

from ethicalgardeners.agent import Agent
from ethicalgardeners.constants import MIN_SEED_RETURNS, MAX_SEED_RETURNS


class GridWorld:
    """
    Represents the physical grid world environment for the Ethical Gardeners
    simulation.

    The GridWorld manages a 2D grid of cells. It handles the flowers and agents
    and manages their placement within the environment. The grid can be
    initialized from a file, randomly generated, or manually configured.

    Attributes:
        width (int): The width of the grid in cells.
        height (int): The height of the grid in cells.
        min_pollution (float): The minimum level of pollution a cell can have
            at any time. The cell pollution decreases over time when flowers
            are planted, but cannot go lower than this minimum value.
        max_pollution (float): The maximum level of pollution a cell can have
            at any time. The cell pollution increases over time when no flowers
            are planted, but cannot go higher than this maximum value.
        pollution_increment (float): Amount by which pollution increases in
            empty cells.
        num_seeds_returned (int): Number of seeds returned when harvesting a
            flower.
        flowers_data (dict): Configuration data for different types of flowers.
        collisions_on (bool): Whether agents can occupy the same cell
            simultaneously.
        grid (list): 2D array of Cell objects representing the environment.
        agents (list): List of all Agent objects in the environment.
    """

    def __init__(self, width=10, height=10, min_pollution=0, max_pollution=100,
                 pollution_increment=1, num_seeds_returned=1,
                 collisions_on=True, flowers_data: dict = None,
                 random_generator=None, grid=None, agents: list = None,
                 flowers: list = None):
        """
        Create a new grid world environment.

        Args:
            width (int, optional): The width of the grid in cells.
            height (int, optional): The height of the grid in cells.
            min_pollution (float, optional): Minimum allowed pollution level
                for any cell.
            max_pollution (float, optional): Maximum allowed pollution level
                for any cell.
            pollution_increment (float, optional): Amount by which pollution
                increases in empty cells.
            num_seeds_returned (int, optional): Number of seeds returned when
                harvesting a flower. If -1, the system of seeds will be
                disabled. If -2, a random number between
                :py:const:`.MIN_SEED_RETURNS` and :py:const:`.MAX_SEED_RETURNS`
                will be used. If -3, the number of seeds returned will be
                randomly determined between :py:const:`.MIN_SEED_RETURNS` and
                :py:const:`.MAX_SEED_RETURNS` each time a flower is harvested.
            flowers_data (dict, optional): Configuration data for different
                types of flowers.
            collisions_on (bool, optional): Whether agents can occupy the same
                cell simultaneously.
            random_generator (:py:class:`numpy.random.RandomState`, optional):
                Custom random generator instance for reproducibility. If None,
                uses the default random
            grid (list, optional): 2D array of Cell objects representing the
                environment. If None, initializes an empty grid.
            agents (list, optional): List of Agent objects to place in the
                grid.
            flowers (list, optional): List of tuples representing flowers to
                place in the grid. Each tuple should be of the form (position,
                flower_type, growth_stage)
        """
        self.width = width
        self.height = height
        self.min_pollution = min_pollution
        self.max_pollution = max_pollution
        self.pollution_increment = pollution_increment
        self.collisions_on = collisions_on

        if flowers_data is None:
            flowers_data = {
                0: {'price': 10, 'pollution_reduction': [0, 0, 0, 0, 5]},
                1: {'price': 5, 'pollution_reduction': [0, 0, 1, 3]},
                2: {'price': 2, 'pollution_reduction': [1]}
            }

        self.flowers_data = flowers_data

        self.random_generator = random_generator if (
                random_generator is not None) else np.random.RandomState()

        if num_seeds_returned == -1:
            self.num_seeds_returned = None  # Seeds system disabled
        elif num_seeds_returned == -2:
            self.num_seeds_returned = self.random_generator.randint(
                MIN_SEED_RETURNS,
                MAX_SEED_RETURNS
            )
        else:
            self.num_seeds_returned = num_seeds_returned

        self.grid = grid if grid is not None else [[]]

        self.agents = []
        # Place agents in the grid
        if agents is not None:
            for agent in agents:
                if not self.valid_position(agent.position):
                    raise ValueError(
                        f"Invalid position for agent: {agent.position}")
                self.place_agent(agent)

        # Place flowers in the grid and add them to the flowers dictionary
        if flowers is not None:
            for position, flower_type, growth_stage in flowers:
                if not self.valid_position(position):
                    raise ValueError(
                        f"Invalid position for flower: {position}")
                self.place_flower(position, flower_type, growth_stage)

    @classmethod
    def init_from_file(cls, file_path, random_generator=None, min_pollution=0,
                       max_pollution=100, pollution_increment=1,
                       num_seeds_returned=1, collisions_on=True):
        """
        Initialize the grid from a file.

        The file format supports:

        - First line: width height
        - Grid representation: G (ground), O (obstacle),
          FX_Y (ground with flower type X at growth stage Y),
          AX (ground with agent ID X)
        - Agent definitions: ID,money,seeds
        - Flowers_data definition: type,price,pollution_reduction

        Example::

            10 10
            G G G O O G G G G G
            G F0_2 G G G O G G G G
            G O G A0 O G G G G G
            G G G G O G G G G G
            O O O O O G G G G G
            G G G G G G G G G G
            G G G G G G G G G G
            G G G G G G G G G G
            G G G G G G G G G G
            G G G G G G G G G G
            0,100,5|10|3
            0,10,5|2|1
            1,5,3|1|0
            2,2,1|0

        Args:
            file_path (str): Path to the file containing the grid
                configuration.
            random_generator (:py:class:`numpy.random.RandomState`, optional):
                Custom random generator instance for reproducibility.
            min_pollution (float, optional): Minimum allowed pollution level
                for any cell.
            max_pollution (float, optional): Maximum allowed pollution level
                for any cell.
            pollution_increment (float, optional): Amount by which pollution
                increases in empty cells.
            num_seeds_returned (int, optional): Number of seeds returned when
                harvesting a flower.
            collisions_on (bool, optional): Whether agents can occupy the same
                cell simultaneously.
        """
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Read width and height from the first line
        first_line = lines[0].strip().split()
        width = int(first_line[0])
        height = int(first_line[1])

        # Initialize the grid with empty cells
        grid = [[None for _ in range(width)] for _ in
                range(height)]

        # parse the grid
        agents_to_create = {}
        flowers_to_create = {}

        for i in range(height):
            cells = lines[i + 1].strip().split()
            for j, cell_code in enumerate(cells):
                if cell_code == 'G':
                    grid[i][j] = Cell(CellType.GROUND)
                elif cell_code == 'O':
                    grid[i][j] = Cell(CellType.OBSTACLE)
                elif cell_code.startswith('F'):
                    grid[i][j] = Cell(CellType.GROUND)
                    flower_info = cell_code[1:].split('_')
                    flower_type = int(flower_info[0])
                    growth_stage = int(flower_info[1])
                    flowers_to_create[(i, j)] = (flower_type, growth_stage)
                elif cell_code.startswith('A'):
                    grid[i][j] = Cell(CellType.GROUND)
                    agent_id = int(cell_code[1:])
                    agents_to_create[agent_id] = (i, j)

        # Create agents
        agents = []
        agent_def_start = height + 1
        agent_def_lines = lines[agent_def_start:
                                agent_def_start + len(agents_to_create)]
        for line in agent_def_lines:
            agent_data = line.strip().split(',')
            agent_id = int(agent_data[0])
            position = agents_to_create[agent_id]
            money = float(agent_data[1])
            seed_counts = list(map(int, agent_data[2].split('|')))
            seeds = {i: count for i, count in enumerate(seed_counts)}
            agent = Agent(position, money, seeds)
            agents.append(agent)

        # Create flowers_data
        flowers_data = {}
        flower_def_start = height + 1 + len(agents_to_create)
        flower_def_lines = lines[flower_def_start:]
        for line in flower_def_lines:
            flower_data = line.strip().split(',')
            flower_type = int(flower_data[0])
            price = int(flower_data[1])
            pollution_reduction = list(map(float, flower_data[2].split('|')))
            flowers_data[flower_type] = {
                'price': price,
                'pollution_reduction': pollution_reduction
            }

        # Place flowers with their growth stage
        flowers = []
        for position, (flower_type, growth_stage) in flowers_to_create.items():
            flowers.append((position, flower_type, growth_stage))

        return cls(width, height, min_pollution, max_pollution,
                   pollution_increment, num_seeds_returned, collisions_on,
                   flowers_data, random_generator, grid, agents, flowers)

    @classmethod
    def init_random(cls, width=10, height=10,
                    obstacles_ratio=0.2, nb_agent=2, min_pollution=0,
                    max_pollution=100, pollution_increment=1,
                    num_seeds_returned=1, collisions_on=True,
                    flowers_data: dict = None, random_generator=None):
        """
        Initialize a random grid with obstacles and agents.

        Args:
            width (int, optional): Width of the grid
            height (int, optional): Height of the grid
            obstacles_ratio (float, optional): Proportion of cells that will be
                obstacles (0.0 to 1.0)
            nb_agent (int, optional): Number of agents to place on the grid
            min_pollution (float, optional): Minimum allowed pollution level
                for any cell.
            max_pollution (float, optional): Maximum allowed pollution level
                for any cell.
            pollution_increment (float, optional): Amount by which pollution
                increases in empty cells.
            num_seeds_returned (int, optional): Number of seeds returned when
                harvesting a flower.
            collisions_on (bool, optional): Whether agents can occupy the same
                cell simultaneously.
            flowers_data (dict, optional): Configuration data for different
                types of flowers.
            random_generator (:py:class:`numpy.random.RandomState`, optional):
                Custom random generator instance for reproducibility. If None,
                uses the default random generator.

        Raises:
            ValueError: If there are not enough valid positions for the
                specified number of agents after placing obstacles.
        """
        random_generator = random_generator if (
                random_generator is not None) else np.random.RandomState()

        # Initialize grid with ground cells
        grid = [[Cell(CellType.GROUND) for _ in range(width)] for _ in
                range(height)]

        # Create a list of all possible positions
        valid_positions = [(i, j) for i in range(height) for j in
                           range(width)]

        # Place obstacles randomly
        indices = np.arange(len(valid_positions))  # choice needs indices
        num_obstacles = int(obstacles_ratio * width * height)
        selected_indices = random_generator.choice(indices,
                                                   num_obstacles,
                                                   replace=False)
        obstacle_positions = [valid_positions[i] for i in selected_indices]

        for pos in obstacle_positions:
            i, j = pos
            grid[i][j] = Cell(CellType.OBSTACLE)
            valid_positions.remove(pos)

        if len(valid_positions) < nb_agent:
            raise ValueError(
                f"Not enough valid positions for {nb_agent} agents")

        indices = np.arange(len(valid_positions))
        selected_indices = random_generator.choice(indices, nb_agent,
                                                   replace=False)
        agent_positions = [valid_positions[i] for i in selected_indices]

        agents = []
        for i in range(nb_agent):
            # Create agent with default values
            agent = Agent(agent_positions[i])
            agents.append(agent)

        return cls(width, height, min_pollution, max_pollution,
                   pollution_increment, num_seeds_returned, collisions_on,
                   flowers_data, random_generator, grid, agents)

    @classmethod
    def init_from_code(cls, grid_config=None, random_generator=None,
                       width=10, height=10, min_pollution=0, max_pollution=100,
                       pollution_increment=1, num_seeds_returned=1,
                       collisions_on=True):
        """
        Initialize the grid directly from code using a configuration
        dictionary.

        This method allows programmatic grid initialization for testing and
        debugging without having to create external files.

        Args:
            grid_config (dict, optional): Configuration dictionary with the
                following structure:

                .. code-block:: python

                    {
                        'width': int,  # Width of the grid
                        'height': int,  # Height of the grid
                        'cells': [  # List of special cells (other than GROUND)
                            {'position': (row, col), 'type': 'OBSTACLE'},
                        ],
                        'min_pollution': float,  # Minimum pollution level
                        'max_pollution': float,  # Maximum pollution level
                        'pollution_increment': float,  # Pollution increment
                        'num_seeds_returned': int,  # Number of seeds returned
                                                    # when harvesting a flower
                        'collisions_on': bool,  # Whether agents can occupy the
                                                # same cell
                        'flowers_data': {  # Optional: custom flower data
                            int: {'price': float,
                            'pollution_reduction': [float, ...]},
                        },
                        'agents': [  # List of agents to create (optional:
                                     # money and seeds)
                            {'position': (row, col), 'money': float,
                            'seeds': {0:int, 1:int, ...}},
                        ],
                        'flowers': [  # List of flowers to create (optional:
                                      # growth stage)
                            {'position': (row, col), 'type': int,
                            'growth_stage': int},
                        ]
                    }

            width (int, optional): Width of the grid.
            height (int, optional): Height of the grid.
            min_pollution (float, optional): Minimum allowed pollution level
                for any cell.
            max_pollution (float, optional): Maximum allowed pollution level
                for any cell.
            pollution_increment (float, optional): Amount by which pollution
                increases in empty cells.
            num_seeds_returned (int, optional): Number of seeds returned when
                harvesting a flower.
            collisions_on (bool, optional): Whether agents can occupy the same
                cell simultaneously.
            random_generator (:py:class:`numpy.random.RandomState`, optional):
                Custom random generator instance for reproducibility.
        """
        if grid_config is None:
            grid_config = {}

        # Set grid dimensions from the configuration
        width = grid_config.get('width', width)
        height = grid_config.get('height', height)

        # Get pollution limits from the configuration or use defaults
        min_pollution = grid_config.get('min_pollution',
                                        min_pollution)
        max_pollution = grid_config.get('max_pollution',
                                        max_pollution)

        # Get pollution increment from the configuration or use default
        pollution_increment = grid_config.get('pollution_increment',
                                              pollution_increment)

        # Get number of seeds returned from the configuration or use default
        num_seeds_returned = grid_config.get('num_seeds_returned',
                                             num_seeds_returned)

        # Get collisions setting from the configuration or use default
        collisions_on = grid_config.get('collisions_on',
                                        collisions_on)

        # Get flowers data from the configuration or use default
        flowers_data = grid_config.get('flowers_data',
                                       None)

        # Initialize grid with ground cells
        grid = [[Cell(CellType.GROUND) for _ in range(width)] for _ in
                range(height)]

        # Place special cells (obstacles, ...) based on the configuration
        for cell_info in grid_config.get('cells', []):
            position = cell_info['position']
            cell_type_str = cell_info['type']

            # Convert string type to CellType enum
            cell_type = CellType[cell_type_str.upper()]

            grid[position[0]][position[1]] = Cell(cell_type)

        # Create and place agents
        agents = []
        for agent_info in grid_config.get('agents', []):
            position = agent_info['position']
            money = agent_info.get('money', 0)
            seeds = agent_info.get('seeds', {0: 10, 1: 10, 2: 10})
            agent = Agent(position, money, seeds)
            agents.append(agent)

        # Create and place flowers
        flowers = []
        for flower_info in grid_config.get('flowers', []):
            position = flower_info['position']
            flower_type = flower_info['type']
            growth_stage = flower_info.get('growth_stage', 0)

            flowers.append((position, flower_type, growth_stage))

        return cls(width=width, height=height, min_pollution=min_pollution,
                   max_pollution=max_pollution,
                   pollution_increment=pollution_increment,
                   num_seeds_returned=num_seeds_returned,
                   collisions_on=collisions_on,
                   flowers_data=flowers_data, grid=grid,
                   agents=agents, flowers=flowers,
                   random_generator=random_generator)

    def place_agent(self, agent: Agent):
        """
        Place an agent in the grid at its current position.

        Args:
            agent (Agent): The agent to place in the grid.

        Raises:
            ValueError: If the agent's position is invalid or already occupied
                and collisions are not allowed.
        """
        if not self.valid_position(agent.position):
            raise ValueError("Invalid position for agent.")

        cell = self.get_cell(agent.position)

        if cell.has_agent() and not self.collisions_on:
            raise ValueError("Cannot place agent in an occupied cell without "
                             "collisions enabled.")

        cell.agent = agent
        self.agents.append(agent)

    def place_flower(self, position, flower_type: int, growth_stage=0):
        """
        Place a flower in the grid at its specified position.

        Args:
            position (tuple): The (x, y) coordinates where the flower will be
                planted.
            flower_type (int): The type of flower to plant.
            growth_stage (int, optional): The initial growth stage of the
                flower (default is 0).

        Raises:
            ValueError: If the flower's position is invalid or if the cell
                already contains a flower.
        """
        if not self.valid_position(position):
            raise ValueError("Invalid position for flower.")

        cell = self.get_cell(position)

        if cell.has_flower():
            raise ValueError("Cannot place flower in a cell that already has "
                             "a flower.")

        cell.flower = Flower(position, flower_type, self.flowers_data,
                             growth_stage)

    def remove_flower(self, position):
        """
        Removes a flower from the specified position in the grid.

        Args:
            position (tuple): The (x, y) coordinates of the flower to remove.

        Raises:
            ValueError: If there is no flower at the specified position.
        """
        cell = self.get_cell(position)
        if not cell.has_flower():
            raise ValueError("Cannot remove flower from a cell that does not "
                             "have a flower.")

        cell.flower = None

    def update_cell(self):
        """
        Updates the pollution and flowers of all cells in the grid.

        For each cell, if it contains a flower, pollution decreases by the
        flower's pollution reduction value and make the flower grow. If it does
        not contain a flower, pollution increases by the pollution increment
        value.
        """
        for row in self.grid:
            for cell in row:
                # Update pollution level
                cell.update_pollution(self.min_pollution, self.max_pollution)

                # If the cell has a flower, make it grow
                if cell.has_flower():
                    cell.flower.grow()

    def valid_position(self, position):
        """
        Checks if a position is valid for an agent to move to.

        A position is valid if:

        1. It is within the grid boundaries

        2. It is not an obstacle cell

        Args:
            position (tuple): The (x, y) coordinates to check.

        Returns:
            bool: True if the position is valid, False otherwise.
        """
        if 0 <= position[0] < self.height and 0 <= position[1] < self.width:
            if self.get_cell(position).can_walk_on():
                return True
            else:
                return False
        else:
            return False

    def valid_move(self, new_position):
        """
        Checks if an agent can move to a new position based on the action.

        A move is valid if:

        1. The new position is valid.

        2. If collisions are enabled, the new position is not occupied by
        another agent.

        Args:
            new_position (tuple): The new (x, y) coordinates of the agent after
                moving.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        # Check if the cell is occupied by another agent
        if not self.valid_position(new_position):
            return False
        if self.collisions_on:
            if self.get_cell(new_position).has_agent():
                return False

        return True

    def get_cell(self, position):
        """
        Gets the cell at the specified position.

        Args:
            position (tuple): The (x, y) coordinates of the cell to retrieve.

        Returns:
            Cell: The cell at the specified position.
        """
        return self.grid[position[0]][position[1]]

    def copy(self):
        """
        Create a deep copy of the GridWorld instance.

        Returns:
            GridWorld: A new instance of GridWorld with the same properties.
        """
        return copy.deepcopy(self)


class CellType(Enum):
    """
    Enum representing the possible types of cells in the grid world.

    Attributes:
        GROUND: A normal cell where agents can walk, plant and harvest flowers.
        OBSTACLE: An impassable cell that agents cannot traverse or interact
            with.
    """
    GROUND = 0
    OBSTACLE = 1


class Cell:
    """
    Represents a single cell in the grid world.

    It can be of different types (:py:class:`CellType`). Some types can
    contain a flower (:py:class:`Flower`) and an agent (:py:class:`.Agent`).
    It can have a pollution level that evolves over time to a speed defined by
    :py:attr:`pollution_increment`.

    Attributes:
        cell_type (CellType): Type of the cell (ground, obstacle).
        flower (Flower): The flower present in this cell, if any.
        agent (Agent): The agent currently occupying this cell, if any.
        pollution (float): Current pollution level of the cell, if applicable.
        pollution_increment (float): Amount by which pollution increases each
            step if no flower is in the cell.

    """

    def __init__(self, cell_type, pollution=50, pollution_increment=1):
        """
        Create a new cell.

        Args:
            cell_type (CellType): The type of cell to create.
            pollution (float, optional): Initial pollution level of the cell.
                Defaults to 50 for ground cells, None for obstacles.
            pollution_increment (float, optional): Amount by which pollution
                increases each step if no flower is in the cell. Defaults to 1.
        """
        self.cell_type = cell_type
        self.flower = None
        self.agent = None
        if cell_type == CellType.GROUND:
            self.pollution = pollution
        elif cell_type == CellType.OBSTACLE:
            self.pollution = None
        self.pollution_increment = pollution_increment

    def update_pollution(self, min_pollution, max_pollution):
        """
        Update the pollution level of the cell based on its current state.

        For ground cells, if the cell contains a flower, its pollution
        decreases by the flower's pollution reduction value, down to the
        minimum pollution level. If the cell does not contain a flower, its
        pollution increases by the pollution increment, up to the maximum
        pollution level.

        Args:
            min_pollution (float): Minimum pollution level allowed.
            max_pollution (float): Maximum pollution level allowed.
        """
        if self.pollution is None:
            return

        if self.has_flower():
            self.pollution = max(
                self.pollution - self.flower.get_pollution_reduction(),
                min_pollution
            )
        else:
            self.pollution = min(
                self.pollution + self.pollution_increment,
                max_pollution
            )

    def can_walk_on(self):
        """
        Check if agents can walk on this cell.

        Returns:
            bool: True if agents can walk on this cell, False otherwise.
        """
        return self.cell_type == CellType.GROUND

    def can_plant_on(self):
        """
        Check if a flower can be planted in this cell.

        Returns:
            bool: True if a flower can be planted in this cell, False
            otherwise.
        """
        return self.cell_type == CellType.GROUND and not self.has_flower()

    def has_flower(self):
        """
        Check if the cell contains a flower.

        Returns:
            bool: True if the cell contains a flower, False otherwise.
        """
        return self.flower is not None

    def has_agent(self):
        """
        Check if the cell is occupied by an agent.

        Returns:
            bool: True if the cell is occupied by an agent, False otherwise.
        """
        return self.agent is not None


class Flower:
    """
    Represents a flower that can be planted and harvested in the environment.

    Flowers grow through several stages and reduce pollution in their cell.
    Different flower types have different growth patterns, prices, and
    pollution reduction capabilities.

    Attributes:
        position (tuple): The (x, y) coordinates of the flower in the grid.
        flower_type (int): The type of flower, determining its growth and
            pollution reduction.
        price (float): The monetary value of the flower when harvested.
        pollution_reduction (list): List of pollution reduction values for each
            growth stage.
        num_growth_stage (int): Total number of growth stages for this flower.
        current_growth_stage (int): Current growth stage of the flower,
            starting at 0.
    """

    def __init__(self, position, flower_type, flowers_data: dict,
                 growth_stage=0):
        """
        Create a new flower.

        Args:
            position (tuple): The (x, y) coordinates where the flower is
                planted.
            flower_type (int): The type of flower to create.
            flowers_data (dict): Configuration data for flower types;
                a dictionary mapping flower type IDs to a dictionary of
                properties, containing ``keys`` and ``pollution_reduction``.
            growth_stage (int, optional): The number of growth stages for
                this flower. Defaults to 0 (the initial stage).
        """
        self.position = position
        self.flower_type = flower_type
        self.price = flowers_data[flower_type]['price']
        self.pollution_reduction = (
            flowers_data)[flower_type]["pollution_reduction"]
        self.num_growth_stage = len(self.pollution_reduction) - 1
        self.current_growth_stage = growth_stage

    def grow(self):
        """
        Advance the flower to the next growth stage if not fully grown.

        By default, the flower grows 1 stage at each time step, up to the
        maximum stage defined for this flower type.
        """
        if self.current_growth_stage < self.num_growth_stage:
            self.current_growth_stage += 1

    def is_grown(self):
        """
        Check if the flower has reached its final growth stage.

        Returns:
            bool: True if the flower is fully grown, False otherwise.
        """
        return self.current_growth_stage == self.num_growth_stage

    def get_pollution_reduction(self):
        """
        Return the current pollution reduction provided by the flower.

        The pollution reduction depends on the current growth stage and the
        flower type.

        Returns:
            float: The amount of pollution reduced by this flower at its
            current stage.
        """
        return self.pollution_reduction[self.current_growth_stage]
