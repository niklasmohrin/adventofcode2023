#!/usr/bin/env python3

import sys
from dataclasses import dataclass
from enum import Enum
from itertools import product
from pathlib import Path


filename = sys.argv[1] if len(sys.argv) > 1 else "input"
data = (Path(__file__).parent / filename).read_text().splitlines()


class Direction(Enum):
    North = (0, -1)
    East = (1, 0)
    South = (0, 1)
    West = (-1, 0)

    def apply_to(self, position):
        return position[0] + self.value[0], position[1] + self.value[1]


@dataclass(frozen=True)
class Brick:
    index: int
    dimensions: list[tuple[int, int]]

    @property
    def xs(self):
        return self.dimensions[0]

    @property
    def ys(self):
        return self.dimensions[1]

    @property
    def zs(self):
        return self.dimensions[2]

    def move(self, delta):
        return Brick(
            self.index,
            [
                (start_x + dx, end_x + dx)
                for (start_x, end_x), dx in zip(self.dimensions, delta)
            ],
        )

    def iter_volume(self):
        return product(*(range(start, end + 1) for start, end in self.dimensions))


max_xy = max_z = 0

bricks = []

for i, line in enumerate(data):
    start, end = line.strip().split("~")
    start_coords = tuple(map(int, start.split(",")))
    end_coords = tuple(map(int, end.split(",")))
    brick = Brick(i, list(zip(start_coords, end_coords)))
    bricks.append(brick)

    for d1, d2 in brick.dimensions:
        assert 0 <= d1 <= d2

    max_xy = max(max_xy, brick.xs[1], brick.ys[1])
    max_z = max(max_z, brick.zs[1])


class BrickStack:
    def __init__(self, max_xy, max_z):
        self.max_xy = max_xy
        self.max_z = max_z
        self.stacks = [
            [[None for x in range(max_xy + 1)] for y in range(max_xy + 1)]
            for z in range(max_z + 1)
        ]
        self.bricks = []

    def push(self, brick):
        while self.would_fit(brick.move((0, 0, -1))):
            brick = brick.move((0, 0, -1))
        self.insert(brick)

    def would_fit(self, brick):
        return all(
            1 <= z <= self.max_z
            and 0 <= x <= self.max_xy
            and 0 <= y <= self.max_xy
            and self.stacks[z][y][x] is None
            for x, y, z in brick.iter_volume()
        )

    def insert(self, brick):
        self.bricks.append(brick)
        for x, y, z in brick.iter_volume():
            self.stacks[z][y][x] = brick.index

    def graph(self):
        g = {}
        for brick in self.bricks:
            g[brick.index] = set()
            for x, y, z in brick.iter_volume():
                below = self.stacks[z - 1][y][x]
                if below is not None and below != brick.index:
                    g[brick.index].add(below)
        return g


stack = BrickStack(max_xy, max_z)
for brick in sorted(bricks, key=lambda brick: brick.zs[0]):
    stack.push(brick)


g = stack.graph()
unsafe_to_remove = set()
for u, vs in g.items():
    if len(vs) == 1:
        unsafe_to_remove.add(next(iter(vs)))
print(len(bricks) - len(unsafe_to_remove))


def transpose_graph(g):
    gT = {u: set() for u in g}
    for u, vs in g.items():
        for v in vs:
            gT[v].add(u)
    return gT


def reachable_without_visiting(g, start, removed_vertex):
    st = [start]
    seen = {start}
    while st:
        u = st.pop()
        for v in g[u]:
            if v != removed_vertex and v not in seen:
                seen.add(v)
                st.append(v)
    assert all(v == removed_vertex or v in seen for u in seen for v in g[u])
    return seen


ground = len(g)
g[ground] = set()
for brick in bricks:
    if len(g[brick.index]) == 0:
        g[brick.index].add(ground)

gT = transpose_graph(g)


falling_bricks_when_removing = {
    brick.index: len(gT) - len(reachable_without_visiting(gT, ground, brick.index)) - 1
    for brick in bricks
}

print(sum(falling_bricks_when_removing.values()))
