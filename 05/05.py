#!/usr/bin/env python3

import sys
from typing import Self, Iterable
from dataclasses import dataclass


@dataclass(order=True, frozen=True, slots=True)
class Interval:
    start: int
    end: int

    def intersection(self, other: Self) -> Self:
        return type(self)(max(self.start, other.start), min(self.end, other.end))

    def difference(self, other: Self):
        if self.intersection(other).is_empty():
            yield self
            return
        if other.start > self.start:
            yield Interval(self.start, min(self.end, other.start))
        if other.end < self.end:
            yield Interval(max(self.start, other.end), self.end)

    def is_empty(self) -> bool:
        return self.start >= self.end

    def shift(self, offset: int) -> Self:
        return type(self)(self.start + offset, self.end + offset)


class IntervalSet:
    intervals: set[Interval]

    def __init__(self, initial: Iterable[Interval] = list()) -> None:
        self.intervals = set()
        for interval in initial:
            self.add(interval)

    def rebuild(self):
        events = []
        for interval in self.intervals:
            events.append((interval.start, False))
            events.append((interval.end, True))
        self.intervals.clear()

        active = start = 0
        for time, is_end in events:
            if not is_end:
                active += 1
                if active == 1:
                    start = time
            else:
                active -= 1
                if active == 0:
                    self.intervals.add(Interval(start, time))

    def add(self, interval: Interval):
        if not interval.is_empty():
            self.intervals.add(interval)

    def remove(self, interval: Interval):
        new_intervals = set()
        for old_interval in self.intervals:
            for new_interval in old_interval.difference(interval):
                new_intervals.add(new_interval)
        self.intervals = new_intervals

    def extract(self, interval: Interval):
        extracted = set(
            i.intersection(interval)
            for i in self.intervals
            if not i.intersection(interval).is_empty()
        )
        self.remove(interval)
        return extracted

    def apply_shifts(self, shifts: Iterable[tuple[Interval, int]]):
        to_add = list()
        for source, offset in shifts:
            extracted = self.extract(source)
            for interval in extracted:
                to_add.append(interval.shift(offset))
        for interval in to_add:
            self.add(interval)
        self.rebuild()

    def min(self) -> int:
        return min(i.start for i in self.intervals)


input_lines = sys.stdin.readlines()

_, seed_list_str = input_lines[0].strip().split("seeds: ", 1)

# part 1
points = list(map(int, seed_list_str.split()))

# part 2
current_intervals = IntervalSet(
    Interval(points[i], points[i] + points[i + 1]) for i in range(0, len(points), 2)
)

line_index = 1

while line_index < len(input_lines):
    assert input_lines[line_index].strip() == ""

    line_index += 2
    new_points = points.copy()
    shifts = []
    while line_index < len(input_lines) and input_lines[line_index].strip() != "":
        dst_range_start, src_range_start, range_len = map(
            int, input_lines[line_index].strip().split()
        )

        for i, value in enumerate(points):
            if src_range_start <= value < src_range_start + range_len:
                new_points[i] = dst_range_start + value - src_range_start
        shifts.append(
            (
                Interval(src_range_start, src_range_start + range_len),
                dst_range_start - src_range_start,
            )
        )

        line_index += 1
    points = new_points
    current_intervals.apply_shifts(shifts)

print(min(points))
print(current_intervals.min())
