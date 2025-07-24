"""
The Renderer module provides visualization capabilities for the Ethical
Gardeners simulation environment.

This module defines the abstract interface and concrete implementations for
rendering the grid world environment. It supports:

1. Real-time visualization - displaying the environment as agents interact
with it

2. Post-analysis recording - saving frames during the simulation for later
video export

The module provides:

1. :py:class:`Renderer`: Abstract base class defining the rendering interface

2. Two concrete implementations:

   - :py:class:`GraphicalRenderer`: Implementation using Pygame for colorful
     interactive visualization
   - :py:class:`ConsoleRenderer`: lightweight text-based display in terminal
     environments

Each renderer visualizes the grid world, including:

* The physical environment (ground, obstacles)
* Agents and their positions
* Flowers and their growth stages
* Pollution levels in each cell
"""
import warnings
from abc import ABC, abstractmethod

from ethicalgardeners.gridworld import CellType
from ethicalgardeners.constants import AGENT_PALETTE, FLOWER_PALETTE


class Renderer(ABC):
    """
    Abstract base class defining the interface for environment visualization.

    This class provides the foundation for different rendering strategies. It
    supports both real-time visualization during simulation execution and
    post-analysis recording for later video export.

    Renderers are responsible for visually representing all elements of the
    simulation environment, including the grid world, agents, flowers, and
    pollution levels.

    Attributes:
        display (bool): Flag to enable rendering. If True, the renderer will
            display the environment.
    """

    def __init__(self, display=False):
        """
        Create the renderer.

        Args:
            display (bool, optional): Flag to enable rendering. If True, the
                renderer will display the environment. Defaults to False.
        """
        self.display = display

    def init(self, grid_world):
        """
        Initialize the renderer with the grid world environment.

        This method is called once at the beginning of simulation to set up
        the rendering environment based on the grid world properties.

        Args:
            grid_world (:py:class:`.GridWorld`): The grid world environment to
                be rendered.
        """
        pass

    @abstractmethod
    def render(self, grid_world, agents: dict):
        """
        Render the current state of the grid world.

        This method visualizes the current state of the environment, including
        the grid cells, agents, flowers, and pollution levels. It should be
        implemented in concrete renderers.

        Args:
            grid_world (:py:class:`.GridWorld`): The current state of the world
                grid to render.
            agents (dict): Dictionary mapping the agent's gymnasium ID to
                the Agent instance of the agents to display.
        """
        pass

    @abstractmethod
    def display_render(self):
        """
        Display the rendered frame in the rendering window.

        This method is called to update the rendering window with the current
        frame. It should be implemented in concrete renderers.
        """
        pass

    def end_render(self):
        """
        Finalize the rendering process.

        This method is called at the end of simulation to perform cleanup tasks
        and finalize any outputs.
        """
        pass


