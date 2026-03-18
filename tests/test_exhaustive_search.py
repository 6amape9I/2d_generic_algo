from __future__ import annotations

from knapsack2d.baseline.exhaustive import ExhaustiveSearchConfig, run_exhaustive_search
from knapsack2d.decoder import LeftBottomDecoder
from knapsack2d.fitness import FitnessEvaluator
from knapsack2d.task_builder import ProblemBuilder


def test_exhaustive_search_finds_solution_for_small_problem() -> None:
    problem = (
        ProblemBuilder()
        .set_name("exhaustive-small")
        .set_container(4, 3)
        .add_item("A", 2, 2, 1)
        .add_item("B", 2, 1, 1)
        .build()
    )

    result = run_exhaustive_search(
        problem,
        LeftBottomDecoder(),
        FitnessEvaluator(),
        ExhaustiveSearchConfig(enabled=True, max_items=4, max_time_seconds=5.0),
    )

    assert result.status in {"completed", "fill_ratio_1"}
    assert result.evaluated_solutions > 0
    assert result.best_value is not None
    assert result.best_chromosome is not None


def test_exhaustive_search_skips_large_problem() -> None:
    problem = (
        ProblemBuilder()
        .set_name("exhaustive-skip")
        .set_container(10, 10)
        .add_item("A", 2, 2, 1)
        .add_item("B", 2, 2, 1)
        .add_item("C", 2, 2, 1)
        .add_item("D", 2, 2, 1)
        .add_item("E", 2, 2, 1)
        .add_item("F", 2, 2, 1)
        .add_item("G", 2, 2, 1)
        .build()
    )

    result = run_exhaustive_search(
        problem,
        LeftBottomDecoder(),
        FitnessEvaluator(),
        ExhaustiveSearchConfig(enabled=True, max_items=6, max_time_seconds=5.0),
    )

    assert result.status == "skipped"
    assert result.best_chromosome is None
