"""Pairwise (all-pairs) combination generator core.

Given a mapping of object-name -> list of candidate states, produce a set of
rows (each row assigns one chosen state to every object) such that every
cross-object value pair is covered: for every pair of distinct objects
(A, B) and every (a in params[A], b in params[B]), at least one row has
A=a AND B=b.

This is the classic all-pairs / pairwise testing reduction: full coverage of
every two-way interaction without enumerating the full cartesian product. The
greedy algorithm here is NOT size-optimal, but it is strictly smaller than the
cartesian product for non-trivial inputs.

Stdlib only.
"""

from __future__ import annotations

from itertools import combinations, product

# A covered/uncovered pair is canonically keyed as
# ((obj_a, val_a), (obj_b, val_b)) with obj_a BEFORE obj_b in the object
# list order. The same key construction is used everywhere — required-set
# generation, the covered-set bookkeeping, and the termination check — so the
# greedy "newly covered" count can never disagree with the loop's termination
# condition. (That disagreement was the prior infinite-loop bug.)
PairKey = tuple[tuple[str, str], tuple[str, str]]


def pairwise(params: dict[str, list[str]]) -> list[dict[str, str]]:
    """Return rows covering every cross-object value pair (greedy all-pairs).

    Each row maps every object name to one chosen state. The returned set
    guarantees that for every pair of distinct objects (A, B) and every
    (a in params[A], b in params[B]) there is a row with A=a and B=b.

    Algorithm (provably terminating greedy):
      1. Compute the full REQUIRED pair set upfront, using object list order
         for canonical keys.
      2. While uncovered pairs remain, pick one uncovered pair (A=a, B=b),
         SEED a new row with {A: a, B: b}, then greedily assign every other
         object the value covering the most still-uncovered pairs.
      3. Each iteration covers AT LEAST the seed pair (a previously-uncovered
         pair) -> uncovered shrinks by >=1 each loop -> terminates in at most
         |required pairs| iterations.

    Objects with an empty state list and inputs with fewer than two objects
    have no cross-object pairs to cover and yield an empty list.
    """
    objects = [obj for obj, states in params.items() if states]
    if len(objects) < 2:
        return []

    # Position of each object in list order, for canonical key ordering.
    order = {obj: i for i, obj in enumerate(objects)}

    def key(obj_x: str, val_x: str, obj_y: str, val_y: str) -> PairKey:
        """Canonical key: lower-ordered object first. Single source of truth."""
        if order[obj_x] <= order[obj_y]:
            return ((obj_x, val_x), (obj_y, val_y))
        return ((obj_y, val_y), (obj_x, val_x))

    # 1. Full required pair set. combinations(objects, 2) yields pairs already
    #    in list order, so key() leaves them as-is here, but we route through
    #    key() anyway so generation and lookup share one code path.
    uncovered: set[PairKey] = set()
    for obj_a, obj_b in combinations(objects, 2):
        for val_a, val_b in product(params[obj_a], params[obj_b]):
            uncovered.add(key(obj_a, val_a, obj_b, val_b))

    total_required = len(uncovered)

    rows: list[dict[str, str]] = []
    while uncovered:
        # 2. Seed the row from one still-uncovered pair so this iteration is
        #    guaranteed to cover >=1 new pair.
        (seed_obj_a, seed_val_a), (seed_obj_b, seed_val_b) = next(iter(uncovered))
        row: dict[str, str] = {seed_obj_a: seed_val_a, seed_obj_b: seed_val_b}

        # Greedily assign every remaining object the value that covers the
        # most still-uncovered pairs against the values already fixed.
        for obj in objects:
            if obj in row:
                continue
            best_state = params[obj][0]
            best_gain = -1
            for state in params[obj]:
                gain = sum(
                    1
                    for fixed_obj, fixed_val in row.items()
                    if key(fixed_obj, fixed_val, obj, state) in uncovered
                )
                if gain > best_gain:
                    best_gain = gain
                    best_state = state
            row[obj] = best_state

        # 3. Mark every pair this complete row now covers.
        for obj_a, obj_b in combinations(objects, 2):
            uncovered.discard(key(obj_a, row[obj_a], obj_b, row[obj_b]))
        rows.append(row)

        # Defensive invariant: the seed pair must now be gone. If the covered
        # bookkeeping ever disagreed with the seed (the prior bug class), this
        # row would have covered 0 new pairs and the loop could spin; fail
        # loud instead of hanging.
        assert len(rows) <= total_required, (
            "pairwise made no progress: row count exceeded the required-pair "
            "upper bound, indicating a key-consistency regression"
        )

    return rows


if __name__ == "__main__":
    import json
    import sys

    payload = json.load(sys.stdin)
    rows = pairwise(payload["params"])
    json.dump(rows, sys.stdout)
