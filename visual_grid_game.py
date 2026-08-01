# visual_grid_game.py — IT3012 Lab 02
# Demonstrates: Partial Observability, Simple Reflex Agent, Model-Based Agent
import random
import tkinter as tk
from tkinter import ttk


# ---------------------------------------------------------------------------
# Direction helpers
# ---------------------------------------------------------------------------

DIRECTIONS = ['North', 'East', 'South', 'West']

# (dx, dy) for each cardinal direction (y increases upward)
DIR_DELTA = {
    'North': (0,  1),
    'East':  (1,  0),
    'South': (0, -1),
    'West':  (-1, 0),
}

def rotate_left(facing: str) -> str:
    """90° counter-clockwise rotation."""
    return DIRECTIONS[(DIRECTIONS.index(facing) - 1) % 4]

def rotate_right(facing: str) -> str:
    """90° clockwise rotation."""
    return DIRECTIONS[(DIRECTIONS.index(facing) + 1) % 4]


# ===========================================================================
# Environment
# ===========================================================================

class VisualGridHuntGame:
    """
    A Pacman-style grid environment.

    Lecture 03 note:
      - get_percept() deliberately omits global coordinates to create a
        PARTIALLY OBSERVABLE environment — the agent cannot know where it is.
    """

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2,
                 custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]           # (x, y), y increases upward
        self.agent_facing = 'North'        # initial orientation

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Default walls — includes a U-shape to trap the Simple Reflex Agent
            self.walls = {
                (2, 2), (2, 3), (2, 4),   # left arm of U
                (3, 4), (4, 4),            # top of U
                (5, 4), (5, 3), (5, 2),   # right arm of U
                (6, 5), (3, 7),
            }

        # Randomly placed food, avoiding walls and agent start
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx, fy = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if (fx, fy) != (0, 0) and (fx, fy) not in self.walls:
                self.food_positions.add((fx, fy))

        # Toxic traps
        self.toxic_traps = set()
        num_traps = max(1, min(3, self.width * self.height // 8))
        while len(self.toxic_traps) < num_traps:
            tx, ty = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if (tx, ty) != (0, 0) and (tx, ty) not in self.walls and (tx, ty) not in self.food_positions:
                self.toxic_traps.add((tx, ty))

        # Adversarial opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox, oy = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if (ox, oy) != (0, 0) and (ox, oy) not in self.walls and (ox, oy) not in self.food_positions:
                self.opponents.append([ox, oy])

        self.score = 0
        self.steps = 0
        self.collision = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _cell_in_direction(self, direction: str) -> tuple:
        """Return the (x, y) cell one step in the given direction from agent_pos."""
        dx, dy = DIR_DELTA[direction]
        return (self.agent_pos[0] + dx, self.agent_pos[1] + dy)

    def _is_blocked(self, cell: tuple) -> bool:
        """True if the cell is a wall or out of bounds."""
        x, y = cell
        return (x < 0 or x >= self.width or
                y < 0 or y >= self.height or
                cell in self.walls)

    # ------------------------------------------------------------------
    # Step 1.1 — Partial Observability: local boolean percepts only
    # The agent can no longer see its global position!
    # ------------------------------------------------------------------

    def get_percept(self) -> dict:
        """
        PARTIAL OBSERVABILITY — returns only what the agent's local sensors can detect.
        Global coordinates (agent_pos) are intentionally omitted.

        Percept keys:
          wall_ahead  — is the cell directly ahead a wall or boundary?
          wall_left   — is the cell to the left a wall or boundary?
          wall_right  — is the cell to the right a wall or boundary?
          food_here   — is there food at the agent's current cell?
          trap_here   — is there a toxic trap at the agent's current cell?
          facing      — the agent's current facing direction (visible on HUD)
          score       — cumulative score
          steps       — steps taken so far
          remaining_food — how many food pellets remain
        """
        ahead = self._cell_in_direction(self.agent_facing)
        left  = self._cell_in_direction(rotate_left(self.agent_facing))
        right = self._cell_in_direction(rotate_right(self.agent_facing))
        pos   = tuple(self.agent_pos)

        return {
            'wall_ahead':      self._is_blocked(ahead),
            'wall_left':       self._is_blocked(left),
            'wall_right':      self._is_blocked(right),
            'food_here':       pos in self.food_positions,
            'trap_here':       pos in self.toxic_traps,
            'facing':          self.agent_facing,
            'score':           self.score,
            'steps':           self.steps,
            'remaining_food':  len(self.food_positions),
        }

    # ------------------------------------------------------------------
    # Action execution — direction-aware
    # ------------------------------------------------------------------

    def execute_action(self, action: str):
        """
        Supported actions:
          move_forward  — move one cell in facing direction (or stay if wall)
          turn_left     — rotate 90° counter-clockwise, no position change
          turn_right    — rotate 90° clockwise, no position change
          collect       — stay in place (food collected automatically on entry)
          Up/Down/Left/Right — legacy absolute moves (for random/keyboard agents)
        """
        self.steps += 1
        new_pos = list(self.agent_pos)

        if action == 'move_forward':
            dx, dy = DIR_DELTA[self.agent_facing]
            new_pos = [self.agent_pos[0] + dx, self.agent_pos[1] + dy]

        elif action == 'turn_left':
            self.agent_facing = rotate_left(self.agent_facing)
            # No position change; skip wall/food checks below
            return

        elif action == 'turn_right':
            self.agent_facing = rotate_right(self.agent_facing)
            return

        elif action == 'collect':
            pass  # stay in place

        # Legacy absolute moves (random agent / keyboard)
        elif action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
            self.agent_facing = 'North'
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
            self.agent_facing = 'South'
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
            self.agent_facing = 'West'
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)
            self.agent_facing = 'East'

        # Apply movement — penalise wall collisions
        if tuple(new_pos) in self.walls or not (
                0 <= new_pos[0] < self.width and 0 <= new_pos[1] < self.height):
            self.score -= 5          # hit boundary / wall
        else:
            self.agent_pos = new_pos

        # Collect food
        pos = tuple(self.agent_pos)
        if pos in self.food_positions:
            self.food_positions.remove(pos)
            self.score += 20

        # Toxic trap
        if pos in self.toxic_traps:
            self.score -= 15

        # Move opponents randomly
        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if   move == 'Up'    and op[1] < self.height - 1: op[1] += 1
            elif move == 'Down'  and op[1] > 0:               op[1] -= 1
            elif move == 'Left'  and op[0] > 0:               op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:  op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 200 or self.collision


# ===========================================================================
# Step 1.2 — Simple Reflex Agent
# ===========================================================================

class SimpleReflexAgent:
    """
    Lecture 03 — Table-driven agents are infeasible; we write agent *programs*.

    A Simple Reflex Agent acts purely on the current percept via IF-THEN rules.
    It has NO memory and NO internal state.

    Fatal flaw (observable in simulation):
      In the U-shaped wall, the agent will loop forever:
        turn_left → move_forward → hit wall → turn_left → ...
    """

    # No __init__: this agent stores NO state between steps.

    def sense_and_act(self, percept: dict) -> str:
        """
        Condition-Action rules — strictly current percept only.
        No history, no memory.
        """
        # Rule 1: collect food if standing on it
        if percept['food_here']:
            return 'collect'

        # Rule 2: if the path ahead is blocked, turn left
        if percept['wall_ahead']:
            return 'turn_left'

        # Rule 3 (default): move forward
        return 'move_forward'


# ===========================================================================
# Step 1.3 — Model-Based Agent
# ===========================================================================

class ModelBasedAgent:
    """
    Lecture 03 — A Model-Based Agent maintains an internal world model.

    Internal state:
      self.visited_cells  — set of relative (x, y) positions the agent has visited
      self.pos            — agent's estimated relative position (starts at origin)
      self.facing         — mirrored facing direction (from percept)
      self.last_action    — the last action taken (for state transition / transition model)
      self.stuck_counter  — counts how many steps the agent has been blocked ahead
      self.turn_bias      — toggles preferred turn direction to break symmetry deadlocks

    Transition model: after 'move_forward' with no wall, update self.pos by DIR_DELTA.
    Sensor model: read facing from percept; wall booleans from percept.

    Escape logic (upgrades over SimpleReflexAgent):
      - Prefers to turn toward the side with an *unvisited* cell.
      - If stuck too long (same position repeated), force the opposite turn.
    """

    def __init__(self):
        self.visited_cells: set = set()
        self.pos: tuple = (0, 0)           # relative position (estimated)
        self.facing: str = 'North'         # mirrored from percept
        self.last_action: str = None
        self.stuck_counter: int = 0
        self.turn_bias: str = 'left'       # preferred turn when both sides free

        # Record starting position
        self.visited_cells.add(self.pos)

    # ------------------------------------------------------------------
    # State update (Transition Model + Sensor Model)
    # ------------------------------------------------------------------

    def _update_state(self, percept: dict):
        """Update internal world model based on last action and current percept."""

        # Sensor model: sync our facing copy with the environment's truth
        self.facing = percept['facing']

        # Transition model: if we moved forward and weren't blocked, update position
        if self.last_action == 'move_forward' and not percept['wall_ahead']:
            # We may have actually moved — estimate by checking whether the
            # cell we tried to enter was free (the environment already applied it).
            # Since we don't have global pos, we track relative displacement.
            dx, dy = DIR_DELTA[self.facing]
            # Note: we updated facing above, but last move was BEFORE this turn,
            # so we need the direction we were facing when we issued move_forward.
            # We store that separately via _pre_move_facing.
            pass  # handled via _pre_move_facing below (see sense_and_act)

        # Mark current relative position as visited
        self.visited_cells.add(self.pos)

    def _cell_after_turn(self, turn: str) -> tuple:
        """
        Return the relative cell one step in the direction we'd face after turning.
        Used to check whether that cell has been visited before.
        """
        new_facing = rotate_left(self.facing) if turn == 'left' else rotate_right(self.facing)
        dx, dy = DIR_DELTA[new_facing]
        return (self.pos[0] + dx, self.pos[1] + dy)

    # ------------------------------------------------------------------
    # Sense-Act (queries both percept AND internal state)
    # ------------------------------------------------------------------

    def sense_and_act(self, percept: dict) -> str:
        """
        Condition-Action rules that consult BOTH the current percept and memory.
        """
        # ---- Update state from percept ----
        self.facing = percept['facing']
        self.visited_cells.add(self.pos)

        # ---- Rule 0: collect food ----
        if percept['food_here']:
            self.last_action = 'collect'
            return 'collect'

        # ---- Resolve forward move ----
        if not percept['wall_ahead']:
            # Compute where we *will* be after moving forward
            dx, dy = DIR_DELTA[self.facing]
            next_pos = (self.pos[0] + dx, self.pos[1] + dy)

            # Prefer unvisited cells — keep moving forward
            if next_pos not in self.visited_cells:
                # Update relative position in the model
                self.pos = next_pos
                self.stuck_counter = 0
                self.last_action = 'move_forward'
                return 'move_forward'

            # Forward cell already visited — try to find a better direction
            self.stuck_counter += 1

        else:
            # Ahead is a wall
            self.stuck_counter += 1

        # ---- Rule 1: try left ----
        left_cell  = self._cell_after_turn('left')
        right_cell = self._cell_after_turn('right')

        left_visited  = left_cell  in self.visited_cells
        right_visited = right_cell in self.visited_cells
        wall_left  = percept['wall_left']
        wall_right = percept['wall_right']

        # ---- Rule 2: both sides free — prefer unvisited, else use bias ----
        if not wall_left and not wall_right:
            if not left_visited and right_visited:
                chosen = 'turn_left'
            elif left_visited and not right_visited:
                chosen = 'turn_right'
            else:
                # Both visited or both unvisited — alternate bias to escape loops
                chosen = 'turn_left' if self.turn_bias == 'left' else 'turn_right'
                self.turn_bias = 'right' if self.turn_bias == 'left' else 'left'

        elif not wall_left and (wall_right or right_visited):
            chosen = 'turn_left'
        elif not wall_right and (wall_left or left_visited):
            chosen = 'turn_right'
        else:
            # Boxed in — forced U-turn (two left turns)
            chosen = 'turn_left'

        # ---- Stuck override: if trapped many steps, flip bias ----
        if self.stuck_counter >= 6:
            self.stuck_counter = 0
            self.turn_bias = 'right' if self.turn_bias == 'left' else 'left'
            chosen = 'turn_left' if self.turn_bias == 'left' else 'turn_right'

        self.last_action = chosen
        return chosen


# ===========================================================================
# GUI
# ===========================================================================

# Arrow polygons for each facing direction (relative to cell centre, scaled at draw time)
ARROW_SHAPES = {
    'North': [(0.5, 0.15), (0.75, 0.55), (0.25, 0.55)],
    'South': [(0.5, 0.85), (0.75, 0.45), (0.25, 0.45)],
    'East':  [(0.85, 0.5), (0.45, 0.25), (0.45, 0.75)],
    'West':  [(0.15, 0.5), (0.55, 0.25), (0.55, 0.75)],
}


class GridGameGUI:
    """Tkinter wrapper — now includes an agent-type selector and facing arrow."""

    # Colour palette
    C_BG        = '#0f172a'
    C_CELL      = '#1e293b'
    C_WALL      = '#475569'
    C_GRID_LINE = '#334155'
    C_FOOD      = '#f59e0b'
    C_TRAP      = '#8b5cf6'
    C_OPPONENT  = '#ef4444'
    C_AGENT     = '#3b82f6'
    C_ARROW     = '#ffffff'

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=0,
                 walls=None):
        self.root = root
        self.root.title('IT3012 Lab 02 — Agent Architectures')
        self.root.configure(bg=self.C_BG)

        self.width  = width
        self.height = height
        self.num_food      = num_food
        self.num_opponents = num_opponents
        self.walls         = walls

        # ---- Agent selector ----
        ctrl_frame = tk.Frame(root, bg=self.C_BG)
        ctrl_frame.pack(pady=(12, 4))

        tk.Label(ctrl_frame, text='Agent Type:', bg=self.C_BG, fg='#94a3b8',
                 font=('Helvetica', 12)).grid(row=0, column=0, padx=(0, 8))

        self.agent_var = tk.StringVar(value='Simple Reflex Agent')
        agent_menu = ttk.Combobox(ctrl_frame, textvariable=self.agent_var, width=22,
                                  values=['Random Agent',
                                          'Simple Reflex Agent',
                                          'Model-Based Agent'],
                                  state='readonly', font=('Helvetica', 12))
        agent_menu.grid(row=0, column=1)

        # ---- Canvas ----
        max_canvas_dim = 560
        self.cell_size = max(30, min(max_canvas_dim // width, max_canvas_dim // height))
        canvas_w = width  * self.cell_size
        canvas_h = height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg=self.C_BG,
                                highlightthickness=0)
        self.canvas.pack(padx=16, pady=8)

        # ---- Status label ----
        self.label = tk.Label(root, text='Score: 0 | Steps: 0',
                              bg=self.C_BG, fg='#e2e8f0', font=('Helvetica', 13))
        self.label.pack(pady=4)

        # ---- Percept / memory panel ----
        self.percept_label = tk.Label(
            root,
            text='Percept: —\nMemory: —',
            bg=self.C_BG, fg='#64748b',
            font=('Courier', 10),
            justify='left',
        )
        self.percept_label.pack(pady=(0, 6))

        # ---- Buttons ----
        btn_frame = tk.Frame(root, bg=self.C_BG)
        btn_frame.pack(pady=(0, 12))

        self.btn = tk.Button(btn_frame, text='▶  Start Simulation',
                             command=self.start_simulation,
                             font=('Helvetica', 12, 'bold'),
                             bg='#1d4ed8', fg='white', relief='flat',
                             padx=14, pady=6, cursor='hand2')
        self.btn.grid(row=0, column=0, padx=6)

        self.reset_btn = tk.Button(btn_frame, text='↺  Reset',
                                   command=self.reset_simulation,
                                   font=('Helvetica', 12),
                                   bg='#334155', fg='#e2e8f0', relief='flat',
                                   padx=14, pady=6, cursor='hand2')
        self.reset_btn.grid(row=0, column=1, padx=6)

        # ---- Agent & environment (created fresh on each start) ----
        self.env   = None
        self.agent = None
        self._build_env()
        self.draw_grid()

    # ------------------------------------------------------------------
    # Environment / agent factory
    # ------------------------------------------------------------------

    def _build_env(self):
        self.env = VisualGridHuntGame(
            width=self.width, height=self.height,
            num_food=self.num_food, num_opponents=self.num_opponents,
            custom_walls=self.walls,
        )

    def _build_agent(self):
        choice = self.agent_var.get()
        if choice == 'Simple Reflex Agent':
            self.agent = SimpleReflexAgent()
        elif choice == 'Model-Based Agent':
            self.agent = ModelBasedAgent()
        else:
            self.agent = None   # Random agent — no class needed

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw_grid(self):
        self.canvas.delete('all')
        cs = self.cell_size

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * cs
                y1 = (self.env.height - 1 - y) * cs
                x2 = x1 + cs
                y2 = y1 + cs

                fill = self.C_WALL if (x, y) in self.env.walls else self.C_CELL
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill,
                                             outline=self.C_GRID_LINE, width=1)

        # Food
        for fx, fy in self.env.food_positions:
            pad = cs * 0.28
            cx = fx * cs + cs / 2
            cy = (self.env.height - 1 - fy) * cs + cs / 2
            r  = cs * 0.22
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                    fill=self.C_FOOD, outline='#d97706', width=1)

        # Toxic traps
        for tx, ty in self.env.toxic_traps:
            pad = cs * 0.22
            x1 = tx * cs + pad
            y1 = (self.env.height - 1 - ty) * cs + pad
            self.canvas.create_rectangle(x1, y1, x1 + cs - 2 * pad, y1 + cs - 2 * pad,
                                         fill=self.C_TRAP, outline='#6d28d9', width=1)

        # Opponents
        for ox, oy in self.env.opponents:
            pad = cs * 0.18
            x1 = ox * cs + pad
            y1 = (self.env.height - 1 - oy) * cs + pad
            self.canvas.create_rectangle(x1, y1, x1 + cs - 2 * pad, y1 + cs - 2 * pad,
                                         fill=self.C_OPPONENT, outline='#b91c1c', width=1)

        # Agent body
        ax, ay = self.env.agent_pos
        r   = cs * 0.35
        cx  = ax * cs + cs / 2
        cy  = (self.env.height - 1 - ay) * cs + cs / 2
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                fill=self.C_AGENT, outline='#1e40af', width=2)

        # Facing direction arrow (triangle)
        facing = self.env.agent_facing
        pts_norm = ARROW_SHAPES[facing]
        cell_x = ax * cs
        cell_y = (self.env.height - 1 - ay) * cs
        pts = []
        for nx, ny in pts_norm:
            pts.append(cell_x + nx * cs)
            pts.append(cell_y + ny * cs)
        self.canvas.create_polygon(pts, fill=self.C_ARROW, outline='', smooth=False)

    # ------------------------------------------------------------------
    # Simulation loop
    # ------------------------------------------------------------------

    def start_simulation(self):
        self._build_env()
        self._build_agent()
        self.btn.config(state='disabled')
        self.reset_btn.config(state='disabled')
        self.draw_grid()
        self._step()

    def reset_simulation(self):
        self._build_env()
        self._build_agent()
        self.label.config(text='Score: 0 | Steps: 0')
        self.percept_label.config(text='Percept: —\nMemory: —')
        self.draw_grid()
        self.btn.config(state='normal')

    def _get_action(self, percept: dict) -> str:
        """Dispatch to the active agent (or random)."""
        if self.agent is None:
            return random.choice(['Up', 'Down', 'Left', 'Right'])
        return self.agent.sense_and_act(percept)

    def _format_percept(self, percept: dict) -> str:
        return (
            f"wall_ahead={percept['wall_ahead']}  "
            f"wall_left={percept['wall_left']}  "
            f"wall_right={percept['wall_right']}\n"
            f"food_here={percept['food_here']}    "
            f"trap_here={percept['trap_here']}    "
            f"facing={percept['facing']}"
        )

    def _format_memory(self) -> str:
        if isinstance(self.agent, ModelBasedAgent):
            return (
                f"visited={len(self.agent.visited_cells)} cells  "
                f"rel_pos={self.agent.pos}  "
                f"stuck={self.agent.stuck_counter}"
            )
        if isinstance(self.agent, SimpleReflexAgent):
            return '(no memory — Simple Reflex Agent)'
        return '(random agent — no model)'

    def _step(self):
        if not self.env.is_done():
            percept = self.env.get_percept()
            action  = self._get_action(percept)
            self.env.execute_action(action)

            self.draw_grid()

            agent_label = self.agent_var.get()
            self.label.config(
                text=(f'[{agent_label}]  '
                      f'Score: {self.env.score} | '
                      f'Steps: {self.env.steps} | '
                      f'Action: {action} | '
                      f'Food left: {len(self.env.food_positions)}')
            )
            self.percept_label.config(
                text=f'Percept: {self._format_percept(percept)}\n'
                     f'Memory:  {self._format_memory()}'
            )
            self.root.after(300, self._step)

        else:
            if self.env.collision:
                end_text = f'💥 Collision! Game Over — Final Score: {self.env.score}'
            elif len(self.env.food_positions) == 0:
                end_text = f'🎉 All food collected! Final Score: {self.env.score}'
            else:
                end_text = f'⏱ Time limit reached — Final Score: {self.env.score}'

            self.label.config(text=end_text)
            self.btn.config(state='normal')
            self.reset_btn.config(state='normal')


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == '__main__':
    # U-shaped wall to trap the Simple Reflex Agent — demonstrates the fatal flaw
    u_shape_walls = [
        (3, 2), (3, 3), (3, 4),   # left pillar
        (4, 4), (5, 4),            # top bar
        (6, 4), (6, 3), (6, 2),   # right pillar
        (2, 6), (7, 6),
        (1, 8), (8, 2),
    ]

    root = tk.Tk()
    app  = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=0,
                       walls=u_shape_walls)
    root.mainloop()