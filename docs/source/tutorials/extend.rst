Tutorial: How to Extend the Ethical Gardeners Environment
=========================================================

This tutorial explains how to extend different components of the Ethical Gardeners environment.

1. Adding or Modifying Reward Functions
---------------------------------------

Reward functions determine how agents are evaluated in the environment. The ``RewardFunctions`` class in ``rewardfunctions.py`` contains methods for calculating rewards.

Current Structure
^^^^^^^^^^^^^^^^^

The ``RewardFunctions`` class calculates three types of rewards:

* Ecological (``compute_ecology_reward``)
* Well-being (``compute_wellbeing_reward``)
* Biodiversity (``compute_biodiversity_reward``)

These rewards are then combined in the ``compute_reward`` method by averaging the 3.

How to Add a New Reward Function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Add a new method to the ``RewardFunctions`` class
2. Modify the ``compute_reward`` method to include your new reward

Example: Adding a Collaboration Reward
""""""""""""""""""""""""""""""""""""""

.. code-block:: python

   def compute_collaboration_reward(self, grid_world_prev, grid_world, agent, action):
       """
       Compute a reward based on how well agents collaborate to maintain
       balanced planting across the grid.

       Args:
           grid_world_prev: The grid world before the action
           grid_world: The current grid world after the action
           agent: The agent performing the action
           action: The action performed

       Returns:
           float: Normalized collaboration reward between -1 and 1
       """
       # Code to calculate collaboration reward

       return reward

Then, modify the ``compute_reward`` method:

.. code-block:: python

   def compute_reward(self, grid_world_prev, grid_world, agent, action):
       """Compute the multi-objective reward for an agent."""
       ecology_reward = self.compute_ecology_reward(grid_world_prev, grid_world, agent, action)
       wellbeing_reward = self.compute_wellbeing_reward(grid_world_prev, grid_world, agent, action)
       biodiversity_reward = self.compute_biodiversity_reward(grid_world_prev, grid_world, agent, action)
       collaboration_reward = self.compute_collaboration_reward(grid_world_prev, grid_world, agent, action)

       return {
           'ecology': ecology_reward,
           'wellbeing': wellbeing_reward,
           'biodiversity': biodiversity_reward,
           'collaboration': collaboration_reward,
           'total': (ecology_reward + wellbeing_reward + biodiversity_reward + collaboration_reward) / 4
       }

2. Adding an Observation Type
-----------------------------

Observations determine how agents perceive the environment. The ``observation.py`` module contains observation strategies.

Current Structure
^^^^^^^^^^^^^^^^^

The module implements an abstract ``ObservationStrategy`` class with two concrete implementations:

* ``TotalObservation``: provides a complete view of the grid
* ``PartialObservation``: provides a limited view around the agent

How to Add a New Observation Type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Create a new class that inherits from ``ObservationStrategy``
2. Implement the ``observation_space`` and ``get_observation`` methods
3. Modify the make_env function to include your new observation type

Example: Adding a Total Observation with Only Pollution Levels and Flower Growth Stages
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. code-block:: python

   class TotalObservationPollutionFlowers(ObservationStrategy):
       """
       Strategy that provides agents with a full view of the grid,
       only including pollution levels and flower growth stages.
       """

       def __init__(self, grid_world):
           """
           Create the observation strategy.

           Args:
               grid_world: The grid world environment to observe
           """
           super().__init__()
           self.observation_shape = (grid_world.width, grid_world.height, FEATURES_PER_CELL)

       def observation_space(self, agent):
           """Define the observation space."""
           return Box(low=0, high=1, shape=self.observation_shape, dtype=np.float32)

       def get_observation(self, grid_world, agent):
           """Generate a complete observation but without every features of the grid."""
           obs = np.zeros(self.observation_shape, dtype=np.float32)

           # Code calculating observation features

           return obs

Then, add your new observation type to the make_env function:

.. code-block:: python

   def make_env(config):
       """Create the environment based on the configuration."""
       # Existing code...

       elif observation_type == "partial":
           obs_range = config.observation.get("range", 1)
           observation_strategy = PartialObservation(
               obs_range
           )
       elif observation_type == "total_pollution_flowers":
           observation_strategy = TotalObservationPollutionFlowers(
               grid_world=grid_world
           )

       # Existing code...

