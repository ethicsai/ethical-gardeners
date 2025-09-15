#!/bin/sh

# This script is meant to submit experiments to the SLURM queue.
# It uses Hydra to handle the configuration for each experiment,
# and the SubmitIt plugin to call SLURM (typically, `squeue`).

# It **MUST** be called from the project root, otherwise the
# config files cannot be found (because we hardcode the config dir).

# The configurations (e.g., hyperparameter search) are set in the
# `configs/exps` folder, and specified here in `--multirun exps=...`
# You must list the names (keys) of experiments you want to launch.
# TODO: maybe take the list of experiments as input with a default?

# FIXME: we may not need the `hydra/launcher=submit_slurm` line since the config was updated

python -m ethicalgardeners.main \
	--multirun exps=exp1,exp2,exp3,exp4,exp5,exp6,exp7,exp8,exp9,exp10,exp11,exp12 \
	hydra/launcher=submitit_slurm \
	--config-dir slurm/configs \
	--config-name config

# FIXME: add `-L sps` to slurm args
# FIXME: add the call to `source ~/ethicalgardeners/activate.sh` before running the Python code. Maybe in `setup`? https://github.com/facebookresearch/hydra/blob/b785290504577b06d7131d87f85cfe121004dce2/plugins/hydra_submitit_launcher/hydra_plugins/hydra_submitit_launcher/config.py#L75
# FIXME: how do we login to wandb?

