"""
The Observation module defines how agents perceive the environment in the
Ethical Gardeners simulation.

This module implements different observation strategies to control what
information agents can access about the environment. It provides:

1. An abstract strategy interface for implementing custom observation methods

2. Two concrete implementations:

   - Complete grid visibility (:py:class:`TotalObservation`)
   - Limited visibility range (:py:class:`PartialObservation`)

Observations are formatted as numpy arrays compatible with Gymnasium
environments.

Custom observation strategies can be implemented by extending the
ObservationStrategy class and implementing the required methods.
"""
from abc import ABC, abstractmethod
from gymnasium.spaces import Box
import numpy as np

from ethicalgardeners.constants import FEATURES_PER_CELL
from ethicalgardeners.worldgrid import CellType


class ObservationStrategy(ABC):
    """
    Abstract base class defining the interface for observation strategies.

    Observation strategies determine how agents perceive the environment,
    defining the structure of the observation space and how observations
    are generated from the world state.

    Attributes:
        agents (dict): A dictionary mapping the gymnasium IDs of the agents
            that will receive observations to their instances
            (e.g. Dict[AgentID, Agent])
    """

    def __init__(self, agents):
        """
        Create the observation strategy.

        Args:
            agents (dict): A dictionary mapping the gymnasium IDs of the agents
                that will receive observations to their instances
                (e.g. Dict[AgentID, Agent])
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

    Each cell in the grid is represented as a vector of features:

    * Cell type (normalized)
    * Pollution level (normalized)
    * Flower presence and type (normalized)
    * Flower growth stage (normalized)
    * Agent presence (normalized)
    * Agent X position (normalized)
    * Agent Y position (normalized)

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
                that will receive observations to their instances
                (e.g. Dict[AgentID, Agent])
        """
        super().__init__(agents)
        self.observation_shape = (grid_world.width, grid_world.height,
                                  FEATURES_PER_CELL)

    def observation_space(self, agent):
        """
        Define the observation space as a Box with the full grid and
        features per cell.

        Args:
            agent (str): The agent for which to define the observation space.

        Returns:
            gym.spaces.Box: A box space with dimensions
                (width, height, FEATURES_PER_CELL).
        """
        return Box(low=0, high=1, shape=self.observation_shape,
                   dtype=np.float32)

    def get_observation(self, grid_world, agent):
        """
        Generate a complete observation of the entire grid.

        Args:
            grid_world (:py:class:`.WorldGrid`): The current state of the grid.
            agent (str): The agent for which to generate the observation.

        Returns:
            numpy.ndarray: A 3D array containing the full grid state.
        """
        obs = np.zeros(self.observation_shape, dtype=np.float32)

        for x in range(self.observation_shape[0]):
            for y in range(self.observation_shape[1]):
                cell = grid_world.get_cell((x, y))

                # Feature 1: Cell type (normalized)
                obs[x, y, 0] = cell.cell_type.value / len(CellType)

                # Feature 2: Pollution level (normalized)
                pollution_normalized = (
                        (cell.pollution - grid_world.min_pollution) /
                        (grid_world.max_pollution - grid_world.min_pollution)
                )
                obs[x, y, 1] = pollution_normalized

                # Feature 3: Flower presence and type (normalized)
                if cell.has_flower():
                    flower_type_normalized = (
                        (cell.flower.flower_type + 1) /
                        len(grid_world.flowers_data)
                    )
                    obs[x, y, 2] = flower_type_normalized

                    # Feature 4: Flower growth stage (normalized)
                    growth_stage_normalized = (
                        (cell.flower.current_growth_stage + 1) /
                        (cell.flower.num_growth_stage + 1)
                    )
                    obs[x, y, 3] = growth_stage_normalized

                # Feature 5: Agent presence (normalized)
                if cell.has_agent():
                    # Find the index of the agent in the grid world
                    agent_idx = None
                    for i, ag in enumerate(grid_world.agents):
                        if cell.agent == ag:
                            agent_idx = i
                            break

                    if agent_idx is not None:
                        agent_normalized = (
                                (agent_idx + 1) / len(grid_world.agents)
                        )
                        obs[x, y, 4] = agent_normalized

                # Feature 6: Agent X position (normalized)
                obs[x, y, 5] = (
                        self.agents[agent].position[0] / (grid_world.width - 1)
                )

                # Feature 7: Agent Y position (normalized)
                obs[x, y, 6] = (
                        self.agents[agent].position[1] /
                        (grid_world.height - 1)
                )

        return obs


