#!/usr/bin/env python3

import itertools
import sys
from functools import cache
from pathlib import Path


filename = sys.argv[1] if len(sys.argv) > 1 else "input"
data = (Path(__file__).parent / filename).read_text().splitlines()


@cache
def possibilities(positions, lengths):
    if len(positions) == 0:
        return len(lengths) == 0
    if len(lengths) == 0:
        return "#" not in positions

    l1 = lengths[0]
    return sum(
        possibilities(positions[i + l1 + 1 :], lengths[1:])
        for i in range(len(positions) - l1)
        if "#" not in positions[:i]
        and "." not in positions[i : i + l1]
        and "#" != positions[i + l1]
    )


total1 = total2 = 0

for line in data:
    positions, lengths_str = line.split(" ", 1)
    lengths = list(map(int, lengths_str.split(",")))

    total1 += possibilities(positions + ".", tuple(lengths))

    positions = "?".join(itertools.repeat(positions, 5))
    lengths *= 5
    total2 += possibilities(positions + ".", tuple(lengths))

print(total1)
print(total2)
