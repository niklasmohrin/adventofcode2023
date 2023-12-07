#!/usr/bin/env python3

import sys
from collections import Counter

cards = sys.stdin.read().strip().splitlines()

total1 = 0
card_counts = Counter(range(len(cards)))

for i, card in enumerate(cards):
    _, numbers = card.split(": ", 1)
    winning_numbers_str, played_numbers_str = numbers.split(" | ")
    winning_numbers = list(map(int, winning_numbers_str.strip().split()))
    played_numbers = list(map(int, played_numbers_str.strip().split()))
    matches = len(set(winning_numbers) & set(played_numbers))

    if matches > 0:
        total1 += 1 << (matches - 1)

    for j in range(i + 1, min(i + 1 + matches, len(cards))):
        card_counts[j] += card_counts[i]
print(total1)
print(sum(card_counts.values()))
