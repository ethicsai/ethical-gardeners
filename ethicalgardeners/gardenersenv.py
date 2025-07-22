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
    # Python 3.13+
    from pettingzoo.utils.agent_selector import (
        AgentSelector as agent_selector)
except ImportError:
    # Python 3.12 and below
    from pettingzoo.utils import agent_selector
from gymnasium.spaces import Discrete


class GardenersEnv(AECEnv):
    """
        Main environment class implementing the PettingZoo AECEnv interface.

        This class orchestrates the entire Ethical Gardeners simulation.

        The environment is configured through a Hydra configuration object that
        specifies grid initialization parameters, agent settings, observation
        type, rendering options, and more.

        Attributes:
            metadata (dict): Environment metadata for PettingZoo compatibility.
            random_generator (:py:class:`np.random.RandomState`): Random number
                generator for reproducible experiments.
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

    def __init__(self, random_generator, grid_world, action_enum, num_iter,
                 render_mode, action_handler, observation_strategy,
                 reward_functions, metrics_collector, renderers):
        """
        Create the Ethical Gardeners environment.

        This method sets up the entire simulation environment based on the
        provided configuration.

        Args:
            random_generator (:py:class:`.np.random.RandomState`): Random
                number generator for reproducibility.
            grid_world (:py:class:`.WorldGrid`): The grid world representing
                the simulation environment.
            action_enum (:py:class:`._ActionEnum`): Enumeration of possible
                actions in the environment.
            num_iter (int): Maximum number of iterations for the simulation.
            render_mode (str): Rendering mode for the environment ('human' or
                'none').
            action_handler (:py:class:`.ActionHandler`): Handler for processing
                agent actions.
            observation_strategy (:py:class:`.ObservationStrategy`): Strategy
                for generating agent observations.
            reward_functions (:py:class:`.RewardFunctions`): Functions for
                calculating agent rewards.
            metrics_collector (:py:class:`.MetricsCollector`): Collector for
                simulation metrics.
            renderers (list): List of renderer objects for visualization.
        """
        super().__init__()

        # Set random generator
        self.random_generator = random_generator

        # Set the grid world
        self.grid_world = grid_world

        # Set PettingZoo parameters
        self.num_iter = num_iter
        self.render_mode = render_mode
        self.possible_agents = [f"agent_{i}" for i in
                                range(len(self.grid_world.agents))]
        self.agents = {self.possible_agents[i]: self.grid_world.agents[i] for i
                       in range(len(self.grid_world.agents))}

        # Set environment components
        self.action_enum = action_enum
        self.action_handler = action_handler
        self.observation_strategy = observation_strategy
        self.reward_functions = reward_functions
        self.metrics_collector = metrics_collector
        self.renderers = renderers

        # Initialize renderers
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
        agent = self.agents[agent_id]
        return self.observation_strategy.observation_space(agent)

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
        self._agent_selector = agent_selector(self.possible_agents)
        self.agent_selection = self._agent_selector.next()

        # Set the random generator if a seed is provided
        if seed is not None:
            self.random_generator = np.random.RandomState(seed)
            self.grid_world.random_generator = self.random_generator

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

        # Update observation and action mask for all agents
        for agent_idx in self.possible_agents:
            agentx = self.agents[agent_idx]
            self.action_handler.update_action_mask(agentx)

            self.observations[agent_idx] = {
                "observation": self._get_observations(agent_idx),
                "action_mask": agentx.action_mask
            }

        # Update the rewards, and info for the agent
        rewards = self._get_rewards(agent_id, action_enum_value)
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
        agent = self.agents[agent_id]
        return self.observation_strategy.get_observation(self.grid_world,
                                                         agent)

    def _get_rewards(self, agent_id, action):
        """
        Calculate the rewards for a specific agent.

        This method delegates to the reward functions to calculate the
        appropriate rewards based on the agent's actions and changes in the
        environment.

        Args:
            agent_id (str): The ID of the agent to calculate rewards for.
            action (:py:class:`._ActionEnum`): The action taken by the agent.

        Returns:
            dict: Dictionary of reward components and total reward with the
                following keys:

                - 'total': The mono-objective reward for the agent. Computed
                  as the average of all reward components.
                - 'ecology': The ecological reward component.
                - 'wellbeing': The wellbeing reward component.
                - 'biodiversity': The biodiversity reward component.
        """
        # get the agent from its ID
        agent = self.agents[agent_id]

        # Compute the rewards
        rewards = self.reward_functions.compute_reward(
            self.prev_grid_world,
            self.grid_world,
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
            dict: Additional information for the specified agent with the
                following keys:

                - 'rewards': The reward dict for the agent containing each
                  reward component and the total reward.
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
                - observation (dict): The current observation. The dictionary
                  contains:

                  - observation (:py:class:`numpy.ndarray`): The agent's view
                    of the environment.
                  - action_mask (:py:class:`numpy.ndarray`): Binary mask
                    indicating valid actions.
                - reward (float): The most recent reward.
                - termination (bool): Whether the agent is in a terminal state.
                - truncation (bool): Whether the episode was truncated.
                - info (dict): Additional information about the agent. Refer to
                  :py:meth:`_get_info` for details on the returned value.
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
