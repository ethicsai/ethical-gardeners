"""
The WorldGrid module represents the physical environment simulation grid.

This module defines the fundamental structures to represent the physical space
where agents (gardeners) interact with the environment, including cells and flowers.
"""

from enum import Enum


pollution_increment = 1
"""
Amount by which pollution increases each step on empty ground cells.

This constant determines how quickly ground cells become polluted when no
flowers are present.
"""

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
            self.pollution += pollution_increment

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


