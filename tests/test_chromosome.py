from __future__ import annotations

import pytest

from knapsack2d.ga.chromosome import Chromosome, to_sequence_solution
from knapsack2d.task_builder import ProblemBuilder


def build_problem():
    return (
        ProblemBuilder()
        .set_name("chromosome")
        .set_container(10, 10)
        .add_item("A", 3, 2, 8, can_rotate=False)
        .add_item("B", 2, 2, 5, can_rotate=True)
        .add_item("C", 1, 4, 6, can_rotate=True)
        .build()
    )


def test_chromosome_contains_all_items_once() -> None:
    problem = build_problem()
    chromosome = Chromosome(
        order=("B", "A", "C"),
        rotations=(True, False, True),
    )

    chromosome.validate_for_problem(problem)


def test_invalid_chromosome_raises_error() -> None:
    problem = build_problem()
    chromosome = Chromosome(
        order=("A", "B", "B"),
        rotations=(False, False, True),
    )

    with pytest.raises(ValueError):
        to_sequence_solution(problem, chromosome)


def test_non_rotatable_items_are_normalized() -> None:
    problem = build_problem()
    chromosome = Chromosome(
        order=("A", "B", "C"),
        rotations=(True, True, False),
    )

    normalized = chromosome.normalized(problem)
    sequence = to_sequence_solution(problem, chromosome)

    assert normalized.rotations[0] is False
    assert sequence.genes[0].rotated is False
