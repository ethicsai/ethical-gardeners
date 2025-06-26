"""
The WorldGrid module represents the physical environment simulation grid.

This module defines the fundamental structures to represent the physical space
where agents (gardeners) interact with the environment, including cells and flowers.
"""
from enum import Enum
from ethicalgardeners.Constants import POLLUTION_INCREMENT, FLOWERS_DATA


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

    It can contain a flower, an agent, and has a pollution level that evolves over time.

    Attributes:
        cell_type (CellType): Type of the cell (ground, obstacle, wall).
        flower (Flower): The flower present in this cell, if any.
        Agent (Agent): The agent currently occupying this cell, if any.
        pollution (float): Current pollution level of the cell.
    """

    def __init__(self, cell_type, pollution):
        """
        Create a new cell.

        Args:
            cell_type (CellType): The type of cell to create.
            pollution (float): Initial pollution level of the cell.
        """
        self.cell_type = cell_type
        self.flower = None
        self.Agent = None
        self.pollution = pollution

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
            self.pollution += POLLUTION_INCREMENT

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
    Different flower types have different growth patterns, prices, and pollution
    reduction capabilities.

    Attributes:
        position (tuple): The (x, y) coordinates of the flower in the grid.
        flower_type (int): The type of flower, determining its growth and pollution reduction.
        price (float): The monetary value of the flower when harvested.
        pollution_reduction (list): List of pollution reduction values for each growth stage.
        num_growth_stage (int): Total number of growth stages for this flower.
        current_growth_stage (int): Current growth stage of the flower, starting at 0.
    """

    def __init__(self, position, flower_type):
        """
        Create a new flower.

        Args:
            position (tuple): The (x, y) coordinates where the flower is planted.
            flower_type (int): The type of flower to create.
        """
        self.position = position
        self.flower_type = flower_type
        self.price = FLOWERS_DATA[flower_type]['price']
        self.pollution_reduction = FLOWERS_DATA[flower_type]["pollution_reduction"]
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
            float: The amount of pollution reduced by this flower at its current stage.
        """
        return self.pollution_reduction[self.current_growth_stage]
