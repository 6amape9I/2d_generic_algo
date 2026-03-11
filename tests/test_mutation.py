from __future__ import annotations

import random

from knapsack2d.ga.chromosome import Chromosome
from knapsack2d.ga.mutation import (
    insert_mutation,
    inversion_mutation,
    rotation_flip_mutation,
    swap_mutation,
)
from knapsack2d.task_builder import ProblemBuilder


def build_problem():
    return (
        ProblemBuilder()
        .set_name("mutation")
        .set_container(10, 10)
        .add_item("A", 3, 2, 8, can_rotate=False)
        .add_item("B", 2, 2, 5)
        .add_item("C", 1, 4, 6)
        .add_item("D", 2, 3, 7)
        .build()
    )


def base_chromosome() -> Chromosome:
    return Chromosome(
        order=("A", "B", "C", "D"),
        rotations=(False, False, True, False),
    )


def test_swap_keeps_item_set() -> None:
    mutated = swap_mutation(base_chromosome(), random.Random(0))
    assert set(mutated.order) == set(base_chromosome().order)


def test_insert_keeps_item_set() -> None:
    mutated = insert_mutation(base_chromosome(), random.Random(1))
    assert set(mutated.order) == set(base_chromosome().order)


def test_inversion_keeps_item_set() -> None:
    mutated = inversion_mutation(base_chromosome(), random.Random(2))
    assert set(mutated.order) == set(base_chromosome().order)


def test_rotation_flip_does_not_rotate_fixed_items() -> None:
    problem = build_problem()
    chromosome = Chromosome(
        order=("A", "B", "C", "D"),
        rotations=(True, False, False, False),
    )

    mutated = rotation_flip_mutation(problem, chromosome, random.Random(3), flips_count=2)

    idx_a = mutated.order.index("A")
    assert mutated.rotations[idx_a] is False
