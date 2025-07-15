"""
Handles the execution of agent actions in the Ethical Gardeners simulation.
"""
import warnings

import numpy as np


class ActionHandler:
    """
    Handles the execution of agent actions in the grid world environment.

    The ActionHandler mediates between agents and the world grid, ensuring that
    actions are only executed when valid. It manages movement validation,
    flower planting and harvesting, and simple waiting actions.

    Attributes:
        grid_world (:py:class:`.WorldGrid`): The grid world environment where
            actions will be executed.
        action_enum (enum): An enumeration of possible actions (UP, DOWN,
            LEFT, RIGHT, HARVEST, WAIT, PLANT_TYPE_i). Created dynamically
            based on the number of flower types available.
    """

    def __init__(self, grid_world, action_enum):
        """
        Create the ActionHandler with a reference to the grid world.

        Args:
            grid_world (:py:class:`.WorldGrid`): The grid world environment
                where actions will be executed.
            action_enum (enum): An enumeration of possible actions (UP, DOWN,
                LEFT, RIGHT, HARVEST, WAIT, PLANT_TYPE_i). Created dynamically
                based on the number of flower types available.
        """
        self.grid_world = grid_world
        self.action_enum = action_enum  # Dynamically created Action enum

    def handle_action(self, agent, action):
        """
        Process an agent's action and execute it in the grid world.

        This method delegates to specific handler methods based on the action
        type.

        Args:
            agent (:py:class:`.Agent`): The agent performing the action.
            action (:py:attr:`action_enum`): The action to perform (UP,
                DOWN, LEFT, RIGHT, HARVEST, WAIT or PLANT_TYPE_i). PLANT_TYPE_i
                plants a flower of type i at the agent's current position.
        """
        if action in [self.action_enum.UP, self.action_enum.DOWN,
                      self.action_enum.LEFT, self.action_enum.RIGHT]:
            self.move_agent(agent, action)
        elif action == self.action_enum.HARVEST:
            self.harvest_flower(agent)
        elif action == self.action_enum.WAIT:
            self.wait(agent)
        else:  # Assume action is a PLANT_TYPE_i action
            self.plant_flower(agent, action.flower_type)

    def move_agent(self, agent, action):
        """
        Move an agent in the specified direction if the move is valid.

        Args:
            agent (:py:class:`.Agent`): The agent to move.
            action (:py:attr:`action_enum`): The direction to move (UP,
                DOWN, LEFT, RIGHT).
        """
        # Compute the new position based on the action
        new_position = self.compute_new_position(agent.position, action)

        if self.grid_world.valid_move(new_position):
            self.grid_world.get_cell(agent.position).agent = None

            agent.move(new_position)

            self.grid_world.get_cell(new_position).agent = agent

        else:
            warnings.warn(
                f"Invalid move attempted by {agent} towards {new_position}. "
                f"The agent remains at its current position."
            )

        agent.turns_without_income += 1

    def plant_flower(self, agent, flower_type):
        """
        Plant a flower of the specified type at the agent's current position.

        The agent must have available seeds of the specified flower type.

        Args:
            agent (:py:class:`.Agent`): The agent planting the flower.
            flower_type (int): The type of flower to plant.
        """
        agent.turns_without_income += 1

        cell = self.grid_world.get_cell(agent.position)
        if not agent.can_plant(flower_type):
            warnings.warn(
                f"Invalid plant attempted by {agent} with flower_type "
                f"{flower_type}. The agent does not have seeds of this type. "
                f"The action is ignored."
            )
            return
        elif not cell.can_plant_on():
            warnings.warn(
                f"Invalid plant attempted by {agent} with flower_type "
                f"{flower_type}. The cell at {agent.position} cannot be "
                f"planted on. The action is ignored."
            )
            return

        agent.use_seed(flower_type)
        self.grid_world.place_flower(agent.position, flower_type)

    def harvest_flower(self, agent):
        """
        Harvest a fully grown flower at the agent's current position.

        The flower must be fully grown to be harvested. Upon harvesting, the
        agent receives seeds and money based on the flower type.

        Args:
            agent (:py:class:`.Agent`): The agent harvesting the flower.
        """
        flower = self.grid_world.get_cell(agent.position).flower
        if not flower:
            warnings.warn(
                f"Invalid harvest attempted by {agent} with flower "
                f"{flower}. There is no flower at {agent.position}. The action"
                f" is ignored."
            )
            agent.turns_without_income += 1
            return

        if not flower.is_grown():
            warnings.warn(
                f"Invalid harvest attempted by {agent} with flower "
                f"{flower}. The flower is not fully grown. The action"
                f" is ignored."
            )
            agent.turns_without_income += 1
            return

        self.grid_world.remove_flower(agent.position)

        if self.grid_world.num_seeds_returned is not None:
            if self.grid_world.num_seeds_returned == -3:
                num_seeds_returned = (
                    self.grid_world.random_generator.randint(1, 5))
            else:
                num_seeds_returned = self.grid_world.num_seeds_returned
            agent.add_seed(flower.flower_type, num_seeds_returned)

        agent.add_money(
            self.grid_world.flowers_data[flower.flower_type]['price'])

    def wait(self, agent):
        """
        Perform a wait action, which does not change the state of the world.

        This action can be used by agents when they do not want to perform
        any other action in the current time step.
        """
        agent.turns_without_income += 1

    def update_action_mask(self, agent):
        """
        Update the action mask for all agents based on the current state of
        the grid world.

        This method checks the validity of each action for each agent and
        updates their action masks accordingly.

        Args:
            agent (:py:class:`.Agent`): The agent for which to update the
                action mask.
        """
        mask = np.ones(len(self.action_enum), dtype=bool)
        if not self.grid_world.valid_move(self.compute_new_position(
                agent.position, self.action_enum.UP)):
            mask[self.action_enum.UP.value] = 0
        if not self.grid_world.valid_move(self.compute_new_position(
                agent.position, self.action_enum.DOWN)):
            mask[self.action_enum.DOWN.value] = 0
        if not self.grid_world.valid_move(self.compute_new_position(
                agent.position, self.action_enum.LEFT)):
            mask[self.action_enum.LEFT.value] = 0
        if not self.grid_world.valid_move(self.compute_new_position(
                agent.position, self.action_enum.RIGHT)):
            mask[self.action_enum.RIGHT.value] = 0
        if not self.grid_world.get_cell(agent.position).flower or \
                not self.grid_world.get_cell(agent.position).flower.is_grown():
            mask[self.action_enum.HARVEST.value] = 0

        # Check planting actions for each flower type
        can_plant_on_cell = self.grid_world.get_cell(
            agent.position).can_plant_on()
        for i in range(len(agent.seeds)):
            plant_action = self.action_enum.get_planting_action_for_type(i)
            if not agent.can_plant(i) or not can_plant_on_cell:
                mask[plant_action.value] = 0

        agent.action_mask = mask

    def compute_new_position(self, position, action):
        """
        Compute the new position based on the current position and action.

        Args:
            position (tuple): The current (x, y) coordinates of the agent.
            action (:py:attr:`action_enum`): The action to perform
                (UP, DOWN, LEFT, RIGHT).

        Returns:
            tuple: The new (x, y) coordinates after applying the action.
        """
        if action == self.action_enum.UP:
            return (position[0] - 1, position[1])
        elif action == self.action_enum.DOWN:
            return (position[0] + 1, position[1])
        elif action == self.action_enum.LEFT:
            return (position[0], position[1] - 1)
        elif action == self.action_enum.RIGHT:
            return (position[0], position[1] + 1)
        else:
            return position
