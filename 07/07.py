#!/usr/bin/env python3

import sys
from itertools import repeat, chain
from collections import Counter

joker_mode = len(sys.argv) > 1 and sys.argv[1] == "--joker"


def card_key(card):
    if not joker_mode:
        return "23456789TJQKA".index(card)
    return "J23456789TQKA".index(card)


def hand_type(card):
    fps_in_order = [
        [1, 1, 1, 1, 1],
        [1, 1, 1, 2],
        [1, 2, 2],
        [1, 1, 3],
        [2, 3],
        [1, 4],
        [5],
    ]

    if not joker_mode:
        fp = sorted(Counter(card).values())
        return fps_in_order.index(fp)

    c = Counter(card)
    jokers = c.pop("J", 0)
    fp = sorted(c.values())

    pad = lambda fp: chain(repeat(0, 5 - len(fp)), fp)

    for i, target_fp in reversed(list(enumerate(fps_in_order))):
        remaining_jokers = jokers
        for card_count, target_count in zip(pad(fp), pad(target_fp)):
            if card_count > target_count:
                break
            remaining_jokers -= target_count - card_count
            if remaining_jokers < 0:
                break
        else:
            return i

    raise ValueError(f"No type reachable: {card}")


def hand_key(card):
    return (hand_type(card), tuple(map(card_key, card)))


cards_with_bids = sorted(
    ((t.split()[0], int(t.split()[1])) for t in sys.stdin.read().strip().splitlines()),
    key=lambda t: hand_key(t[0]),
)
total_winnings = sum(i * b for i, (_, b) in enumerate(cards_with_bids, start=1))
print(total_winnings)
