# agent.py
import random
import math


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
    """A Goal-Based/Planning Agent that uses BFS, DFS, UCS, or A*
    to find optimal paths to food pellets before taking physical actions."""

    def __init__(self):
        self.plan = []  # Stores the sequence of actions to execute
        self.active_algo = 'AStar'  # Change to 'BFS', 'DFS', 'UCS', or 'AStar' to compare

    # ------------------------------------------------------------------ #
    #  Helper: get valid neighbouring states from a given position
    # ------------------------------------------------------------------ #
    def _get_neighbours(self, pos, grid_size, walls):
        """Return list of (action, new_position) pairs for valid moves."""
        x, y = pos
        width, height = grid_size
        neighbours = []

        # Each possible move and its resulting position
        moves = [
            ('Up',    (x, y + 1)),
            ('Down',  (x, y - 1)),
            ('Left',  (x - 1, y)),
            ('Right', (x + 1, y)),
        ]

        for action, (nx, ny) in moves:
            # Stay within grid boundaries and avoid walls
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                neighbours.append((action, (nx, ny)))

        return neighbours

    # ------------------------------------------------------------------ #
    #  Heuristic Functions for Informed Search
    # ------------------------------------------------------------------ #
    def manhattan_distance(self, pos, goal):
        """Calculate Manhattan distance: h(n) = |x1 - x2| + |y1 - y2|"""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        """Calculate Euclidean distance: h(n) = sqrt((x1-x2)^2 + (y1-y2)^2)"""
        return math.sqrt((pos[0] - goal[0]) ** 2 + (pos[1] - goal[1]) ** 2)

    # ------------------------------------------------------------------ #
    #  BFS — Breadth-First Search  (FIFO Queue)
    # ------------------------------------------------------------------ #
    def bfs_search(self, start, goal, grid_size, walls):
        """Find a path from start to goal using Breadth-First Search.
        Uses a FIFO queue (deque) so the shallowest nodes are expanded first."""
        from collections import deque

        frontier = deque()              # FIFO queue
        frontier.append((start, []))    # (current_position, path_of_actions)
        reached = {start}               # Graph search: track visited states

        while frontier:
            current_pos, path = frontier.popleft()  # FIFO — shallowest first

            # Goal test
            if current_pos == goal:
                return path

            # Expand neighbours
            for action, neighbour in self._get_neighbours(current_pos, grid_size, walls):
                if neighbour not in reached:
                    reached.add(neighbour)
                    frontier.append((neighbour, path + [action]))

        return []  # No path found

    # ------------------------------------------------------------------ #
    #  DFS — Depth-First Search  (LIFO Stack)
    # ------------------------------------------------------------------ #
    def dfs_search(self, start, goal, grid_size, walls):
        """Find a path from start to goal using Depth-First Search.
        Uses a LIFO stack (list.pop()) so the deepest nodes are expanded first."""
        frontier = []                   # LIFO stack
        frontier.append((start, []))    # (current_position, path_of_actions)
        reached = {start}               # Graph search: track visited states

        while frontier:
            current_pos, path = frontier.pop()  # LIFO — deepest first

            # Goal test
            if current_pos == goal:
                return path

            # Expand neighbours
            for action, neighbour in self._get_neighbours(current_pos, grid_size, walls):
                if neighbour not in reached:
                    reached.add(neighbour)
                    frontier.append((neighbour, path + [action]))

        return []  # No path found

    # ------------------------------------------------------------------ #
    #  UCS — Uniform-Cost Search  (Priority Queue ordered by g(n))
    # ------------------------------------------------------------------ #
    def ucs_search(self, start, goal, grid_size, walls):
        """Find a path from start to goal using Uniform-Cost Search.
        Uses a min-heap priority queue ordered by cumulative path cost g(n).
        Each move has a uniform cost of 1 in this grid."""
        import heapq

        frontier = []                          # Priority queue (min-heap)
        heapq.heappush(frontier, (0, start, []))  # (cost, position, path)
        reached = {}                           # Maps state -> best cost seen

        while frontier:
            cost, current_pos, path = heapq.heappop(frontier)

            # Goal test (checked when node is popped — UCS guarantees optimality)
            if current_pos == goal:
                return path

            # Skip if we already found a cheaper path to this state
            if current_pos in reached and reached[current_pos] <= cost:
                continue
            reached[current_pos] = cost

            # Expand neighbours (each move costs 1)
            for action, neighbour in self._get_neighbours(current_pos, grid_size, walls):
                new_cost = cost + 1
                if neighbour not in reached or reached[neighbour] > new_cost:
                    heapq.heappush(frontier, (new_cost, neighbour, path + [action]))

        return []  # No path found

    # ------------------------------------------------------------------ #
    #  A* Search  (Priority Queue ordered by f(n) = g(n) + h(n))
    # ------------------------------------------------------------------ #
    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        """Find a path from start to goal using A* Search.
        Uses a min-heap priority queue ordered by f(n) = g(n) + h(n).
        Supports 'manhattan' and 'euclidean' heuristic types."""
        import heapq

        # Select the heuristic function
        if heuristic_type == 'euclidean':
            heuristic = self.euclidean_distance
        else:
            heuristic = self.manhattan_distance

        frontier = []                           # Priority queue (min-heap)
        reached_states = set()                  # Track visited states

        # Initial state: f(n) = g(n) + h(n), g(n) = 0
        h_start = heuristic(start_pos, goal_pos)
        f_start = 0 + h_start
        heapq.heappush(frontier, (f_start, 0, start_pos, []))  # (f_cost, g_cost, current_pos, path_taken)

        while frontier:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)

            # Goal test
            if current_pos == goal_pos:
                return path_taken

            # Skip if already visited
            if current_pos in reached_states:
                continue
            reached_states.add(current_pos)

            # Expand neighbours
            for action, neighbour in self._get_neighbours(current_pos, grid_size, walls):
                if neighbour not in reached_states:
                    g_new = g_cost + 1
                    h_new = heuristic(neighbour, goal_pos)
                    f_new = g_new + h_new
                    heapq.heappush(frontier, (f_new, g_new, neighbour, path_taken + [action]))

        return []  # No path found

    # ------------------------------------------------------------------ #
    #  Main agent loop
    # ------------------------------------------------------------------ #
    def sense_and_act(self, percept: dict) -> str:
        """If the current plan is empty, pick the closest food and compute
        a new plan using the active search algorithm. Then pop and return
        the next action from the plan."""

        # If no plan exists, compute one
        if not self.plan:
            agent_pos = percept['agent_pos']
            grid_size = percept['grid_size']
            walls = set(percept['walls'])
            all_food = percept.get('remaining_food', percept.get('all_food', []))

            if not all_food:
                # No food left — move randomly
                return random.choice(['Up', 'Down', 'Left', 'Right'])

            # Pick the closest food pellet (Manhattan distance heuristic for selection)
            closest_food = min(
                all_food,
                key=lambda f: abs(f[0] - agent_pos[0]) + abs(f[1] - agent_pos[1])
            )

            # Run the selected search algorithm
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(agent_pos, closest_food, grid_size, walls)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(agent_pos, closest_food, grid_size, walls)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(agent_pos, closest_food, grid_size, walls)
            elif self.active_algo == 'AStar':
                self.plan = self.astar_search(agent_pos, closest_food, walls, grid_size)

            # Fallback if search finds no path
            if not self.plan:
                return random.choice(['Up', 'Down', 'Left', 'Right'])

        return self.plan.pop(0)


if __name__ == "__main__":
    # Testing Checkpoint
    agent = SearchAgent()
    start = (0, 0)
    goal = (3, 4)
    manhattan = agent.manhattan_distance(start, goal)
    euclidean = agent.euclidean_distance(start, goal)
    print(f"Manhattan distance between {start} and {goal}: {manhattan}")
    print(f"Euclidean distance between {start} and {goal}: {euclidean}")