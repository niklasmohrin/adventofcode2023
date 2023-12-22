#!/usr/bin/env python3

import sys
from collections import deque
from enum import Enum
from itertools import product
from pathlib import Path


filename = sys.argv[1] if len(sys.argv) > 1 else "input"
grid = (Path(__file__).parent / filename).read_text().splitlines()


class Direction(Enum):
    North = (0, -1)
    East = (1, 0)
    South = (0, 1)
    West = (-1, 0)

    def apply_to(self, position):
        return position[0] + self.value[0], position[1] + self.value[1]


def reachable_in_exactly(number_of_steps, starting_positions, blocked_positions):
    if number_of_steps == 0:
        return starting_positions
    return reachable_in_exactly(
        number_of_steps - 1,
        {d.apply_to(p) for p in starting_positions for d in Direction}
        - blocked_positions,
        blocked_positions,
    )


blocked_positions = set()
starting_positions = set()
for y, row in enumerate(grid):
    for x, val in enumerate(row):
        match val:
            case "S":
                starting_positions.add((x, y))
            case "#":
                blocked_positions.add((x, y))

height = len(grid)
width = len(grid[0])

for y in range(height):
    blocked_positions.add((-1, y))
    blocked_positions.add((width, y))
for x in range(width):
    blocked_positions.add((x, -1))
    blocked_positions.add((x, height))

print(len(reachable_in_exactly(64, starting_positions, blocked_positions)))

####

# Observations (mostly discarded ideas):
# - the edges of the map don't have any blocked positions
# - it's a grid, so it's bipartite
#   => can solve within each partition / only need to solve in partition corresponding to parity of iterations
# - with each iteration, the set of reached positions grows (strictly) monotonically
# - iteration count suggests that we cannot, even if each step is fast, do one step for each iteration
# - supposedly, in the end, there will be lots of maps with all cells filled and only some not completely filled
# - in the input, the row and column of the starting position does not contain any blocking positions
#   => the maximum extent of x and y is obvious
# - each reached point is described as a multiset of direction vectors
# - each reached point that is not on the same map-x-coordinate or map-y-coordinate as S can be assumed to be reached by the path that first walks to the corner of the start map and then two straight lines to the corner of the destination map
# - even better: each reached point can be assumed to be reached by the path that first goes to the map by using the free path on the middle cross (and maybe going to the corner of the map in the end)
#   => for each entry point into a map, we can calculate the minimum iterations to cover the full map
#   => and then, we should be able to calculate how many maps we need to go until the maps are not fully covered
#   => for those, we brute force?
#     => if we always enter in the corner, there are only four possible entries
#     => but we also enter delayed elsewhere, right?


def distances_in_bounded_grid(grid, start):
    dist = dict()
    dist[start] = 0
    queue = deque([start])
    while queue:
        u = queue.popleft()
        for direction in Direction:
            v = vx, vy = direction.apply_to(u)
            if (
                0 <= vy < len(grid)
                and 0 <= vx < len(grid[vy])
                and grid[vy][vx] != "#"
                and v not in dist
            ):
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist


def rotate_clockwise(grid):
    height = len(grid)
    width = len(grid[0])
    rotated = [[None] * height for _ in range(width)]
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            rotated[x][width - 1 - y] = val
    return rotated


def gauss_sum(k):
    return (k * (k + 1)) // 2


def infinite_reachable_in_exactly_with_assumptions(grid, start, number_of_steps):
    assert len(grid) == len(grid[0])
    n = len(grid)
    assert n % 2 == 1

    edge_of_grid = set(product([0, n - 1], range(n))) | set(
        product(range(n), [0, n - 1])
    )
    assert len(blocked_positions & edge_of_grid) == 0

    def for_north_and_first_quadrant(grid, start):
        distances_from_start = distances_in_bounded_grid(grid, start)
        d_start_top = distances_from_start[(start[0], 0)]
        d_start_top_right = distances_from_start[(n - 1, 0)]
        distances_from_bottom_edge = distances_in_bounded_grid(grid, (start[0], n - 1))
        distances_from_bottom_right = distances_in_bounded_grid(grid, (0, n - 1))
        total = 0
        for y in range(n):
            for x in range(n):
                if (x, y) not in distances_from_start:
                    continue
                # north

                # to reach the point (x, y) in a map k maps above the center map, we need to move
                # - from the start to the top (distances_from_start[(start[0], 0)])
                # - one step into the new map (1)
                # - k-1 full maps north ((k-1) * n)
                # - from there to (x, y) (distances_from_bottom_edge[point])
                # and this all needs to be doable in number_of_steps, so
                #
                #     distances_from_start[(start[0], 0)] + 1 + (k-1) * height + distances_from_bottom_edge[point] <= number_of_steps
                #     (k-1) * n <= number_of_steps - distances_from_start[(start[0], 0)] - 1 - distances_from_bottom_edge[point]

                # how many k > 0 exist such that (x, y) is reachable in the map k maps above the start in exactly number_of_steps steps
                # => any k' <= k with same parity suffices, that is, rounded up half of the k' <= k? where k is the maximum possible one

                d_to_edge = d_start_top
                d_from_edge = distances_from_bottom_edge[(x, y)]
                # need max k with (k-1) * n <= number_of_steps - d_to_edge - d_from_edge - 1 and same parity
                # either max k in general, or k decreased by one for parity
                middle_bound = number_of_steps - d_to_edge - d_from_edge - 1
                if middle_bound >= 0:
                    k = (middle_bound // n) + 1
                    if ((k - 1) * n) % 2 != middle_bound % 2:
                        k -= 1
                    assert k >= 0
                    k = (k + 1) // 2
                    total += k

                # quadrant
                d_to_edge = d_start_top_right
                d_from_edge = distances_from_bottom_right[(x, y)]
                # in first column next to start, we have the same situation as with north, but with slightly longer path
                middle_bound = number_of_steps - d_to_edge - d_from_edge - 2
                if middle_bound >= 0:
                    k = (middle_bound // n) + 1
                    if ((k - 1) * n) % 2 != middle_bound % 2:
                        k -= 1
                    assert k >= 0
                    # now, the reachable maps look like a staircase, so in total we have the sum
                    # sum roundup(i / 2) for i <= k
                    # sum (i + 1) // 2 for i <= k
                    # sum i/2 for even i <= k + sum (i + 1)/2 for odd i <= k
                    # sum i/2 for even i <= k + sum i / 2 for even i <= k + 1
                    # sum i for i <= k // 2 + sum i for i <= (k + 1) // 2
                    total += gauss_sum(k // 2) + gauss_sum((k + 1) // 2)
        return total

    distances_from_start = distances_in_bounded_grid(grid, start)
    in_center_map = sum(
        1
        for y in range(n)
        for x in range(n)
        if (x, y) in distances_from_start
        and distances_from_start[(x, y)] <= number_of_steps
        and distances_from_start[(x, y)] % 2 == number_of_steps % 2
    )

    total = in_center_map
    for _ in range(4):
        total += for_north_and_first_quadrant(grid, start)
        grid = rotate_clockwise(grid)
        # start is in the middle, no need to rotate
    return total


print(
    infinite_reachable_in_exactly_with_assumptions(
        grid, next(iter(starting_positions)), 26501365
    )
)
