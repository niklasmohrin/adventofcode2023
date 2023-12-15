#!/usr/bin/env python3

import itertools
import sys
from collections import Counter
from pathlib import Path


filename = sys.argv[1] if len(sys.argv) > 1 else "input"
grid = (Path(__file__).parent / filename).read_text().splitlines()


def load_of(moving_points, *, height):
    return sum(height - y for x, y in moving_points)


def move_north(solid_points, moving_points, *, height, width):
    new_moving_points = []

    for x in range(width):
        first = 0
        stacked_up = Counter()
        for y in range(height):
            if (x, y) in solid_points:
                first = y + 1
            elif (x, y) in moving_points:
                stacked_up[first] += 1

        for first, count in stacked_up.items():
            for i in range(count):
                new_moving_points.append((x, first + i))

    return frozenset(new_moving_points)


def rotate_clockwise(points, *, width):
    return frozenset((width - 1 - y, x) for x, y in points)


height = len(grid)
width = len(grid[0])
solid_points = frozenset(
    (x, y) for y, row in enumerate(grid) for x, c in enumerate(row) if c == "#"
)
moving_points = frozenset(
    (x, y) for y, row in enumerate(grid) for x, c in enumerate(row) if c == "O"
)

print(
    load_of(
        move_north(solid_points, moving_points, height=height, width=width),
        height=height,
    )
)


def spin_cycle(solid_points, moving_points, *, height, width):
    for _ in range(4):
        new_moving_points = move_north(
            solid_points, moving_points, height=height, width=width
        )

        height, width, solid_points, moving_points = (
            width,
            height,
            rotate_clockwise(solid_points, width=width),
            rotate_clockwise(new_moving_points, width=width),
        )

    return moving_points


iteration_of_state = dict()
state_of_iteration = []

for i in itertools.count():
    # print("=" * 20)
    # print(i)
    # print(load_of(height, width, solid_points, moving_points))
    # for y in range(height):
    #     for x in range(width):
    #         if (x, y) in solid_points:
    #             print("#", end="")
    #         elif (x, y) in moving_points:
    #             print("O", end="")
    #         else:
    #             print(".", end="")
    #     print()

    key = moving_points
    if key in iteration_of_state:
        cycle_start = iteration_of_state[key]
        cycle_length = i - cycle_start
        target = 1000000000
        equiv_target = cycle_start + ((target - cycle_start) % cycle_length)
        print(load_of(state_of_iteration[equiv_target], height=height))
        break
    iteration_of_state[key] = i
    state_of_iteration.append(key)
    moving_points = spin_cycle(solid_points, moving_points, height=height, width=width)
