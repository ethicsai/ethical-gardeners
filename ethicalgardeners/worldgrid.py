"""
The WorldGrid module represents the physical environment simulation grid.

This module defines the fundamental structures to represent the physical space
where agents (gardeners) interact with the environment, including cells and flowers.
"""
from enum import Enum
from ethicalgardeners.action import Action
from ethicalgardeners.defaultvalues import (FLOWERS_DATA, \
                                            POLLUTION_INCREMENT,
                                            STARTING_CELL_POLLUTION, \
                                            STARTING_AGENT_SEEDS,
                                            STARTING_AGENT_MONEY, COLLISIONS_ON,
                                            NUM_SEEDS_RETURNED, DEFAULT_WIDTH,
                                            DEFAULT_HEIGHT, MIN_POLLUTION,
                                            MAX_POLLUTION)


class WorldGrid:
    """
    Represents the physical grid world environment for the Ethical Gardeners simulation.

    The WorldGrid manages a 2D grid of cells. It handles the flowers and agents
    and manages their placement within the environment. The grid can be
    initialized from a file, randomly generated, or manually configured.

    Attributes:
        width (int): The width of the grid in cells.
        height (int): The height of the grid in cells.
        min_pollution (float): Minimum allowed pollution level for any cell.
        max_pollution (float): Maximum allowed pollution level for any cell.
        pollution_increment (float): Amount by which pollution increases in
                                     empty cells.
        num_seeds_returned (int): Number of seeds returned when harvesting a flower.
        flowers_data (dict): Configuration data for different types of flowers.
        collisions_on (bool): Whether agents can occupy the same cell simultaneously.
        grid (list): 2D array of Cell objects representing the environment.
        agents (list): List of all Agent objects in the environment.
        flowers (dict): Dictionary of flower's name and color organized by
                        flower type.
    """

    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT,
                 min_pollution=MIN_POLLUTION, max_pollution=MAX_POLLUTION,
                 pollution_increment=POLLUTION_INCREMENT,
                 num_seeds_returned=NUM_SEEDS_RETURNED,
                 flowers_data=FLOWERS_DATA, collisions_on=COLLISIONS_ON):
        """
        Create a new grid world environment.

        Args:
            width (int): The width of the grid in cells.
            height (int): The height of the grid in cells.
            min_pollution (float): Minimum allowed pollution level for any cell.
            max_pollution (float): Maximum allowed pollution level for any cell.
            pollution_increment (float): Amount by which pollution increases in
                                         empty cells.
            num_seeds_returned (int): Number of seeds returned when harvesting
                                      a flower.
            flowers_data (dict): Configuration data for different types of flowers.
            collisions_on (bool): Whether agents can occupy the same cell
                                  simultaneously.
        """
        self.width = width
        self.height = height
        self.min_pollution = min_pollution
        self.max_pollution = max_pollution
        self.pollution_increment = pollution_increment
        self.num_seeds_returned = num_seeds_returned
        self.flowers_data = flowers_data
        self.collisions_on = collisions_on

        self.grid = [[]]
        self.agents = []
        self.flowers = {i: [] for i in range(len(flowers_data))}

    def init_from_file(self, file_path):
        """
        Initialize the grid from a file.

        The file format supports:
        - First line: width height
        - Grid representation: G (ground), O (obstacle), W (wall),
          FX_Y (ground with flower type X at growth stage Y),
          AX (ground with agent ID X)
        - Agent definitions: ID,money,seeds
        - Flower definitions: type,price,pollution_reduction

        Example:
        ```
        10 10
        G G G W W G G G G G
        G F0_2 G G W G G G G G
        G O G A0 W G G G G G
        G G G G W G G G G G
        W W W W W G G G G G
        G G G G G G G G G G
        G G G G G G G G G G
        G G G G G G G G G G
        G G G G G G G G G G
        G G G G G G G G G G
        0,100,5|10|3
        0,2,1|2|3
        ```

        Args:
            file_path (str): Path to the file containing the grid configuration.
        """
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Read width and height from the first line
        first_line = lines[0].strip().split()
        self.width = int(first_line[0])
        self.height = int(first_line[1])

        # Initialize the grid with empty cells
        self.grid = [[Cell(CellType.GROUND) for _ in range(self.width)] for _ in
                     range(self.height)]

        #parse the grid
        agents_to_create = {}
        flowers_to_create = {}

        for i in range(self.height):
            cells = lines[i + 1].strip().split()
            for j, cell_code in enumerate(cells):
                if cell_code == 'G':
                    self.grid[i][j] = Cell(CellType.GROUND)
                elif cell_code == 'O':
                    self.grid[i][j] = Cell(CellType.OBSTACLE)
                elif cell_code == 'W':
                    self.grid[i][j] = Cell(CellType.WALL)
                elif cell_code.startswith('F'):
                    self.grid[i][j] = Cell(CellType.GROUND)
                    flower_info = cell_code[1:].split('_')
                    flower_type = int(flower_info[0])
                    growth_stage = int(flower_info[1])
                    flowers_to_create[(i, j)] = (flower_type, growth_stage)
                elif cell_code.startswith('A'):
                    self.grid[i][j] = Cell(CellType.GROUND)
                    agent_id = int(cell_code[1:])
                    agents_to_create[agent_id] = (i, j)

        # Create agents
        agent_def_lines = lines[self.height + 1:self.height + 1 + len(agents_to_create)]
        for line in agent_def_lines:
            agent_data = line.strip().split(',')
            agent_id = int(agent_data[0])
            position = agents_to_create[agent_id]
            money = float(agent_data[1])
            seeds = list(map(int, agent_data[2].split('|')))
            agent = Agent(position, money, seeds)
            self.place_agent(agent)

        # Create flowers_data
        flower_def_lines = lines[self.height + 1 + len(agents_to_create):]
        for line in flower_def_lines:
            flower_data = line.strip().split(',')
            flower_type = int(flower_data[0])
            price = int(flower_data[1])
            pollution_reduction = list(map(float, flower_data[2].split('|')))
            self.flowers_data[flower_type] = {
                'price': price,
                'pollution_reduction': pollution_reduction
            }

        # Place flowers with their growth stage
        for position, (flower_type, growth_stage) in flowers_to_create.items():
            flower = Flower(position, flower_type, self.flowers_data)
            # Set growth stage
            for _ in range(growth_stage):
                flower.grow()
            self.place_flower(flower)

    def place_agent(self, agent):
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

        if cell.have_Agent() and not self.collisions_on:
            raise ValueError("Cannot place agent in an occupied cell without "
                             "collisions enabled.")

        cell.Agent = agent
        self.agents.append(agent)

    def place_flower(self, flower):
        """
        Place a flower in the grid at its specified position.

        Args:
            flower (Flower): The flower to place in the grid.

        Raises:
            ValueError: If the flower's position is invalid or if the cell
                        already contains a flower.
        """
        if not self.valid_position(flower.position):
            raise ValueError("Invalid position for flower.")

        cell = self.get_cell(flower.position)

        if cell.have_flower():
            raise ValueError("Cannot place flower in a cell that already has "
                             "a flower.")

        cell.flower = flower

    def remove_flower(self, position):
        """
        Removes a flower from the specified position in the grid.

        Args:
            position (tuple): The (x, y) coordinates of the flower to remove.

        Raises:
            ValueError: If there is no flower at the specified position.
        """
        cell = self.get_cell(position)
        if not cell.have_flower():
            raise ValueError("Cannot remove flower from a cell that does not "
                             "have a flower.")

        cell.flower = None

    def update_pollution(self):
        """
        Updates the pollution level of all cells in the grid.

        For each cell, if it contains a flower, pollution decreases by the
        flower's pollution reduction value. If it does not contain a flower,
        pollution increases by the pollution increment value.
        """
        for row in self.grid:
            for cell in row:
                cell.update_pollution(self.min_pollution, self.max_pollution)

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
            if not self.get_cell(position).cell_type == CellType.OBSTACLE:
                return True
            else:
                return False
        else:
            return False

    def get_cell(self, position):
        """
        Gets the cell at the specified position.

        Args:
            position (tuple): The (x, y) coordinates of the cell to retrieve.

        Returns:
            Cell: The cell at the specified position.
        """
        return self.grid[position[0]][position[1]]


