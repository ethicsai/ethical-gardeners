import unittest
from ethicalgardeners.worldgrid import Flower


class TestFlower(unittest.TestCase):
    """Unit tests for the :py:class:`.Flower` class."""

    def setUp(self):
        """Initialize necessary objects before tests.

        This method sets up a test environment with a flower of type 0
        at position (5, 5) which has multiple growth stages.
        """
        self.position = (5, 5)
        self.flower_type = 0
        self.flowers_data = {
            0: {"price": 10, "pollution_reduction": [0, 0, 0, 0, 5]},
            1: {"price": 5, "pollution_reduction": [0, 0, 1, 3]},
            2: {"price": 2, "pollution_reduction": [1]}
        }
        self.flower = Flower(self.position, self.flower_type, self.flowers_data)

    def test_grow_from_initial_stage(self):
        """Test flower growth from its initial stage.

        This test verifies that when the grow method is called on a newly
        planted flower, its current_growth_stage increases by 1.
        """
        initial_stage = self.flower.current_growth_stage

        self.flower.grow()

        # Verify the growth stage has increased by 1
        self.assertEqual(self.flower.current_growth_stage, initial_stage + 1)

    def test_grow_multiple_times(self):
        """Test flower growth over multiple stages.

        This test verifies that a flower grows correctly through multiple
        stages, with each call to grow() incrementing the growth stage by 1.
        """
        initial_stage = self.flower.current_growth_stage

        # grow less than num_growth_stage
        grow_times = self.flower.num_growth_stage - 1

        for i in range(grow_times):
            self.flower.grow()
            # Verify current stage is as expected
            self.assertEqual(self.flower.current_growth_stage, initial_stage + i + 1)

    def test_grow_until_final_stage(self):
        """Test flower growth until its final stage.

        This test verifies that a flower can grow through all available stages
        and stops growing once it reaches its final growth stage.
        """
        # Grow the flower until its maximum stage
        for _ in range(self.flower.num_growth_stage):
            self.flower.grow()

        # Verify it's at the maximum allowed stage
        self.assertEqual(self.flower.current_growth_stage, self.flower.num_growth_stage)

        # Try to grow it one more time
        self.flower.grow()

        # Verify it doesn't grow beyond the maximum stage
        self.assertEqual(self.flower.current_growth_stage, self.flower.num_growth_stage)

        # Verify it's considered fully grown
        self.assertTrue(self.flower.is_grown())