3. Adding Actions and Handling Them
-----------------------------------

Actions determine what agents can do in the environment. The ``action.py`` and ``actionhandler.py`` modules manage actions.

Current Structure
^^^^^^^^^^^^^^^^^

* ``action.py`` defines the enumeration of possible actions
* ``actionhandler.py`` implements action handling

How to Add New Actions
^^^^^^^^^^^^^^^^^^^^^^

1. Modify the ``create_action_enum`` function in ``action.py``
2. Add a handling method in ``ActionHandler``
3. Update the ``handle_action`` method to call your new method
4. Update the ``update_action_mask`` method to include your new action

Example: Adding a Pollution Cleaning Action
"""""""""""""""""""""""""""""""""""""""""""

First, modify ``create_action_enum`` in ``action.py``:

.. code-block:: python

   def create_action_enum(num_flower_type=1):
       """Dynamically create an enumeration of actions."""
       actions = {
           'UP': 0,
           'DOWN': 1,
           'LEFT': 2,
           'RIGHT': 3,
           'HARVEST': 4,
           'WAIT': 5,
           'CLEAN': 6,  # New action for cleaning pollution
       }

       for i in range(num_flower_type):
           action_name = f'PLANT_TYPE_{i}'
           actions[action_name] = auto()

       return Enum('Action', actions, type=_ActionEnum)

Then, add a method in ``ActionHandler``:

.. code-block:: python

   def clean_pollution(self, agent):
       """
       Clean pollution at the agent's current position.

       This action reduces pollution in the current cell by a fixed amount.

       Args:
           agent: The agent performing the cleaning action
       """
       # handle the cleaning action

Finally, update ``handle_action``:

.. code-block:: python

   def handle_action(self, agent, action):
       """Process an agent's action and execute it in the grid world."""
       if action in [self.action_enum.UP, self.action_enum.DOWN,
                     self.action_enum.LEFT, self.action_enum.RIGHT]:
           self.move_agent(agent, action)
       elif action == self.action_enum.HARVEST:
           self.harvest_flower(agent)
       elif action == self.action_enum.WAIT:
           self.wait(agent)
       elif action == self.action_enum.CLEAN:
           self.clean_pollution(agent)
       else:  # Assume action is a PLANT_TYPE_i action
           self.plant_flower(agent, action.flower_type)

Don't forget to update ``update_action_mask`` to handle the new action:

.. code-block:: python

   def update_action_mask(self, agent):
       """Update the action mask for the agent."""
       # Existing code...

       # Always allow cleaning action if the cell has pollution
       cell = self.grid_world.get_cell(agent.position)
       if cell.pollution is None:
           mask[self.action_enum.CLEAN.value] = 0

       # Rest of existing code...

4. Adding a Cell Type
---------------------

Cell types define different parts of the environment. They are defined in ``worldgrid.py``.

Current Structure
^^^^^^^^^^^^^^^^^

* ``CellType`` is an enumeration with two types: ``GROUND`` and ``OBSTACLE``
* ``Cell`` is a class that represents a grid cell

How to Add a New Cell Type
^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Add a new value to the ``CellType`` enumeration
2. Modify the ``Cell`` class to handle the new type
3. Update the methods of the ``Cell`` class
4. Modify the grid initialization to include the new cell type
5. Modify the config
6. Modify the renderers to visualize the new cell type

