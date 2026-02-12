from __future__ import annotations

from collections import Counter
from typing import List

from .rules import sort_key
from .tiles import WILDCARD


def choose_discard(hand: List[str]) -> str:
    """Simple heuristic AI: keep pairs, near-sequences, and wildcards."""
    counts = Counter(hand)

    def score(tile: str) -> float:
        if tile == WILDCARD:
            return 999.0

        s = 0.0
        c = counts[tile]
        if c >= 2:
            s += 3.0

        suit = tile[:3]
        rank = int(tile[3:])

        for d in (-2, -1, 1, 2):
            r2 = rank + d
            if 1 <= r2 <= 9:
                t2 = f"{suit}{r2}"
                s += 1.2 if counts[t2] else 0

        # edge tiles are slightly weaker
        if rank in (1, 9):
            s -= 0.3
        return s

    candidate = min(hand, key=lambda t: (score(t), sort_key(t)))
    return candidate
