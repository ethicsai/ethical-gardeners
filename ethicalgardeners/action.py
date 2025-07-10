"""
Actions module defines the possible actions agents can take in the environment.

This module contains:

* a function to create the Action enumeration that represents all possible
  actions a gardener agent can perform in the environment.
* a function to get a list of actions that do not involve planting flowers.
* a function to get the planting action corresponding to a specific flower
  type.

These actions are handled by the :py:class:`.ActionHandler` class.
"""
from enum import Enum, auto


def create_action_enum(num_flower_type=1):
    """
    Dynamically create an enumeration of actions for agents in the grid world
    based on the number of flower types.

    These actions allow agents to move around the grid, interact with flowers,
    or simply wait. This enum is created dynamically to allow for custom
    flower types when planting.

    Args:
        num_flower_type (int): The number of flower types available for
            planting. Defaults to 1.

    Returns:
        Enum: An enumeration of actions that agents can perform:

        * UP: Move up one cell.
        * DOWN: Move down one cell.
        * LEFT: Move left one cell.
        * RIGHT: Move right one cell.
        * HARVEST: Harvest a flower from the current cell.
        * WAIT: Do nothing for this turn.
        * PLANT_TYPE_i: Plant a flower of type i (where i is the index of the
          flower type, starting from 0).
    """
    actions = {
        'UP': 0,
        'DOWN': 1,
        'LEFT': 2,
        'RIGHT': 3,
        'HARVEST': 4,
        'WAIT': 5
    }

    # Add an action for each type of flower
    for i in range(num_flower_type):
        actions[f'PLANT_TYPE_{i}'] = auto()

    return Enum('Action', actions)


def get_non_planting_actions(action_enum):
    """
    Get a list of actions that do not involve planting flowers.

    This function filters out the planting actions from the provided action
    enumeration.

    Args:
        action_enum (Enum): The action enumeration containing all possible
            actions.

    Returns:
        list: A list of actions that do not involve planting flowers.
    """
    return [action for action in action_enum
            if not action.name.startswith('PLANT_TYPE_')]


def get_planting_action_for_type(action_enum, flower_type):
    """
    Returns the planting action corresponding to the specified flower type.

    Args:
        action_enum (Enum): The action enumeration containing all possible
            actions.
        flower_type (int): The index of the flower type (0, 1, 2, ...).

    Returns:
        Enum member: The planting action for the specified flower type.
        None: If no corresponding action is found.
    """
    action_name = f'PLANT_TYPE_{flower_type}'
    for action in action_enum:
        if action.name == action_name:
            return action
    return None
