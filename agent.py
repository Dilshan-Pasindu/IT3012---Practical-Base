# agent.py
import random


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SimpleReflexAgent:
    """A Simple Reflex Agent that uses only IF-THEN Condition-Action rules.
    It has no memory or internal state — it reacts purely to the current percept."""

    def sense_and_act(self, percept: dict) -> str:
        # Condition-Action Rule 1: IF food_here THEN collect (move to pick up)
        if percept.get('food_here'):
            return 'Up'

        # Condition-Action Rule 2: IF wall_ahead THEN turn left
        if percept.get('wall_ahead'):
            return 'Left'

        # Condition-Action Rule 3: ELSE move forward
        return 'Up'


class ModelBasedAgent:
    """A Model-Based Agent that maintains an internal memory state
    to remember past actions and avoid getting stuck in loops."""

    def __init__(self):
        # Internal state: memory of sweep direction and exploration state
        self.last_action = None
        self.action_history = []
        self.horizontal_direction = 'Right'  # Current sweep direction (memory)
        self.state = 'sweep'  # Exploration state: 'sweep' or 'step_up' (memory)

    def sense_and_act(self, percept: dict) -> str:
        directions = ['Up', 'Down', 'Left', 'Right']

        # Transition Model: Record the last action into history
        if self.last_action is not None:
            self.action_history.append(self.last_action)

        # Sensor Model: Process current percept and query internal memory state

        if percept.get('wall_ahead'):
            if self.state == 'sweep':
                # Wall/boundary hit while sweeping → step up to next row (memory update)
                self.state = 'step_up'
                action = 'Up'
            elif self.state == 'step_up':
                # Wall while stepping up (top boundary) → reverse sweep using memory
                self.horizontal_direction = 'Left' if self.horizontal_direction == 'Right' else 'Right'
                self.state = 'sweep'
                action = self.horizontal_direction
            else:
                # Fallback: use memory to choose a different direction
                available = [d for d in directions if d != self.last_action]
                action = random.choice(available)
        else:
            if self.state == 'step_up':
                # Successfully stepped up → reverse direction from memory and sweep
                self.horizontal_direction = 'Left' if self.horizontal_direction == 'Right' else 'Right'
                self.state = 'sweep'
                action = self.horizontal_direction
            else:
                # Continue sweeping in current direction from memory
                action = self.horizontal_direction

        self.last_action = action
        return action


class SearchAgent:
    """Placeholder for Practical 3: Problem-Solving Agent with BFS search."""
    pass