class ConsoleRenderer(Renderer):
    """
    Text-based implementation of the Renderer interface.

    This renderer displays the simulation environment as ASCII characters in
    the console. It provides a lightweight, platform-independent visualization
    solution that works in terminal environments.

    The renderer uses a configurable set of characters to represent different
    elements of the environment (agents, flowers, empty cells, etc.).

    Attributes:
        characters (dict): Mapping of environment elements to their ASCII
            character representations. The default mapping includes:

            * 'ground': ' ' (space) - Empty ground cell
            * 'obstacle': '#' - Cell with an obstacle
            * 'flower': 'F' - Cell with a flower
            * 'agent': 'A' - Cell with an agent
        display (bool): Inherited from Renderer. Flag to enable rendering. If
            True, the renderer will display the environment in the console.
        grid_representation (list): List of strings representing the grid
            world, where each string corresponds to a row in the grid.
        _grid_world (GridWorld): The grid world environment to
            render.
        _agents (dict): Dictionary mapping the agent's gymnasium
            ID to the Agent instance.
    """

    def __init__(self, characters=None, display=False):
        """
        Create the console renderer.

        Args:
            characters (dict, optional): Mapping of environment elements to
                their ASCII character representations. Defaults to a basic set
                with ' ' for empty cells, '#' for obstacles, 'F' for flowers,
                and 'A' for agents.
            display (bool, optional): Flag to enable rendering. If True, the
                renderer will display the environment in the console.
        """
        super().__init__(display)
        self.characters = characters if characters else {
            'ground': ' ',
            'obstacle': '"',
            'flower': 'F',
            'agent': 'A'
        }

        self._grid_world = None
        self._agents = None

    def render(self, grid_world, agents: dict):
        """
        Render the current state of the grid world as text.

        This method create a text representation of the grid world, using the
        character mappings to display different elements. Each cell is
        represented by a single character followed by numbers for plants and
        agents, with rows separated by newlines.

        Args:
            grid_world (:py:class:`.GridWorld`): The current state of the world
                grid to render.
            agents (dict): Dictionary mapping the agent's gymnasium ID to
                the Agent instance of the agents to display.
        """
        # Store references to grid_world and agents
        self._grid_world = grid_world
        self._agents = agents

        # Create a grid representation of the world
        self.grid_representation = []
        for i in range(grid_world.height):
            row = []
            row.append("|")  # Start of row
            for j in range(grid_world.width):
                cell = grid_world.get_cell((i, j))

                # Empty cell by default
                cell_char = self.characters.get('ground', ' ')

                # Check cell type and update character accordingly
                if cell.cell_type == CellType.OBSTACLE:
                    cell_char = self.characters.get('obstacle', '#')

                # Verify if the cell contains a flower
                if cell.has_flower():
                    cell_char = self.characters.get('flower', 'F')
                    flower_type = cell.flower.flower_type
                    growth_stage = cell.flower.current_growth_stage
                    cell_char = f"{cell_char}{flower_type}_{growth_stage}"

                # Verify if the cell contains an agent (above all)
                if cell.has_agent():
                    cell_char = self.characters.get('agent', 'A')
                    agent_id = grid_world.agents.index(cell.agent)
                    cell_char = f"{cell_char}{agent_id}"

                # Add the pollution level
                if cell.pollution is not None:
                    cell_char += f" {cell.pollution}"
                else:
                    cell_char += f" {' ' * len(str(grid_world.max_pollution))}"

                row.append(cell_char)
                row.append('|')  # Separator for cells
            self.grid_representation.append(''.join(row))

    def display_render(self):
        """
        Display the rendered frame in the console.

        This method prints the grid representation to the console, showing
        the current state of the environment with all elements represented by
        their respective characters.
        """
        if self.display:
            # Display the grid representation in the console
            print("\n" + "-" * (self._grid_world.width * 2 + 1))
            print("\n".join(self.grid_representation))
            print("\n" + "-" * (self._grid_world.width * 2 + 1))

            # Display additional information about agents
            print(f"Number of agents: {len(self._agents)}")
            for idx, agent in self._agents.items():
                print(
                    f"{idx}: Position={agent.position}, Money={agent.money},"
                    f" Seeds={agent.seeds}")