Example: Adding a "WATER" Cell Type
"""""""""""""""""""""""""""""""""""

.. code-block:: python

   class CellType(Enum):
       """Enum representing the possible types of cells in the grid world."""
       GROUND = 0
       OBSTACLE = 1
       WATER = 2  # New cell type

Modify the ``Cell`` class to handle this new type:

.. code-block:: python

   def __init__(self, cell_type, pollution=50, pollution_increment=1):
       """Create a new cell."""
       self.cell_type = cell_type
       self.flower = None
       self.agent = None

       if cell_type == CellType.GROUND:
           self.pollution = pollution
       elif cell_type == CellType.OBSTACLE:
           self.pollution = None
       elif cell_type == CellType.WATER:
           self.pollution = pollution * 0.5  # Water initially has less pollution

       self.pollution_increment = pollution_increment

   def update_pollution(self, min_pollution, max_pollution):
       """Update the pollution level of the cell based on its current state."""
       if self.pollution is None:
           return

       if self.has_flower():
           self.pollution = max(
               self.pollution - self.flower.get_pollution_reduction(),
               min_pollution
           )
       else:
           # Water self-cleans
           if self.cell_type == CellType.WATER:
               self.pollution = max(
                   self.pollution - self.pollution_increment * 0.5,
                   min_pollution
               )
           else:
               self.pollution = min(
                   self.pollution + self.pollution_increment,
                   max_pollution
               )

   def can_walk_on(self):
       """Check if agents can walk on this cell."""
       return self.cell_type in [CellType.GROUND, CellType.WATER]

   def can_plant_on(self):
       """Check if a flower can be planted in this cell."""
       # Cannot plant in water
       return self.cell_type == CellType.GROUND and not self.has_flower()

Modify the grid initialization to include the new cell type by doing one of the following:

- Add the following to ``init_from_file`` after placing ground and obstacle cells:

.. code-block:: python

   elif cell_code == 'W':
       grid[i][j] = Cell(CellType.WATER)

- Add a water_ratio parameter to ``init_random`` and add the following after placing ground and obstacle cells and updating valid_positions:

.. code-block:: python

   # Place obstacles randomly
   indices = np.arange(len(valid_positions))  # choice needs indices
   num_waters = int(water_ratio * width * height)
   selected_indices = random_generator.choice(indices,
                                              num_waters,
                                              replace=False)
   water_positions = [valid_positions[i] for i in selected_indices]

   for pos in water_positions:
    i, j = pos
    grid[i][j] = Cell(CellType.WATER)
    valid_positions.remove(pos)

- If you want to use ``init_from_code``, you don't need to modify the code.

Modify the config to include the new cell type:

- Modify ``from_code.yaml`` to place water cell or add the ``water_ratio`` parameter in ``random.yaml`` if you want to place water cells in the grid.

- Modify ``console.yaml``, ``graphical.yaml`` and ``full.yaml`` to include the new cell type in the characters and colors dictionaries.

Modify the renderers to visualize the new cell type:

Add the following to the ``render`` method of ``ConsoleRenderer`` after defining the character for ground and obstacle cells:

.. code-block:: python

   elif cell.cell_type == CellType.WATER:
       cell_char = self.characters.get('water', 'W')

Add the following to the ``render`` method of ``GraphicalRenderer`` after defining the color for ground and obstacle cells:

.. code-block:: python

   elif cell.cell_type == CellType.WATER:
       cell_color = self.colors['water']

5. Adding or Modifying Metrics
------------------------------

Metrics allow tracking agent performance and environment state.

Current Structure
^^^^^^^^^^^^^^^^^

* The class stores metrics in a dictionary
* ``export_metrics`` exports metrics to a CSV file
* ``send_metrics`` sends metrics to Weights & Biases

How to Add New Metrics
^^^^^^^^^^^^^^^^^^^^^^

1. Add new keys to the ``metrics`` dictionary in initialization
2. Update metrics during simulation
3. Modify ``_prepare_metrics`` to include your new metrics

Example: Adding Diversity Metrics
"""""""""""""""""""""""""""""""""

.. code-block:: python

   def __init__(self, ...):
       # Existing code...

       self.metrics = {
           # Existing metrics...

           # New metrics
           "diversity": {},
           "agent_cooperation_score": 0.0,
       }

   def update_metrics(self, grid_world, agents, rewards):
       """Update metrics based on the current state of the grid."""
       # Existing code to update metrics...

       # Calculate new metrics

   def _prepare_metrics(self):
       """Prepare a formatted dictionary of metrics for export or sending."""
       metrics_dict = {
           # Existing metrics...
       }

       # Add new metrics
       metrics_dict['diversity'] = diversity
       metrics_dict['agent_cooperation_score'] = self.metrics["agent_cooperation_score"]

       return metrics_dict

6. Adding a New Renderer Type
-----------------------------

