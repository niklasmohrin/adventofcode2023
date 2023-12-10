#!/usr/bin/env python3

import sys
from collections import defaultdict
from pathlib import Path

import more_itertools


filename = sys.argv[1] if len(sys.argv) > 1 else "input"
data = (Path(__file__).parent / filename).read_text().splitlines()

north = (0, -1)
south = (0, 1)
west = (-1, 0)
east = (1, 0)

directions = (north, west, south, east)

pipe_kinds = {
    "|": (north, south),
    "-": (west, east),
    "L": (north, east),
    "J": (north, west),
    "7": (west, south),
    "F": (east, south),
}

g = defaultdict(set)
start = None
for y, row in enumerate(data):
    for x, c in enumerate(row):
        if c == "S":
            assert start is None
            start = x, y
        if c in pipe_kinds:
            for dx, dy in pipe_kinds[c]:
                g[(x, y)].add((x + dx, y + dy))
                g[(x + dx, y + dy)].add((x, y))

assert start is not None
assert len(g[start]) == 2

prev = start
cur = next(iter(g[start]))
loop_vertices = [start]

while cur != start:
    loop_vertices.append(cur)
    for dx, dy in pipe_kinds[data[cur[1]][cur[0]]]:
        n = cur[0] + dx, cur[1] + dy
        if n != prev:
            prev = cur
            cur = n
            break
    else:
        assert False, "Loop pipe was only connected on one side?"

print(len(loop_vertices) // 2)

left_of_loop_vertices = set()
loop_vertices_set = set(loop_vertices)
for a, b in more_itertools.pairwise(loop_vertices):
    direction = b[0] - a[0], b[1] - a[1]
    left_direction = directions[(directions.index(direction) + 1) % len(directions)]
    for lx, ly in (a, b):
        nx = lx + left_direction[0]
        ny = ly + left_direction[1]
        if (
            0 <= ny < len(data)
            and 0 <= nx < len(data[ny])
            and (nx, ny) not in loop_vertices_set
        ):
            left_of_loop_vertices.add((nx, ny))

comp_index_of = dict()
comp_count = 0
for sy in range(len(data)):
    for sx in range(len(data[sy])):
        if (sx, sy) not in loop_vertices_set and (sx, sy) not in comp_index_of:
            comp_index_of[(sx, sy)] = comp_count
            comp_count += 1
            stack = [(sx, sy)]
            while stack:
                x, y = stack.pop()
                for direction in directions:
                    nx = x + direction[0]
                    ny = y + direction[1]
                    if (
                        0 <= ny < len(data)
                        and 0 <= nx < len(data[ny])
                        and (nx, ny) not in loop_vertices_set
                        and (nx, ny) not in comp_index_of
                    ):
                        comp_index_of[(nx, ny)] = comp_index_of[(x, y)]
                        stack.append((nx, ny))

comps = [[] for _ in range(comp_count)]
for v, comp_index in comp_index_of.items():
    comps[comp_index].append(v)

# Holds in all examples; otherwise, find another outside vertex
assert (0, 0) not in loop_vertices_set

left_of_loop_comp_indices = [
    i for i, comp in enumerate(comps) if any(v in left_of_loop_vertices for v in comp)
]
left_of_loop_count = sum(len(comps[i]) for i in left_of_loop_comp_indices)
inside_count = (
    left_of_loop_count
    if comp_index_of[(0, 0)] not in left_of_loop_comp_indices
    else sum(map(len, data)) - left_of_loop_count - len(loop_vertices)
)

print(inside_count)

# for y in range(len(data)):
#     for x in range(len(data[y])):
#         if (x, y) in loop_vertices_set:
#             print("#", end="")
#         elif (x, y) in left_of_loop_vertices:
#             print("L", end="")
#         elif comp_index_of[(x, y)] in left_of_loop_comp_indices:
#             print("l", end="")
#         else:
#             print(".", end="")
#     print()
