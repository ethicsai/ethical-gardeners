import unittest
from unittest.mock import Mock, patch

from math import log

from ethicalgardeners.action import create_action_enum
from ethicalgardeners.rewardfunctions import RewardFunctions
from ethicalgardeners.constants import MAX_PENALTY_TURNS


class TestRewardFunctions(unittest.TestCase):
    """
    Tests for the RewardFunctions class.

    This test suite covers the reward calculation methods for ecology,
    wellbeing, biodiversity and combined rewards in the Ethical Gardeners
    environment.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.

        Creates a RewardFunctions instance and mocks for grid_world, agent,
        and actions.
        """
        self.action_enum = create_action_enum(3)

        self.reward_functions = RewardFunctions(self.action_enum)
        self.mock_grid_world_prev = Mock()
        self.mock_grid_world = Mock()
        self.mock_agent = Mock()

    def test_compute_reward(self):
        """
        Test the computeReward method that combines individual reward
        components.

        Verifies that the method correctly calls individual reward functions
        and averages their results for the total reward.
        """
        # Patch individual reward methods with predefined return values
        with patch.object(self.reward_functions,
                          'compute_ecology_reward',
                          return_value=0.5) as mock_ecology:
            with patch.object(self.reward_functions,
                              'compute_wellbeing_reward',
                              return_value=0.3) as mock_wellbeing:
                with patch.object(self.reward_functions,
                                  'compute_biodiversity_reward',
                                  return_value=0.2) as mock_biodiversity:
                    result = self.reward_functions.compute_reward(
                        self.mock_grid_world_prev,
                        self.mock_grid_world,
                        self.mock_agent,
                        self.action_enum.PLANT_TYPE_0
                    )

                    # Verify that individual reward methods were called
                    mock_ecology.assert_called_once()
                    mock_wellbeing.assert_called_once()
                    mock_biodiversity.assert_called_once()

                    # Verify correct reward calculation
                    expected = {
                        'ecology': 0.5,
                        'wellbeing': 0.3,
                        'biodiversity': 0.2,
                        'total': (0.5 + 0.3 + 0.2) / 3
                    }
                    self.assertEqual(result, expected)

    def test_compute_ecology_reward_plant(self):
        """
        Test computeEcologyReward method for planting action.

        Verifies reward calculation when an agent plants a flower.
        """
        # Set up the environment and agent
        self.mock_grid_world.max_pollution = 100
        self.mock_grid_world.min_pollution = 0
        self.mock_agent.position = (1, 1)

        # Set up the cell with a planted flower
        mock_cell = Mock()
        mock_cell.has_flower.return_value = True
        mock_cell.pollution = 50

        # Configure flower and cell
        mock_flower = Mock()
        mock_flower.flower_type = 0
        mock_cell.flower = mock_flower

        self.mock_grid_world.get_cell.return_value = mock_cell

        # Configure flower data with pollution reduction values
        flower_data = Mock()
        flower_data.pollution_reduction = [1, 2, 3]
        self.mock_grid_world.flowers_data = {0: flower_data}

        # Test the method
        result = self.reward_functions.compute_ecology_reward(
            self.mock_grid_world_prev,
            self.mock_grid_world,
            self.mock_agent,
            self.action_enum.PLANT_TYPE_0
        )

        # Calculate expected reward manually
        r_plant = sum([1, 2, 3]) * (1 / (50 - 100 + 0.01))  # 6 * (1/(-49.99))
        r_max = (100 - 0) * (1 / 0.01)  # 10000
        expected = r_plant / r_max

        self.assertAlmostEqual(result, expected)

    def test_compute_ecology_reward_harvest(self):
        """
        Test computeEcologyReward method for harvesting action.

        Verifies reward calculation when an agent harvests a flower.
        """
        # Set up the environment and agent
        self.mock_grid_world.max_pollution = 100
        self.mock_grid_world.min_pollution = 0
        self.mock_agent.position = (1, 1)

        # Set up cell states before and after harvesting
        mock_cell = Mock()
        mock_cell.has_flower.return_value = False
        mock_cell.pollution = 50

        mock_prev_cell = Mock()
        mock_flower = Mock()
        mock_flower.flower_type = 0
        mock_prev_cell.flower = mock_flower

        self.mock_grid_world.get_cell.return_value = mock_cell
        self.mock_grid_world_prev.get_cell.return_value = mock_prev_cell

        # Configure flower data with pollution reduction
        flower_data = Mock()
        flower_data.pollution_reduction = [1, 2, 3]
        self.mock_grid_world.flowers_data = {0: flower_data}

        # Test the method
        result = self.reward_functions.compute_ecology_reward(
            self.mock_grid_world_prev,
            self.mock_grid_world,
            self.mock_agent,
            self.action_enum.HARVEST
        )

        # Calculate expected reward manually
        r_harvest = 3 * (50 - 0)  # 3 (last value in pollution_reduction)
        r_max = 100 - 0
        expected = r_harvest / r_max

        self.assertAlmostEqual(result, expected)

    def test_compute_wellbeing_reward_harvest(self):
        """
        Test computeWellbeingReward method for harvesting action.

        Verifies wellbeing reward when harvesting flowers based on their price.
        """
        # Set up the agent and position
        self.mock_agent.position = (1, 1)

        # Set up cell states before and after harvesting
        mock_cell = Mock()
        mock_cell.has_flower.return_value = False

        mock_prev_cell = Mock()
        mock_flower = Mock()
        mock_flower.flower_type = 0
        mock_prev_cell.flower = mock_flower

        self.mock_grid_world.get_cell.return_value = mock_cell
        self.mock_grid_world_prev.get_cell.return_value = mock_prev_cell

        # Configure flower price data
        self.mock_grid_world.flowers_data = {
            0: {"price": 10},
            1: {"price": 20}
        }

        # Test the method
        result = self.reward_functions.compute_wellbeing_reward(
            self.mock_grid_world_prev,
            self.mock_grid_world,
            self.mock_agent,
            self.action_enum.HARVEST
        )

        # Verify result
        expected = 10 / 20  # Price of 0 / highest flower price
        self.assertEqual(result, expected)

    def test_compute_wellbeing_reward_penalty(self):
        """
        Test computeWellbeingReward method for non-harvesting actions.

        Verifies that penalty is applied based on turns without income.
        """
        # Set up the agent with turns without income
        self.mock_agent.turns_without_income = 5

        # Test the method with a non-harvest action
        result = self.reward_functions.compute_wellbeing_reward(
            self.mock_grid_world_prev,
            self.mock_grid_world,
            self.mock_agent,
            self.action_enum.WAIT
        )

        # Verify penalty calculation
        expected = -min(5 / MAX_PENALTY_TURNS, 1.0)
        self.assertEqual(result, expected)

    def test_compute_biodiversity_reward_positive(self):
        """
        Test computeBiodiversityReward function for a positive planting action.

        Verifies biodiversity reward calculation based on Shannon-Wiener index
        for a planting action that increases biodiversity by planting an
        underrepresented flower type.
        """
        # Set up the agent and position
        self.mock_agent.position = (1, 1)

        # Set up cell with a flower of type 2 (underrepresented)
        mock_cell = Mock()
        mock_cell.has_flower.return_value = True
        mock_flower = Mock()
        mock_flower.flower_type = 2
        mock_cell.flower = mock_flower
        self.mock_grid_world.get_cell.return_value = mock_cell

        # Configure flower data types
        self.mock_grid_world.flowers_data = {0: {}, 1: {}, 2: {}}

        # Create mock agents with planted flowers
        agent1 = Mock()
        agent2 = Mock()

        # Assign flowers to agents
        agent1.flowers_planted = {0: 2, 1: 1}
        agent2.flowers_planted = {0: 1, 1: 1, 2: 1}

        self.mock_grid_world.agents = [agent1, agent2]

        # Test biodiversity reward for planting a type 2 flower
        result = self.reward_functions.compute_biodiversity_reward(
            self.mock_grid_world_prev,
            self.mock_grid_world,
            self.mock_agent,
            self.action_enum.PLANT_TYPE_2
        )

        # Calculate expected Shannon-Wiener biodiversity indices manually
        # Before planting
        p0_before = 3 / 5
        p1_before = 2 / 5
        biodiversity_before = -(p0_before * log(p0_before) +
                                p1_before * log(p1_before))

        # After planting
        p0_after = 3 / 6
        p1_after = 2 / 6
        p2_after = 1 / 6
        biodiversity_after = -(p0_after * log(p0_after) +
                               p1_after * log(p1_after) +
                               p2_after * log(p2_after))

        # Max biodiversity
        max_biodiversity = log(3)  # 3 types of flowers

        # Expected reward
        expected = ((biodiversity_after - biodiversity_before) /
                    max_biodiversity)

        self.assertGreater(result, 0)
        self.assertAlmostEqual(result, expected)

    def test_compute_biodiversity_reward_negative(self):
        """
        Test computeBiodiversityReward function for a negative planting action.

        Verifies biodiversity reward calculation based on Shannon-Wiener index
        for a planting action that decreases biodiversity by planting an
        overrepresented flower type.
        """
        # Set up the agent and position
        self.mock_agent.position = (1, 1)

        # Set up cell with a flower of type 0 (already overrepresented)
        mock_cell = Mock()
        mock_cell.has_flower.return_value = True
        mock_flower = Mock()
        mock_flower.flower_type = 0
        mock_cell.flower = mock_flower
        self.mock_grid_world.get_cell.return_value = mock_cell

        # Configure flower data types
        self.mock_grid_world.flowers_data = {0: {}, 1: {}, 2: {}}

        # Create mock agents with planted flowers
        agent1 = Mock()
        agent2 = Mock()

        # Assign flowers to agents
        agent1.flowers_planted = {0: 2, 1: 1}
        agent2.flowers_planted = {0: 1, 1: 1}

        self.mock_grid_world.agents = [agent1, agent2]

        # Test biodiversity reward for planting a type 0 flower
        result = self.reward_functions.compute_biodiversity_reward(
            self.mock_grid_world_prev,
            self.mock_grid_world,
            self.mock_agent,
            self.action_enum.PLANT_TYPE_0
        )

        # Calculate expected Shannon-Wiener biodiversity indices manually
        # Before planting
        p0_before = 2 / 4
        p1_before = 2 / 4
        biodiversity_before = -(p0_before * log(p0_before) +
                                p1_before * log(p1_before))

        # After planting
        p0_after = 3 / 5
        p1_after = 2 / 5
        biodiversity_after = -(p0_after * log(p0_after) +
                               p1_after * log(p1_after))

        # Max biodiversity
        max_biodiversity = log(3)  # 3 types of flowers

        # Expected reward
        expected = ((biodiversity_after - biodiversity_before) /
                    max_biodiversity)

        self.assertLess(result, 0)
        self.assertAlmostEqual(result, expected)
