# grid_game.py
import random


class GridHuntGame:
    """A small Pacman-style grid environment (4x4) where an agent collects food."""

    def __init__(self, width=4, height=4):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)

        # Place a few random food pellets and obstacles (walls)
        self.food_positions = {(1, 2), (2, 3), (3, 0), (2, 1)}
        self.walls = {(1, 1), (2, 2)}

        self.toxic_traps = set()
        num_traps = max(1, min(3, self.width * self.height // 8))
        while len(self.toxic_traps) < num_traps:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            pos_tuple = (tx, ty)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls and pos_tuple not in self.food_positions:
                self.toxic_traps.add(pos_tuple)

        self.score = 0
        self.steps = 0

    def get_percept(self, agent) -> dict:
        return {
            'agent_pos': list(self.agent_pos),
            'smells_food': tuple(self.agent_pos) in self.food_positions,
            'smells_toxin': tuple(self.agent_pos) in self.toxic_traps,
            'hit_wall': tuple(self.agent_pos) in self.walls,
            'score': self.score,
            'remaining_food': len(self.food_positions)
        }

    def execute_action(self, agent, action: str):
        self.steps += 1
        new_pos = list(self.agent_pos)

        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        # Check collision with walls
        if tuple(new_pos) in self.walls:
            self.score -= 5  # Penalty for hitting a wall
        else:
            self.agent_pos = new_pos

        # Check if eating food
        tuple_pos = tuple(self.agent_pos)
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20  # Reward for eating food pellet

        if tuple_pos in self.toxic_traps:
            self.score -= 15  # Penalty for stepping on a toxic trap

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 20