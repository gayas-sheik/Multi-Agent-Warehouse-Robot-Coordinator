class Coordinator:
    def __init__(self, robots, packages):
        self.robots = robots
        self.packages = packages
        self.total_assignments = 0

    # Calculate Manhattan distance between two warehouse cells.
    @staticmethod
    def distance(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Allocate available packages to suitable idle robots.
    def allocate_tasks(self):
        idle_robots = [
            robot for robot in self.robots
            if robot.current_task is None and not robot.failed
        ]

        # Recovery tasks are handled before normal waiting tasks.
        recovery_packages = [
            package for package in self.packages
            if package.status == "Dropped"
            and package.assigned_robot is None
        ]

        # Collect packages that are still waiting for pickup.
        waiting_packages = [
            package for package in self.packages
            if package.status == "Waiting"
            and package.assigned_robot is None
        ]

        # Assign each dropped package to the closest available robot.
        for package in recovery_packages:
            if not idle_robots:
                break

            robot = min(
                idle_robots,
                key=lambda r: self.distance(
                    r.position,
                    package.current_position
                )
            )

            if robot.assign_task(package):
                self.total_assignments += 1
                idle_robots.remove(robot)

        # Assign each waiting package to the closest available robot.
        for package in waiting_packages:
            if not idle_robots:
                break

            robot = min(
                idle_robots,
                key=lambda r: self.distance(
                    r.position,
                    package.pickup
                )
            )

            if robot.assign_task(package):
                self.total_assignments += 1
                idle_robots.remove(robot)