"""
Actions module defines the possible actions agents can take in the environment.

This module contains the Action enumeration that represents all possible
actions a gardener agent can perform in the environment.
"""
from enum import Enum


class Action(Enum):
    """
    Enum representing the possible actions an agent can take in the environment.

    These actions allow agents to move around the grid, interact with flowers,
    or simply wait.

    Attributes:
        UP: Move up one cell.
        DOWN: Move down one cell.
        LEFT: Move left one cell.
        RIGHT: Move right one cell.
        PLANT: Plant a flower on the current cell.
        HARVEST: Harvest a flower from the current cell.
        WAIT: Do nothing for this turn.
    """
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    PLANT = 4
    HARVEST = 5
    WAIT = 6
