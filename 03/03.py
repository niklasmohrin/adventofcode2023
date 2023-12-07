#!/usr/bin/env python3


from collections import defaultdict
from pathlib import Path
from string import digits
from math import inf

input_path = Path(__file__).parent / "input"
input_data = input_path.read_text().splitlines()

in_range = lambda x, y: 0 <= y < len(input_data) and 0 <= x < len(input_data[y])
is_part = (
    lambda x, y: in_range(x, y)
    and input_data[y][x] not in digits
    and input_data[y][x] != "."
)


def adj_cells(y, x_start, x_end):
    yield x_start - 1, y
    yield x_end, y
    for x in range(x_start - 1, x_end + 1):
        yield x, y - 1
        yield x, y + 1


def is_adj_to_any_part(y, x_start, x_end):
    return any(is_part(x, y) for x, y in adj_cells(y, x_start, x_end))


total1 = 0

nums_adj_to_gear = defaultdict(list)

for y in range(len(input_data)):
    digit_start = None
    for x in range(len(input_data[y])):
        if input_data[y][x] in digits and digit_start is None:
            digit_start = x
        elif input_data[y][x] not in digits and digit_start is not None:
            if is_adj_to_any_part(y, digit_start, x):
                total1 += int(input_data[y][digit_start:x])
            for gx, gy in adj_cells(y, digit_start, x):
                if in_range(gx, gy) and input_data[gy][gx] == "*":
                    nums_adj_to_gear[(gx, gy)].append(int(input_data[y][digit_start:x]))
            digit_start = None
    x = len(input_data[y])
    if digit_start is not None and is_adj_to_any_part(y, digit_start, x):
        total1 += int(input_data[y][digit_start:x])
        for gx, gy in adj_cells(y, digit_start, x):
            if in_range(gx, gy) and input_data[gy][gx] == "*":
                nums_adj_to_gear[(gx, gy)].append(int(input_data[y][digit_start:x]))

print(total1)

total2 = 0
for adj_nums in nums_adj_to_gear.values():
    if len(adj_nums) == 2:
        total2 += adj_nums[0] * adj_nums[1]
print(total2)
