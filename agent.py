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
        # Internal state: memory of past actions taken
        self.last_action = None
        self.action_history = []

    def sense_and_act(self, percept: dict) -> str:
        actions = ['Up', 'Down', 'Left', 'Right']

        # Transition Model: Record the last action into history
        if self.last_action is not None:
            self.action_history.append(self.last_action)

        # Sensor Model: Process current percept and query memory

        # Rule 1: IF food_here THEN collect
        if percept.get('food_here'):
            action = 'Up'
            self.last_action = action
            return action

        # Rule 2: IF wall_ahead THEN check memory to choose a different direction
        if percept.get('wall_ahead'):
            # Query memory: if last action was already a turn, try a different one
            if self.last_action == 'Left':
                action = 'Right'
            elif self.last_action == 'Right':
                action = 'Down'
            elif self.last_action == 'Down':
                action = 'Up'
            else:
                action = 'Left'

            self.last_action = action
            return action

        # Rule 3: ELSE move forward, but check memory for repetition
        # Detect if the agent is repeating the same action (loop detection)
        if len(self.action_history) >= 3 and len(set(self.action_history[-3:])) == 1:
            # Agent is stuck repeating — choose a different direction from memory
            available = [a for a in actions if a != self.last_action]
            action = random.choice(available)
        else:
            action = 'Up'

        self.last_action = action
        return action


class SearchAgent:
    """Placeholder for Practical 3: Problem-Solving Agent with BFS search."""
    pass