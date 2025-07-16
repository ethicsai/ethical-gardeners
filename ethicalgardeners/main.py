import os

import hydra
from ethicalgardeners.gardenersenv import GardenersEnv

@hydra.main(version_base=None, config_path=os.getcwd())
def main(config):
    # Initialise the environment with the provided configuration
    env = GardenersEnv(config)
    env.reset(seed=42)

    # Main loop for the environment
    for i, agent in enumerate(env.agent_iter()):
        observations, rewards, termination, truncation, infos = env.last()

        if termination or truncation:
            break
        else:
            action = env.action_space(agent).sample()

        env.step(action)

    # Close the environment
    env.close()

if __name__ == "__main__":
    main()
