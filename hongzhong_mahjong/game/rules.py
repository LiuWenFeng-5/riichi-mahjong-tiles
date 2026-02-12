from __future__ import annotations

from collections import Counter
from functools import lru_cache
from typing import Iterable, Tuple

from .tiles import SUITS, WILDCARD


def sort_key(code: str) -> tuple[int, int]:
    if code == WILDCARD:
        return (99, 0)
    suit_order = {"Man": 0, "Pin": 1, "Sou": 2}
    return (suit_order[code[:3]], int(code[3:]))


def normalize_hand(hand: Iterable[str]) -> list[str]:
    return sorted(hand, key=sort_key)


def is_win(hand: Iterable[str]) -> bool:
    tiles = list(hand)
    if len(tiles) % 3 != 2:
        return False

    counts = Counter(tiles)
    wildcards = counts.pop(WILDCARD, 0)

    # try every possible pair candidate (including wildcard pair)
    candidates = set(counts.keys())
    candidates.add("__WILDCARD_PAIR__")

    for pair in candidates:
        c = counts.copy()
        w = wildcards

        if pair == "__WILDCARD_PAIR__":
            if w < 2:
                continue
            w -= 2
        else:
            need = max(0, 2 - c.get(pair, 0))
            if need > w:
                continue
            w -= need
            c[pair] -= 2 - need
            if c[pair] <= 0:
                c.pop(pair, None)

        suit_states = []
        for suit in SUITS:
            suit_states.append(tuple(c.get(f"{suit}{r}", 0) for r in range(1, 10)))

        if can_finish_all(tuple(suit_states), w):
            return True

    return False


@lru_cache(maxsize=None)
def can_finish_all(suit_states: Tuple[Tuple[int, ...], ...], wildcards: int) -> bool:
    if all(sum(s) == 0 for s in suit_states):
        return wildcards % 3 == 0

    # choose a non-empty suit to process first
    for i, state in enumerate(suit_states):
        if sum(state) == 0:
            continue
        need_options = meld_needs_for_suit(state)
        for need in need_options:
            if need <= wildcards:
                next_states = list(suit_states)
                next_states[i] = (0,) * 9
                if can_finish_all(tuple(next_states), wildcards - need):
                    return True
        return False
    return False


@lru_cache(maxsize=None)
def meld_needs_for_suit(state: Tuple[int, ...]) -> Tuple[int, ...]:
    results = set()

    @lru_cache(maxsize=None)
    def dfs(arr: Tuple[int, ...]) -> Tuple[int, ...]:
        if sum(arr) == 0:
            return (0,)

        # find first tile present
        i = next(idx for idx, n in enumerate(arr) if n > 0)
        found = set()

        # triplet option
        trip_need = max(0, 3 - arr[i])
        if arr[i] > 0:
            nxt = list(arr)
            remove = min(3, nxt[i])
            nxt[i] -= remove
            for tail in dfs(tuple(nxt)):
                found.add(trip_need + tail)

        # sequence option
        if i <= 6:
            nxt = list(arr)
            seq_need = 0
            for j in (i, i + 1, i + 2):
                if nxt[j] > 0:
                    nxt[j] -= 1
                else:
                    seq_need += 1
            for tail in dfs(tuple(nxt)):
                found.add(seq_need + tail)

        return tuple(sorted(found))

    results.update(dfs(state))
    return tuple(sorted(results))