Renderers visualize the simulation environment. The ``renderer.py`` module defines an abstract ``Renderer`` class and concrete implementations like ``GraphicalRenderer`` (using Pygame) and ``ConsoleRenderer`` (text-based).

Current Structure
^^^^^^^^^^^^^^^^

* ``Renderer``: Abstract base class with methods:
* ``init(grid_world)``: Sets up the rendering environment
* ``render(grid_world, agents)``: Renders the current state (abstract)
* ``display_render()``: Updates the display with the current frame (abstract)
* ``end_render()``: Finalizes rendering and handles cleanup

* Concrete implementations:

  * ``GraphicalRenderer``: Colorful Pygame visualization
  * ``ConsoleRenderer``: Text-based visualization in terminal

How to Add a New Renderer
^^^^^^^^^^^^^^^^^^^^^^^^

1. Create a new class that inherits from ``Renderer``
2. Implement the required abstract methods
3. Register your renderer in the configuration system
4. Modify the make_env function to include your new renderer

Example: Adding a Heatmap Renderer
"""""""""""""""""""""""""""""""""

.. code-block:: python

   class HeatmapRenderer(Renderer):
       """
       Renderer that visualizes the environment as a pollution heatmap using matplotlib.

       This renderer focuses on pollution levels across the grid, displaying them
       as a color-coded heatmap with additional annotations for agents and flowers.
       """

       def __init__(self, post_analysis_on=False, out_dir_path=None, cmap='coolwarm'):
           """
           Create the heatmap renderer.

           Args:
               post_analysis_on (bool, optional): Flag to enable saving frames for
                   post-simulation video generation. Defaults to False.
               out_dir_path (str, optional): Directory path where output files will be saved.
                   Required if post_analysis_on is True. Defaults to None.
               cmap (str, optional): Matplotlib colormap to use for the heatmap.
                   Defaults to 'coolwarm'.
           """
           super().__init__()
           self.cmap = cmap
           self.fig = None
           self.ax = None

           self.post_analysis_on = post_analysis_on
           self.out_dir_path = out_dir_path
           self.frames = []

           # Initialize run_id for video output naming
           self._run_id = None
           if post_analysis_on:
               import time
               self._run_id = int(time.time())

           import matplotlib.pyplot as plt
           self.plt = plt

       def init(self, grid_world):
           """
           Initialize the matplotlib figure based on the grid world dimensions.

           Args:
               grid_world (WorldGrid): The grid world environment to be rendered.
           """
           pass

       def render(self, grid_world, agents):
           """
           Render the current state of the grid world as a heatmap.

           Args:
               grid_world (WorldGrid): The current state of the world grid to render.
               agents (dict): Dictionary mapping agent IDs to Agent objects.
           """
           pass

       def display_render(self):
           """
           Display the rendered frame in a matplotlib window.
           """
           pass

       def end_render(self):
           """
           Finalize the rendering process and clean up resources.

           If post_analysis_on is True, generates and saves a video from the
           collected frames using opencv.
           """
           # If post_analysis is enabled and we have frames, create a video
           if self.post_analysis_on and self.frames:
               # Same code as in end_render of GraphicalRenderer

               print(f"Heatmap video saved at {output_path}")

           # Close the matplotlib figure
           self.plt.close(self.fig)

To use this new renderer, you would configure it in your config:

.. code-block:: yaml

   renderer:
      heatmap:
         enabled: true
         post_analysis_on: true
         out_dir_path: "./videos"
         cmap: 'coolwarm'

And modify the ``make_env`` function to include the new renderer:

.. code-block:: python

   # Initialise renderer
        self.renderers = []

        # Existing renderers

        if config.renderer.heatmap.get("enabled", False):
            post_analysis_on = config.renderer.heatmap.get(
                "post_analysis_on",  False
            )
            out_dir = config.renderer.heatmap.get("out_dir_path", "./videos")
            cmap = config.renderer.heatmap.get("cmap", 'coolwarm')

            heatmap_renderer = HeatmapRenderer(
                post_analysis_on=post_analysis_on,
                out_dir_path=out_dir,
                cmap=cmap
            )
            self.renderers.append(heatmap_renderer)
