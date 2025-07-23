# Hydra Configuration for Ethical Gardeners

This document explains how to use and customize the Hydra configuration system for the Ethical Gardeners simulation environment.

## Overview

The Ethical Gardeners project uses [Hydra](https://hydra.cc/) for configuration management. Hydra allows you to modularly combine different configuration components to create customized simulation setups without changing the code.

## Configuration Structure

The configuration is organized into the following groups:

```
configs/
├── config.yaml                # Main configuration file with defaults
├── grid/                      # Grid initialization configurations
├── observation/               # Observation strategy configurations
├── metrics/                   # Metrics collection configurations
└── renderer/                  # Visualization configurations
```

## Configuration Groups

### Main Configuration (`config.yaml`)

The main configuration file defines defaults for all configuration groups and general settings like random seed and simulation length.

### Grid Configurations

Controls how the environment grid is initialized:

- **`random.yaml`**: Creates a randomly generated grid with configurable dimensions, obstacle density, and number of agents.
- **`from_code.yaml`**: Creates a grid with hardcoded cell positions, obstacles, agents, and starting resources.
- **`from_file.yaml`**: Loads a grid configuration from an external text file.

### Observation Configurations

Determines how agents perceive the environment:

- **`partial.yaml`**: Agents can only observe a limited area around them (configurable vision range).
- **`total.yaml`**: Agents have complete visibility of the entire grid.

### Metrics Configurations

Controls how simulation metrics are collected and exported:

- **`none.yaml`**: Disables metrics collection.
- **`export.yaml`**: Exports metrics to CSV files but doesn't send to external services.
- **`send.yaml`**: Sends metrics to external monitoring services (like WandB) but doesn't export to CSV.
- **`full.yaml`**: Exports metrics to CSV files and sends to external monitoring services (like WandB).

### Renderer Configurations

Controls how the simulation is visualized:

- **`none.yaml`**: No visualization.
- **`console.yaml`**: Text-based visualization in the terminal with customizable characters. Appends a GraphicalRenderer to the list of renderers to generate a post-analysis video without displaying it.
- **`graphical.yaml`**: Graphical visualization with customizable cell size and colors. Saves the post-analysis video to the out_dir_path directory.
- **`full.yaml`**: Both console and graphical visualization simultaneously. Saves the post-analysis video to the out_dir_path directory.

## Using Configurations

### Modifying Default Configurations

You can change the default configuration by editing the `defaults` section in `config.yaml`. For example, to change the default grid initialization method from random to from_code:

```yaml
defaults:
  - grid: from_code           # Changed from random
  - observation: partial
  - metrics: export
  - renderer: graphical
  - _self_
```

### Command Line Overrides

You can override configurations when running the simulation with command line arguments:

```bash
python -m ethicalgardeners.main grid=from_file observation=total metrics=full
```

### Common Configuration Combinations

Here are some useful configuration combinations:

- **Training setup**: `grid=random metrics=full renderer=none`
- **Visualization setup**: `grid=from_code renderer=graphical`
- **Debug setup**: `grid=from_code renderer=console`
- **Analysis setup**: `grid=from_file metrics=export renderer=none`

### Advanced Configuration

For more complex configurations, you can override specific parameters:

```bash
python -m ethicalgardeners.main \
  grid=from_code \
  grid.config.width=20 \
  grid.config.height=20 \
  observation=partial \
  observation.range=2 \
  renderer=graphical \
  renderer.graphical.cell_size=30 \
  num_iterations=5000
```

## Custom Configurations

You can create your own configuration files by adding new YAML files to the appropriate directories (e.g., `configs/grid/my_custom_grid.yaml`). These can then be used by specifying them in the command line or in the defaults section of `config.yaml`.

## Further Documentation

For more information on Hydra configuration, visit the [Hydra documentation](https://hydra.cc/docs/intro/).