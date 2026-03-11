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
