"""
The MetricsCollector module provides metrics tracking and exporting
capabilities for the Ethical Gardeners simulation environment.

This module enables monitoring of simulation runs by:

1. Collecting various metrics during simulation execution
2. Exporting metrics to local files like CSV files for offline analysis
3. Sending metrics to monitoring services like Weights and Biases (WandB)

The metrics tracked include:

* Current simulation step
* Flower planted and harvested statistics (overall and per-agent)
* Pollution levels across the environment
* Agent rewards and accumulated rewards
* Currently selected agent

The module is designed to be configurable, allowing users to enable or disable
metrics export and sending based on their research requirements.
"""


class MetricsCollector:
    """
    Collects, tracks and exports metrics from the Ethical Gardeners simulation.

    This class is responsible for gathering various performance metrics during
    simulation runs, storing them internally, and optionally exporting them to
    files or sending them to external monitoring services like WandB.

    Metrics are updated at each step of the simulation and can be reset when
    the environment is reset.

    Attributes:
        out_dir_path (str): Directory path where metrics will be exported when
            export_on is True.
        export_on (bool): Flag indicating whether metrics should be exported to
            local files like CSV files.
        send_on (bool): Flag indicating whether metrics should be sent to
            external services like WandB.
        metrics (dict): Dictionary containing all collected metrics, including:

            * step (int): Current step in the simulation.
            * episode (int): Current episode number.
            * total_planted_flowers (int): Total number of flowers planted by
              all agents.
            * num_planted_flowers_per_agent (dict): Flowers planted per agent.
            * total_harvested_flowers (int): Total number of flowers harvested.
            * num_harvested_flowers_per_agent (dict): Flowers harvested per
              agent.
            * avg_pollution_percent (float): Average pollution percentage
              across all cells.
            * num_cells_pollution_above_90 (int): Number of cells with
              pollution > 90%.
            * num_cells_pollution_above_75 (int): Number of cells with
              pollution > 75%.
            * num_cells_pollution_above_50 (int): Number of cells with
              pollution > 50%.
            * num_cells_pollution_above_25 (int): Number of cells with
              pollution > 25%.
            * rewards (dict): Current rewards for each agent.
            * accumulated_rewards (dict): Cumulative rewards for each agent.
            * agent_selection (str): Currently selected agent.
        run (wandb.run): An WandB run instance for logging metrics. Can be
            provided externally or created internally if send_on is True.
        _run_id (int): Unique identifier for the run, used for file naming
            during export.
    """

    def __init__(self, out_dir_path, export_on, send_on, wandb_run=None,
                 **wandb_params):
        """
        Create the metrics collector.

        Args:
            out_dir_path (str): Directory path where metrics will be exported
                when export_on is True.
            export_on (bool): Flag indicating whether metrics should be
                exported to local files like CSV files.
            send_on (bool): Flag indicating whether metrics should be sent to
                external services like WandB.
            wandb_run (wandb.run, optional): An existing WandB run instance to
                use for logging metrics. If None, a new run will be created if
                send_on is True.
            **wandb_params: Additional parameters to pass to wandb.init() if
                a new run is created. This can include project name, entity,
                config, etc.
        """
        self.out_dir_path = out_dir_path
        self.export_on = export_on
        self.send_on = send_on
        self.metrics = {
            "step": 0,  # Current step in the simulation
            "episode": 1,  # Current episode number
            "total_planted_flowers": 0,
            "num_planted_flowers_per_agent": {},
            "total_harvested_flowers": 0,
            "num_harvested_flowers_per_agent": {},
            "avg_pollution_percent": 0.0,
            "num_cells_pollution_above_90": 0,
            "num_cells_pollution_above_75": 0,
            "num_cells_pollution_above_50": 0,
            "num_cells_pollution_above_25": 0,
            "rewards": {},
            "accumulated_rewards": {},
            "agent_selection": None,  # Currently selected agent
        }
        self._run_id = None  # Unique identifier for the run

        if export_on or send_on:
            import time

            self._run_id = int(time.time())

        self.run = wandb_run
        # Initialize WandB if not already done
        if self.send_on:
            try:
                import wandb
            except ImportError:
                raise ImportError(
                    "Error while importing wandb module. "
                    "WandB is required to use send_metrics. "
                    "Please install WandB with `pip install wandb` "
                    "or `pip install ethicalgardeners[metrics]`"
                )

            if not self.run:
                if wandb_params is None:
                    wandb_params = {}
                project = wandb_params.pop("project", "ethical-gardeners")
                name = wandb_params.pop("name", f"run_{self._run_id}")
                reinit = wandb_params.pop("reinit", "create_new")
                self.run = wandb.init(project=project,
                                      name=name,
                                      reinit=reinit,
                                      **wandb_params)

    def update_metrics(self, grid_world, rewards, agent_selection: str):
        """
        Update all tracked metrics based on the current state of the
        simulation.

        This method computes and updates various metrics including flower
        planting/harvesting statistics, pollution levels, rewards. It should be
        called after each step of the simulation.

        Args:
            grid_world (:py:class:`.GridWorld`): The current state of the world
                grid.
            rewards (dict): Dictionary of rewards for each agent.
            agent_selection (str): Currently selected agent.
        """
        self.metrics["step"] += 1
        self.metrics["num_planted_flowers_per_agent"] = {
            i: sum(grid_world.agents[i].flowers_planted.values()) for i in
            range(len(grid_world.agents))
        }
        self.metrics["num_harvested_flowers_per_agent"] = {
            i: sum(grid_world.agents[i].flowers_harvested.values()) for i in
            range(len(grid_world.agents))
        }
        self.metrics["total_planted_flowers"] = sum(
            self.metrics["num_planted_flowers_per_agent"].values()
        )

        self.metrics["total_harvested_flowers"] = sum(
            self.metrics["num_harvested_flowers_per_agent"].values()
        )

        self.metrics["avg_pollution_percent"] = 0
        self.metrics["num_cells_pollution_above_90"] = 0
        self.metrics["num_cells_pollution_above_75"] = 0
        self.metrics["num_cells_pollution_above_50"] = 0
        self.metrics["num_cells_pollution_above_25"] = 0
        max_pollution = grid_world.max_pollution
        num_cells = 0
        for row in grid_world.grid:
            for cell in row:
                if cell.pollution is not None:
                    self.metrics["avg_pollution_percent"] += cell.pollution
                    num_cells += 1
                    if (cell.pollution * 100 / max_pollution) > 25:
                        self.metrics["num_cells_pollution_above_25"] += 1
                    if (cell.pollution * 100 / max_pollution) > 50:
                        self.metrics["num_cells_pollution_above_50"] += 1
                    if (cell.pollution * 100 / max_pollution) > 75:
                        self.metrics["num_cells_pollution_above_75"] += 1
                    if (cell.pollution*100/max_pollution) > 90:
                        self.metrics["num_cells_pollution_above_90"] += 1

        if len(grid_world.grid) > 0:
            self.metrics["avg_pollution_percent"] /= num_cells

        self.metrics["rewards"] = rewards
        for agent, reward in rewards.items():
            if agent in self.metrics["accumulated_rewards"]:
                self.metrics["accumulated_rewards"][agent] += reward
            else:
                self.metrics["accumulated_rewards"][agent] = reward
        self.metrics["agent_selection"] = agent_selection

    def finish_episode(self):
        """
        Finish the current episode.

        This method finishes the current WandB run and creates a new run_id. It
        should be called at the end of a simulation run to properly close the
        WandB session and ensure all metrics are saved.
        """
        self.metrics["episode"] += 1

    def close(self):
        """
        Close the metrics collector.

        This method finishes the current WandB run if send_on is True. It
        should be called when the metrics collector is no longer needed to
        ensure all resources are properly released.
        """
        if self.send_on:
            if self.run:
                self.run.finish()

    def reset_metrics(self):
        """
        Reset all metrics to their initial values.

        This method should be called when the environment is reset to ensure
        metrics are tracked correctly for each new simulation run.
        """
        self.metrics = {
            "step": 0,
            "episode": self.metrics["episode"],
            "total_planted_flowers": 0,
            "num_planted_flowers_per_agent": {},
            "total_harvested_flowers": 0,
            "num_harvested_flowers_per_agent": {},
            "avg_pollution_percent": 0.0,
            "num_cells_pollution_above_90": 0,
            "num_cells_pollution_above_75": 0,
            "num_cells_pollution_above_50": 0,
            "num_cells_pollution_above_25": 0,
            "rewards": {},
            "accumulated_rewards": {},
            "agent_selection": None,
        }

    def export_metrics(self):
        """
        Export collected metrics to a local file.

        This method exports the current metrics to a CSV file in the specified
        output directory if export_on is True. A new file is created for each
        run of the program, and metrics are appended to this file at each call.
        """
        if self.export_on:
            import os
            try:
                import csv
            except ImportError:
                raise ImportError(
                    "Error while importing csv module. "
                )

            # Create output directory if it doesn't exist
            if not os.path.exists(self.out_dir_path):
                os.makedirs(self.out_dir_path)

            # Generate filename with run_id
            filename = os.path.join(self.out_dir_path,
                                    "simulation_metrics.csv")

            # Prepare row with metrics
            metrics_row = self._prepare_metrics()

            # Check if file exists to determine if we need to write headers
            file_exists = os.path.isfile(filename)

            # Write or append to CSV
            with open(filename, 'a' if file_exists else 'w',
                      newline='') as csvfile:
                writer = csv.DictWriter(csvfile,
                                        fieldnames=list(metrics_row.keys()))

                if not file_exists:
                    writer.writeheader()

                writer.writerow(metrics_row)

    def send_metrics(self):
        """
        Send collected metrics to Weights and Biases (WandB).

        This method sends the current metrics to WandB for visualization and
        experiment tracking if send_on is True. It automatically handles WandB
        initialization if needed and logs all relevant metrics from the current
        simulation state.
        """
        if self.send_on:
            # Prepare metrics dictionary for wandb
            metrics_to_log = self._prepare_metrics()

            # Log metrics to wandb
            self.run.log(metrics_to_log)

    def _prepare_metrics(self):
        """
        Prepare a formatted dictionary of metrics for export or sending.

        Returns:
            dict: Dictionary containing all metrics in a format ready for
            export/logging
        """
        metrics_dict = {
            'step': self.metrics["step"],
            'episode': self.metrics['episode'],
            'total_planted_flowers': self.metrics['total_planted_flowers'],
        }

        # Add per-agent metrics
        for agent, count in (
                self.metrics['num_planted_flowers_per_agent'].items()):
            metrics_dict[f'planted_flowers_agent_{agent}'] = count

        metrics_dict['total_harvested_flowers'] = self.metrics[
            'total_harvested_flowers']

        for agent, count in (
                self.metrics['num_harvested_flowers_per_agent'].items()):
            metrics_dict[f'harvested_flowers_agent_{agent}'] = count

        metrics_dict.update({
            'avg_pollution_percent': self.metrics['avg_pollution_percent'],
            'num_cells_pollution_above_90': self.metrics[
                'num_cells_pollution_above_90'],
            'num_cells_pollution_above_75': self.metrics[
                'num_cells_pollution_above_75'],
            'num_cells_pollution_above_50': self.metrics[
                'num_cells_pollution_above_50'],
            'num_cells_pollution_above_25': self.metrics[
                'num_cells_pollution_above_25'],
            'agent_selection': self.metrics['agent_selection']
        })

        for agent, reward in self.metrics['rewards'].items():
            metrics_dict[f'reward_{agent}'] = reward

        for agent, acc_reward in self.metrics['accumulated_rewards'].items():
            metrics_dict[f'accumulated_reward_{agent}'] = acc_reward

        return metrics_dict
