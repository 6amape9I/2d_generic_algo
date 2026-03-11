from __future__ import annotations

from knapsack2d.decoder import LeftBottomDecoder
from knapsack2d.fitness import FitnessEvaluator
from knapsack2d.ga.config import GAConfig
from knapsack2d.ga.optimizer import GeneticOptimizer
from knapsack2d.task_builder import ProblemBuilder


def test_optimizer_smoke() -> None:
    problem = (
        ProblemBuilder()
        .set_name("ga-smoke")
        .set_container(8, 6)
        .add_item("A", 3, 2, 8)
        .add_item("B", 4, 3, 12)
        .add_item("C", 5, 2, 7, can_rotate=False)
        .add_item("D", 2, 2, 4)
        .add_item("E", 1, 3, 5)
        .build()
    )
    config = GAConfig(
        population_size=20,
        max_generations=8,
        stagnation_limit=100,
        seed=42,
    )
    optimizer = GeneticOptimizer(
        config=config,
        decoder=LeftBottomDecoder(),
        fitness_evaluator=FitnessEvaluator(),
    )

    result = optimizer.run(problem)

    assert result.best_individual is not None
    assert len(result.final_population) == config.population_size
    assert len(result.history.generations) == config.max_generations

    best_values = [snapshot.best_total_value for snapshot in result.history.generations]
    assert all(curr >= prev for prev, curr in zip(best_values, best_values[1:]))
