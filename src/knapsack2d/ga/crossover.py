from __future__ import annotations

import random

from knapsack2d.ga.chromosome import Chromosome
from knapsack2d.models import ProblemInstance


def order_crossover(
    problem: ProblemInstance,
    parent1: Chromosome,
    parent2: Chromosome,
    rng: random.Random,
    left: int | None = None,
    right: int | None = None,
) -> Chromosome:
    if len(parent1.order) != len(parent2.order):
        raise ValueError("parents must have the same chromosome length")

    length = len(parent1.order)
    if length < 2:
        return parent1.normalized(problem)

    if left is None or right is None:
        cut_a, cut_b = sorted(rng.sample(range(length), 2))
        left = cut_a
        right = cut_b + 1

    if not (0 <= left < right <= length):
        raise ValueError("invalid crossover segment")

    child_order: list[str | None] = [None] * length
    child_order[left:right] = parent1.order[left:right]

    segment_items = set(parent1.order[left:right])
    free_positions = [idx for idx, item_id in enumerate(child_order) if item_id is None]
    remaining = [item_id for item_id in parent2.order if item_id not in segment_items]

    for idx, item_id in zip(free_positions, remaining, strict=True):
        child_order[idx] = item_id

    if any(item_id is None for item_id in child_order):
        raise ValueError("failed to construct child order in OX")

    p1_rotation = dict(zip(parent1.order, parent1.rotations, strict=True))
    p2_rotation = dict(zip(parent2.order, parent2.rotations, strict=True))

    child_rotations: list[bool] = []
    for index, item_id in enumerate(child_order):
        assert item_id is not None
        if left <= index < right:
            child_rotations.append(p1_rotation[item_id])
        else:
            child_rotations.append(p2_rotation[item_id])

    child = Chromosome(
        order=tuple(item_id for item_id in child_order if item_id is not None),
        rotations=tuple(child_rotations),
    )
    return child.normalized(problem)