class PartialObservation(ObservationStrategy):
    """
    Strategy that provides agents with a limited view around their position.

    This strategy simulates limited perception by only showing agents a
    square area centered on their current position.

    Each cell in the visible area is represented as a vector of features:

    * Cell type (normalized)
    * Pollution level (normalized)
    * Flower presence and type (normalized)
    * Flower growth stage (normalized)
    * Agent presence (normalized)
    * Agent's X position (normalized)
    * Agent's Y position (normalized)

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
                that will receive observations to their instances
                (e.g. Dict[AgentID, Agent])
            range (int, optional): The number of cells visible in each
                direction from the agent.
        """
        super().__init__(agents)
        self.range = range
        self.observation_shape = (2 * range + 1, 2 * range + 1,
                                  FEATURES_PER_CELL)

    def observation_space(self, agent):
        """
        Define the observation space as a Box with dimensions based on the
        range.

        Args:
            agent (str): The agent for which to define the observation space.

        Returns:
            gym.spaces.Box: A box space with dimensions based on the visibility
            range and features per cell.
        """
        return Box(low=0, high=1, shape=self.observation_shape,
                   dtype=np.float32)

    def get_observation(self, grid_world, agent):
        """
        Generate a partial observation centered on the agent's position.

        Each cell in the visible area is represented with multiple features.
        Areas outside the grid boundaries appear as zeros in the observation.

        Args:
            grid_world (:py:class:`.WorldGrid`): The current state of the grid.
            agent (str): The agent for which to generate the observation.

        Returns:
            numpy.ndarray: A 3D array containing the visible portion of the
                grid with all features.
        """
        obs = np.zeros(self.observation_shape, dtype=np.float32)
        agent_x, agent_y = self.agents[agent].position

        for i in range(self.observation_shape[0]):
            for j in range(self.observation_shape[1]):
                x = agent_x + j - self.range
                y = agent_y + i - self.range

                if 0 <= y < grid_world.height and 0 <= x < grid_world.width:
                    cell = grid_world.get_cell((x, y))

                    # Feature 1: Cell type (normalized)
                    obs[i, j, 0] = cell.cell_type.value / len(CellType)

                    # Feature 2: Pollution level (normalized)
                    pollution_normalized = (
                        (cell.pollution - grid_world.min_pollution) /
                        (grid_world.max_pollution - grid_world.min_pollution)
                    )
                    obs[i, j, 1] = pollution_normalized

                    # Feature 3: Flower presence and type (normalized)
                    if cell.has_flower():
                        flower_type_normalized = (
                            (cell.flower.flower_type + 1) /
                            len(grid_world.flowers_data)
                        )
                        obs[i, j, 2] = flower_type_normalized

                        # Feature 4: Flower growth stage (normalized)
                        growth_stage_normalized = (
                            (cell.flower.current_growth_stage + 1) /
                            (cell.flower.num_growth_stage + 1)
                        )
                        obs[i, j, 3] = growth_stage_normalized

                    # Feature 5: Agent presence (normalized)
                    if cell.has_agent():
                        # Find the index of the agent in the grid world
                        agent_idx = None
                        for idx, ag in enumerate(grid_world.agents):
                            if cell.agent == ag:
                                agent_idx = idx
                                break

                        if agent_idx is not None:
                            agent_normalized = (
                                (agent_idx + 1) / len(grid_world.agents)
                            )
                            obs[i, j, 4] = agent_normalized

                    # Feature 6: Agent X position (normalized)
                    obs[i, j, 5] = agent_x / (grid_world.width - 1)

                    # Feature 7: Agent Y position (normalized)
                    obs[i, j, 6] = agent_y / (grid_world.height - 1)

        return obs
