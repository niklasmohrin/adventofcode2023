#!/usr/bin/env python3

import sys
from pathlib import Path

import more_itertools

filename = sys.argv[1] if len(sys.argv) > 1 else "input"
data = (Path(__file__).parent / filename).read_text().splitlines()

difference_array = lambda arr: [b - a for a, b in more_itertools.pairwise(arr)]


def predict_value(arr):
    if set(arr) == {0}:
        return 0
    return arr[-1] + predict_value(difference_array(arr))


predicted_values = map(
    lambda line: predict_value(list(map(int, line.strip().split()))), data
)
print(sum(predicted_values))

predicted_values_backwards = map(
    lambda line: predict_value(list(map(int, reversed(line.strip().split())))), data
)
print(sum(predicted_values_backwards))
