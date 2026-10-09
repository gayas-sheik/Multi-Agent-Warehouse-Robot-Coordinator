import heapq
import pygame

from environment import (
    ROWS,
    COLS,
    warehouse
)


# Calculate Manhattan distance used as the A* heuristic.
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# Return all valid neighboring cells that are not warehouse obstacles.
def get_neighbors(position):
    row, col = position

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    neighbors = []

    for dr, dc in directions:
        nr = row + dr
        nc = col + dc

        if 0 <= nr < ROWS and 0 <= nc < COLS:
            if warehouse[nr][nc] == 0:
                neighbors.append((nr, nc))

    return neighbors

# Find the shortest available path from start to goal using A*.
def a_star(start, goal, blocked=None):
    if blocked is None:
        blocked = set()
    else:
        blocked = set(blocked)

    # Validate that both positions are inside the warehouse grid.
    if not (
        0 <= start[0] < ROWS
        and 0 <= start[1] < COLS
        and 0 <= goal[0] < ROWS
        and 0 <= goal[1] < COLS
    ):
        return []

    # A robot cannot start from or move to an obstacle cell.
    if warehouse[start[0]][start[1]] == 1:
        return []

    if warehouse[goal[0]][goal[1]] == 1:
        return []

    if start == goal:
        return [start]

    open_set = []
    heapq.heappush(
        open_set,
        (heuristic(start, goal), 0, start)
    )

    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current_g, current = heapq.heappop(open_set)

        # Ignore outdated entries already replaced by a shorter path.
        if current_g != g_score.get(current):
            continue

        # Reconstruct and return the path once the goal is reached.
        if current == goal:
            path = [current]

            while current in came_from:
                current = came_from[current]
                path.append(current)

            path.reverse()
            return path

        # Explore all valid neighboring cells.
        for neighbor in get_neighbors(current):
            # Temporarily occupied robot cells are treated as blocked.
            # The goal itself remains allowed because collision checking
            # is handled separately during robot movement.
            if neighbor in blocked and neighbor != goal:
                continue

            tentative_g = current_g + 1

            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g

                f_score = tentative_g + heuristic(neighbor, goal)

                heapq.heappush(
                    open_set,
                    (f_score, tentative_g, neighbor)
                )

    return []

# Represents an autonomous warehouse robot and its current task state.
class Robot:

    def __init__(self, robot_id, start, color):
        self.id = robot_id
        self.position = start
        self.color = color
        self.current_task = None
        self.path = []
        self.path_index = 0
        self.state = "Idle"
        self.move_timer = 0
        self.move_delay = 170
        self.completed_tasks = 0
        self.total_distance = 0
        self.replans = 0
        self.failed = False

    # Assign a package to the robot and generate its initial path.
    def assign_task(self, package):
        if self.failed:
            return False

        self.current_task = package
        package.assigned_robot = self

        # Recover a package that was dropped by another failed robot.
        if package.status == "Dropped":
            self.state = "Going to Package"

            if not self.calculate_path(package.current_position):
                self.current_task = None
                package.assigned_robot = None
                return False

        # Assign a normal waiting package.
        else:
            package.status = "Assigned"
            self.state = "Going to Pickup"

            if not self.calculate_path(package.pickup):
                package.status = "Waiting"
                package.assigned_robot = None
                self.current_task = None
                return False

        return True

    # Calculate an A* path to the specified destination.
    def calculate_path(self, destination, blocked=None):
        self.path = a_star(
            self.position,
            destination,
            blocked
        )

        self.path_index = 0
        self.replans += 1

        return bool(self.path)

    # Update the robot's movement and task progress.
    def update(self, other_positions):
        if self.failed:
            return

        if self.current_task is None:
            self.state = "Idle"
            return

        current_time = pygame.time.get_ticks()

        if current_time - self.move_timer < self.move_delay:
            return

        self.move_timer = current_time

        # Phase 1: Move to the package pickup location.
        if self.state == "Going to Pickup":
            target = self.current_task.pickup

            if self.position == target:
                self.current_task.status = "Picked Up"
                self.current_task.current_position = self.position
                self.state = "Going to Delivery"

                if not self.calculate_path(self.current_task.delivery):
                    self._cancel_task()

                return

        # Phase 1B: Move to a package dropped by a failed robot.
        elif self.state == "Going to Package":
            target = self.current_task.current_position

            if self.position == target:
                self.current_task.status = "Picked Up"
                self.current_task.current_position = self.position
                self.state = "Going to Delivery"

                if not self.calculate_path(self.current_task.delivery):
                    self._cancel_task()

                return

        # Phase 2: Move to the package delivery location.
        elif self.state == "Going to Delivery":
            target = self.current_task.delivery

            if self.position == target:
                self.current_task.status = "Delivered"
                self.completed_tasks += 1
                self.current_task = None
                self.path = []
                self.path_index = 0
                self.state = "Idle"
                return

        # Stop if there is no remaining path to follow.
        if self.path_index >= len(self.path) - 1:
            return

        next_position = self.path[self.path_index + 1]

        # Avoid collisions with other active robots.
        if next_position in other_positions:
            if self.state == "Going to Pickup":
                target = self.current_task.pickup
            elif self.state == "Going to Package":
                target = self.current_task.current_position
            else:
                target = self.current_task.delivery

            # Recalculate the route around the temporary blockage.
            self.calculate_path(
                target,
                blocked=other_positions
            )
            return

        # Move the robot forward by one grid cell.
        self.path_index += 1
        self.position = self.path[self.path_index]

        # Carry the package along with the robot after pickup.
        if (
            self.current_task is not None
            and self.current_task.status == "Picked Up"
        ):
            self.current_task.current_position = self.position

        self.total_distance += 1

    # Cancel the current task when a valid route cannot be maintained.
    def _cancel_task(self):
        self.current_task.status = "Waiting"
        self.current_task.assigned_robot = None
        self.current_task = None
        self.path = []
        self.path_index = 0
        self.state = "Idle"