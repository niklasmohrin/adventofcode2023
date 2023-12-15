#!/usr/bin/env python3

import sys
from dataclasses import dataclass, field
from pathlib import Path


filename = sys.argv[1] if len(sys.argv) > 1 else "input"
data = (Path(__file__).parent / filename).read_text().removesuffix("\n")


def string_hash(s):
    h = 0
    for c in s:
        h += ord(c)
        h *= 17
        h %= 256
    return h


print(sum(map(string_hash, data.split(","))))


@dataclass
class Box:
    box_id: int
    time = 0
    lenses: dict = field(default_factory=dict)

    def remove_lens(self, label):
        if label in self.lenses:
            del self.lenses[label]

    def insert_or_assign(self, label, focal_length):
        if label in self.lenses:
            insertion_time = self.lenses[label][0]
        else:
            insertion_time = self.time
            self.time += 1
        self.lenses[label] = (insertion_time, focal_length)

    def total_focusing_power(self):
        return sum(
            (1 + self.box_id) * rank * focal_length
            for rank, (_label, (_insertion_time, focal_length)) in enumerate(
                sorted(self.lenses.items(), key=lambda t: t[1][0]), start=1
            )
        )


boxes = list(map(Box, range(256)))
for instruction in data.split(","):
    if "=" in instruction:
        label, focal_length_str = instruction.split("=", 1)
        boxes[string_hash(label)].insert_or_assign(label, int(focal_length_str))
    else:
        label = instruction.removesuffix("-")
        boxes[string_hash(label)].remove_lens(label)

print(sum(map(Box.total_focusing_power, boxes)))
