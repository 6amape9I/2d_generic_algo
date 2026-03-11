from __future__ import annotations

import random

from knapsack2d.ga.chromosome import Chromosome
from knapsack2d.ga.crossover import order_crossover
from knapsack2d.task_builder import ProblemBuilder


def test_ox_child_contains_all_items_without_duplicates() -> None:
    problem = (
        ProblemBuilder()
        .set_name("ox")
        .set_container(10, 10)
        .add_item("A", 3, 2, 8, can_rotate=False)
        .add_item("B", 2, 2, 5)
        .add_item("C", 1, 4, 6)
        .add_item("D", 2, 3, 7)
        .build()
    )
    p1 = Chromosome(
        order=("A", "B", "C", "D"),
        rotations=(True, False, True, False),
    )
    p2 = Chromosome(
        order=("C", "D", "B", "A"),
        rotations=(False, True, False, True),
    )

    child = order_crossover(problem, p1, p2, random.Random(0), left=1, right=3)

    assert len(child.order) == len(p1.order)
    assert set(child.order) == set(p1.order)


def test_ox_inherits_rotations_from_parent_source() -> None:
    problem = (
        ProblemBuilder()
        .set_name("ox-rot")
        .set_container(10, 10)
        .add_item("A", 3, 2, 8, can_rotate=False)
        .add_item("B", 2, 2, 5)
        .add_item("C", 1, 4, 6)
        .add_item("D", 2, 3, 7)
        .build()
    )
    p1 = Chromosome(
        order=("A", "B", "C", "D"),
        rotations=(True, False, True, False),
    )
    p2 = Chromosome(
        order=("C", "D", "B", "A"),
        rotations=(False, True, False, True),
    )

    child = order_crossover(problem, p1, p2, random.Random(1), left=1, right=3)

    assert child.order == ("D", "B", "C", "A")
    assert child.rotations == (True, False, True, False)
