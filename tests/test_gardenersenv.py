import unittest
import os
import shutil
import tempfile
from omegaconf import OmegaConf

from ethicalgardeners.gardenersenv import GardenersEnv
from ethicalgardeners.constants import DEFAULT_GRID_CONFIG
from ethicalgardeners.action import create_action_enum


class TestGardenersEnv(unittest.TestCase):
    """
    Functional tests for the :py:class:`.GardenersEnv` environment.
    """

    def setUp(self):
        """
        Set up the test environment.

        Creates a temporary directory and initializes a
        :py:class:`.GardenersEnv` instance.
        """
        self.temp_dir = tempfile.mkdtemp()
        self.config = OmegaConf.create({
            'random_seed': 42,
            'grid': {
                'init_method': 'from_code',
                'config': DEFAULT_GRID_CONFIG
            },
            'observation': {
                'type': 'total'
            },
            'metrics': {
                'export_on': False,
                'send_on': False,
                'out_dir_path': self.temp_dir
            },
            'renderer': {
                'graphical': {
                    'enabled': False
                },
                'console': {
                    'enabled': False
                }
            }
        })
        self.env = GardenersEnv(self.config)
        self.env.reset()

    def tearDown(self):
        """
        Clean up after each test.
        """
        self.env.close()
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """
        Test that the environment initializes correctly.

        Verifies core components and agent setup.
        """
        self.assertIsNotNone(self.env.grid_world)
        self.assertIsNotNone(self.env.action_handler)
        self.assertIsNotNone(self.env.observation_strategy)
        self.assertIsNotNone(self.env.metrics_collector)
        self.assertEqual(len(self.env.renderers), 0)  # No renderers enabled

        expected_agents = len(DEFAULT_GRID_CONFIG['agents'])
        self.assertEqual(len(self.env.agents), expected_agents)

        # Check if action space is correct
        action_enum = create_action_enum(
            num_flower_type=3)  # Default has 3 flower types
        self.assertEqual(self.env.action_space('agent_0').n,
                         len(action_enum))

    def test_movement_actions(self):
        """
        Test that agents can move in all four directions via :py:meth:`.step`.
        """
        action_enum = create_action_enum(num_flower_type=3)
        agent = self.env.agents['agent_0']
        start = agent.position

        # UP
        self.env.step(action_enum.UP.value)
        self.assertEqual(agent.position, (start[0] - 1, start[1]))
        self.assertAlmostEqual(self.env.rewards['agent_0'],
                               -0.0333333333333333)  # With 1 turn out of 10
        # without earning money

        # RIGHT
        self.env.step(action_enum.WAIT.value)  # Pass agent_1 turn
        self.env.step(action_enum.RIGHT.value)
        self.assertEqual(agent.position, (start[0] - 1, start[1] + 1))
        self.assertAlmostEqual(self.env.rewards['agent_0'],
                               -0.0666666666666667)  # With 2 turn out of 10
        # without earning money

        # DOWN
        self.env.step(action_enum.WAIT.value)  # Pass agent_1 turn
        self.env.step(action_enum.DOWN.value)
        self.assertEqual(agent.position, (start[0], start[1] + 1))
        self.assertAlmostEqual(self.env.rewards['agent_0'],
                               -0.0999999999999999)  # With 3 turn out of 10
        # without earning money

        # LEFT
        self.env.step(action_enum.WAIT.value)  # Pass agent_1 turn
        self.env.step(action_enum.LEFT.value)
        self.assertEqual(agent.position, start)
        self.assertAlmostEqual(self.env.rewards['agent_0'],
                               -0.1333333333333333)  # With 4 turn out of 10
        # without earning money

    def test_plant_and_harvest_flowers(self):
        """
        Test planting and harvesting actions change state, metrics, and
        rewards.
        """
        action_enum = create_action_enum(num_flower_type=3)
        agent = self.env.agents['agent_0']
        init_seeds = agent.seeds[0]

        # Plant type 0
        self.env.step(action_enum.get_planting_action_for_type(0).value)
        self.assertEqual(agent.seeds[0], init_seeds - 1)
        self.assertLessEqual(self.env.rewards['agent_0'], 0)

        # Grow to maturity
        cell = self.env.grid_world.get_cell(agent.position)
        cell.flower.current_growth_stage = cell.flower.num_growth_stage - 1

        # Harvest
        init_money = agent.money
        flower_price = (
            self.env.grid_world.flowers_data)[cell.flower.flower_type]['price']
        self.env.step(action_enum.WAIT.value)  # Pass agent_1 turn
        self.env.step(action_enum.HARVEST.value)
        self.assertFalse(cell.has_flower())
        self.assertGreater(
            self.env.infos['agent_0']['rewards']['wellbeing'], 0
        )
        self.assertEqual(agent.money, init_money + flower_price)

    def test_metrics_export(self):
        """
        Test that metrics are exported to CSV when enabled.
        """
        self.env.metrics_collector.export_on = True
        action_enum = create_action_enum(num_flower_type=3)
        self.env.step(action_enum.UP.value)

        files = os.listdir(self.temp_dir)
        self.assertTrue(any(f.endswith('.csv') for f in files))

    def test_seed_exhaustion_constraints(self):
        """
        Test that agents cannot plant once seeds are exhausted and inventory
        never goes negative.
        """
        action_enum = create_action_enum(num_flower_type=1)
        agent = self.env.agents['agent_0']
        agent.seeds[0] = 0  # Set seeds to zero

        before = agent.seeds[0]
        self.env.step(action_enum.get_planting_action_for_type(0).value)
        self.assertEqual(agent.seeds[0], before)
        self.assertLessEqual(self.env.rewards['agent_0'], 0)
