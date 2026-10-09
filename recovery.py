import pygame
import pygame.gfxdraw

from environment import (
    OFFSET_X,
    OFFSET_Y,
    CELL_SIZE,
    GRID,
    WHITE,
    BLACK,
    TEXT_COLOR,
    MUTED_TEXT,
    PANEL_COLOR,
    PANEL_BORDER,
    PATH_COLOR,
    SUCCESS,
    WARNING,
    DANGER,
    INFO,
    warehouse
)

MAX_ROBOT_FAILURES = 3


class FailureRecovery:
    def __init__(self, robots, packages, coordinator):
        self.robots = robots
        self.packages = packages
        self.coordinator = coordinator
        self.robot_failures = 0
        self.reassignments = 0

    def fail_robot(self, robot_id):
        if self.robot_failures >= MAX_ROBOT_FAILURES:
            return False

        robot = next(
            (r for r in self.robots if r.id == robot_id),
            None
        )

        if robot is None or robot.failed:
            return False

        drop_position = robot.position

        if (
            robot.current_task is not None
            and robot.current_task.status == "Picked Up"
            and robot.path_index < len(robot.path) - 1
        ):
            candidate = robot.path[robot.path_index + 1]
            if warehouse[candidate[0]][candidate[1]] == 0:
                drop_position = candidate

        robot.failed = True
        robot.state = "FAILED"
        robot.path = []
        robot.path_index = 0
        self.robot_failures += 1

        if robot.current_task is not None:
            package = robot.current_task
            package.assigned_robot = None

            if package.status == "Picked Up":
                package.current_position = drop_position
                package.status = "Dropped"
            else:
                package.current_position = package.pickup
                package.status = "Waiting"

            robot.current_task = None
            self.reassignments += 1

        return True


