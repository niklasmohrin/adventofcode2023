#!/usr/bin/env python3

import sys
from pathlib import Path

import networkx as nx


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "input"
    data = (Path(__file__).parent / filename).read_text().splitlines()

    g = nx.Graph()

    for line in data:
        a, bs = line.split(": ", 1)
        for b in bs.split():
            g.add_edge(a, b)

    cut_value, partitions = nx.stoer_wagner(g)
    assert cut_value <= 3
    assert len(partitions) == 2
    print(len(partitions[0]) * len(partitions[1]))


if __name__ == "__main__":
    main()
