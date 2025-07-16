"""
Module containing reward functions for the Ethical Gardeners environment.

This module defines some reward function used to compute rewards for agents:

* :py:meth:`~RewardFunctions.compute_ecology_reward`: Computes the ecological
  reward based on the agent's action, specifically for planting and
  harvesting flowers.
* :py:meth:`~RewardFunctions.compute_wellbeing_reward`: Computes the well-being
  reward based on the agent's action, specifically for selling flowers and
  giving a penalty for not earning money.
* :py:meth:`~RewardFunctions.compute_biodiversity_reward`: Computes the
  biodiversity reward based on the number of different flower types planted
  by all the agents and how much the agent helps increase diversity.
"""
from math import log

from ethicalgardeners.constants import MAX_PENALTY_TURNS


class RewardFunctions:
    """
    Class for computing rewards in the Ethical Gardeners environment.

    This class is responsible for calculating different types of rewards for
    agents based on their actions in the environment. The rewards are designed
    to encourage ecologically beneficial behaviors, well-being, and
    biodiversity.

    Each reward component is normalized to a range between -1 and 1.

    Attributes:
        action_enum (enum): An enumeration of possible actions (UP, DOWN,
            LEFT, RIGHT, HARVEST, WAIT, PLANT_TYPE_i). Created dynamically
            based on the number of flower types available.
    """

    def __init__(self, action_enum):
        """Create the RewardFunctions object.

        Args:
            action_enum (enum): An enumeration of possible actions (UP, DOWN,
                LEFT, RIGHT, HARVEST, WAIT, PLANT_TYPE_i). Created dynamically
                based on the number of flower types available.
        """
        self.action_enum = action_enum

    def compute_reward(self, grid_world_prev, grid_world, agent, action):
        """
        Compute the mono-objective reward for an agent based on its action in
        the environment.

        The reward is a combination of ecological, well-being, and biodiversity
        rewards, normalized to a range between -1 and 1.

        Args:
            grid_world_prev (:py:class:`.WorldGrid`): The grid world
                environment before the action.
            grid_world (:py:class:`.WorldGrid`): The grid world environment.
            agent (:py:class:`.Agent`): The agent performing the action.
            action (:py:attr:`action_enum`): The action performed.

        Returns:
            dict: A dictionary containing the ecological, well-being, and
            biodiversity rewards, as well as the total reward averaged across
            these components.
        """
        ecology_reward = self.compute_ecology_reward(grid_world_prev,
                                                     grid_world, agent, action)
        wellbeing_reward = self.compute_wellbeing_reward(grid_world_prev,
                                                         grid_world, agent,
                                                         action)
        biodiversity_reward = self.compute_biodiversity_reward(grid_world_prev,
                                                               grid_world,
                                                               agent, action)

        return {'ecology': ecology_reward,
                'wellbeing': wellbeing_reward,
                'biodiversity': biodiversity_reward,
                'total': (ecology_reward + wellbeing_reward +
                          biodiversity_reward) / 3}

    def compute_ecology_reward(self, grid_world_prev, grid_world, agent,
                               action):
        """
        Compute the ecological reward for an agent based on its action in the
        environment.

        For planting actions, calculates the expected future impact of
        pollution reduction, normalized against the maximum theoretical impact.
        For harvesting actions, multiply the impact the flower had on the
        environment before harvesting with the pollution of the cell, also
        normalized against the maximum. Penalizes harvesting actions only if
        the pollution level is above the minimum pollution level.


        Args:
            grid_world_prev (:py:class:`.WorldGrid`): The grid world
                environment before the action.
            grid_world (:py:class:`.WorldGrid`): The grid world environment.
            agent (:py:class:`.Agent`): The agent performing the action.
            action (:py:attr:`action_enum`): The action performed.

        Returns:
            float: The normalized ecological reward (between -1 and 1) for
            planting and harvesting actions, or 0 for other actions.
        """
        # Reward computed only for planting and harvesting actions
        if action not in self.action_enum.get_non_planting_actions():
            p_max = grid_world.max_pollution
            p_min = grid_world.min_pollution
            position = agent.position
            cell = grid_world.get_cell(position)

            # Check if a flower has been planted in the cell
            if not cell.has_flower():
                return 0.0

            flower = cell.flower
            flower_type = flower.flower_type
            flower_pollution_reduction = (
                grid_world.flowers_data[flower_type]['pollution_reduction'])

            # Current pollution level in the cell
            cell_pollution = cell.pollution

            # Compute the maximum possible impact
            r_max = (p_max - p_min) * 1/0.01

            # Compute the expected future impact of pollution reduction
            r_plant = (sum(flower_pollution_reduction) * 1 / (
                        cell_pollution - p_max + 0.01))  # Avoid zero-division

            # Normalize the reward against the maximum possible impact
            if r_max > 0:
                return r_plant / r_max
            else:
                return 0.0
        elif action == self.action_enum.HARVEST:
            p_max = grid_world.max_pollution
            p_min = grid_world.min_pollution
            position = agent.position
            prev_cell = grid_world_prev.get_cell(position)
            cell = grid_world.get_cell(position)

            # Check if a flower has been harvested in the cell
            if cell.has_flower():
                return 0.0

            # Check if the previous cell had a flower
            if not prev_cell.has_flower():
                return 0.0

            flower = prev_cell.flower
            flower_type = flower.flower_type
            if len(grid_world.flowers_data[
                       flower_type]['pollution_reduction']) == 0:
                return 0.0
            flower_pollution_grown_reduction = (
                grid_world.flowers_data[flower_type]['pollution_reduction'][-1])

            # Current pollution level in the cell
            cell_pollution = cell.pollution

            # Compute the maximum possible impact
            r_max = p_max - p_min

            # Compute the expected future impact of pollution reduction
            r_harvest = (flower_pollution_grown_reduction *
                         (cell_pollution - p_min))

            # Normalize the reward against the maximum possible impact
            if r_max > 0:
                return r_harvest / r_max
            else:
                return 0.0
        else:
            return 0.0

    def compute_wellbeing_reward(self, grid_world_prev, grid_world, agent,
                                 action):
        """
        Compute the well-being reward for an agent based on its action in the
        environment.

        Well-being rewards are calculated based on the price of the harvested
        flowers compared to the most expensive flower type. Penalises the agent
        for not earning money by giving a penalty based on the number of turns
        without income, normalized to a maximum penalty.

        Args:
            grid_world_prev (:py:class:`.WorldGrid`): The grid world
                environment before the action.
            grid_world (:py:class:`.WorldGrid`): The grid world environment.
            agent (:py:class:`.Agent`): The agent performing the action.
            action (:py:attr:`action_enum`): The action performed.
        Returns:
            float: The normalized well-being reward (between -1 and 1).
        """
        # Reward computed only for harvesting actions
        if action == self.action_enum.HARVEST:
            position = agent.position
            prev_cell = grid_world_prev.get_cell(position)
            cell = grid_world.get_cell(position)

            # Check if a flower has been harvested in the cell
            if cell.has_flower():
                return 0.0

            # Check if the previous cell had a flower
            if not prev_cell.has_flower():
                return 0.0

            flower = prev_cell.flower
            flower_type = flower.flower_type

            # Get the monetary value of the flower
            flower_value = grid_world.flowers_data[flower_type]['price']

            # Normalize the reward based on the maximum possible value
            highest_flower_value = max(
                grid_world.flowers_data[ft]['price'] for ft in
                grid_world.flowers_data)
            return flower_value / highest_flower_value
        else:
            # Calculate penalty for not earning money
            return -min(agent.turns_without_income / MAX_PENALTY_TURNS, 1.0)

    def compute_biodiversity_reward(self, grid_world_prev, grid_world, agent,
                                    action):
        """
        Compute the biodiversity reward for an agent based on its action in the
        environment.

        Biodiversity rewards are calculated based on the number of different
        flower types planted by the agent using the Shannon-Wiener index.
        Compares the index before and after the planting action to determine
        the impact.

        Args:
            grid_world_prev (:py:class:`.WorldGrid`): The grid world
                environment before the action.
            grid_world (:py:class:`.WorldGrid`): The grid world environment.
            agent (:py:class:`.Agent`): The agent performing the action.
            action (:py:attr:`action_enum`): The action performed.

        Returns:
            float: The normalized biodiversity reward (between -1 and 1).
        """
        if action in self.action_enum.get_non_planting_actions():
            return 0.0

        position = agent.position
        cell = grid_world.get_cell(position)

        # Check if a flower has been planted in the cell
        if not cell.has_flower():
            return 0.0

        # Get the flower type that has been planted
        planted_flower_type = cell.flower.flower_type

        # Count the number of different flower types planted by all agents
        flowers = {flower_type: 0 for flower_type in
                   grid_world.flowers_data.keys()}
        total_flowers = 0

        for agent in grid_world.agents:
            for flower_type, count in agent.flowers_planted.items():
                flowers[flower_type] += count
                total_flowers += count

        # Create a dictionary to hold the flower counts before planting
        prev_flowers = dict(flowers)  # Copy current flower counts
        prev_flowers[planted_flower_type] -= 1  # Remove the planted flower
        prev_total = total_flowers - 1

        # Compute the ratio of each flower type and use Shannon-Wiener index
        # to compute biodiversity
        # before
        prev_biodiversity = 0
        for flower_type in prev_flowers:
            if prev_flowers[flower_type] > 0:
                ratio = prev_flowers[flower_type] / prev_total
                prev_biodiversity -= ratio * log(ratio)

        # after
        biodiversity = 0
        for flower_type in flowers:
            if flowers[flower_type] > 0:
                ratio = flowers[flower_type] / total_flowers
                biodiversity -= ratio * log(ratio)

        max_biodiversity = log(len(grid_world.flowers_data))

        # Compute the impact of the agent's planting action and normalize
        if max_biodiversity > 0:
            return (biodiversity - prev_biodiversity) / max_biodiversity
        else:
            return 0.0
