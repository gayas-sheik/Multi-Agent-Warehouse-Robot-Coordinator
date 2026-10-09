# Multi-Agent Warehouse Robot Coordinator

## Foundations of Artificial Intelligence Case Study

A Python and Pygame-based warehouse simulation in which five autonomous robot agents coordinate package deliveries using A* pathfinding, distance-based task allocation, collision avoidance, and failure recovery.

## Project Overview

The system models a warehouse as a **25 × 25 grid** containing static obstacles, package pickup locations, and delivery locations.

A central coordinator assigns packages to available robots. Each robot independently plans and follows a path using A* search with Manhattan distance as its heuristic. Robots check the positions of other active robots to avoid collisions and can recalculate their paths when the next cell is occupied.

When a robot fails, the system makes its unfinished package available for recovery and reassignment to another active robot.

## Features

- Multi-agent warehouse simulation with five robot agents
- Grid-based environment with static obstacles
- Management of ten packages with pickup and delivery locations
- A* pathfinding using Manhattan distance
- Distance-based greedy task allocation
- Collision checking and dynamic path replanning
- Robot failure simulation
- Package recovery and task reassignment
- Interactive Pygame visualization and monitoring dashboard
- Live display of robot states, package states, task assignments, distance, failures, and other statistics
- Pause, resume, reset, and robot failure controls

## Project Configuration

| Component | Configuration |
|---|---|
| Warehouse grid | 25 × 25 |
| Robots | 5 |
| Packages | 10 |
| Maximum supported robot failures | 3 |
| Programming language | Python 3.10 |
| Visualization framework | Pygame 2.6.1 |
| Pathfinding algorithm | A* Search |
| Heuristic | Manhattan Distance |
| Development environment | VS Code and Conda |
| Operating system | Windows 11 |

## Technology Stack

- **Python:** Simulation logic, algorithms, and agent behaviour
- **Pygame:** Warehouse visualization, rendering, and keyboard controls
- **A* Search:** Robot pathfinding
- **Manhattan Distance:** Heuristic for grid-based navigation
- **Conda:** Python environment management
- **Git and GitHub:** Version control and source code hosting

## Project Structure

```text
Multi-Agent-Warehouse-Robot-Coordinator/
├── main.py
├── environment.py
├── robot.py
├── coordinator.py
├── recovery.py
├── README.md
└── .gitignore
```

- **main.py:** Initializes Pygame, creates the simulation objects, runs the main loop, handles keyboard input, and updates the visualization.
- **environment.py:** Defines the warehouse grid, obstacles, packages, coordinates, and environment-related visualization.
- **robot.py:** Implements robot behaviour, A* pathfinding, movement, collision checking, and path recalculation.
- **coordinator.py:** Assigns packages to available robots using distance-based selection.
- **recovery.py:** Handles robot failures, package recovery, task reassignment, and related dashboard functions.
- **README.md:** Documents the project, setup, features, and usage.

## How the System Works

1. The warehouse, robots, and packages are initialized.
2. The coordinator identifies available robots and unassigned packages.
3. Dropped packages requiring recovery receive priority over normal waiting packages.
4. The coordinator selects the closest available, non-failed robot using Manhattan distance.
5. The assigned robot uses A* to plan a path to the pickup location.
6. After pickup, the robot plans a path to the delivery location.
7. Before moving, the robot checks whether its next cell is occupied by another active robot.
8. If the next cell is blocked by another robot, the robot can recalculate its path.
9. If a robot fails, its unfinished package is made available for recovery and reassignment.
10. The process continues until packages are delivered or no further progress is possible.

## Algorithms

### A* Pathfinding

A* combines the cost already incurred with an estimate of the remaining cost:

`f(n) = g(n) + h(n)`

Where:

- `g(n)` is the actual path cost from the starting position to the current node.
- `h(n)` is the estimated cost from the current node to the goal.
- `f(n)` is the total estimated path cost.

### Manhattan Distance

The heuristic is:

`h(n) = |x1 - x2| + |y1 - y2|`

It is suitable for the simulation because robots move horizontally and vertically, without diagonal movement.

### Task Allocation

The coordinator uses a distance-based greedy strategy to select the closest available robot for a package. This approach is straightforward but does not guarantee globally optimal task scheduling.

### Collision Avoidance and Recovery

Robots check the occupancy of their next cell before moving. If another active robot occupies that cell, the robot can treat occupied positions as temporary obstacles during path recalculation.

The recovery mechanism handles failures before and after package pickup and allows unfinished tasks to be reassigned.

## Installation and Setup

### Prerequisites

- Python 3.10
- Conda or another Python environment manager
- Pygame 2.6.1

### 1. Clone the repository

```bash
git clone https://github.com/gayas-sheik/Multi-Agent-Warehouse-Robot-Coordinator.git
cd Multi-Agent-Warehouse-Robot-Coordinator
```

### 2. Create a Conda environment

```bash
conda create -n warehouse-ai python=3.10
conda activate warehouse-ai
```

If the environment already exists, activate it instead of creating it again.

### 3. Install Pygame

```bash
python -m pip install pygame==2.6.1
```

### 4. Run the simulation

```bash
python main.py
```

Run the command from the project root directory, where `main.py` is located.

## Keyboard Controls

| Key | Action |
|---|---|
| `1` | Simulate failure of Robot 1 |
| `2` | Simulate failure of Robot 2 |
| `3` | Simulate failure of Robot 3 |
| `4` | Simulate failure of Robot 4 |
| `5` | Simulate failure of Robot 5 |
| `SPACE` | Pause or resume the simulation |
| `R` | Reset the simulation |
| `ESC` | Exit the application |

The system supports up to three robot failures. Failed robots remain inactive and do not automatically return to operation.

## Testing

The project documentation records ten test cases covering:

1. Normal multi-agent operation
2. A* pathfinding and obstacle avoidance
3. Multi-agent collision avoidance
4. Robot failure before package pickup
5. Robot failure after package pickup
6. Package recovery and reassignment
7. Three robot failures
8. Pause and resume functionality
9. Reset functionality
10. End-to-end system execution

The documented test cases were marked as passed during the project's observed testing sessions.

## Limitations

- The project is a software simulation, not a deployment on physical warehouse robots.
- The warehouse uses a fixed-size grid.
- Task allocation is distance-based and greedy, rather than globally optimized.
- The system has a defined limit of three robot failures.
- Failed robots cannot be repaired or reintegrated automatically.
- Robot interaction is handled through shared simulation state; there is no direct robot-to-robot communication protocol.
- Real-world sensors, localization, and physical robot control are not implemented.

## Future Improvements

- More advanced global task scheduling
- Improved traffic management and deadlock handling
- Dynamic warehouse layouts and larger environments
- Robot repair and reintegration
- Physical sensor integration and localization
- Quantitative benchmarking of task completion time, path length, and coordination performance

## Project Scope

This project demonstrates classical AI concepts, including heuristic search, autonomous agents, task allocation, collision handling, and rule-based failure recovery. It does not use machine learning or deep learning.

## Author

**Gayas Sheik**

B.Tech Computer Science and Engineering  
Amrita Vishwa Vidyapeetham, Coimbatore

## License

No license has been specified for this project.
