"""
Handles the execution of agent actions in the Ethical Gardeners simulation.
"""
from ethicalgardeners.action import Action


class ActionHandler:
    """
    Handles the execution of agent actions in the grid world environment.

    The ActionHandler mediates between agents and the world grid, ensuring that
    actions are only executed when valid. It manages movement validation,
    flower planting and harvesting, and simple waiting actions.
    """

    def __init__(self, grid_world):
        """
        Create the ActionHandler with a reference to the grid world.

        Args:
            grid_world (:py:class:`.WorldGrid`): The grid world environment
                where actions will be executed.
        """
        self.grid_world = grid_world

    def handle_action(self, agent, action, flower_type=None):
        """
        Process an agent's action and execute it in the grid world.

        This method delegates to specific handler methods based on the action
        type.

        Args:
            agent (:py:class:`.Agent`): The agent performing the action.
            action (:py:class:`.Action`): The action to perform (UP, DOWN,
                LEFT, RIGHT, PLANT, HARVEST, or WAIT).
            flower_type (int, optional): The type of flower to plant when the
                action is PLANT. Required only for PLANT actions.
        """
        if action in [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]:
            self.move_agent(agent, action)
        elif action == Action.PLANT:
            self.plant_flower(agent, flower_type)
        elif action == Action.HARVEST:
            self.harvest_flower(agent)
        elif action == Action.WAIT:
            self.wait(agent)

    def move_agent(self, agent, action):
        """
        Move an agent in the specified direction if the move is valid.

        Args:
            agent (:py:class:`.Agent`): The agent to move.
            action (:py:class:`.Action`): The direction to move (UP, DOWN,
                LEFT, RIGHT).
        """
        # Compute the new position based on the action
        new_position = agent.position
        if action == Action.UP:
            new_position = (agent.position[0] - 1, agent.position[1])
        elif action == Action.DOWN:
            new_position = (agent.position[0] + 1, agent.position[1])
        elif action == Action.LEFT:
            new_position = (agent.position[0], agent.position[1] - 1)
        elif action == Action.RIGHT:
            new_position = (agent.position[0], agent.position[1] + 1)

        if self.grid_world.valid_move(new_position):
            agent.move(action)

            self.grid_world.get_cell(agent.position).agent = None
            self.grid_world.get_cell(new_position).agent = agent

            agent.turns_without_income += 1

    def plant_flower(self, agent, flower_type):
        """
        Plant a flower of the specified type at the agent's current position.

        The agent must have available seeds of the specified flower type.

        Args:
            agent (:py:class:`.Agent`): The agent planting the flower.
            flower_type (int): The type of flower to plant.

        Raises:
            ValueError: If the agent does not have seeds of the specified type
                or if the current cell already contains a flower.
        """
        if (agent.can_plant(flower_type) and
                self.grid_world.get_cell(agent.position).can_plant_on()):
            agent.use_seed(flower_type)

            self.grid_world.place_flower(agent.position, flower_type)

            agent.turns_without_income += 1
        else:
            raise ValueError("Agent cannot plant this flower type.")

    def harvest_flower(self, agent):
        """
        Harvest a fully grown flower at the agent's current position.

        The flower must be fully grown to be harvested. Upon harvesting, the
        agent receives seeds and money based on the flower type.

        Args:
            agent (:py:class:`.Agent`): The agent harvesting the flower.

        Raises:
            ValueError: If there is no flower at the agent's position or if the
                flower is not fully grown.
        """
        flower = self.grid_world.get_cell(agent.position).flower
        if flower and flower.is_grown():
            self.grid_world.remove_flower(agent.position)

            if self.grid_world.num_seeds_returned is not None:
                if self.grid_world.num_seeds_returned == -3:
                    num_seeds_returned = (
                        self.grid_world.random_generator.randint(1, 5))
                else:
                    num_seeds_returned = self.grid_world.num_seeds_returned
                agent.add_seed(flower.flower_type, num_seeds_returned)

            agent.add_money(
                self.grid_world.flowers_data[flower.flower_type]['price'])
        else:
            raise ValueError(
                "No flower to harvest at this position or flower cannot be"
                " harvested.")

    def wait(self, agent):
        """
        Perform a wait action, which does not change the state of the world.

        This action can be used by agents when they do not want to perform
        any other action in the current time step.
        """
        agent.turns_without_income += 1
