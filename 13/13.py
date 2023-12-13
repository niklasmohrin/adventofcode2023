#!/usr/bin/env python3

import sys
from collections import defaultdict
from functools import reduce
from pathlib import Path


filename = sys.argv[1] if len(sys.argv) > 1 else "input"
grids = (Path(__file__).parent / filename).read_text().split("\n\n")


def transpose(matrix):
    transposed = [[None] * len(matrix) for _ in range(len(matrix[0]))]

    for y, row in enumerate(matrix):
        for x, val in enumerate(row):
            transposed[x][y] = val

    return transposed


def is_reflection(s, i):
    length = min(i, len(s) - i)
    return s[i - length : i] == s[i : i + length][::-1]


def col_reflection_indices(grid):
    row_reflections = (
        {i for i in range(len(row)) if is_reflection(row, i)} for row in grid
    )
    return reduce(set.intersection, row_reflections)


def grid_reflection_scores(grid):
    return (
        sum(col_reflection_indices(grid))
        + sum(col_reflection_indices(transpose(grid))) * 100
    )


def reflection_errors(s, i):
    length = min(i, len(s) - i)
    for dist in range(length):
        if s[i - 1 - dist] != s[i + dist]:
            yield i - 1 - dist, i + dist


def single_change_col_reflection_indices(grid):
    for col_index in range(len(grid[0])):
        working_row_count = 0
        fixes_in_their_row = []
        for y, row in enumerate(grid):
            match list(reflection_errors(row, col_index)):
                case []:
                    working_row_count += 1
                case [single_error_xs]:
                    for single_error_x in single_error_xs:
                        fixes_in_their_row.append((single_error_x, y))
        if working_row_count + 1 == len(grid):
            assert len(fixes_in_their_row) == 2
            for change in fixes_in_their_row:
                yield change, col_index


def single_change_grid_reflection_scores(grid):
    scores_of_change = defaultdict(list)
    for (x, y), col_index in single_change_col_reflection_indices(grid):
        scores_of_change[(x, y)].append(col_index)
    for (y, x), row_index in single_change_col_reflection_indices(transpose(grid)):
        scores_of_change[(x, y)].append(100 * row_index)

    # Note: This is not really needed, because there aren't any inputs where a change
    #       would result in more than one reflection.
    changes_with_single_reflection = {
        change: scores[0]
        for change, scores in scores_of_change.items()
        if len(scores) == 1
    }
    assert len(changes_with_single_reflection) <= 2
    assert len(set(changes_with_single_reflection.values())) == 1
    return next(iter(changes_with_single_reflection.values()))


total1 = total2 = 0

for grid_str in grids:
    grid = grid_str.splitlines()
    total1 += grid_reflection_scores(grid)
    total2 += single_change_grid_reflection_scores(grid)

print(total1)
print(total2)
