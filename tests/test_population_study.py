from __future__ import annotations

from knapsack2d.ga.config import GAConfig
from knapsack2d.models import Container, Item, ProblemInstance
from knapsack2d.policies import VoidBlockPolicy
from knapsack2d.ui.controllers.run_controller import RunRequest, execute_run_request
from knapsack2d.ui.run_models import PopulationStudyConfig


def test_execute_run_request_population_study_collects_points() -> None:
    problem = ProblemInstance(
        name="study-run",
        container=Container(6, 5),
        items=(
            Item("A", 3, 2, 1, can_rotate=True),
            Item("B", 2, 2, 1, can_rotate=False),
            Item("C", 1, 4, 1, can_rotate=True),
            Item("D", 2, 3, 1, can_rotate=True),
        ),
    )
    request = RunRequest(
        problem=problem,
        config=GAConfig(
            population_size=4,
            max_generations=3,
            stagnation_limit=3,
            tournament_size=2,
            seed=7,
        ),
        void_block_policy=VoidBlockPolicy.DISABLED,
        population_study=PopulationStudyConfig(
            enabled=True,
            population_sizes=(2, 3, 4, 5, 6),
        ),
    )

    outcome = execute_run_request(request)

    assert outcome.population_study is not None
    assert len(outcome.population_study.points) == 5
    assert [point.population_size for point in outcome.population_study.points] == [2, 3, 4, 5, 6]
    assert outcome.primary_result.best_individual.fitness_key == max(
        point.fitness_key for point in outcome.population_study.points
    )
