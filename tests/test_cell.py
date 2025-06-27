import unittest
from unittest.mock import Mock
from ethicalgardeners.worldgrid import Cell, CellType
from ethicalgardeners.constants import POLLUTION_INCREMENT

class TestCell(unittest.TestCase):
    """Unit tests for the :py:class:`.Cell` class."""

    def setUp(self):
        """Initialize necessary objects before tests.

        This method sets up a test environment with a ground cell at medium pollution
        and a mock flower that reduces pollution by 5.
        """
        self.min_pollution = 0
        self.max_pollution = 100
        self.cell = Cell(CellType.GROUND, 50)

        # Create a mock flower with a pollution reduction value
        self.mock_flower = Mock()
        self.mock_flower.get_pollution_reduction.return_value = 5

    def test_update_pollution_with_flower_above_min(self):
        """Test pollution update when a cell has a flower and is above minimum.

        This test verifies that the cell's pollution decreases by the correct amount
        when it contains a flower and its pollution level is above the minimum.
        """
        # Add a flower to the cell
        self.cell.flower = self.mock_flower

        initial_pollution = self.cell.pollution

        self.cell.update_pollution(self.min_pollution, self.max_pollution)

        # Verify the pollution has decreased by the correct amount
        self.assertEqual(self.cell.pollution, initial_pollution - 5)

    def test_update_pollution_with_flower_at_min(self):
        """Test pollution update when a cell has a flower and is at minimum pollution.

        This test verifies that the cell's pollution stays at the minimum value
        when it contains a flower and its pollution is already at the minimum level.
        """
        # Set the cell to minimum pollution
        self.cell.pollution = self.min_pollution
        self.cell.flower = self.mock_flower

        self.cell.update_pollution(self.min_pollution, self.max_pollution)

        # Verify the pollution remains at the minimum
        self.assertEqual(self.cell.pollution, self.min_pollution)

    def test_update_pollution_without_flower_below_max(self):
        """Test pollution update when a cell has no flower and is below maximum.

        This test verifies that the cell's pollution increases by the correct amount
        when it does not contain a flower and its pollution level is below the maximum.
        """
        self.cell.flower = None

        initial_pollution = self.cell.pollution

        self.cell.update_pollution(self.min_pollution, self.max_pollution)

        # Verify the pollution has increased by the correct amount
        self.assertEqual(self.cell.pollution, initial_pollution + POLLUTION_INCREMENT)

    def test_update_pollution_without_flower_at_max(self):
        """Test pollution update when a cell has no flower and is at maximum pollution.

        This test verifies that the cell's pollution stays at the maximum value
        when it does not contain a flower and its pollution is already at the maximum level.
        """
        # Set the cell to maximum pollution
        self.cell.pollution = self.max_pollution
        self.cell.flower = None

        self.cell.update_pollution(self.min_pollution, self.max_pollution)

        # Verify the pollution remains at the maximum
        self.assertEqual(self.cell.pollution, self.max_pollution)