from ethicalgardeners.action import Action


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
        flowers_planted (dict): Counter of flowers planted by type.
        flowers_harvested (dict): Counter of flowers harvested by type.
    """
    def __init__(self, position, money=0.0, seeds=None):
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

    def move(self, direction):
        """
        Move the agent in the specified direction.

        Updates the agent's position based on the direction action.

        Args:
            direction (:py:class:`.Action`): The direction to move (UP, DOWN,
                LEFT, RIGHT).
        """
        if direction == Action.UP:
            self.position = (self.position[0] - 1, self.position[1])
        elif direction == Action.DOWN:
            self.position = (self.position[0] + 1, self.position[1])
        elif direction == Action.LEFT:
            self.position = (self.position[0], self.position[1] - 1)
        elif direction == Action.RIGHT:
            self.position = (self.position[0], self.position[1] + 1)

    def can_plant(self, flower_type):
        """
        Check if the agent has seeds available to plant a specific flower type.

        Args:
            flower_type (int): The type of flower to check seed availability for.

        Returns:
            bool: True if the agent has at least one seed of the specified type
                of if seed count is -1 because this represenys infinite seeds.
        """

        if self.seeds[flower_type] == -1:
            # If the seed count is -1, it represents infinite seeds
            return True

        return self.seeds[flower_type] > 0

    def use_seed(self, flower_type):
        """
        Use a seed to plant a flower of the specified type.

        Decrements the seed count for the flower type and increments the
        flowers_planted counter. If seed count is -1, this represents infinite
        seeds and the count is not decremented.

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

            self.flowers_planted[flower_type] += 1
            return True

        return False

    def add_money(self, amount):
        """
        Add money to the agent's wealth.

        Args:
            amount (float): The amount of money to add.
        """
        self.money += amount

    def add_seed(self, flower_type, num_seeds):
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
