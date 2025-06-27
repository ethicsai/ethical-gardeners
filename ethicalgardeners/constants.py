POLLUTION_INCREMENT = 1
"""
Amount by which pollution increases each step on empty ground cells.

This constant determines how quickly ground cells become polluted when no
flowers are present.
"""

FLOWERS_DATA = {
    0: {"price": 10, "pollution_reduction": [0, 0, 0, 0, 5]},
    1: {"price": 5, "pollution_reduction": [0, 0, 1, 3]},
    2: {"price": 2, "pollution_reduction": [1]}
}
"""
Configuration data for different flower types.

Dictionary mapping flower type IDs to their properties:
- price: The monetary value when harvested
- pollution_reduction: List of pollution reduction values for each growth stage
"""
