#!/usr/bin/env python3

import sys
from pathlib import Path


EXPANSIONS = [2, 1000000]


filename = sys.argv[1] if len(sys.argv) > 1 else "input"
data = (Path(__file__).parent / filename).read_text().splitlines()

vertices = [
    (x, y) for y in range(len(data)) for x in range(len(data[y])) if data[y][x] == "#"
]
empty_rows = {y for y in range(len(data)) if "#" not in data[y]}
empty_cols = {
    x
    for x in range(len(data[0]))
    if not any(data[y][x] == "#" for y in range(len(data)))
}

for expansion in EXPANSIONS:
    total = sum(
        abs(ux - vx)
        + abs(uy - vy)
        + (expansion - 1) * len(set(range(min(uy, vy), max(uy, vy))) & empty_rows)
        + (expansion - 1) * len(set(range(min(ux, vx), max(ux, vx))) & empty_cols)
        for i, (ux, uy) in enumerate(vertices)
        for vx, vy in vertices[:i]
    )
    print(total)
