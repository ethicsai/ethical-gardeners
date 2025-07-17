"""
The GardenersEnv module provides the main simulation environment for the
Ethical Gardeners reinforcement learning platform.

This module implements the PettingZoo AECEnv interface, serving as the primary
entry point of the simulation. It coordinates all simulation components:

1. World representation and state management (:py:mod:`.worldgrid`)
2. Agent actions and interactions (:py:class:`.ActionHandler`)
3. Observation generation (:py:mod:`.observation`)
4. Reward calculation (:py:class:`.RewardFunctions`)
5. Metrics tracking (:py:class:`.MetricsCollector`)
6. Visualization rendering (:py:mod:`.renderer`)

The environment is highly configurable through Hydra configuration files.
"""
import numpy as np
from pettingzoo import AECEnv
# import agent_selector or AgentSelector depending on python version
try:
    # Python 3.12 or earlier
    from pettingzoo.utils.agent_selector import AgentSelector
    use_function = True
except ImportError:
    try:
        # Python 3.13 or later
        from pettingzoo.utils import agent_selector
        use_function = False
    except ImportError:
        raise ImportError("Cannot agent_selector or AgentSelector")
from gymnasium.spaces import Discrete

from ethicalgardeners.action import create_action_enum
from ethicalgardeners.worldgrid import WorldGrid
from ethicalgardeners.actionhandler import ActionHandler
from ethicalgardeners.observation import TotalObservation, PartialObservation
from ethicalgardeners.rewardfunctions import RewardFunctions
from ethicalgardeners.metricscollector import MetricsCollector
from ethicalgardeners.renderer import ConsoleRenderer, GraphicalRenderer


