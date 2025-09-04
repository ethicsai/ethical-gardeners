import unittest
import tempfile
import numpy as np
import os

from ethicalgardeners.gridworld import GridWorld, CellType


class TestWorldGrid(unittest.TestCase):
    """Unit tests for the :py:class:`.WorldGrid` class initialization methods.
    """

    def setUp(self):
        """Initialize test environment before each test."""
        # Create a temporary file for init_from_file tests
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file_path = self.temp_file.name
        self.temp_file.write(b"5 5\n")
        self.temp_file.write(b"G G G O O\n")
        self.temp_file.write(b"G F0_2 G G O\n")
        self.temp_file.write(b"G O G A0 O\n")
        self.temp_file.write(b"G G G G O\n")
        self.temp_file.write(b"O O O O O\n")
        self.temp_file.write(b"0,100,5|10|3\n")
        self.temp_file.write(b"0,2,1|2|3\n")
        self.temp_file.close()

        # Configuration for init_from_code tests
        self.test_config = {
            'width': 4,
            'height': 4,
            'max_pollution': 50.0,
            'num_seeds_returned': -1,
            'collisions_on': False,
            'flowers_data': {
                0: {'price': 10, 'pollution_reduction': [0, 1, 2, 3]},
            },
            'cells': [
                {'position': (0, 0), 'type': 'OBSTACLE'},
                {'position': (1, 1), 'type': 'OBSTACLE'}
            ],
            'agents': [
                {'position': (2, 2), 'money': 50.0,
                 'seeds': {0: 3, 1: 3, 2: 3}}
            ],
            'flowers': [
                {'position': (3, 3), 'type': 0, 'growth_stage': 2}
            ]
        }

    def tearDown(self):
        """Clean up after each test."""
        # Remove the temporary file created for init_from_file tests
        try:
            os.remove(self.temp_file_path)
        except OSError:
            pass

    def test_init_from_file(self):
        """
        Test grid initialization from a file.

        This test verifies that:
        1. The grid dimensions are correctly set
        2. Cells are properly initialized with their types
        3. Agents are created and placed at the correct positions
        4. Flowers are created with the correct types and growth stages
        """
        self.test_grid = GridWorld.init_from_file(
            {'file_path': self.temp_file_path}
        )

        # Check grid dimensions
        self.assertEqual(self.test_grid.width, 5)
        self.assertEqual(self.test_grid.height, 5)

        # Check cell types
        self.assertEqual(self.test_grid.grid[0][3].cell_type,
                         CellType.OBSTACLE)
        self.assertEqual(self.test_grid.grid[2][1].cell_type,
                         CellType.OBSTACLE)
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
                         {0: 5, 1: 10, 2: 3})

    def test_init_random(self):
        """
        Test random grid initialization.

        This test verifies that:
        1. The grid has the correct dimensions
        2. The number of obstacles is as specified
        3. The correct number of agents is created and placed
        """
        # Set random seed for reproducibility
        random_generator = np.random.RandomState(42)

        width = 10
        height = 8
        obstacles_ratio = 0.3
        nb_agents = 3

        self.test_grid = GridWorld.init_random(
            {'obstacles_ratio': obstacles_ratio, 'nb_agent': nb_agents},
            width, height,
            random_generator=random_generator
            )

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

    def test_numpy_random_generator_in_world_grid(self):
        """Test using NumPy's PRNG with WorldGrid's random_generator.

        This test verifies that:
        1. WorldGrid correctly works with NumPy's RandomState as
            random_generator
        2. Two grids with the same NumPy seed produce identical agent
            placements
        3. Two grids with different NumPy seeds produce different agent
            placements
        """
        import numpy as np
        from ethicalgardeners.gridworld import GridWorld, CellType

        # Create NumPy random generators with different seeds
        np_random1 = np.random.RandomState(42)
        np_random2 = np.random.RandomState(
            42)  # Same seed, should produce same results
        np_random3 = np.random.RandomState(
            100)  # Different seed, should produce different results

        # Give the same obstacles ratio and number of agents for all grids
        obstacles_ratio = 0.2
        nb_agents = 5

        grid1 = GridWorld.init_random({'obstacles_ratio': obstacles_ratio,
                                      'nb_agent': nb_agents},
                                      width=10, height=10,
                                      random_generator=np_random1)
        grid2 = GridWorld.init_random({'obstacles_ratio': obstacles_ratio,
                                      'nb_agent': nb_agents},
                                      width=10, height=10,
                                      random_generator=np_random2)
        grid3 = GridWorld.init_random({'obstacles_ratio': obstacles_ratio,
                                      'nb_agent': nb_agents},
                                      width=10, height=10,
                                      random_generator=np_random3)

        # Collect agent positions from each grid
        agent_positions1 = [agent.position for agent in grid1.agents]
        agent_positions2 = [agent.position for agent in grid2.agents]
        agent_positions3 = [agent.position for agent in grid3.agents]

        # Verify that agents in grid1 and grid2 have the same positions
        self.assertEqual(agent_positions1, agent_positions2)

        # Verify that agents in grid1 and grid3 have different positions
        self.assertNotEqual(agent_positions1, agent_positions3)

        # Collect obstacle positions from each grid
        obstacles_positions1 = []
        obstacles_positions2 = []
        obstacles_positions3 = []

        for i in range(grid1.height):
            for j in range(grid1.width):
                if grid1.grid[i][j].cell_type == CellType.OBSTACLE:
                    obstacles_positions1.append((i, j))
                if grid2.grid[i][j].cell_type == CellType.OBSTACLE:
                    obstacles_positions2.append((i, j))
                if grid3.grid[i][j].cell_type == CellType.OBSTACLE:
                    obstacles_positions3.append((i, j))

        # Verify that obstacles are the same with the same seeds
        self.assertEqual(obstacles_positions1, obstacles_positions2)

        # Verify that obstacles are different with different seeds
        self.assertNotEqual(obstacles_positions1, obstacles_positions3)

    def test_init_from_code(self):
        """
        Test grid initialization from code using a configuration dictionary.

        This test verifies that:
        1. The grid dimensions match the configuration
        2. Special cells (obstacles, ...) are placed correctly
        3. Agents are created with the specified properties
        4. Flowers are created with the correct types and growth stages
        """
        self.test_grid = GridWorld.init_from_code(
            {'grid_config': self.test_config}
        )

        # Check grid dimensions
        self.assertEqual(self.test_grid.width, 4)
        self.assertEqual(self.test_grid.height, 4)

        # Check GridWorld properties
        self.assertEqual(self.test_grid.min_pollution, 0.0)
        self.assertEqual(self.test_grid.max_pollution, 50.0)
        self.assertEqual(self.test_grid.pollution_increment, 1.0)
        self.assertEqual(self.test_grid.num_seeds_returned, None)
        self.assertFalse(self.test_grid.collisions_on)

        # Check flowers data
        self.assertEqual(len(self.test_grid.flowers_data), 1)
        self.assertEqual(self.test_grid.flowers_data[0]['price'], 10)
        self.assertEqual(self.test_grid.flowers_data[0]['pollution_reduction'],
                         [0, 1, 2, 3])

        # Check special cells
        self.assertEqual(self.test_grid.grid[0][0].cell_type,
                         CellType.OBSTACLE)
        self.assertEqual(self.test_grid.grid[1][1].cell_type,
                         CellType.OBSTACLE)

        # Check agent
        self.assertTrue(self.test_grid.grid[2][2].has_agent())
        self.assertEqual(self.test_grid.grid[2][2].agent.position,
                         (2, 2))
        self.assertEqual(self.test_grid.grid[2][2].agent.money,
                         50.0)
        self.assertEqual(self.test_grid.grid[2][2].agent.seeds,
                         {0: 3, 1: 3, 2: 3})

        # Check flower
        self.assertTrue(self.test_grid.grid[3][3].has_flower())
        flower = self.test_grid.grid[3][3].flower
        self.assertEqual(flower.position, (3, 3))
        self.assertEqual(flower.flower_type, 0)
        self.assertEqual(flower.current_growth_stage, 2)

    def test_init_from_code_without_config(self):
        """
        Test grid initialization from code without giving a configuration
        dictionary.

        This test verifies that:
        1. The grid dimensions match the configuration
        2. Special cells (obstacles, ...) are placed correctly
        3. Agents are created with the specified properties
        4. Flowers are created with the correct types and growth stages
        """
        self.test_grid = GridWorld.init_from_code()

        # Check grid dimensions
        self.assertEqual(self.test_grid.width, 10)
        self.assertEqual(self.test_grid.height, 10)

        # Check GridWorld properties
        self.assertEqual(self.test_grid.min_pollution, 0.0)
        self.assertEqual(self.test_grid.max_pollution, 100.0)
        self.assertEqual(self.test_grid.pollution_increment, 1.0)
        self.assertEqual(self.test_grid.num_seeds_returned, 1)
        self.assertTrue(self.test_grid.collisions_on)

        # Check flowers data
        self.assertEqual(len(self.test_grid.flowers_data), 3)
        self.assertEqual(self.test_grid.flowers_data[0]['price'], 10)
        self.assertEqual(
            self.test_grid.flowers_data[0]['pollution_reduction'],
            [0, 0, 0, 0, 5])
