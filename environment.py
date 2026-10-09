import pygame
import pygame.gfxdraw

# ============================================================
# Display and grid configuration
# ============================================================

WIDTH, HEIGHT = 1280, 800
ROWS, COLS = 25, 25
CELL_SIZE = 24
OFFSET_X, OFFSET_Y = 20, 70

WAREHOUSE_WIDTH = COLS * CELL_SIZE
WAREHOUSE_HEIGHT = ROWS * CELL_SIZE

# ============================================================
# Colors
# ============================================================

BACKGROUND = (18, 19, 23)
FLOOR = (242, 243, 245)
WALL = (52, 55, 62)
GRID = (198, 201, 206)
GRID_DARK = (178, 181, 187)
WHITE = (248, 249, 250)
BLACK = (20, 20, 22)
SHELF_EDGE = (78, 81, 89)
SHELF_HIGHLIGHT = (105, 108, 117)
PACKAGE_OUTLINE = (214, 137, 20)
DELIVERY_GLOW = (115, 240, 170)

ROBOT_COLORS = [
    (55, 130, 255),
    (235, 75, 75),
    (55, 190, 115),
    (175, 90, 235),
    (255, 170, 45)
]

PACKAGE_COLOR = (255, 174, 45)
DELIVERY_COLOR = (55, 195, 125)
PATH_COLOR = (255, 185, 55)
TEXT_COLOR = (225, 227, 231)
MUTED_TEXT = (155, 160, 170)
PANEL_COLOR = (30, 32, 38)
PANEL_BORDER = (90, 94, 104)
SUCCESS = (70, 220, 125)
WARNING = (255, 195, 65)
DANGER = (245, 80, 80)
INFO = (75, 155, 255)

# ============================================================
# Warehouse grid
# ============================================================

warehouse = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# Vertical shelf rows with wide cross-aisles.
for col in [4, 8, 12, 16, 20]:
    for row in range(2, 23):
        if row not in [6, 12, 18]:
            warehouse[row][col] = 1

# Horizontal shelf sections.
for row, segments in [
    (9, [(1, 3), (5, 7), (9, 11), (13, 15), (17, 19), (21, 23)]),
    (16, [(1, 3), (5, 7), (9, 11), (13, 15), (17, 19), (21, 23)])
]:
    for start, end in segments:
        for col in range(start, end + 1):
            warehouse[row][col] = 1


class Package:
    def __init__(self, package_id, pickup, delivery):
        self.id = package_id
        self.pickup = pickup
        self.delivery = delivery
        self.status = "Waiting"
        self.current_position = pickup
        self.assigned_robot = None


def create_packages():
    return [
        Package(1, (2, 2), (23, 22)),
        Package(2, (4, 6), (21, 18)),
        Package(3, (5, 11), (20, 2)),
        Package(4, (7, 14), (3, 22)),
        Package(5, (8, 19), (22, 14)),
        Package(6, (11, 2), (2, 17)),
        Package(7, (13, 7), (23, 6)),
        Package(8, (14, 15), (4, 21)),
        Package(9, (19, 2), (11, 23)),
        Package(10, (21, 10), (14, 3))
    ]


def draw_warehouse(screen):
    warehouse_rect = pygame.Rect(
        OFFSET_X,
        OFFSET_Y,
        WAREHOUSE_WIDTH,
        WAREHOUSE_HEIGHT
    )

    pygame.draw.rect(screen, FLOOR, warehouse_rect)

    for row in range(ROWS):
        for col in range(COLS):
            x = OFFSET_X + col * CELL_SIZE
            y = OFFSET_Y + row * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            if warehouse[row][col] == 1:
                pygame.draw.rect(screen, WALL, rect)
                pygame.draw.line(
                    screen,
                    SHELF_EDGE,
                    (x + 1, y + 1),
                    (x + CELL_SIZE - 2, y + 1),
                    1
                )
                pygame.draw.line(
                    screen,
                    SHELF_HIGHLIGHT,
                    (x + 2, y + 2),
                    (x + 2, y + CELL_SIZE - 3),
                    1
                )
            else:
                pygame.draw.rect(screen, FLOOR, rect)

            pygame.draw.rect(screen, GRID, rect, 1)

    pygame.draw.rect(screen, PANEL_BORDER, warehouse_rect, 2)


def draw_package(screen, package):
    if package.status == "Delivered":
        return

    if package.status == "Dropped":
        row, col = package.current_position
    elif package.status != "Picked Up":
        row, col = package.pickup
    else:
        row = col = None

    if row is not None:
        x = OFFSET_X + col * CELL_SIZE
        y = OFFSET_Y + row * CELL_SIZE
        size = max(10, CELL_SIZE - 8)
        rect = pygame.Rect(
            x + (CELL_SIZE - size) // 2,
            y + (CELL_SIZE - size) // 2,
            size,
            size
        )

        pygame.draw.rect(
            screen,
            PACKAGE_OUTLINE,
            rect.inflate(2, 2),
            border_radius=4
        )
        pygame.draw.rect(
            screen,
            PACKAGE_COLOR,
            rect,
            border_radius=3
        )

        highlight = pygame.Rect(
            rect.x + 2,
            rect.y + 2,
            max(2, rect.width // 3),
            max(2, rect.height // 3)
        )
        pygame.draw.rect(
            screen,
            (255, 220, 125),
            highlight,
            border_radius=1
        )

    row, col = package.delivery
    x = OFFSET_X + col * CELL_SIZE
    y = OFFSET_Y + row * CELL_SIZE
    center = (
        x + CELL_SIZE // 2,
        y + CELL_SIZE // 2
    )

    radius = max(6, CELL_SIZE // 3)

    pygame.gfxdraw.aacircle(
        screen,
        center[0],
        center[1],
        radius,
        DELIVERY_GLOW
    )
    pygame.gfxdraw.aacircle(
        screen,
        center[0],
        center[1],
        max(4, radius - 2),
        DELIVERY_COLOR
    )

    pygame.gfxdraw.aacircle(
        screen,
        center[0],
        center[1],
        2,
        WHITE
    )