class CellType(Enum):
    """
    Enum representing the possible types of cells in the grid world.

    Attributes:
        GROUND: A normal cell where agents can walk, plant and harvest flowers.
        OBSTACLE: An impassable cell that agents cannot traverse or interact with.
        WALL: A boundary cell that defines the limits of the environment.
    """
    GROUND = 0
    OBSTACLE = 1
    WALL = 2


class Cell:
    """
    Represents a single cell in the grid world.

    It can contain a flower, an agent, and has a pollution level that evolves
    over time.

    Attributes:
        cell_type (CellType): Type of the cell (ground, obstacle, wall).
        flower (Flower): The flower present in this cell, if any.
        Agent (Agent): The agent currently occupying this cell, if any.
        pollution (float): Current pollution level of the cell.
        pollution_increment (float): Amount by which pollution increases each
                                     step if no flower in the cell.

    """

    def __init__(self, cell_type, pollution=STARTING_CELL_POLLUTION,
                 pollution_increment=POLLUTION_INCREMENT):
        """
        Create a new cell.

        Args:
            cell_type (CellType): The type of cell to create.
            pollution (float): Initial pollution level of the cell. Defaults to 50.
            pollution_increment (float): Amount by which pollution increases
                                         each step if no flower in the cell.
                                         Defaults to 1.
        """
        self.cell_type = cell_type
        self.flower = None
        self.Agent = None
        self.pollution = pollution
        self.pollution_increment = pollution_increment

    def update_pollution(self, min_pollution, max_pollution):
        """
        Update the pollution level of the cell based on its current state.

        If the cell contains a flower, its pollution decreases by the flower's
        pollution reduction value, down to the minimum pollution level.
        If the cell does not contain a flower, its pollution increases by
        the pollution increment, up to the maximum pollution level.

        Args:
            min_pollution (float): Minimum pollution level allowed.
            max_pollution (float): Maximum pollution level allowed.
        """
        if self.have_flower() and self.pollution > min_pollution:
            self.pollution -= self.flower.get_pollution_reduction()
        elif not self.have_flower() and self.pollution < max_pollution:
            self.pollution += self.pollution_increment

    def is_ground(self):
        """
        Check if the cell is of type GROUND.

        Returns:
            bool: True if the cell is of type GROUND, False otherwise.
        """
        return self.cell_type == CellType.GROUND

    def have_flower(self):
        """
        Check if the cell contains a flower.

        Returns:
            bool: True if the cell contains a flower, False otherwise.
        """
        return self.flower is not None

    def have_Agent(self):
        """
        Check if the cell is occupied by an agent.

        Returns:
            bool: True if the cell is occupied by an agent, False otherwise.
        """
        return self.Agent is not None


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

    def __init__(self, position, flower_type, flowers_data=FLOWERS_DATA):
        """
        Create a new flower.

        Args:
            position (tuple): The (x, y) coordinates where the flower is planted.
            flower_type (int): The type of flower to create.
            flowers_data (dict): Configuration data for flower types, mapping
                                 flower type IDs to their properties (price,
                                 pollution reduction).
        """
        self.position = position
        self.flower_type = flower_type
        self.price = flowers_data[flower_type]['price']
        self.pollution_reduction = flowers_data[flower_type]["pollution_reduction"]
        self.num_growth_stage = len(self.pollution_reduction)
        self.current_growth_stage = 0

    def grow(self):
        """
        Advance the flower to the next growth stage if not fully grown.

        Each call increments the current_growth_stage by 1, up to the maximum
        defined for this flower type.
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


class Agent:
    """
    Represents a gardener agent in the environment.

    Agents can move around the grid, plant and harvest flowers, manage seeds,
    and accumulate money from harvesting flowers.

    Attributes:
        position (tuple): The (x, y) coordinates of the agent in the grid.
        money (float): The agent's current monetary wealth.
        seeds (dict): Dictionary mapping flower types to the number of seeds
                      the agent has.
        flowers_planted (dict): Counter of flowers planted by type.
        flowers_harvested (dict): Counter of flowers harvested by type.
    """
    def __init__(self, position, money=STARTING_AGENT_MONEY,
                 seeds=STARTING_AGENT_SEEDS):
        """
        Create a new agent.

        Args:
            position (tuple): The (x, y) coordinates where the agent starts.
            money (float, optional): Initial amount of money the agent has.
                                     Defaults to 0.
            seeds (dict, optional): Dictionary mapping flower types to initial
                                    seed counts. Defaults to 10 for each type.
        """
        self.position = position
        self.money = money
        self.seeds = seeds
        self.flowers_planted = {i: 0 for i in self.seeds}
        self.flowers_harvested = {i: 0 for i in self.seeds}

    def move(self, direction):
        """
        Move the agent in the specified direction.

        Updates the agent's position based on the direction action.

        Args:
            direction (:py:class:`.Action`): The direction to move (UP, DOWN,
            LEFT, RIGHT).
        """
        if direction == Action.UP:
            self.position = (self.position[0] - 1, self.position[1])
        elif direction == Action.DOWN:
            self.position = (self.position[0] + 1, self.position[1])
        elif direction == Action.LEFT:
            self.position = (self.position[0], self.position[1] - 1)
        elif direction == Action.RIGHT:
            self.position = (self.position[0], self.position[1] + 1)

    def can_plant(self, flower_type):
        """
        Check if the agent has seeds available to plant a specific flower type.

        Args:
            flower_type (int): The type of flower to check seed availability for.

        Returns:
            bool: True if the agent has at least one seed of the specified type
            of if seed count is -1 because this represenys infinite seeds.
        """

        if self.seeds[flower_type] == -1:
            # If the seed count is -1, it represents infinite seeds
            return True

        return self.seeds[flower_type] > 0

    def use_seed(self, flower_type):
        """
        Use a seed to plant a flower of the specified type.

        Decrements the seed count for the flower type and increments the
        flowers_planted counter. If seed count is -1, this represents infinite
        seeds and the count is not decremented.

        Args:
            flower_type (int): The type of flower to plant.

        Returns:
            bool: True if the seed was successfully used, False if no seeds
            available.
        """
        if self.can_plant(flower_type):
            if self.seeds[flower_type] != -1:
                # Only decrement if the seed count is not infinite
                self.seeds[flower_type] -= 1

            self.flowers_planted[flower_type] += 1
            return True

        return False

    def add_money(self, amount):
        """
        Add money to the agent's wealth.

        Args:
            amount (float): The amount of money to add.
        """
        self.money += amount

    def add_seed(self, flower_type, num_seeds):
        """
        Add seeds of a specific flower type to the agent's inventory.

        Args:
            flower_type (int): The type of flower seeds to add.
            num_seeds (int): The number of seeds to add.
        """
        self.seeds[flower_type] += num_seeds
