"""Constant values used throughout the Ethical Gardeners simulation.
"""
MAX_PENALTY_TURNS = 10
"""
Maximum number of turns used to normalize the well-being penalty.

This constant defines the maximum number of turns without income after which
an agent receives the maximum well-being penalty (-1.0). It is used in the
`computeWellbeingReward` function to normalize the penalty given to agents
who haven't earned money, using the formula:
`-min(agent.turns_without_income / MAX_PENALTY_TURNS, 1.0)`

The higher this value, the more lenient the system is towards agents that go
for longer periods without harvesting and selling flowers.
"""

FEATURES_PER_CELL = 7
"""
Number of features per cell in the grid.

This constant defines the number of features that each cell in the grid
contains. It is used in the observation strategies to determine the shape of
the observation space. Each cell's features include:

* Cell type (normalized)
* Pollution level (normalized)
* Flower presence and type (normalized)
* Flower growth stage (normalized)
* Agent presence (normalized)
* Agent X position (normalized)
* Agent Y position (normalized)
"""

agent_palette = [
    (255, 40, 40),    # Bright red
    (255, 96, 55),    # Coral
    (255, 127, 80),   # Coral red
    (255, 69, 0),     # Red-orange
    (255, 99, 71),    # Tomato
    (255, 140, 0),    # Dark orange
    (255, 165, 0),    # Orange
    (255, 191, 0),    # Amber
    (255, 215, 0),    # Gold
    (255, 220, 80),   # Golden yellow
    (255, 230, 120),  # Light gold
    (255, 193, 193),  # Light salmon
    (255, 182, 193),  # Light pink
    (255, 105, 180),  # Hot pink
    (255, 20, 147),   # Deep pink
    (255, 0, 255),    # Magenta
    (238, 130, 238),  # Violet
    (221, 160, 221),  # Plum
    (218, 112, 214),  # Orchid
    (199, 21, 133),   # Medium violet-red
    (186, 85, 211),   # Medium orchid
    (148, 0, 211),    # Dark violet
    (138, 43, 226),   # Blue violet
    (123, 104, 238),  # Medium slate blue
    (106, 90, 205),   # Slate blue
    (72, 61, 139),    # Dark slate blue
    (153, 50, 204),   # Dark orchid
    (139, 0, 139),    # Dark magenta
    (128, 0, 128),    # Purple
    (102, 0, 102),    # Dark purple
    (75, 0, 130),     # Indigo
    (205, 92, 92),    # Indian red
    (220, 20, 60),    # Crimson
    (178, 34, 34),    # Firebrick
    (139, 0, 0),      # Dark red
    (128, 0, 0),      # Maroon
    (210, 105, 30),   # Chocolate
    (160, 82, 45),    # Sienna
    (230, 230, 250),  # Lavender
    (216, 191, 216),  # Thistle
]
"""
This palette provides a range of 40 colors for agents, from reddish to purple
hues, ensuring a visually distinct representation of agents in the simulation.
Used in the :py:meth:`.GraphicalRenderer._generate_colors` method.
"""

flower_palette = [
    (173, 255, 47),   # Green-yellow
    (154, 205, 50),   # Yellow-green
    (0, 255, 0),      # Lime
    (50, 205, 50),    # Lime green
    (0, 250, 154),    # Medium spring green
    (0, 255, 127),    # Spring green
    (60, 179, 113),   # Medium sea green
    (46, 139, 87),    # Sea green
    (34, 139, 34),    # Forest green
    (0, 128, 0),      # Green
    (0, 100, 0),      # Dark green
    (85, 107, 47),    # Dark olive green
    (107, 142, 35),   # Olive drab
    (128, 128, 0),    # Olive
    (189, 183, 107),  # Dark khaki
    (240, 230, 140),  # Khaki
    (238, 232, 170),  # Pale goldenrod
    (250, 250, 210),  # Light goldenrod yellow
    (255, 255, 224),  # Light yellow
    (255, 255, 0),    # Yellow
    (255, 215, 0),    # Gold
    (184, 134, 11),   # Dark goldenrod
    (218, 165, 32),   # Goldenrod
    (238, 221, 130),  # Light goldenrod
    (102, 205, 170),  # Medium aquamarine
    (127, 255, 212),  # Aquamarine
    (152, 251, 152),  # Pale green
    (144, 238, 144),  # Light green
    (143, 188, 143),  # Dark sea green
    (32, 178, 170)    # Light sea green
]
"""
This palette provides a range of 30 colors for flowers, from greenish to
yellowish hues, ensuring a visually distinct representation of flowers in the
simulation. Used in the :py:meth:`.GraphicalRenderer._generate_colors` method
"""
