"""
Actions module defines the possible actions agents can take in the environment.

This module contains:

* a function to create the Action enumeration that represents all possible
  actions a gardener agent can perform in the environment.
* methods to get actions that do not involve planting flowers.
* methods to get the planting action corresponding to a specific flower type.

These actions are handled by the :py:class:`.ActionHandler` class.
"""
from enum import Enum, auto


class _ActionEnum(Enum):
    """
    Custom enum for actions.

    :meta public:
    """

    def __init__(self, *args, **kwargs):
        """
        Create the action enum.

        This constructor initializes the action enum and extracts the flower
        type for planting actions.
        """
        super().__init__()
        if self.name.startswith('PLANT_TYPE_'):
            # Extract the flower type from the name
            # Remember that the name must be formatted as `PLANT_TYPE_{i}`,
            # we are interested in getting the `{i}`.
            flower_type = self.name.replace('PLANT_TYPE_', '')
            self.flower_type = int(flower_type)
        else:
            self.flower_type = None

    @classmethod
    def get_non_planting_actions(cls):
        """
        Get a list of actions that do not involve planting flowers.

        Returns:
            list: A list of actions that do not involve planting flowers.
        """
        return [
            action for action in cls
            if not action.name.startswith('PLANT_TYPE_')
        ]

    @classmethod
    def get_planting_action_for_type(cls, flower_type):
        """
        Returns the planting action corresponding to the specified flower type.

        Args:
            flower_type (int): The index of the flower type (0, 1, 2, ...).

        Returns:
            Enum member: The planting action for the specified flower type.
            None: If no corresponding action is found.
        """
        action_name = f'PLANT_TYPE_{flower_type}'
        try:
            return cls[action_name]
        except KeyError:
            return None


def create_action_enum(num_flower_type=1):
    """
    Dynamically create an enumeration of actions for agents in the grid world
    based on the number of flower types.

    Args:
        num_flower_type (int): The number of flower types available for
            planting. Defaults to 1.

    Returns:
        Enum: An enumeration of actions that agents can perform.
    """
    actions = {
        'UP': 0,
        'DOWN': 1,
        'LEFT': 2,
        'RIGHT': 3,
        'HARVEST': 4,
        'WAIT': 5,
    }

    for i in range(num_flower_type):
        action_name = f'PLANT_TYPE_{i}'
        actions[action_name] = auto()

    return Enum('Action', actions, type=_ActionEnum)
