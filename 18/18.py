#!/usr/bin/env python3

import itertools
import operator
import sys
from collections import Counter
from enum import Enum
from pathlib import Path


filename = sys.argv[1] if len(sys.argv) > 1 else "input"
data = (Path(__file__).parent / filename).read_text().splitlines()


class Direction(Enum):
    North = (0, -1)
    East = (1, 0)
    South = (0, 1)
    West = (-1, 0)


def find_area(vertices):
    get_x = operator.itemgetter(0)
    get_y = operator.itemgetter(1)
    toggle_xs = []
    area = prev_size = prev_y = 0
    for y, new_points in itertools.groupby(sorted(vertices, key=get_y), get_y):
        new_xs = map(get_x, new_points)
        new_toggle_xs = [
            x
            for x, count in Counter(itertools.chain(toggle_xs, new_xs)).items()
            if count % 2 == 1
        ]
        assert len(new_toggle_xs) % 2 == 0

        prev_active = next_active = False
        prev_events = ((x, False) for x in toggle_xs)
        next_events = ((x, True) for x in new_toggle_xs)
        next_size = both_size = 0
        for x, is_next in sorted(itertools.chain(prev_events, next_events)):
            both_active_before = prev_active and next_active
            if is_next:
                next_active = not next_active
                if next_active:
                    next_start = x
                else:
                    next_size += x - next_start + 1
            else:
                prev_active = not prev_active
            both_active_after = prev_active and next_active
            if both_active_before != both_active_after:
                if both_active_after:
                    both_start = x
                else:
                    both_size += x - both_start + 1
        area += (y - prev_y + 1) * prev_size - both_size
        prev_size, prev_y, toggle_xs = next_size, y, new_toggle_xs
    assert len(toggle_xs) == 0
    return area


for part in (1, 2):
    boundary = [(0, 0)]

    for line in data:
        direction_str, distance_str, color = line.split(" ")
        match part:
            case 1:
                distance = int(distance_str)
            case 2:
                color = color.removeprefix("(#").removesuffix(")")
                direction_str = "RDLU"[int(color[5])]
                distance = int(color[:5], 16)

        direction = {
            "U": Direction.North,
            "R": Direction.East,
            "D": Direction.South,
            "L": Direction.West,
        }[direction_str]

        boundary.append(
            (
                boundary[-1][0] + distance * direction.value[0],
                boundary[-1][1] + distance * direction.value[1],
            )
        )

    print(find_area(boundary[:-1]))
