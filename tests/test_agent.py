import unittest
from ethicalgardeners.agent import Agent


class TestAgent(unittest.TestCase):
    """Unit tests for the :py:class:`.Agent` class."""

    def setUp(self):
        """Initialize necessary objects before tests.

        This method sets up a test environment with an agent at position
        (5, 5).
        """
        self.initial_position = (5, 5)
        self.agent = Agent(position=self.initial_position)

    def test_consecutive_moves(self):
        """Test consecutive moves in different directions.

        This test verifies that when the agent makes multiple moves in
        sequence, its final position correctly reflects all movements applied.
        """
        # Perform a sequence of moves
        self.agent.move((4, 5))
        self.agent.move((4, 6))
        self.agent.move((4, 7))
        self.agent.move((5, 7))

        # Expected final position after the sequence of moves
        expected_final_position = (5, 7)

        # Verify the position was correctly updated
        self.assertEqual(self.agent.position, expected_final_position)

    def test_add_money(self):
        """Test adding money to agent's wealth.

        Verifies that the add_money method correctly increases the agent's
        monetary wealth by the specified amount.
        """
        initial_money = 100.0
        self.agent.money = initial_money

        amount_to_add = 50.0
        self.agent.add_money(amount_to_add)

        # Verify that the agent's money has been updated correctly
        self.assertEqual(self.agent.money, initial_money + amount_to_add)

    def test_add_seed(self):
        """Test adding seeds to agent's inventory.

        Verifies that the add_seed method correctly increases the agent's
        seed count for a specific flower type.
        """
        flower_type = 0
        initial_seeds = 5
        self.agent.seeds[flower_type] = initial_seeds

        seeds_to_add = 3
        self.agent.add_seed(flower_type, seeds_to_add)

        # Verify that the agent's seed count for the flower type has been
        # updated
        self.assertEqual(self.agent.seeds[flower_type],
                         initial_seeds + seeds_to_add)

    def test_can_plant_with_seeds(self):
        """Test if agent can plant when seeds are available.

        Verifies that the can_plant method returns True when the agent
        has seeds available for a specific flower type.
        """
        flower_type = 0
        self.agent.seeds[flower_type] = 5
        self.assertTrue(self.agent.can_plant(flower_type))

    def test_can_plant_with_infinite_seeds(self):
        """Test if agent can plant with infinite seeds.

        Verifies that the can_plant method returns True when the agent
        has infinite seeds (represented by -1).
        """
        flower_type = 0
        self.agent.seeds[flower_type] = -1
        self.assertTrue(self.agent.can_plant(flower_type))

    def test_can_plant_without_seeds(self):
        """Test if agent cannot plant when no seeds are available.

        Verifies that the can_plant method returns False when the agent
        has no seeds available for a specific flower type.
        """
        flower_type = 0
        self.agent.seeds[flower_type] = 0
        self.assertFalse(self.agent.can_plant(flower_type))

    def test_use_seed_with_flower_object(self):
        """Test using a seed and tracking flower objects.

        Verifies that when a seed is used, the seed count is correctly
        decremented
        """
        flower_type = 0
        self.agent.seeds[flower_type] = 3

        # Verify that the seed count is decremented
        self.assertTrue(self.agent.use_seed(flower_type))
        self.assertEqual(self.agent.seeds[flower_type], 2)
