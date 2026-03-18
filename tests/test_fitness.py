from __future__ import annotations

from knapsack2d.fitness import FitnessEvaluator
from knapsack2d.models import DecodedLayout, Placement
from knapsack2d.task_builder import ProblemBuilder


def test_fitness_counts_valid_overflow_and_virtual() -> None:
    problem = (
        ProblemBuilder()
        .set_name("fitness")
        .set_container(4, 4)
        .add_item("A", 2, 2, 10)
        .add_item("B", 2, 2, 9)
        .build()
    )
    layout = DecodedLayout(
        placements=[
            Placement("A", 0, 0, 2, 2, False, 10),
            Placement("B", 3, 0, 2, 2, False, 9),
            Placement(None, 0, 2, 1, 1, False, 0, is_virtual=True),
        ],
        steps=[],
        used_solution_order=["A", "B"],
    )

    breakdown = FitnessEvaluator().evaluate(problem, layout)

    assert breakdown.total_value == 10
    assert breakdown.packed_items_count == 2
    assert breakdown.valid_items_count == 1
    assert breakdown.overflow_items_count == 1
    assert breakdown.virtual_blocks_count == 1
    assert breakdown.used_area_inside == 4
    assert breakdown.fill_ratio == 0.25
    assert breakdown.large_first_score == 8


def test_fitness_rewards_large_blocks_earlier() -> None:
    problem = (
        ProblemBuilder()
        .set_name("fitness-large-first")
        .set_container(5, 3)
        .add_item("L", 3, 2, 1)
        .add_item("S", 1, 2, 1)
        .build()
    )

    layout_large_first = DecodedLayout(
        placements=[
            Placement("L", 0, 0, 3, 2, False, 6),
            Placement("S", 3, 0, 1, 2, False, 2),
        ],
        steps=[],
        used_solution_order=["L", "S"],
    )
    layout_small_first = DecodedLayout(
        placements=[
            Placement("S", 3, 0, 1, 2, False, 2),
            Placement("L", 0, 0, 3, 2, False, 6),
        ],
        steps=[],
        used_solution_order=["S", "L"],
    )

    evaluator = FitnessEvaluator()
    large_first = evaluator.evaluate(problem, layout_large_first)
    small_first = evaluator.evaluate(problem, layout_small_first)

    assert large_first.total_value == small_first.total_value
    assert large_first.large_first_score > small_first.large_first_score
