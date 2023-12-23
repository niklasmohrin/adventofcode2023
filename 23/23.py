#!/usr/bin/env python3

import sys
from enum import Enum
from functools import cache, partial
from math import inf
from pathlib import Path


sys.setrecursionlimit(10000)


class Direction(Enum):
    North = (0, -1)
    East = (1, 0)
    South = (0, 1)
    West = (-1, 0)

    def apply_to(self, position):
        return position[0] + self.value[0], position[1] + self.value[1]


def longest_path_length_dag(g, start, end):
    @cache
    def dfs(u, p):
        if u == end:
            return 0
        return 1 + max(map(partial(dfs, p=u), g[u] - {p}), default=-inf)

    return dfs(start, None)


def compress_graph(g):
    g = {u: {v: 1 for v in vs} for u, vs in g.items()}
    while True:
        candidates = (u for u, vs in g.items() if len(vs) == 2)
        try:
            u = next(candidates)
        except StopIteration:
            return g

        (v1, w1), (v2, w2) = g.pop(u).items()
        g[v1].pop(u)
        g[v2].pop(u)
        g[v1][v2] = g[v2][v1] = w1 + w2


def longest_path_length_undirected(g, start, end):
    cur_len = max_len = 0
    in_path = set()
    stack = [(True, start, 0)]
    while stack:
        entering, u, w = stack.pop()
        if entering:
            cur_len += w
            assert u not in in_path
            in_path.add(u)

            if u == end:
                max_len = max(max_len, cur_len)

            stack.append((False, u, w))
            stack.extend((True, v, w) for v, w in g[u].items() if v not in in_path)
        else:
            cur_len -= w
            in_path.remove(u)

    return max_len


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "input"
    grid = (Path(__file__).parent / filename).read_text().splitlines()

    height = len(grid)
    width = len(grid[0])

    start_x_candidates = {x for x, c in enumerate(grid[0]) if c != "#"}
    end_x_candidates = {x for x, c in enumerate(grid[-1]) if c != "#"}
    assert len(start_x_candidates) == len(end_x_candidates) == 1

    start = (next(iter(start_x_candidates)), 0)
    end = (next(iter(end_x_candidates)), height - 1)

    def make_graph(valid_directions):
        g = {start: set()}
        stack = [start]
        while stack:
            u = ux, uy = stack.pop()
            for direction in valid_directions[grid[uy][ux]]:
                v = vx, vy = direction.apply_to(u)
                if 0 <= vx < width and 0 <= vy < height and grid[vy][vx] != "#":
                    g[u].add(v)
                    if v not in g:
                        g[v] = set()
                        stack.append(v)
        return g

    g1 = make_graph(
        {
            ".": list(Direction),
            "^": [Direction.North],
            ">": [Direction.East],
            "v": [Direction.South],
            "<": [Direction.West],
        }
    )
    print(longest_path_length_dag(g1, start, end))

    g2 = make_graph({c: list(Direction) for c in ".^>v<"})
    print(longest_path_length_undirected(compress_graph(g2), start, end))


if __name__ == "__main__":
    main()
