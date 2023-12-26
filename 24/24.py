#!/usr/bin/env python3

import itertools
import sys
from dataclasses import dataclass
from fractions import Fraction
from numbers import Real
from pathlib import Path
from typing import Self

import sympy


@dataclass(frozen=True)
class Vec:
    dimensions: tuple[Real, ...]

    @classmethod
    def from_str(cls, s) -> Self:
        return cls(dimensions=tuple(Fraction(n) for n in s.split(", ")))

    def __add__(self, other) -> Self:
        return type(self)(
            dimensions=tuple(
                x1 + x2
                for x1, x2 in zip(self.dimensions, other.dimensions, strict=True)
            )
        )

    def __mul__(self, factor) -> Self:
        return type(self)(dimensions=tuple(x * factor for x in self.dimensions))

    @property
    def x(self):
        return self.dimensions[0]

    @property
    def y(self):
        return self.dimensions[1]

    @property
    def z(self):
        return self.dimensions[2]


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "input"
    data = (Path(__file__).parent / filename).read_text().splitlines()
    lines = [tuple(Vec.from_str(v) for v in li.split(" @ ")) for li in data]

    count = 0

    for (x1, v1), (x2, v2) in itertools.combinations(lines, 2):
        assert 0 not in [*v1.dimensions, *v2.dimensions]

        denom = v2.y - v1.y * v2.x / v1.x
        if denom != 0:
            t2 = (x1.y + (x2.x - x1.x) * v1.y / v1.x - x2.y) / denom
            t1 = ((x2.x - x1.x) + t2 * v2.x) / v1.x
            if t1 >= 0 and t2 >= 0:
                c = x1 + v1 * t1
                if all(200000000000000 <= x <= 400000000000000 for x in [c.x, c.y]):
                    count += 1
    print(count)

    USED_LINES = 3  # suffices to narrow it down to a single solution

    system = []
    p = sympy.symbols("px py pz", domain=sympy.S.Integers)
    v = sympy.symbols("vx vy vz", domain=sympy.S.Integers)

    for i, (hp, hv) in enumerate(lines[:USED_LINES]):
        ti = sympy.Symbol(f"t{i:03}", nonnegative=True)

        for p1, v1, p2, v2 in zip(hp.dimensions, hv.dimensions, p, v, strict=True):
            system.append(sympy.Eq(int(p1) + ti * int(v1), p2 + ti * v2))

    solution = sympy.solve(system, dict=True)
    assert len(solution) == 1
    print(sum(solution[0][dim] for dim in p))


if __name__ == "__main__":
    main()
