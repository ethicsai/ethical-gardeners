"""
The Observation module defines how agents perceive the environment in the
Ethical Gardeners simulation.

This module implements different observation strategies to control what
information agents can access about the environment. It provides:

1. An abstract strategy interface for implementing custom observation methods

2. Two concrete implementations:

   - Complete grid visibility (TotalObservation)
   - Limited visibility range (PartialObservation)

Observations are formatted as numpy arrays compatible with Gymnasium
environments.

Custom observation strategies can be implemented by extending the 
ObservationStrategy class and implementing the required methods.
"""
from abc import ABC, abstractmethod
import gymnasium as gym
from gymnasium.spaces import Box
import numpy as np

from ethicalgardeners.worldgrid import CellType

class ObservationStrategy(ABC):
    """
    Abstract base class defining the interface for observation strategies.

    Observation strategies determine how agents perceive the environment,
    defining the structure of the observation space and how observations
    are generated from the world state.

    Attributes:
        agents (dict): A dictionary mapping the gymnasium IDs of the agents
            that will receive observations to their objects.
    """

    def __init__(self, agents):
        """
        Create the observation strategy.

        Args:
            agents (dict): A dictionary mapping the gymnasium IDs of the agents
                that will receive observations to their objects.
        """
        self.agents = agents

    @abstractmethod
    def observation_space(self, agent):
        """
        Define the observation space for a specific agent.

        Args:
            agent (str): The agent for which to define the observation space.

        Returns:
            gym.Space: The observation space for the specified agent.
        """
        pass

    @abstractmethod
    def get_observation(self, grid_world, agent):
        """
        Generate an observation for an agent based on the current world state.

        Args:
            grid_world (:py:class:`.WorldGrid`): The current state of the grid.
            agent (str): The agent for which to generate the observation.

        Returns:
            numpy.ndarray: The observation for the specified agent.
        """
        pass

class TotalObservation(ObservationStrategy):
    """
    Strategy that provides agents with a complete view of the entire grid.

    This strategy gives agents perfect information about the state of the
    environment, including all cells, agents, and flowers.

    Attributes:
        observation_shape (tuple): The dimensions of the observation
            (width, height).
    """

    def __init__(self, grid_world, agents):
        """
        Create the total observation strategy.

        Args:
            grid_world (:py:class:`.WorldGrid`): The grid world environment to
                observe.
            agents (dict): A dictionary mapping the gymnasium IDs of the agents
                that will receive observations to their objects.
        """
        super().__init__(agents)
        self.observation_shape = (grid_world.width, grid_world.height)

    def observation_space(self, agent):
        """
        Define the observation space as a Box with the full grid dimensions.

        Args:
            agent (str): The agent for which to define the observation space.

        Returns:
            gym.spaces.Box: A box space with dimensions matching the full grid.
        """
        return Box(low=0, high=len(CellType), shape=self.observation_shape,
                   dtype=np.int8)

    def get_observation(self, grid_world, agent):
        """
        Generate a complete observation of the entire grid.

        Args:
            grid_world (:py:class:`.WorldGrid`): The current state of the grid.
            agent (str): The agent for which to generate the observation.

        Returns:
            numpy.ndarray: A 2D array containing the full grid state.
        """
        obs = np.zeros(self.observation_shape, dtype=np.int8)

        for x in range(self.observation_shape[0]):
            for y in range(self.observation_shape[1]):
                obs[x, y] = grid_world.grid[x, y]

        return obs

class PartialObservation(ObservationStrategy):
    """
    Strategy that provides agents with a limited view around their position.

    This strategy simulates limited perception by only showing agents a
    square area centered on their current position.

    Attributes:
        range (int): The visibility range in cells around the agent's position.
        observation_shape (tuple): The dimensions of the observation
            (2*range+1, 2*range+1).
    """

    def __init__(self, agents, range=1):
        """
        Create the partial observation strategy.

        Args:
            agents (dict): A dictionary mapping the gymnasium IDs of the agents
                that will receive observations to their objects.
            range (int, optional): The number of cells visible in each
                direction from the agent.
        """
        super().__init__(agents)
        self.range = range
        self.observation_shape = (2 * range + 1, 2 * range + 1)

    def observation_space(self, agent):
        """
        Define the observation space as a Box with dimensions based on the
        range.

        Args:
            agent (str): The agent for which to define the observation space.

        Returns:
            gym.spaces.Box: A box space with dimensions based on the visibility
            range.
        """
        return Box(low=0, high=len(CellType), shape=self.observation_shape,
                   dtype=np.int8)

    def get_observation(self, grid_world, agent):
        """
        Generate a partial observation centered on the agent's position.

        Areas outside the grid boundaries appear as zeros in the observation.

        Args:
            grid_world (:py:class:`.WorldGrid`): The current state of the grid.
            agent (str): The agent for which to generate the observation.

        Returns:
            numpy.ndarray: A 2D array containing the visible portion of the
                grid.
        """
        obs = np.zeros(self.observation_shape, dtype=np.int8)
        agent_x, agent_y = self.agents[agent].position

        for i in range(self.observation_shape[0]):
            for j in range(self.observation_shape[1]):
                x = agent_x + j - self.range
                y = agent_y + i - self.range

                if 0 <= y < grid_world.height and 0 <= x < grid_world.width:
                    obs[i, j] = grid_world.grid[x, y]

        return obs
