"""
Unit tests for the Observation module.

This module tests the different observation strategies to ensure they
correctly generate observations based on the world state.
"""
import unittest
from unittest.mock import Mock
import numpy as np

from ethicalgardeners.observation import TotalObservation, PartialObservation
from ethicalgardeners.worldgrid import CellType


class TestTotalObservation(unittest.TestCase):
    """
    Tests for the TotalObservation strategy.

    Ensures that the TotalObservation strategy correctly provides
    full grid observations.
    """

    def setUp(self):
        """
        Set up test fixtures.

        Creates mock grid world and agent objects for testing.
        """
        self.grid_world = Mock()
        self.grid_world.width = 5
        self.grid_world.height = 4
        self.grid_world.grid = np.zeros((5, 4), dtype=np.int8)

        # Set some test values in the grid
        self.grid_world.grid[1, 1] = CellType.OBSTACLE.value
        self.grid_world.grid[2, 2] = CellType.WALL.value

        self.agents = {'agent1': Mock()}
        self.observation = TotalObservation(self.grid_world, self.agents)

    def test_observation_space(self):
        """
        Test observation space creation.

        Verifies that the observation space is a Box with the correct
        dimensions and data type.
        """
        space = self.observation.observation_space('agent1')
        self.assertEqual(space.shape, (5, 4))

    def test_get_observation(self):
        """
        Test observation generation.

        Ensures that the observation correctly reflects the current state of
        the grid.
        """
        obs = self.observation.get_observation(self.grid_world,
                                               'agent1')

        # Check observation dimensions
        self.assertEqual(obs.shape, (5, 4))

        # Check specific cell values
        self.assertEqual(obs[1, 1], CellType.OBSTACLE.value)
        self.assertEqual(obs[2, 2], CellType.WALL.value)

        # Check that all other cells are ground (0)
        self.assertEqual(obs[0, 0], 0)
        self.assertEqual(obs[4, 3], 0)


class TestPartialObservation(unittest.TestCase):
    """
    Tests for the PartialObservation strategy.

    Ensures that the PartialObservation strategy correctly provides limited
    view observations centered on an agent's position.
    """

    def setUp(self):
        """
        Set up test fixtures.

        Creates mock grid world and agent objects for testing with different
        viewing ranges.
        """
        self.grid_world = Mock()
        self.grid_world.width = 10
        self.grid_world.height = 10
        self.grid_world.grid = np.zeros((10, 10), dtype=np.int8)

        # Add some features to the grid
        self.grid_world.grid[5, 5] = CellType.OBSTACLE.value
        self.grid_world.grid[7, 7] = CellType.WALL.value

        # Create agent at position (5,5)
        self.agent = Mock()
        self.agent.position = (5, 5)
        self.agents = {'agent1': self.agent}

        # Create observation with a viewing range of 2
        self.observation = PartialObservation(self.agents, 2)

    def test_observation_space(self):
        """
        Test observation space creation.

        Verifies that the observation space is a Box with dimensions based on
        the viewing range.
        """
        space = self.observation.observation_space('agent1')
        self.assertEqual(space.shape, (5, 5))

    def test_get_observation_center(self):
        """
        Test observation generation for an agent in the center of the grid.

        Ensures that the partial observation correctly shows the area around
        the agent's position.
        """
        obs = self.observation.get_observation(self.grid_world,
                                               'agent1')

        # Check observation dimensions
        self.assertEqual(obs.shape, (5, 5))

        # Agent is at (5,5), so the obstacle should be at (2, 2)
        self.assertEqual(obs[2, 2], CellType.OBSTACLE.value)

        # Wall at (7,7) should be at (4, 4)
        self.assertEqual(obs[4, 4], CellType.WALL.value)

    def test_get_observation_edge(self):
        """
        Test observation generation for an agent near the edge of the grid.

        Ensures that the partial observation correctly handles grid boundaries
        by filling with zeros.
        """
        # Move agent to corner (0,0)
        self.agent.position = (0, 0)

        obs = self.observation.get_observation(self.grid_world,
                                               'agent1')

        # Check that areas outside the grid are filled with zeros only the
        # bottom-right quadrant of the observation should have valid values
        for i in range(self.observation.observation_shape[0]):
            for j in range(self.observation.observation_shape[1]):
                x = j - self.observation.range
                y = i - self.observation.range

                if x < 0 or y < 0:
                    self.assertEqual(obs[i, j], 0,
                                     f"Position ({i},{j}) should be 0")