
import sys
import ctypes
import pygame

from environment import (
    WIDTH,
    HEIGHT,
    BACKGROUND,
    ROBOT_COLORS,
    create_packages,
    draw_warehouse,
    draw_package
)

from robot import Robot
from coordinator import Coordinator
from recovery import FailureRecovery, draw_path, draw_robot, draw_ui


def create_robots():
    return [
        Robot(1, (1, 1), ROBOT_COLORS[0]),
        Robot(2, (12, 1), ROBOT_COLORS[1]),
        Robot(3, (1, 12), ROBOT_COLORS[2]),
        Robot(4, (12, 12), ROBOT_COLORS[3]),
        Robot(5, (23, 1), ROBOT_COLORS[4])
    ]


def reset_simulation():
    robots = create_robots()
    packages = create_packages()
    coordinator = Coordinator(robots, packages)
    recovery = FailureRecovery(robots, packages, coordinator)
    return robots, packages, coordinator, recovery


def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT),
        pygame.RESIZABLE
    )

    pygame.display.set_caption(
        "Multi-Agent Warehouse Robot Coordinator — 25×25 / 5 Robots / 10 Packages"
    )

    hwnd = pygame.display.get_wm_info()["window"]
    ctypes.windll.user32.ShowWindow(hwnd, 3)

    simulation_surface = pygame.Surface((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    robots, packages, coordinator, recovery = reset_simulation()

    paused = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_SPACE:
                    paused = not paused

                elif event.key in (
                    pygame.K_1,
                    pygame.K_2,
                    pygame.K_3,
                    pygame.K_4,
                    pygame.K_5
                ):
                    robot_id = {
                        pygame.K_1: 1,
                        pygame.K_2: 2,
                        pygame.K_3: 3,
                        pygame.K_4: 4,
                        pygame.K_5: 5
                    }[event.key]

                    recovery.fail_robot(robot_id)

                elif event.key == pygame.K_r:
                    robots, packages, coordinator, recovery = reset_simulation()
                    paused = False

        if not paused:
            coordinator.allocate_tasks()

            # Refresh occupied cells before each robot moves.
            for robot in robots:
                if robot.failed:
                    continue

                other_positions = {
                    other.position
                    for other in robots
                    if other is not robot and not other.failed
                }

                robot.update(other_positions)

        simulation_surface.fill(BACKGROUND)

        draw_warehouse(simulation_surface)

        for robot in robots:
            if robot.current_task is not None:
                draw_path(
                    simulation_surface,
                    robot.path[robot.path_index:]
                )

        for package in packages:
            draw_package(
                simulation_surface,
                package
            )

        for robot in robots:
            draw_robot(
                simulation_surface,
                robot
            )

        draw_ui(
            simulation_surface,
            robots,
            packages,
            coordinator,
            recovery,
            paused
        )

        window_width, window_height = screen.get_size()

        # Preserve the original aspect ratio when resizing.
        scale = min(
            window_width / WIDTH,
            window_height / HEIGHT
        )

        scaled_width = max(1, int(WIDTH * scale))
        scaled_height = max(1, int(HEIGHT * scale))

        scaled_surface = pygame.transform.smoothscale(
            simulation_surface,
            (scaled_width, scaled_height)
        )

        screen.fill(BACKGROUND)

        offset_x = (window_width - scaled_width) // 2
        offset_y = (window_height - scaled_height) // 2

        screen.blit(
            scaled_surface,
            (offset_x, offset_y)
        )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
