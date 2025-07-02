import unittest
import tempfile
import random

from ethicalgardeners.worldgrid import WorldGrid, CellType


class TestWorldGrid(unittest.TestCase):
    """Unit tests for the :py:class:`.WorldGrid` class initialization methods."""

    def setUp(self):
        """Initialize test environment before each test."""
        self.test_grid = WorldGrid()

        # Create a temporary file for init_from_file tests
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file_path = self.temp_file.name
        self.temp_file.write(b"5 5\n")
        self.temp_file.write(b"G G G W W\n")
        self.temp_file.write(b"G F0_2 G G W\n")
        self.temp_file.write(b"G O G A0 W\n")
        self.temp_file.write(b"G G G G W\n")
        self.temp_file.write(b"W W W W W\n")
        self.temp_file.write(b"0,100,5|10|3\n")
        self.temp_file.write(b"0,2,1|2|3\n")
        self.temp_file.close()

        # Configuration for init_from_code tests
        self.test_config = {
            'width': 4,
            'height': 4,
            'cells': [
                {'position': (0, 0), 'type': 'WALL'},
                {'position': (1, 1), 'type': 'OBSTACLE'}
            ],
            'agents': [
                {'position': (2, 2), 'money': 50.0, 'seeds': {0:3, 1:3, 2:3}}
            ],
            'flowers': [
                {'position': (3, 3), 'type': 0, 'growth_stage': 2}
            ]
        }

    def test_init_from_file(self):
        """
        Test grid initialization from a file.

        This test verifies that:
        1. The grid dimensions are correctly set
        2. Cells are properly initialized with their types
        3. Agents are created and placed at the correct positions
        4. Flowers are created with the correct types and growth stages
        """
        self.test_grid.init_from_file(self.temp_file_path)

        # Check grid dimensions
        self.assertEqual(self.test_grid.width, 5)
        self.assertEqual(self.test_grid.height, 5)

        # Check cell types
        self.assertEqual(self.test_grid.grid[0][3].cell_type, CellType.WALL)
        self.assertEqual(self.test_grid.grid[2][1].cell_type, CellType.OBSTACLE)
        self.assertEqual(self.test_grid.grid[1][0].cell_type, CellType.GROUND)

        # Check flower placement and growth stage
        self.assertTrue(self.test_grid.grid[1][1].has_flower())
        flower = self.test_grid.grid[1][1].flower
        self.assertEqual(flower.flower_type, 0)
        self.assertEqual(flower.current_growth_stage, 2)

        # Check agent placement
        self.assertTrue(self.test_grid.grid[2][3].has_agent())
        self.assertEqual(self.test_grid.grid[2][3].agent.money, 100.0)
        self.assertEqual(self.test_grid.grid[2][3].agent.seeds,
                         {0:5, 1:10, 2:3})

    def test_init_random(self):
        """
        Test random grid initialization.

        This test verifies that:
        1. The grid has the correct dimensions
        2. The number of obstacles is as specified
        3. The correct number of agents is created and placed
        """
        # Set random seed for reproducibility
        random.seed(42)

        width = 10
        height = 8
        obstacles_ratio = 0.3
        nb_agents = 3

        self.test_grid = WorldGrid(width=width, height=height)
        self.test_grid.init_random(obstacles_ratio=obstacles_ratio,
                                   nb_agent=nb_agents)

        # Check grid dimensions
        self.assertEqual(self.test_grid.width, width)
        self.assertEqual(self.test_grid.height, height)

        # Count obstacles
        obstacle_count = sum(1 for row in self.test_grid.grid for cell in row
                             if cell.cell_type == CellType.OBSTACLE)
        expected_obstacles = int(obstacles_ratio * width * height)

        # Check number of obstacles
        self.assertEqual(obstacle_count, expected_obstacles)

        # Check number of agents
        self.assertEqual(len(self.test_grid.agents), nb_agents)

    def test_init_from_code(self):
        """
        Test grid initialization from code using a configuration dictionary.

        This test verifies that:
        1. The grid dimensions match the configuration
        2. Special cells (walls, obstacles) are placed correctly
        3. Agents are created with the specified properties
        4. Flowers are created with the correct types and growth stages
        """
        self.test_grid.init_from_code(self.test_config)

        # Check grid dimensions
        self.assertEqual(self.test_grid.width, 4)
        self.assertEqual(self.test_grid.height, 4)

        # Check special cells
        self.assertEqual(self.test_grid.grid[0][0].cell_type, CellType.WALL)
        self.assertEqual(self.test_grid.grid[1][1].cell_type, CellType.OBSTACLE)

        # Check agent
        self.assertTrue(self.test_grid.grid[2][2].has_agent())
        self.assertEqual(self.test_grid.grid[2][2].agent.position,
                         (2, 2))
        self.assertEqual(self.test_grid.grid[2][2].agent.money,
                         50.0)
        self.assertEqual(self.test_grid.grid[2][2].agent.seeds,
                         {0:3, 1:3, 2:3})

        # Check flower
        self.assertTrue(self.test_grid.grid[3][3].has_flower())
        flower = self.test_grid.grid[3][3].flower
        self.assertEqual(flower.position, (3, 3))
        self.assertEqual(flower.flower_type, 0)
        self.assertEqual(flower.current_growth_stage, 2)