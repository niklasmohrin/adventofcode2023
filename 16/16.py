#!/usr/bin/env python3

import sys
from pathlib import Path


filename = sys.argv[1] if len(sys.argv) > 1 else "input"
grid = (Path(__file__).parent / filename).read_text().splitlines()


class Direction:
    north = (0, -1)
    south = (0, 1)
    west = (-1, 0)
    east = (1, 0)


def simulate(start):
    stack = [start]
    seen = set()

    def push(x, y, d):
        if (x, y, d) not in seen:
            stack.append((x, y, d))
            seen.add((x, y, d))

    while stack:
        x, y, dir = stack.pop()
        nx, ny = x + dir[0], y + dir[1]
        if not (0 <= ny < len(grid) and 0 <= nx < len(grid[ny])):
            continue
        match (dir, grid[ny][nx]):
            case (_, "."):
                push(nx, ny, dir)
            case (Direction.north, "\\"):
                push(nx, ny, Direction.west)
            case (Direction.west, "\\"):
                push(nx, ny, Direction.north)
            case (Direction.south, "\\"):
                push(nx, ny, Direction.east)
            case (Direction.east, "\\"):
                push(nx, ny, Direction.south)
            case (Direction.north, "/"):
                push(nx, ny, Direction.east)
            case (Direction.west, "/"):
                push(nx, ny, Direction.south)
            case (Direction.south, "/"):
                push(nx, ny, Direction.west)
            case (Direction.east, "/"):
                push(nx, ny, Direction.north)
            case (Direction.north | Direction.south, "|"):
                push(nx, ny, dir)
            case (Direction.west | Direction.east, "-"):
                push(nx, ny, dir)
            case (Direction.north | Direction.south, "-"):
                push(nx, ny, Direction.west)
                push(nx, ny, Direction.east)
            case (Direction.west | Direction.east, "|"):
                push(nx, ny, Direction.north)
                push(nx, ny, Direction.south)

    return len({(x, y) for x, y, _ in seen})


print(simulate((-1, 0, Direction.east)))

height = len(grid)
width = len(grid[0])
best = 0
for y in range(height):
    best = max(
        best,
        simulate((-1, y, Direction.east)),
        simulate((width, y, Direction.west)),
    )
for x in range(len(grid[0])):
    best = max(
        best,
        simulate((x, -1, Direction.south)),
        simulate((x, height, Direction.north)),
    )
print(best)
