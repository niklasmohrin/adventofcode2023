#!/usr/bin/env python3

import itertools
import sys
from collections import defaultdict
from math import lcm

data = sys.stdin.readlines()

directions = data[0].strip()

g = defaultdict(list)
for line in data[2:]:
    lhs, rhs = line.split(" = ", 1)
    r1, r2 = rhs.strip("\n()").split(", ")
    g[lhs].append(r1)
    g[lhs].append(r2)


def traverse_naive(starts, is_end):
    cur = starts
    for i, direction in enumerate(itertools.cycle(directions)):
        if all(map(is_end, cur)):
            print(i)
            return
        cur = [g[v][direction == "R"] for v in cur]


def find_cycle_length(start, is_end):
    start = (start, 0)

    succ = lambda vi: (
        g[vi[0]][directions[vi[1]] == "R"],
        (vi[1] + 1) % len(directions),
    )

    prev = start
    disc = {start: 0}
    end_at = None
    while (s := succ(prev)) not in disc:
        disc[s] = disc[prev] + 1
        if is_end(prev[0]):
            assert end_at is None
            end_at = disc[prev]
        prev = s
    cycle_start = disc[succ(prev)]
    assert cycle_start <= end_at
    assert end_at == len(disc) - cycle_start
    return len(disc) - cycle_start


def traverse_with_assumptions(starts, is_end):
    # Observations:
    # - Each start goes into a cycle after < 10 steps.
    # - In each cycle, there is exactly one end.
    # - This end is exactly where the start would be, if the cycle would come back to it.
    # - Therefore, it takes one full cycle length from the start to get to this end node.
    # - The end is reached after any positive amount of full cycles.
    # The first time everyone is on an end is the lowest common multiple of the cycle lengths for each of the starts.
    print(lcm(*(find_cycle_length(v, is_end) for v in starts)))


traverse_naive(["AAA"], lambda v: v == "ZZZ")
traverse_with_assumptions(
    [v for v in g.keys() if v.endswith("A")], lambda v: v.endswith("Z")
)
