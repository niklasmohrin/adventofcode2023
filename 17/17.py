#!/usr/bin/env python3

import heapq
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


filename = sys.argv[1] if len(sys.argv) > 1 else "input"
data = (Path(__file__).parent / filename).read_text().splitlines()
grid = [list(map(int, line)) for line in data]


class Direction(Enum):
    North = (0, -1)
    East = (1, 0)
    South = (0, 1)
    West = (-1, 0)


@dataclass(frozen=True, order=True)
class Node:
    x: int
    y: int
    is_left_horizontally: bool


def min_heat_loss_for_forward_range(min_forward, max_forward):
    dist = {Node(0, 0, False): 0, Node(0, 0, True): 0}
    pq = [(v, k) for k, v in dist.items()]
    heapq.heapify(pq)

    while pq:
        dist_then, node = heapq.heappop(pq)
        if dist_then > dist[node]:
            continue
        directions = (
            [Direction.West, Direction.East]
            if node.is_left_horizontally
            else [Direction.North, Direction.South]
        )
        for dir in directions:
            dx, dy = dir.value
            for i in range(min_forward, max_forward + 1):
                nx = node.x + i * dx
                ny = node.y + i * dy
                if 0 <= ny < len(grid) and 0 <= nx < len(grid[ny]):
                    new_node = Node(nx, ny, not node.is_left_horizontally)
                    weight_along_edge = (
                        sum(grid[node.y][x] for x in range(nx, node.x, -dx))
                        if dx != 0
                        else sum(grid[y][node.x] for y in range(ny, node.y, -dy))
                    )
                    if (
                        new_node not in dist
                        or dist[node] + weight_along_edge < dist[new_node]
                    ):
                        dist[new_node] = dist[node] + weight_along_edge
                        heapq.heappush(pq, (dist[new_node], new_node))

    return min(
        dist[Node(len(grid[-1]) - 1, len(grid) - 1, False)],
        dist[Node(len(grid[-1]) - 1, len(grid) - 1, True)],
    )


print(min_heat_loss_for_forward_range(1, 3))
print(min_heat_loss_for_forward_range(4, 10))