def draw_path(screen, path):
    if len(path) < 2:
        return

    points = [
        (
            OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2,
            OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
        )
        for row, col in path
    ]

    radius = max(2, CELL_SIZE // 8)

    # Crisp antialiased path dots only.
    for x, y in points:
        pygame.gfxdraw.filled_circle(
            screen,
            x,
            y,
            radius,
            PATH_COLOR
        )
        pygame.gfxdraw.aacircle(
            screen,
            x,
            y,
            radius,
            PATH_COLOR
        )


def draw_robot(screen, robot):
    row, col = robot.position

    x = OFFSET_X + col * CELL_SIZE
    y = OFFSET_Y + row * CELL_SIZE

    center = (
        x + CELL_SIZE // 2,
        y + CELL_SIZE // 2
    )

    radius = max(8, CELL_SIZE // 2 - 2)

    if robot.failed:
        pygame.gfxdraw.aacircle(
            screen,
            center[0],
            center[1],
            radius,
            DANGER
        )
        pygame.draw.circle(
            screen,
            DANGER,
            center,
            radius,
            2
        )

        pygame.draw.line(
            screen,
            DANGER,
            (center[0] - 7, center[1] - 7),
            (center[0] + 7, center[1] + 7),
            2
        )
        pygame.draw.line(
            screen,
            DANGER,
            (center[0] + 7, center[1] - 7),
            (center[0] - 7, center[1] + 7),
            2
        )
        return

    # Antialiased outer ring.
    pygame.gfxdraw.filled_circle(
        screen,
        center[0],
        center[1],
        radius + 1,
        (28, 30, 35)
    )
    pygame.gfxdraw.filled_circle(
        screen,
        center[0],
        center[1],
        radius,
        robot.color
    )

    # Clean inner face.
    pygame.gfxdraw.filled_circle(
        screen,
        center[0],
        center[1],
        max(4, CELL_SIZE // 4),
        WHITE
    )

    font = pygame.font.SysFont("Arial", 12, bold=True)
    label = font.render(str(robot.id), True, BLACK)

    screen.blit(
        label,
        (
            center[0] - label.get_width() // 2,
            center[1] - label.get_height() // 2
        )
    )


def draw_status_pill(screen, font, text, x, y, color, width=118):
    rect = pygame.Rect(x, y, width, 23)

    pygame.draw.rect(
        screen,
        tuple(max(0, c // 4) for c in color),
        rect,
        border_radius=11
    )

    pygame.draw.rect(
        screen,
        color,
        rect,
        1,
        border_radius=11
    )

    label = font.render(text, True, color)

    screen.blit(
        label,
        (
            x + (width - label.get_width()) // 2,
            y + (23 - label.get_height()) // 2
        )
    )


def draw_ui(screen, robots, packages, coordinator, recovery, paused):
    title_font = pygame.font.SysFont("Arial", 22, bold=True)
    section_font = pygame.font.SysFont("Arial", 17, bold=True)
    font = pygame.font.SysFont("Arial", 14)
    small = pygame.font.SysFont("Arial", 12)
    tiny = pygame.font.SysFont("Arial", 11)

    # Header
    screen.blit(
        title_font.render(
            "MULTI-AGENT WAREHOUSE ROBOT COORDINATOR",
            True,
            WHITE
        ),
        (20, 22)
    )

    active = sum(not r.failed for r in robots)
    status = "PAUSED" if paused else "RUNNING"
    status_color = WARNING if paused else SUCCESS

    draw_status_pill(
        screen,
        small,
        status,
        1085,
        20,
        status_color,
        110
    )

    # Warehouse labels
    screen.blit(
        small.render("25 × 25 WAREHOUSE GRID", True, MUTED_TEXT),
        (20, 52)
    )

    # Main dashboard
    panel = pygame.Rect(650, 70, 610, 700)

    pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=8)
    pygame.draw.rect(screen, PANEL_BORDER, panel, 2, border_radius=8)

    # Coordinator header
    screen.blit(
        title_font.render("COORDINATOR AGENT", True, WHITE),
        (675, 92)
    )

    screen.blit(
        font.render(
            f"SYSTEM STATUS  •  {status}",
            True,
            status_color
        ),
        (675, 124)
    )

    screen.blit(
        font.render(
            f"ACTIVE ROBOTS  {active}/{len(robots)}",
            True,
            TEXT_COLOR
        ),
        (1030, 124)
    )

    pygame.draw.line(
        screen,
        PANEL_BORDER,
        (675, 150),
        (1235, 150),
        1
    )

    # Robot monitoring
    screen.blit(
        section_font.render("ROBOT MONITOR", True, WHITE),
        (675, 166)
    )

    y = 198

    for robot in robots:
        status_text = robot.state.replace("_", " ")

        if robot.failed:
            status_color = DANGER
        elif "DELIVERY" in status_text.upper():
            status_color = SUCCESS
        elif "PICKUP" in status_text.upper():
            status_color = WARNING
        elif "IDLE" in status_text.upper():
            status_color = INFO
        else:
            status_color = TEXT_COLOR

        screen.blit(
            font.render(
                f"R{robot.id}",
                True,
                robot.color
            ),
            (680, y + 3)
        )

        draw_status_pill(
            screen,
            tiny,
            status_text[:18],
            715,
            y,
            status_color,
            145
        )

        screen.blit(
            small.render(
                f"Tasks {robot.completed_tasks}",
                True,
                TEXT_COLOR
            ),
            (875, y + 5)
        )

        screen.blit(
            small.render(
                f"Distance {robot.total_distance}",
                True,
                TEXT_COLOR
            ),
            (965, y + 5)
        )

        screen.blit(
            small.render(
                f"Replans {robot.replans}",
                True,
                TEXT_COLOR
            ),
            (1080, y + 5)
        )

        y += 38

    # Package monitor
    pygame.draw.line(
        screen,
        PANEL_BORDER,
        (675, y + 2),
        (1235, y + 2),
        1
    )

    y += 18

    screen.blit(
        section_font.render("PACKAGE MONITOR", True, WHITE),
        (675, y)
    )

    delivered = sum(p.status == "Delivered" for p in packages)
    picked = sum(p.status == "Picked Up" for p in packages)
    assigned = sum(p.status == "Assigned" for p in packages)
    waiting = sum(p.status == "Waiting" for p in packages)
    dropped = sum(p.status == "Dropped" for p in packages)

    screen.blit(
        small.render(
            f"Delivered {delivered}   In Transit {picked}   "
            f"Assigned {assigned}   Waiting {waiting}   Dropped {dropped}",
            True,
            TEXT_COLOR
        ),
        (675, y + 25)
    )

    y += 50

    package_rows = (len(packages) + 1) // 2

    for row in range(package_rows):
        for index, x in (
            (row, 680),
            (row + package_rows, 965)
        ):
            if index >= len(packages):
                continue

            package = packages[index]

            if package.status == "Delivered":
                color = SUCCESS
            elif package.status == "Picked Up":
                color = WARNING
            elif package.status == "Dropped":
                color = DANGER
            elif package.status == "Assigned":
                color = INFO
            else:
                color = TEXT_COLOR

            screen.blit(
                tiny.render(
                    f"P{package.id:02d}  {package.status.upper()}",
                    True,
                    color
                ),
                (x, y)
            )

        y += 19

    # Performance cards
    y += 8

    pygame.draw.line(
        screen,
        PANEL_BORDER,
        (675, y),
        (1235, y),
        1
    )

    y += 15

    screen.blit(
        section_font.render("PERFORMANCE", True, WHITE),
        (675, y)
    )

    y += 28

    total_distance = sum(r.total_distance for r in robots)
    total_replans = sum(r.replans for r in robots)

    metrics = [
        ("DELIVERED", f"{delivered}/{len(packages)}", SUCCESS),
        ("ASSIGNMENTS", str(coordinator.total_assignments), INFO),
        ("DISTANCE", str(total_distance), WARNING),
        ("REPLANS", str(total_replans), INFO),
        ("FAILURES", f"{recovery.robot_failures}/{MAX_ROBOT_FAILURES}", DANGER),
        ("REASSIGNED", str(recovery.reassignments), WARNING)
    ]

    card_w = 170
    card_h = 45

    for i, (label, value, color) in enumerate(metrics):
        col = i % 3
        row = i // 3

        x = 675 + col * 188
        card_y = y + row * 50

        card = pygame.Rect(x, card_y, card_w, card_h)

        pygame.draw.rect(
            screen,
            (24, 26, 31),
            card,
            border_radius=6
        )

        pygame.draw.rect(
            screen,
            color,
            card,
            1,
            border_radius=6
        )

        screen.blit(
            tiny.render(label, True, MUTED_TEXT),
            (x + 10, card_y + 7)
        )

        screen.blit(
            font.render(value, True, color),
            (x + 10, card_y + 24)
        )

    # Footer / controls
    pygame.draw.line(
        screen,
        PANEL_BORDER,
        (20, 715),
        (620, 715),
        1
    )

    controls = (
        "1-5  FAIL ROBOT     "
        "SPACE  PAUSE / RESUME     "
        "R  RESET     "
        "ESC  EXIT"
    )

    screen.blit(
        small.render(controls, True, MUTED_TEXT),
        (20, 726)
    )

    legend = (
        "■ Package    ○ Delivery    "
        "● Robot    ■ Path    ✕ Failed"
    )

    screen.blit(
        small.render(legend, True, MUTED_TEXT),
        (20, 750)
    )