class GraphicalRenderer(Renderer):
    """
    Pygame-based implementation of the Renderer interface.

    This renderer creates a graphical visualization of the simulation using
    the Pygame library. It provides a colorful and intuitive representation
    of the environment that updates in real-time and/or can be saved for
    post-simulation video generation.

    The renderer displays:

    * Grid cells with colors indicating their state (empty, obstacles)
    * Agents represented by distinct colored shapes
    * Flowers with colors reflecting their type and growth stage and different
      colors for different flower types
    * Pollution levels shown as color intensity

    Attributes:
        display (bool): Inherited from Renderer. Flag to enable rendering. If
            True, the renderer will display the environment in a Pygame
            window.
        cell_size (int): The size of each cell in pixels, determining the
            overall window dimensions.
        colors (dict): Mapping of environment elements to their RGB color
            representations. The default mapping includes:

            * 'background': (200, 200, 200) - Light gray background
            * 'obstacle': (100, 100, 100) - Gray for obstacles
            * 'ground': (70, 255, 70) - Green for ground cells (the green
              component changes dynamically based on pollution level)
        agent_colors (dict): Dictionary to store colors for agents
        flower_colors (dict): Dictionary to store colors for flowers
        pygame (:py:mod:`pygame`): Reference to the Pygame module for graphical
            rendering.
        window (:py:class:`pygame.Surface`): The Pygame surface where the
            environment is rendered.
        clock (:py:class:`pygame.time.Clock`): Clock object to control
            rendering frame rate.
        font (:py:class:`pygame.font.Font`): Font object for rendering text in
            the environment (e.g., for displaying agent information).
        post_analysis_on (bool): Flag indicating whether to save frames for
            post-simulation video generation.
        out_dir_path (str): Directory path where output files will be saved
            when post_analysis_on is True.
        frames (list): Collection of rendered frames for video generation
            when post_analysis_on is True.
        _run_id (int): Unique identifier for the run, used to name output files
            when post_analysis_on is True.
    """

    def __init__(self, cell_size=32, colors=None, post_analysis_on=False,
                 display=False, out_dir_path=None):
        """
        Create the graphical renderer.

        Args:
            cell_size (int, optional): The size of each cell in pixels.
                Defaults to 32.
            colors (dict, optional): Mapping of environment elements to their
                RGB color representations. Defaults to a basic set with light
                gray for background, gray for obstacles, and green for ground.
            post_analysis_on (bool, optional): Flag to enable saving frames for
                post-simulation video generation. Defaults to False.
            display (bool, optional): Flag to enable rendering. If True, the
                renderer will display the environment in a Pygame window.
            out_dir_path (str, optional): Directory path where output files
                will be saved. Required if post_analysis_on is True. Defaults
                to None.
        """
        super().__init__(display)
        self.cell_size = cell_size
        self.colors = colors if colors else {
            'background': (200, 200, 200),  # Light gray background
            'obstacle': (100, 100, 100),  # Gray for obstacles
            'ground': (70, 255, 70),  # Green for ground cells (define the red
            # and blue components of the displayed ground color. The green
            # component changes dynamically based on pollution level
        }

        self.post_analysis_on = post_analysis_on
        self.out_dir_path = out_dir_path if post_analysis_on else "videos"

        # Dictionaries to store colors for agents and flowers
        self.agent_colors = {}
        self.flower_colors = {}

        try:
            import pygame
            self.pygame = pygame
        except ImportError:
            warnings.warn(
                "Error while importing pygame. "
                "PyGame is required to use post_analysis_on or display the "
                "graphical renderer. For this run, the graphical renderer will"
                " be disabled. "
                "Please install PyGame with `pip install pygame` "
                "or `pip install ethicalgardeners[viz]`"
            )
            self.display = False
            self.post_analysis_on = False

        # Create Pygame window and clock
        self.window = None
        self.clock = None

        self._run_id = None  # Unique identifier for the run

        if post_analysis_on:
            import time

            self._run_id = int(time.time())

        self.frames = []  # List to store frames for video generation

    def init(self, grid_world):
        """
        Initialize the Pygame window based on the grid world dimensions.

        This method creates the Pygame window with dimensions calculated from
        the grid world size and the cell size. It sets up the display surface
        where the environment will be rendered.

        Args:
            grid_world (:py:class:`.GridWorld`): The grid world environment to
                be rendered.
        """
        if self.display or self.post_analysis_on:
            self.pygame.init()

            self.clock = self.pygame.time.Clock()

            # Calculate window dimensions based on grid size and cell size
            window_width = grid_world.width * self.cell_size
            window_height = grid_world.height * self.cell_size

            # Create the pygame window
            self.window = self.pygame.display.set_mode(
                (window_width, window_height)
            )
            self.pygame.display.set_caption("Ethical Gardeners Simulation")

            # Create a font for displaying text
            self.font = self.pygame.font.SysFont('Arial', 12)

            # Generate colors for agents and flowers
            self._generate_colors(grid_world)

    def _generate_colors(self, grid_world):
        """
        Generate distinct colors for each agent and flower type using
        predefined palettes.

        Args:
            grid_world (:py:class:`.GridWorld`): The grid world containing
                agents and flower data
        """
        # Assign colors to agents from the predefined palette
        for i, agent in enumerate(grid_world.agents):
            # Use modulo to handle cases where there are more agents than
            # colors in the palette
            palette_index = i % len(AGENT_PALETTE)
            self.agent_colors[i] = AGENT_PALETTE[palette_index]

        # Assign colors to flower types from the predefined palette
        for i, flower_type in enumerate(grid_world.flowers_data.keys()):
            # Use modulo to handle cases where there are more flower types than
            # colors
            palette_index = i % len(FLOWER_PALETTE)
            self.flower_colors[flower_type] = FLOWER_PALETTE[
                palette_index]

    def render(self, grid_world, agents: dict):
        """
        Render the current state of the grid world using Pygame.

        This method draws the grid world, including cells, agents, flowers,
        and pollution levels. Doesn't display the frame directly; instead,
        it prepares the frame for rendering in the Pygame window. If
        post_analysis_on is True, saves the current frame for later video
        generation.

        Args:
            grid_world (:py:class:`.GridWorld`): The current state of the world
                grid to render.
            agents (dict): Dictionary mapping the agent's gymnasium ID to
                the Agent instance of the agents to display.
        """
        if self.display or self.post_analysis_on:
            # Fill the window with a background color
            self.window.fill(self.colors['background'])

            # Draw each cell in the grid
            for i in range(grid_world.height):
                for j in range(grid_world.width):
                    cell = grid_world.get_cell((i, j))
                    cell_rect = self.pygame.Rect(
                        j * self.cell_size,
                        i * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )

                    # Determine cell color based on cell type
                    if cell.cell_type == CellType.GROUND:
                        # Shade ground cells based on pollution level
                        # Darker green = more polluted
                        # lighter green = less polluted
                        pollution_ratio = (
                                cell.pollution / grid_world.max_pollution)
                        green_value = 255 - int(pollution_ratio * 110)
                        cell_color = (
                            self.colors['ground'][0],
                            green_value,
                            self.colors['ground'][2]
                        )
                    elif cell.cell_type == CellType.OBSTACLE:
                        cell_color = self.colors['obstacle']

                    # Draw cell
                    self.pygame.draw.rect(self.window, cell_color, cell_rect)
                    self.pygame.draw.rect(self.window, (0, 0, 0),
                                          cell_rect, 1)  # Black border

                    # Draw flower if present
                    if cell.has_flower():
                        flower = cell.flower
                        flower_type = flower.flower_type

                        # Use flower_colors dictionary to get the base color
                        base_color = self.flower_colors.get(flower_type,
                                                            (0, 200, 0))

                        # Adjust color based on flower type and growth stage
                        growth_ratio = (flower.current_growth_stage /
                                        max(1, flower.num_growth_stage))
                        flower_color = (
                            int(base_color[0] * (0.5 + 0.5 * growth_ratio)),
                            int(base_color[1] * (0.5 + 0.5 * growth_ratio)),
                            int(base_color[2] * (0.5 + 0.5 * growth_ratio))
                        )

                        # Draw flower as a circle, size depends on growth stage
                        flower_radius = int(
                            self.cell_size * 0.3 * (0.5 + 0.5 * growth_ratio))
                        self.pygame.draw.circle(
                            self.window,
                            flower_color,
                            (j * self.cell_size + self.cell_size // 2,
                             i * self.cell_size + self.cell_size // 2),
                            flower_radius
                        )

                    # Draw pollution level as text if it's not None
                    if cell.pollution is not None:
                        pollution_text = self.font.render(
                            f"{int(cell.pollution)}", True, (0, 0, 0)
                        )
                    else:
                        pollution_text = self.font.render(
                            "", True, (0, 0, 0)
                        )

                    self.window.blit(
                        pollution_text,
                        (j * self.cell_size + 2, i * self.cell_size + 2)
                    )

            # Draw agents
            for agent_id, agent in agents.items():
                i, j = agent.position
                # Get the index of the agent in the grid world
                agent_idx = grid_world.agents.index(agent)

                # Use the agent_colors dictionary to get the agent's color
                agent_color = self.agent_colors.get(agent_idx,
                                                    self.colors.get(
                                                        'agent', (255, 0, 0))
                                                    )

                # Draw agent as a rectangle
                agent_rect = self.pygame.Rect(
                    j * self.cell_size + self.cell_size // 4,
                    i * self.cell_size + self.cell_size // 4,
                    self.cell_size // 2,
                    self.cell_size // 2
                )
                self.pygame.draw.rect(self.window, agent_color, agent_rect)

                # Draw agent ID
                id_text = self.font.render(str(agent_id), True,
                                           (255, 255, 255))
                self.window.blit(
                    id_text,
                    (j * self.cell_size + self.cell_size // 2 - 4,
                     i * self.cell_size + self.cell_size // 2 - 6)
                )

            # If post_analysis is enabled, save the current frame
            if self.post_analysis_on:
                frame = self.pygame.surfarray.array3d(self.window)
                frame = frame.swapaxes(0, 1)
                self.frames.append(frame)

    def display_render(self):
        """
        Display the rendered frame in the Pygame window.

        This method updates the Pygame display with the current frame.
        """
        if self.display:
            self.pygame.display.flip()

            # Handle Pygame events to prevent window from becoming unresponsive
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    self.end_render()

    def end_render(self):
        """
        Finalize the rendering process and clean up resources.

        This method shuts down the Pygame display and, if post_analysis_on is
        True, generates and saves a video from the collected frames using
        opencv.
        """
        if self.display or self.post_analysis_on:
            self._create_video()

            self.pygame.quit()

    def _create_video(self):
        # If post_analysis is enabled and we have frames, create a video
        if self.post_analysis_on and self.frames:
            import os
            try:
                import cv2
            except ImportError:
                warnings.warn(
                    "Error while importing cv2. "
                    "OpenCV is required to use post_analysis_on. "
                    "Please install OpenCV with `pip install cv2` "
                    "or `pip install ethicalgardeners[viz]`"
                )
                print("Couldn't create video, OpenCV not installed.")
                return

            # Create output directory if it doesn't exist
            os.makedirs(self.out_dir_path, exist_ok=True)

            # Define video properties based on the first frame
            height, width, _ = self.frames[0].shape
            output_path = os.path.join(self.out_dir_path,
                                       f'simulation_video_{self._run_id}.mp4')

            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(output_path, fourcc, 10, (width, height))

            # Write each frame to the video
            for frame in self.frames:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                video.write(frame)

            video.release()

            print(f"Video saved at {output_path}")
