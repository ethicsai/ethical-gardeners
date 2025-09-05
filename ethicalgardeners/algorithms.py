"""
Utilities to train and evaluate RL agents using Stable Baselines3 on the
EthicalGardeners PettingZoo AEC environment.
"""
import glob
import os
import time
import numpy as np

from gymnasium import Env
from pettingzoo.utils import BaseWrapper


class SB3Wrapper(BaseWrapper, Env):
    """
    Wrapper to adapt a PettingZoo AEC environment to be compatible with Stable
    Baselines3.
    - Only returns the observation (without action mask) for the current agent.
    - the observation_space and action_space are aligned with the current
      agent.
    """
    def reset(self, seed=None, options=None):
        """
        Align the observation_space and action_space with the current agent and
        return the initial observation and info as per Gymnasium API.
        """
        super().reset(seed, options)

        self.observation_space = (
            super().observation_space(self.agent_selection)
        )
        self.action_space = super().action_space(self.agent_selection)

        # Return initial observation, info as per Gymnasium API
        return self.observe(self.agent_selection), {}

    def step(self, action):
        current_agent = self.agent_selection

        super().step(action)

        next_agent = self.agent_selection

        return (
            self.observe(next_agent),
            self.rewards[current_agent],
            self.terminations[current_agent],
            self.truncations[current_agent],
            self.infos[current_agent]
        )

    def observe(self, agent):
        """
        Return the observation without the action mask for the current agent.
        """
        return super().observe(agent)["observation"]

    def action_mask(self):
        """
        Return the action mask for the current agent.
        """
        return super().observe(self.agent_selection)["action_mask"]


def mask_fn(env):
    """
    Return the function that provides the action mask for the current agent.
    """
    return env.action_mask()


# Saved files helpers
def _policy_prefix(algorithm_name: str):
    """
    Generate a prefix for saving/loading policies based on the algorithm.

    Args:
        algorithm_name: The algorithm name (e.g., "maskable_ppo", "dqn"). It is
            used in the policy name.
    """
    return f"{algorithm_name}"


def save_model(model, algorithm_name: str):
    """
    Save the trained model with a timestamped filename.

    Args:
        model: The trained model to save.
        env: The environment instance.
        algorithm_name: The algorithm name (e.g., "maskable_ppo", "dqn"). It is
            used in the saved file's name.
    """
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = f"{_policy_prefix(algorithm_name)}_{ts}"
    model.save(path)
    return f"{path}.zip"


def get_latest_policy(algorithm_name: str):
    """
    Retrieve the most recently saved policy file for the given environment and
    algorithm.

    Args:
        algorithm_name: The algorithm name (e.g., "maskable_ppo", "dqn"). It is
            used in the search pattern for the saved file.
    """
    try:
        pattern = f"{_policy_prefix(algorithm_name)}*.zip"
        latest = max(glob.glob(pattern), key=os.path.getctime)
    except ValueError:
        print("Policy not found.")
        raise SystemExit(0)

    return latest


def make_SB3_env(env_fn, config):
    """
    Create a Stable Baselines3 compatible environment with action masking.

    Args:
        env_fn: A function that takes a config and returns a PettingZoo AEC env
        config: Hydra configuration parameters for the environment.
    """
    try:
        from sb3_contrib.common.wrappers import ActionMasker
    except ImportError as e:
        raise RuntimeError(
            "This algorithm requires `sb3-contrib`. "
            "Install it via: pip install sb3-contrib"
        ) from e

    env = SB3Wrapper(env_fn(config))
    env = ActionMasker(env, mask_fn)
    env.reset(seed=config["random_seed"])

    return env


def make_env_thunk(env_fn, config):
    """
    Return a thunk that creates a Stable Baselines3 compatible environment.

    Args:
        env_fn: A function that takes a config and returns a PettingZoo AEC env
        config: Hydra configuration parameters for the environment.
    """
    def thunk():
        return make_SB3_env(env_fn, config)

    return thunk


