from copy import deepcopy
import hydra

from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy

# from stable_baselines3 import DQN

from stable_baselines3.common.vec_env import DummyVecEnv  # , SubprocVecEnv

from ethicalgardeners import algorithms, make_env
from ethicalgardeners.main import run_simulation, _find_config_path


@hydra.main(version_base=None, config_path=_find_config_path())
def main(config):
    algo = "maskable_ppo"  # "dqn" or "maskable_ppo"

    # ---- Training ----
    num_envs = 10
    total_timesteps = 0
    configs = [deepcopy(config) for _ in range(num_envs)]
    for i, cfg in enumerate(configs):
        cfg["random_seed"] = 42 + i  # a different seed for each env
        cfg["num_iterations"] = 2048
        total_timesteps += cfg["num_iterations"]

    # When num_envs > 1, multiple environments are created using the provided
    # configs and run in parallel using either SubprocVecEnv or DummyVecEnv.
    # When num_envs = 1, a single environment is created using the first config
    if num_envs > 1:
        env_fns = [algorithms.make_env_thunk(make_env, cfg) for cfg in configs]
        vec_cls = DummyVecEnv  # or SubprocVecEnv
        env = vec_cls(env_fns)
    else:
        env = algorithms.make_SB3_env(make_env, configs[0])

    # Create the model using the provided model function
    model = MaskablePPO(MaskableActorCriticPolicy, env, verbose=3)
    # or model = DQN("MlpPolicy", env, verbose=3)

    algorithms.train(model, algo, total_timesteps=total_timesteps)

    # ---- Evaluation ----
    env = make_env(config)

    policy_path = algorithms.get_latest_policy(algo)
    model = MaskablePPO.load(policy_path)
    # or model = DQN.load(policy_path)

    round_rewards, total_rewards, winrate, scores = algorithms.evaluate(
        env, model, algo,
        num_games=5, deterministic=True,
        needs_action_mask=True  # True for MaskablePPO, False for DQN
    )

    print("Rewards by round: ", round_rewards)
    print("Total rewards (incl. negative rewards): ", total_rewards)
    print("Winrate: ", winrate)
    print("Final scores: ", scores)

    # ---- Use the trained model as an agent in the environment ----
    env = make_env(config)

    agent_algorithms = [model for _ in range(2)]

    # Main loop for the environment
    run_simulation(
        env, agent_algorithms, deterministic=[True, True],
        needs_action_mask=[True, True]
    )


if __name__ == "__main__":
    main()
