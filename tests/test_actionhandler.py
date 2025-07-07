import unittest
from unittest.mock import Mock

from ethicalgardeners.actionhandler import ActionHandler
from ethicalgardeners.action import Action
from ethicalgardeners.agent import Agent


class TestActionHandler(unittest.TestCase):
    """Unit tests for the :py:class:`.ActionHandler` class."""

    def setUp(self):
        """Initialize necessary objects before each test.

        This method sets up a mock grid_world and agent for testing
        the ActionHandler methods.
        """
        self.grid_world = Mock()
        self.action_handler = ActionHandler(self.grid_world)
        self.agent = Mock(spec=Agent)
        self.agent.position = (3, 3)
        self.agent.turns_without_income = 0

    def test_move_agent(self):
        """Test the move_agent method.

        Verifies that move_agent correctly checks if a move is valid
        and updates the agent's position when it is.
        """
        # Mock valid_move to return True
        self.grid_world.valid_move.return_value = True

        self.action_handler.move_agent(self.agent, Action.UP)

        new_position = (self.agent.position[0] - 1, self.agent.position[1])

        # Verify that valid_move was called with correct parameters
        self.grid_world.valid_move.assert_called_with(new_position)

        # Verify that agent.move was called with the correct action
        self.agent.move.assert_called_with(Action.UP)

    def test_move_agent_invalid(self):
        """Test move_agent with invalid move.

        Verifies that agent.move is not called when the move is invalid.
        """
        # Mock valid_move to return False
        self.grid_world.valid_move.return_value = False

        self.action_handler.move_agent(self.agent, Action.UP)

        # Verify that valid_move was called
        self.grid_world.valid_move.assert_called_once()

        # Verify that agent.move was not called
        self.agent.move.assert_not_called()

    def test_plant_flower_success(self):
        """Test planting a flower successfully.

        Verifies that when an agent can plant a flower, the handler
        correctly uses a seed and places a flower on the grid.
        """
        flower_type = 0
        self.agent.can_plant.return_value = True

        self.action_handler.plant_flower(self.agent, flower_type)

        # Verify the agent's methods were called correctly
        self.agent.can_plant.assert_called_with(flower_type)
        self.agent.use_seed.assert_called_with(flower_type)

        # Verify the flower was placed on the grid
        self.grid_world.place_flower.assert_called_with(self.agent.position,
                                                        flower_type)

    def test_plant_flower_failure(self):
        """Test planting a flower when the agent cannot.

        Verifies that a ValueError is raised when an agent cannot plant
        the requested flower type.
        """
        flower_type = 0
        self.agent.can_plant.return_value = False

        with self.assertRaises(ValueError):
            self.action_handler.plant_flower(self.agent, flower_type)

        # Verify the agent's method was called correctly
        self.agent.can_plant.assert_called_with(flower_type)

        # Verify no seed was used and no flower was placed
        self.agent.use_seed.assert_not_called()
        self.grid_world.place_flower.assert_not_called()

    def test_harvest_flower_success(self):
        """Test harvesting a flower successfully.

        Verifies that when a grown flower exists at the agent's position,
        it is harvested and the agent receives the appropriate rewards.
        """
        # Setup mock cell with a grown flower
        mock_cell = Mock()
        mock_flower = Mock()
        mock_cell.flower = mock_flower
        mock_flower.is_grown.return_value = True
        mock_flower.flower_type = 0

        self.grid_world.get_cell.return_value = mock_cell
        self.grid_world.flowers_data = {0: {'price': 10.0}}
        self.grid_world.num_seeds_returned = 2

        self.action_handler.harvest_flower(self.agent)

        # Verify the flower was checked and removed
        mock_flower.is_grown.assert_called_once()
        self.grid_world.remove_flower.assert_called_with(self.agent.position)

        # Verify the agent received rewards
        self.agent.add_seed.assert_called_with(0, 2)
        self.agent.add_money.assert_called_with(10.0)

    def test_harvest_flower_not_grown(self):
        """Test harvesting a flower that is not grown.

        Verifies that a ValueError is raised when trying to harvest
        a flower that is not fully grown.
        """
        mock_cell = Mock()
        mock_flower = Mock()
        mock_cell.flower = mock_flower
        mock_flower.is_grown.return_value = False

        self.grid_world.get_cell.return_value = mock_cell

        with self.assertRaises(ValueError):
            self.action_handler.harvest_flower(self.agent)

        # Verify no flower was removed and no rewards given
        self.grid_world.remove_flower.assert_not_called()
        self.agent.add_seed.assert_not_called()
        self.agent.add_money.assert_not_called()

    def test_harvest_flower_no_flower(self):
        """Test harvesting when no flower exists.

        Verifies that a ValueError is raised when trying to harvest
        from a cell that has no flower.
        """
        mock_cell = Mock()
        mock_cell.flower = None

        self.grid_world.get_cell.return_value = mock_cell

        with self.assertRaises(ValueError):
            self.action_handler.harvest_flower(self.agent)