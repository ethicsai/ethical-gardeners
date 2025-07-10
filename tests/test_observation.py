"""
Unit tests for the Observation module.

This module tests the different observation strategies to ensure they
correctly generate observations based on the world state.
"""
import unittest
from unittest.mock import Mock
import numpy as np

from ethicalgardeners.constants import FEATURES_PER_CELL
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
        Set up tests.

        Creates mock grid world and agent objects for testing.
        """
        self.grid_world = Mock()
        self.grid_world.width = 10
        self.grid_world.height = 10
        self.grid_world.min_pollution = 0
        self.grid_world.max_pollution = 100

        self.grid_world.flowers_data = {
            0: {"price": 10, "pollution_reduction": [0, 0, 0, 0, 5]},
            1: {"price": 5, "pollution_reduction": [0, 0, 1, 3]},
            2: {"price": 2, "pollution_reduction": [1]}
        }

        # Create a GROUND mock cell
        self.mock_ground_cell = Mock()
        self.mock_ground_cell.cell_type = CellType.GROUND
        self.mock_ground_cell.pollution = 50
        self.mock_ground_cell.has_agent = lambda: False
        self.mock_ground_cell.has_flower = lambda: False

        # Create an OBSTACLE mock cell
        self.mock_obstacle_cell = Mock()
        self.mock_obstacle_cell.cell_type = CellType.OBSTACLE
        self.mock_obstacle_cell.pollution = 0
        self.mock_obstacle_cell.has_agent = lambda: False
        self.mock_obstacle_cell.has_flower = lambda: False

        # Create a GROUND cell with a flower
        self.mock_flower_cell = Mock()
        self.mock_flower_cell.cell_type = CellType.GROUND
        self.mock_flower_cell.pollution = 25
        self.mock_flower_cell.has_agent = lambda: False
        self.mock_flower_cell.has_flower = lambda: True

        self.mock_flower = Mock()
        self.mock_flower.flower_type = 0
        self.mock_flower.current_growth_stage = 2
        self.mock_flower.num_growth_stage = 4
        self.mock_flower_cell.flower = self.mock_flower

        # Set get_cell to return different cells based on position
        def get_cell_side_effect(position):
            if position == (2, 2):
                return self.mock_obstacle_cell
            elif position == (8, 8):
                return self.mock_flower_cell
            else:
                return self.mock_ground_cell

        self.grid_world.get_cell.side_effect = get_cell_side_effect

        # Create a mock agent at (5, 5)
        self.mock_agent = Mock()
        self.mock_agent.position = (5, 5)
        self.grid_world.agents = [self.mock_agent]

        self.agents = {'agent1': self.mock_agent}

        self.observation = TotalObservation(self.grid_world, self.agents)

    def test_observation_space(self):
        """
        Test observation space creation.

        Verifies that the observation space is a Box with the correct
        dimensions and data type.
        """
        space = self.observation.observation_space('agent1')
        self.assertEqual(space.shape, (10, 10, FEATURES_PER_CELL))

    def test_get_observation(self):
        """
        Test observation generation.

        Ensures that the observation correctly reflects the current state of
        the grid.
        """
        obs = self.observation.get_observation(self.grid_world,
                                               'agent1')

        # Check observation dimensions
        self.assertEqual(obs.shape, (10, 10, FEATURES_PER_CELL))

        # Check specific cell values
        self.assertEqual(obs[1, 1, 0], CellType.GROUND.value / len(CellType))

        # Obstacle at (2, 2)
        self.assertAlmostEqual(obs[2, 2, 0],
                               CellType.OBSTACLE.value / len(CellType))

        # Flower at (8, 8)
        self.assertAlmostEqual(obs[8, 8, 0],
                               CellType.GROUND.value / len(CellType))
        self.assertTrue(obs[8, 8, 2] > 0)  # Flower is present
        self.assertAlmostEqual(obs[8, 8, 3],
                               (2 + 1) / (4 + 1))  # Current growth stage


class TestPartialObservation(unittest.TestCase):
    """
    Tests for the PartialObservation strategy.

    Ensures that the PartialObservation strategy correctly provides limited
    view observations centered on an agent's position.
    """

    def setUp(self):
        """
        Set up tests.

        Creates mock grid world and agent objects for testing with different
        viewing ranges.
        """
        self.grid_world = Mock()
        self.grid_world.width = 10
        self.grid_world.height = 10
        self.grid_world.min_pollution = 0
        self.grid_world.max_pollution = 100

        self.grid_world.flowers_data = {
            0: {"price": 10, "pollution_reduction": [0, 0, 0, 0, 5]},
            1: {"price": 5, "pollution_reduction": [0, 0, 1, 3]},
            2: {"price": 2, "pollution_reduction": [1]}
        }

        # Create a GROUND mock cell
        self.mock_ground_cell = Mock()
        self.mock_ground_cell.cell_type = CellType.GROUND
        self.mock_ground_cell.pollution = 50
        self.mock_ground_cell.has_agent = lambda: False
        self.mock_ground_cell.has_flower = lambda: False

        # Create an OBSTACLE mock cell
        self.mock_obstacle_cell = Mock()
        self.mock_obstacle_cell.cell_type = CellType.OBSTACLE
        self.mock_obstacle_cell.pollution = 0
        self.mock_obstacle_cell.has_agent = lambda: False
        self.mock_obstacle_cell.has_flower = lambda: False

        # Create a GROUND cell with a flower
        self.mock_flower_cell = Mock()
        self.mock_flower_cell.cell_type = CellType.GROUND
        self.mock_flower_cell.pollution = 25
        self.mock_flower_cell.has_agent = lambda: False
        self.mock_flower_cell.has_flower = lambda: True

        self.mock_flower = Mock()
        self.mock_flower.flower_type = 0
        self.mock_flower.current_growth_stage = 2
        self.mock_flower.num_growth_stage = 4
        self.mock_flower_cell.flower = self.mock_flower

        # Set get_cell to return different cells based on position
        def get_cell_side_effect(position):
            if position == (3, 3):
                return self.mock_obstacle_cell
            elif position == (7, 7):
                return self.mock_flower_cell
            else:
                return self.mock_ground_cell

        self.grid_world.get_cell.side_effect = get_cell_side_effect

        # Create a mock agent at (5, 5)
        self.mock_agent = Mock()
        self.mock_agent.position = (5, 5)
        self.grid_world.agents = [self.mock_agent]

        self.agents = {'agent1': self.mock_agent}

        # Create observation with a viewing range of 2
        self.observation = PartialObservation(self.agents, 2)

    def test_observation_space(self):
        """
        Test observation space creation.

        Verifies that the observation space is a Box with dimensions based on
        the viewing range.
        """
        space = self.observation.observation_space('agent1')
        self.assertEqual(space.shape, (5, 5, FEATURES_PER_CELL))

    def test_get_observation_center(self):
        """
        Test observation generation for an agent in the center of the grid.

        Ensures that the partial observation correctly shows the area around
        the agent's position.
        """
        obs = self.observation.get_observation(self.grid_world,
                                               'agent1')

        # Check observation dimensions
        self.assertEqual(obs.shape, (5, 5, FEATURES_PER_CELL))

        # Agent is at (5,5), so the obstacle should be at (2, 2)
        self.assertAlmostEqual(obs[2, 2, 0],
                               CellType.GROUND.value / len(CellType))

        # Obstacle at (3, 3) should be at (0, 0)
        self.assertAlmostEqual(obs[0, 0, 0],
                               CellType.OBSTACLE.value / len(CellType))

        # Flower at (7, 7) should be at (4, 4)
        self.assertAlmostEqual(obs[4, 4, 0],
                               CellType.GROUND.value / len(CellType))
        self.assertTrue(obs[4, 4, 2] > 0)  # Flower is present
        self.assertAlmostEqual(obs[4, 4, 3],
                               (2 + 1)/(4 + 1))  # Current growth stage

    def test_get_observation_edge(self):
        """
        Test observation generation for an agent near the edge of the grid.

        Ensures that the partial observation correctly handles grid boundaries
        by filling with zeros.
        """
        # Move agent to corner (0,0)
        self.mock_agent.position = (0, 0)

        obs = self.observation.get_observation(self.grid_world,
                                               'agent1')

        # Check that areas outside the grid are filled with zeros only the
        # bottom-right quadrant of the observation should have valid values
        for i in range(self.observation.observation_shape[0]):
            for j in range(self.observation.observation_shape[1]):
                x = j - self.observation.range
                y = i - self.observation.range

                if x < 0 or y < 0:
                    self.assertTrue(np.all(obs[i, j, :2] == 0))
