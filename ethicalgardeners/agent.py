"""
Represents a gardener agent in the Ethical Gardeners simulation.
"""


class Agent:
    """
    Represents a gardener agent in the environment.

    Agents can move around the grid, plant and harvest flowers, manage seeds,
    and accumulate money from harvesting flowers.

    Attributes:
        position (tuple): The (x, y) coordinates of the agent in the grid.
        money (float): The agent's current monetary wealth.
        seeds (dict): Dictionary mapping flower types to the number of seeds
            the agent has.
        flowers_planted (dict): Counter of flowers this agent has planted on
            the grid by type.
        flowers_harvested (dict): Counter of flowers this agent has harvested
            by type. (Note that, because an agent can harvest flowers planted
            by another agent, this counter can be very different from the
            ``flowers_planted`` counter.)
        turns_without_income (int): Number of turns the agent has not earned
            money.
        action_mask (list): Action mask indicating valid actions for the agent.
    """
    def __init__(self, position, money=0.0, seeds: dict = None):
        """
        Create a new agent.

        Args:
            position (tuple): The (x, y) coordinates where the agent starts.
            money (float, optional): Initial amount of money the agent has.
                Defaults to 0.
            seeds (dict, optional): Dictionary mapping flower types to initial
                seed counts. Defaults to 10 for each type.
        """
        self.position = position
        self.money = money
        if seeds is None:
            self.seeds = {0: 10, 1: 10, 2: 10}
        else:
            self.seeds = seeds
        self.flowers_planted = {i: 0 for i in self.seeds}
        self.flowers_harvested = {i: 0 for i in self.seeds}
        self.turns_without_income = 0
        self.action_mask = None  # Action mask to indicate valid actions

    def move(self, new_position):
        """
        Move the agent in the specified direction.

        Updates the agent's position based on the direction action.

        Args:
            new_position (tuple): The (x, y) coordinates of the agent in the
                grid.
        """
        self.position = new_position

    def can_plant(self, flower_type: int):
        """
        Check if the agent has seeds available to plant a specific flower type.

        Args:
            flower_type (int): The type of flower to check seed availability
                for.

        Returns:
            bool: True if the agent has at least one seed of the specified type
            or if seed count is -1 because this represents infinite seeds.
        """

        if self.seeds[flower_type] == -1:
            # If the seed count is -1, it represents infinite seeds
            return True

        return self.seeds[flower_type] > 0

    def use_seed(self, flower_type: int):
        """
        Use a seed to plant a flower of the specified type.

        Decrements the seed count for the flower type. If seed count is -1,
        this represents infinite seeds so the count is not decremented.

        Args:
            flower_type (int): The type of flower to plant.

        Returns:
            bool: True if the seed was successfully used, False if no seeds
            available.
        """
        if self.can_plant(flower_type):
            if self.seeds[flower_type] != -1:
                # Only decrement if the seed count is not infinite
                self.seeds[flower_type] -= 1
            return True

        return False

    def add_money(self, amount):
        """
        Add money to the agent's wealth.

        Args:
            amount (float): The amount of money to add.
        """
        self.money += amount

    def add_seed(self, flower_type: int, num_seeds):
        """
        Add seeds of a specific flower type to the agent's inventory.

        Args:
            flower_type (int): The type of flower seeds to add.
            num_seeds (int): The number of seeds to add.
        """
        if self.seeds[flower_type] == -1:
            # If the seed count is -1, it represents infinite seeds
            return
        self.seeds[flower_type] += num_seeds
