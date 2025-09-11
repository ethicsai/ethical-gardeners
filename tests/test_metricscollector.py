import unittest
from unittest.mock import Mock
import os
import tempfile
import shutil

import csv

from ethicalgardeners.metricscollector import MetricsCollector


class TestMetricsCollector(unittest.TestCase):
    """Unit tests for the :py:class:`.MetricsCollector` class.

    Test metrics updating and export.
    """

    def setUp(self):
        """Set up test fixtures before each test method.

        Creates a temporary directory for metrics export and initializes test
        objects.
        """
        # Create temporary directory for export tests
        self.temp_dir = tempfile.mkdtemp()

        self.collector = MetricsCollector(
            out_dir_path=self.temp_dir,
            export_on=True,
            send_on=False
        )

        # Set up mock grid_world with mock cells and mock agents
        self.mock_grid_world = Mock()

        # Mock cells with pollution data
        cells_pollution = [[25, 30, 50], [55, 75, 80], [90, 95, 100]]
        mock_grid = []
        for i in range(3):
            row = []
            for j in range(3):
                cell = Mock()
                cell.pollution = cells_pollution[i][j]
                row.append(cell)
            mock_grid.append(row)

        self.mock_grid_world.grid = mock_grid
        self.mock_grid_world.max_pollution = 100

        # Mock agents with planted and harvested flowers
        agent1 = Mock()
        agent2 = Mock()

        agent1.flowers_planted = {0: 2}
        agent1.flowers_harvested = {0: 1}

        agent2.flowers_planted = {0: 1}
        agent2.flowers_harvested = {0: 0}

        self.mock_grid_world.agents = [agent1, agent2]

        # Test data
        self.rewards = {'agent_0': 10.5, 'agent_1': -5.2}
        self.agent_selection = "agent_0"

    def tearDown(self):
        """Clean up test fixtures after each test method.

        Removes the temporary directory used for export tests.
        """
        shutil.rmtree(self.temp_dir)

    def test_export_metrics(self):
        """Test the :py:meth:`~MetricsCollector.export_metrics` method.

        Verifies that metrics are correctly exported to a CSV file when
        export_on is True.
        """
        # Update metrics
        self.collector.update_metrics(
            self.mock_grid_world,
            self.rewards,
            self.agent_selection
        )

        # Export metrics
        self.collector.export_metrics()

        # Check if the file was created
        expected_filename = (
            os.path.join(self.temp_dir, "simulation_metrics.csv")
        )
        self.assertTrue(os.path.exists(expected_filename))

        # Read the CSV file and verify content
        with (open(expected_filename, 'r', newline='') as csvfile):
            reader = csv.DictReader(csvfile)
            rows = list(reader)

            # Should have exactly one row (header not counted)
            self.assertEqual(len(rows), 1)

            row = rows[0]

            # Check basic metrics
            self.assertEqual(int(row['step']), 1)
            self.assertEqual(int(row['total_planted_flowers']), 3)

            self.assertEqual(int(row['total_harvested_flowers']), 1)

            # Check per-agent metrics
            self.assertEqual(int(row['planted_flowers_agent_0']), 2)
            self.assertEqual(int(row['planted_flowers_agent_1']), 1)
            self.assertEqual(int(row['harvested_flowers_agent_0']), 1)
            self.assertEqual(int(row['harvested_flowers_agent_1']), 0)
            self.assertEqual(float(row['reward_agent_0']), 10.5)
            self.assertEqual(float(row['reward_agent_1']), -5.2)

            # Check pollution metrics
            self.assertEqual(int(row['num_cells_pollution_above_90']), 2)
            self.assertEqual(int(row['num_cells_pollution_above_75']), 4)
            self.assertEqual(int(row['num_cells_pollution_above_50']), 6)
            self.assertEqual(int(row['num_cells_pollution_above_25']), 8)
            expected_avg_pollution = (
                    (25 + 30 + 50 + 55 + 75 + 80 + 90 + 95 + 100) / 9)
            self.assertEqual(
                float(row['avg_pollution_percent']), expected_avg_pollution)

            # Check rewards and agent selection
            self.assertEqual(float(row['reward_agent_0']), 10.5)
            self.assertEqual(float(row['reward_agent_1']), -5.2)
            self.assertEqual(
                float(row['accumulated_reward_agent_0']), 10.5)
            self.assertEqual(
                float(row['accumulated_reward_agent_1']), -5.2)
            self.assertEqual(row['agent_selection'], self.agent_selection)

        # Update metrics again and export to check appending
        self.collector.metrics["step"] = 2
        self.collector.metrics["accumulated_rewards"] = {
            0: 20.0,
            1: -2.0
        }
        self.collector.export_metrics()

        # Read the CSV again and check for two rows
        with open(expected_filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 2)
            self.assertEqual(int(rows[1]['step']), 2)
            self.assertEqual(
                float(rows[1]['accumulated_reward_agent_0']), 20.0)
            self.assertEqual(
                float(rows[1]['accumulated_reward_agent_1']), -2.0)
