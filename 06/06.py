#!/usr/bin/env python3

from more_itertools import ilen
from functools import reduce
import operator


def possibilities(time, record_distance):
    return ilen(
        filter(
            lambda d: d > record_distance,
            map(lambda t: t * (time - t), range(time + 1)),
        )
    )


times_str = input().removeprefix("Time:").strip()
record_distances_str = input().removeprefix("Distance:").strip()

times1 = list(map(int, times_str.split()))
record_distances1 = list(map(int, record_distances_str.split()))
total1 = reduce(
    operator.mul, (possibilities(t, d) for t, d in zip(times1, record_distances1)), 1
)
print(total1)

time2 = int(times_str.replace(" ", ""))
record_distance2 = int(record_distances_str.replace(" ", ""))
print(possibilities(time2, record_distance2))