def train(model, algorithm_name: str = "maskable_ppo", total_timesteps=10_000):
    """
    Train a given model and save it.

    Args:
        model: A model instance to train. The model class should contain a
            `learn` method and a `save` method as in Stable Baselines3.
        algorithm_name: The algorithm name (e.g., "maskable_ppo", "dqn"). It is
            used in the saved file's name.
        total_timesteps: The total number of timesteps to train the model.
    """
    print(f"Starting training with {algorithm_name}")

    model.learn(total_timesteps=total_timesteps)

    save_model(model, algorithm_name)

    print("Model has been saved.")
    print("Finished training")


def evaluate(env, model, algorithm_name: str = "maskable_ppo", num_games=100,
             seed=42, deterministic=True, needs_action_mask=False, **kwargs):
    """
    Evaluate a trained agent vs a random agent

    Args:
        env: A PettingZoo AEC environment instance.
        model: A trained model instance to evaluate. The model class should
            contain a `predict` method as in Stable Baselines3.
        algorithm_name: The algorithm name (e.g., "maskable_ppo", "dqn"). It is
            used in the printed messages.
        num_games: The number of games to play for the evaluation.
        seed: The random seed for the environment. The seed is incremented
            for each game to ensure different initial conditions.
        deterministic: Whether to use deterministic actions when predicting
            with the model.
        needs_action_mask: Whether the algorithm requires an action mask
            (e.g., MaskablePPO) or not (e.g., DQN).
        **kwargs: Additional keyword arguments to pass to the model's predict
            method.
    """
    print(f"Starting evaluation with {algorithm_name}. Trained agent will play"
          f" as {env.possible_agents[1]}.")

    scores = {agent: 0 for agent in env.possible_agents}
    total_rewards = {agent: 0 for agent in env.possible_agents}
    round_rewards = []

    for i in range(num_games):
        env_seed = seed + i  # Different seed for each game
        env.reset(env_seed)

        for agent in env.agent_iter():
            obs, reward, termination, truncation, info = env.last()
            observation, action_mask = obs.values()

            if termination or truncation:
                if (env.rewards[env.possible_agents[0]] !=
                        env.rewards[env.possible_agents[1]]):
                    winner = max(env.rewards, key=env.rewards.get)
                    scores[winner] += env.rewards[winner]
                for a in env.possible_agents:
                    total_rewards[a] += env.rewards[a]
                round_rewards.append(env.rewards)
                break
            else:
                if agent == env.possible_agents[0]:
                    # Random agent
                    action = env.action_space(agent).sample(action_mask)
                else:
                    # Trained agent
                    action = predict_action(
                        model,
                        observation,
                        action_mask,
                        needs_action_mask=needs_action_mask,
                        deterministic=deterministic,
                        **kwargs
                    )

            env.step(action)

    env.close()

    winrate = 0 if sum(scores.values()) == 0 else (
            scores[env.possible_agents[1]] / sum(scores.values()))

    return round_rewards, total_rewards, winrate, scores


def predict_action(model, observation, action_mask, needs_action_mask=False,
                   deterministic=True, **kwargs):
    """
    Predict the next action using the model, considering the action mask if
    needed.

    The action mask is used only if the algorithm supports it
    (e.g. MaskablePPO). Otherwise, if the chosen action is not valid,
    a valid action is chosen at random.

    Args:
        model: A trained model instance to use for prediction. The model class
            should contain a `predict` method as in Stable Baselines3.
        observation: The current observation from the environment.
        action_mask: The action mask indicating valid actions.
        needs_action_mask: Whether the algorithm requires an action mask
            (e.g., MaskablePPO) or not (e.g., DQN).
        deterministic: Whether to use deterministic actions when predicting
            with the model.
        **kwargs: Additional keyword arguments to pass to the model's predict
            method.
    """
    if needs_action_mask:
        act = int(model.predict(
            observation,
            action_masks=action_mask,
            deterministic=deterministic,
            **kwargs
        )[0])
    else:
        # Non maskable algorithms (e.g. dqn)
        act = int(model.predict(
            observation,
            deterministic=deterministic,
            **kwargs
        )[0])

        # If the chosen action is not valid, choose a valid action at random
        if action_mask is not None:
            if not action_mask[act]:
                valid = np.flatnonzero(action_mask)

                act = int(np.random.choice(valid))
    return act
