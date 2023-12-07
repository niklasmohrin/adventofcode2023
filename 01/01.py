#!/usr/bin/env python3

from collections import defaultdict
from pathlib import Path
from string import digits
from math import inf

input_path = Path(__file__).parent / "input"

num_strs = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
]

total1 = total2 = 0
for line in input_path.read_text().splitlines():
    ds = [int(c) for c in line if c in digits]
    total1 += 10 * ds[0] + ds[-1]

    occs = defaultdict(list)
    for i in range(len(line)):
        if line[i] in digits:
            occs[int(line[i])].append(i)
        for num, s in enumerate(num_strs):
            if line[i:i+len(s)] == s:
                occs[num].append(i)
    first = min(range(10), key=lambda d: occs[d][0] if len(occs[d]) > 0 else inf)
    last = max(range(10), key=lambda d: occs[d][-1] if len(occs[d]) > 0 else -inf)
    total2 += 10 * first + last

print(total1)
print(total2)