class GardenersEnv(AECEnv):
    """
        Main environment class implementing the PettingZoo AECEnv interface.

        This class orchestrates the entire Ethical Gardeners simulation.

        The environment is configured through a Hydra configuration object that
        specifies grid initialization parameters, agent settings, observation
        type, rendering options, and more.

        Attributes:
            metadata (dict): Environment metadata for PettingZoo compatibility.
            config (object): Configuration object containing all environment
                settings.
            random_generator (np.random.RandomState): Random number generator
                for reproducible experiments.
            grid_world (:py:class:`.WorldGrid`): The simulated 2D grid world
                environment.
            prev_grid_world (:py:class:`.WorldGrid`): Copy of the previous grid
                world state.
            action_enum (:py:class:`._ActionEnum`): Enumeration of possible
                actions in the environment.
            possible_agents (list): List of all agent IDs in the environment.
            agents (dict): Mapping from agent IDs to Agent objects.
            action_handler (:py:class:`.ActionHandler`): Handler for processing
                agent actions.
            observation_strategy (:py:class:`.ObservationStrategy`): Strategy
                for generating agent observations.
            reward_functions (:py:class:`.RewardFunctions`): Functions for
                calculating agent rewards.
            metrics_collector (:py:class:`.MetricsCollector`): Collector for
                simulation metrics.
            renderers (list): List of renderer objects for visualization.
            num_iter (int): Maximum number of iterations for the simulation.
            render_mode (str): Current rendering mode ('human' or 'none').
            observations (dict): Current observations for all agents.
            rewards (dict): Current rewards for all agents.
            terminations (dict): Terminal state flags for all agents.
            truncations (dict): Truncation flags for all agents.
            infos (dict): Additional information for all agents.
            num_moves (int): Current number of moves executed in the
                simulation.
            actions_in_current_turn (int): Number of actions taken in the
                current turn.
        """
    metadata = {
        'render_modes': ['human', 'none'],
        'name': "ethical_gardeners"
    }

    def __init__(self, config):
        """
        Create the Ethical Gardeners environment.

        This method sets up the entire simulation environment based on the
        provided configuration.

        Args:
            config (object): Hydra configuration object containing all
                environment settings.
        """
        super().__init__()
        self.config = config

        # Random generator initialization
        self.random_generator = None
        random_seed = config.get("random_seed", None)
        if random_seed is not None:
            self.random_generator = np.random.RandomState(random_seed)

        # Common parameters for all grid initializations
        min_pollution = config.grid.get("min_pollution", 0)
        max_pollution = config.grid.get("max_pollution", 100)
        pollution_increment = config.grid.get("pollution_increment", 1)
        collisions_on = config.grid.get("collisions_on", True)
        num_seeds_returned = config.grid.get("num_seeds_returned", 1)
        flowers_data = config.grid.get("flowers_data", None)

        # Grid initialization
        grid_init_method = config.grid.get("init_method", "random")

        if grid_init_method == "from_file":
            file_path = config.grid.file_path
            self.grid_world = WorldGrid.init_from_file(
                file_path=file_path
            )

        elif grid_init_method == "from_code":
            grid_config = config.grid.get("config", None)

            if grid_config is not None:
                if "min_pollution" in grid_config:
                    min_pollution = grid_config["min_pollution"]
                if "max_pollution" in grid_config:
                    max_pollution = grid_config["max_pollution"]
                if "pollution_increment" in grid_config:
                    pollution_increment = grid_config["pollution_increment"]
                if "collisions_on" in grid_config:
                    collisions_on = grid_config["collisions_on"]
                if "num_seeds_returned" in grid_config:
                    num_seeds_returned = grid_config["num_seeds_returned"]
                if "flowers_data" in grid_config:
                    flowers_data = grid_config["flowers_data"]

                self.grid_world = WorldGrid.init_from_code(
                    grid_config=grid_config
                )
            else:
                self.grid_world = WorldGrid.init_from_code()

        elif grid_init_method == "random":
            width = config.grid.get("width", 10)
            height = config.grid.get("height", 10)
            obstacles_ratio = config.grid.get("obstacles_ratio", 0.2)
            nb_agent = config.grid.get("nb_agent", 2)

            self.grid_world = WorldGrid.init_random(
                width=width,
                height=height,
                random_generator=self.random_generator,
                obstacles_ratio=obstacles_ratio,
                nb_agent=nb_agent
            )

        else:
            self.grid_world = WorldGrid.init_random()

        # Set the grid properties
        self.grid_world.min_pollution = min_pollution
        self.grid_world.max_pollution = max_pollution
        self.grid_world.pollution_increment = pollution_increment
        self.grid_world.collisions_on = collisions_on
        self.grid_world.num_seeds_returned = num_seeds_returned
        if flowers_data is not None:
            self.grid_world.flowers_data = flowers_data

        # Create the action space from the number of flowers types
        num_flower_types = len(self.grid_world.flowers_data)
        self.action_enum = create_action_enum(num_flower_types)

        # Set PettingZoo parameters
        self.num_iter = config.get("num_iterations", 1000)
        self.render_mode = config.get("render_mode", "none")
        self.possible_agents = [f"agent_{i}" for i in
                                range(len(self.grid_world.agents))]
        self.agents = {self.possible_agents[i]: self.grid_world.agents[i] for i
                       in range(len(self.grid_world.agents))}

        # Initialise ActionHandler
        self.action_handler = ActionHandler(
            self.grid_world,
            self.action_enum
        )

        # Initialise observation strategy
        observation_type = config.observation.get("type", "total")
        if observation_type == "total":
            self.observation_strategy = TotalObservation(
                self.grid_world,
                self.agents
            )
        elif observation_type == "partial":
            obs_range = config.observation.get("range", 1)
            self.observation_strategy = PartialObservation(
                self.agents,
                obs_range
            )
        else:
            self.observation_strategy = TotalObservation(
                self.grid_world,
                self.agents
            )

        # Initialise reward functions
        self.reward_functions = RewardFunctions(
            self.action_enum
        )

        # Initialise metrics collector
        metrics_out_dir = config.metrics.get("out_dir_path", "./metrics")
        export_metrics = config.metrics.get("export_on", False)
        send_metrics = config.metrics.get("send_on", False)
        self.metrics_collector = MetricsCollector(
            metrics_out_dir,
            export_metrics,
            send_metrics
        )

        # Initialise renderer
        self.renderers = []

        if config.renderer.graphical.get("enabled", False):
            post_analysis_on = config.renderer.graphical.get(
                "post_analysis_on", False
            )
            out_dir = config.renderer.graphical.get("out_dir_path", "./videos")
            cell_size = config.renderer.graphical.get("cell_size", 50)
            colors = config.renderer.graphical.get("colors", None)

            graphical_renderer = GraphicalRenderer(
                cell_size=cell_size,
                colors=colors,
                post_analysis_on=post_analysis_on,
                out_dir_path=out_dir,
            )
            self.renderers.append(graphical_renderer)

        if config.renderer.console.get("enabled", False):
            post_analysis_on = config.renderer.console.get(
                "post_analysis_on",  False
            )
            out_dir = config.renderer.console.get("out_dir_path", "./videos")
            characters = config.renderer.console.get("characters", None)

            console_renderer = ConsoleRenderer(
                characters=characters,
                post_analysis_on=post_analysis_on,
                out_dir_path=out_dir,

            )
            self.renderers.append(console_renderer)

        for renderer in self.renderers:
            renderer.init(self.grid_world)

    def action_space(self, agent_id):
        """
        Return the action space for a specific agent.

        This method returns a Discrete space representing all possible actions
        the agent can take in the environment.

        Args:
            agent_id (str): The ID of the agent to get the action space for.

        Returns:
            gymnasium.spaces.Discrete: The action space for the specified
                agent.
        """
        return Discrete(len(self.action_enum))

    def observation_space(self, agent_id):
        """
        Return the observation space for a specific agent.

        This method delegates to the observation strategy to return the
        appropriate observation space based on the configured observation type.

        Args:
            agent_id (str): The ID of the agent to get the observation space
                for.

        Returns:
            gymnasium.spaces.Space: The observation space for the specified
                agent.
        """
        return self.observation_strategy.observation_space(agent_id)

    def reset(self, seed=None, options=None):
        """
        Reset the environment to its initial state.

        This method resets the agent selector, metrics collector, move counter,
        and initializes the observations, rewards, terminations, truncations,
        and info dictionaries for all agents.

        Args:
            seed (int, optional): Random seed for environment initialization.
            options (dict, optional): Additional options for reset
                customization.

        Returns:
            tuple: A tuple containing:
                - observations (dict): Initial observations for all agents.
                - infos (dict): Additional information for all agents.
        """
        # Initialise the agent selector
        # Selects the agent selector class based on the Python version
        if use_function:
            self._agent_selector = AgentSelector(self.possible_agents)
        else:
            self._agent_selector = agent_selector(self.possible_agents)
        self.agent_selection = self._agent_selector.next()

        # Reset metrics
        self.metrics_collector.reset_metrics()

        # Reset move counter
        self.num_moves = 0

        # Reset the counter of actions in the turn
        self.actions_in_current_turn = 0

        # Save the previous grid world state for rewards calculation
        self.prev_grid_world = self.grid_world.copy()

        # Initialise needed data structures for all agents
        self.observations = {agent_id: None for agent_id in
                             self.possible_agents}
        self.rewards = {agent_id: 0 for agent_id in self.possible_agents}
        self.terminations = {agent_id: False for agent_id in
                             self.possible_agents}
        self.truncations = {agent_id: False for agent_id in
                            self.possible_agents}
        self.infos = {agent_id: {} for agent_id in self.possible_agents}

        # Update action masks for all agents
        for agent_id in self.possible_agents:
            self.action_handler.update_action_mask(self.agents[agent_id])

        # Initialise the observations for all agents
        for agent_id in self.possible_agents:
            self.observations[agent_id] = {
                "observation": self._get_observations(agent_id),
                "action_mask": self.agents[agent_id].action_mask
            }

        return self.observations, self.infos

    def step(self, action):
        """
        Execute a step in the environment for the current agent.

        This method processes the action for the current agent, updates the
        environment state, calculates rewards, generates new observations,
        updates metrics, and selects the next agent to act.

        If all agents have taken an action in the current turn, it updates the
        environmental conditions (pollution, flower growth).

        Args:
            action (int): The action to take for the current agent.

        Returns:
            dict: The observation for the next agent to act.
        """
        if (self.truncations[self.agent_selection] or
                self.terminations[self.agent_selection]):
            self._was_dead_step(action)
            return

        # Update action masks for all agents
        for agent_id in self.possible_agents:
            self.action_handler.update_action_mask(self.agents[agent_id])

        agent_id = self.agent_selection
        agent = self.agents[agent_id]

        # Handle the action for the agent
        action_enum_value = list(self.action_enum)[action]
        self.action_handler.handle_action(agent, action_enum_value)

        # Increment action counter for the current turn
        self.actions_in_current_turn += 1

        # Count active agents (those that are not terminated or truncated)
        active_agents = sum(1 for a in self.possible_agents if
                            not (self.terminations[a] or self.truncations[a]))

        # Update pollution once all active agents have acted
        if self.actions_in_current_turn >= active_agents:
            self.grid_world.update_cell()
            self.actions_in_current_turn = 0

        # Update the observations, rewards, and info for the agent
        self.observations[agent_id] = {
            "observation": self._get_observations(agent_id),
            "action_mask": agent.action_mask
        }
        rewards = self._get_rewards(agent_id, self.grid_world,
                                    self.prev_grid_world, action_enum_value)
        self.rewards[agent_id] = rewards['total']
        self.infos[agent_id] = self._get_info(agent_id, rewards)

        # Update metrics
        self.metrics_collector.update_metrics(
            self.grid_world,
            self.rewards,
            self.agent_selection
        )

        # Export and send metrics if configured
        self.metrics_collector.export_metrics()
        self.metrics_collector.send_metrics()

        # Save the current grid world state for the next step
        self.prev_grid_world = self.grid_world.copy()

        self.num_moves += 1

        # Check if the agent has reached a terminal state
        self.truncations = {agent: self.num_moves >= self.num_iter
                            for agent in self.possible_agents}

        # Selects the next agent
        self.agent_selection = self._agent_selector.next()

        self.render()

        return self.observe(self.agent_selection)

    def observe(self, agent_id):
        """
        Return the current observation for a specific agent.

        Args:
            agent_id (str): The ID of the agent to get the observation for.

        Returns:
            dict: The observation for the specified agent, containing:
                - observation: The agent's view of the environment.
                - action_mask: Binary mask indicating valid actions.
        """
        return self.observations[agent_id]

    def render(self):
        """
        Render the current state of the environment.

        This method uses all configured renderers to visualize the current
        state of the grid world and agents.
        """
        for renderer in self.renderers:
            renderer.render(self.grid_world, self.agents)

            if self.render_mode == "human":
                renderer.display_render()

    def close(self):
        """
        Close the environment and clean up resources.

        This method finalizes all renderers.
        """
        for renderer in self.renderers:
            renderer.end_render()

    def _get_observations(self, agent_id):
        """
        Generate the observation for a specific agent.

        This method delegates to the observation strategy to generate the
        appropriate observation based on the agent's configured observation
        type.

        Args:
            agent_id (str): The ID of the agent to generate the observation
                for.

        Returns:
            object: The observation for the specified agent.
        """
        return self.observation_strategy.get_observation(self.grid_world,
                                                         agent_id)

    def _get_rewards(self, agent_id, grid_world, prev_grid_world, action):
        """
        Calculate the rewards for a specific agent.

        This method delegates to the reward functions to calculate the
        appropriate rewards based on the agent's actions and changes in the
        environment.

        Args:
            agent_id (str): The ID of the agent to calculate rewards for.
            grid_world (:py:class:`.WorldGrid`): The current state of the grid
                world.
            prev_grid_world (:py:class:`.WorldGrid`): The previous state of the
                grid world.
            action (:py:class:`._ActionEnum`): The action taken by the agent.

        Returns:
            dict: Dictionary of reward components and total reward.
        """
        # get the agent from its ID
        agent = self.agents[agent_id]

        # Compute the rewards
        rewards = self.reward_functions.compute_reward(
            prev_grid_world,
            grid_world,
            agent,
            action
        )

        return rewards

    def _get_info(self, agent_id, rewards):
        """
        Generate additional information for a specific agent.

        This method creates a dictionary of additional information that is
        provided alongside the observation and reward.

        Args:
            agent_id (str): The ID of the agent to generate info for.
            rewards (dict): The reward components for the agent.

        Returns:
            dict: Additional information for the specified agent.
        """
        return {
            'rewards': rewards,
        }

    def last(self):
        """
        Return the most recent environment step information.

        This method returns all relevant information about the most recent
        step taken by the current agent.

        Returns:
            tuple: A tuple containing:
                - observation (dict): The current observation.
                - reward (float): The most recent reward.
                - termination (bool): Whether the agent is in a terminal state.
                - truncation (bool): Whether the episode was truncated.
                - info (dict): Additional information.
        """
        agent_id = self.agent_selection
        observation = self.observations[agent_id]
        reward = self.rewards[agent_id]
        termination = self.terminations[agent_id]
        truncation = self.truncations[agent_id]
        info = self.infos[agent_id]

        return observation, reward, termination, truncation, info

    def _was_dead_step(self, action=None):
        """
        Handle a step for an agent that is already terminated or truncated.

        This method is called when an agent attempts to take an action after
        it has already reached a terminal state or the episode has been
        truncated. It assigns zero reward and selects the next agent.

        Args:
            action (int, optional): The action that was attempted.
        """
        agent_id = self.agent_selection
        self.rewards[agent_id] = 0
        self._agent_selector.next()
