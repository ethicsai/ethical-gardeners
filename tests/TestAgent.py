import unittest
from ethicalgardeners.WorldGrid import Agent
from ethicalgardeners.Action import Action


class TestAgent(unittest.TestCase):
    """Unit tests for the :py:class:`.Agent` class."""

    def setUp(self):
        """Initialize necessary objects before tests.

        This method sets up a test environment with an agent at position (5, 5).
        """
        self.initial_position = (5, 5)
        self.agent = Agent(position=self.initial_position)

    def test_move_up(self):
        """Test agent movement in the UP direction.

        This test verifies that when the agent moves up, its position is correctly
        updated by decreasing the row coordinate by 1.
        """
        self.agent.move(Action.UP)

        # Expected position after moving up: row decreases by 1
        expected_position = (self.initial_position[0] - 1, self.initial_position[1])

        # Verify the position was correctly updated
        self.assertEqual(self.agent.position, expected_position)

    def test_move_down(self):
        """Test agent movement in the DOWN direction.

        This test verifies that when the agent moves down, its position is correctly
        updated by increasing the row coordinate by 1.
        """
        self.agent.move(Action.DOWN)

        # Expected position after moving down: row increases by 1
        expected_position = (self.initial_position[0] + 1, self.initial_position[1])

        # Verify the position was correctly updated
        self.assertEqual(self.agent.position, expected_position)

    def test_move_left(self):
        """Test agent movement in the LEFT direction.

        This test verifies that when the agent moves left, its position is correctly
        updated by decreasing the column coordinate by 1.
        """
        self.agent.move(Action.LEFT)

        # Expected position after moving left: column decreases by 1
        expected_position = (self.initial_position[0], self.initial_position[1] - 1)

        # Verify the position was correctly updated
        self.assertEqual(self.agent.position, expected_position)

    def test_move_right(self):
        """Test agent movement in the RIGHT direction.

        This test verifies that when the agent moves right, its position is correctly
        updated by increasing the column coordinate by 1.
        """
        self.agent.move(Action.RIGHT)

        # Expected position after moving right: column increases by 1
        expected_position = (self.initial_position[0], self.initial_position[1] + 1)

        # Verify the position was correctly updated
        self.assertEqual(self.agent.position, expected_position)

    def test_consecutive_moves(self):
        """Test consecutive moves in different directions.

        This test verifies that when the agent makes multiple moves in sequence,
        its final position correctly reflects all movements applied.
        """
        # Perform a sequence of moves
        self.agent.move(Action.UP)  # (4, 5)
        self.agent.move(Action.RIGHT)  # (4, 6)
        self.agent.move(Action.RIGHT)  # (4, 7)
        self.agent.move(Action.DOWN)  # (5, 7)

        # Expected final position after the sequence of moves
        expected_final_position = (5, 7)

        # Verify the position was correctly updated
        self.assertEqual(self.agent.position, expected_final_position)