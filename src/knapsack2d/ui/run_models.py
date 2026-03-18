from __future__ import annotations

from dataclasses import dataclass

from knapsack2d.baseline.exhaustive import ExhaustiveSearchResult
from knapsack2d.ga.optimizer import GAResult


@dataclass(frozen=True)
class PopulationStudyConfig:
    enabled: bool = False
    population_sizes: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if len(self.population_sizes) != 5:
            raise ValueError("population study requires exactly 5 population sizes")
        if any(size < 2 for size in self.population_sizes):
            raise ValueError("population_sizes must contain values >= 2")
        if self.enabled and len(set(self.population_sizes)) != len(self.population_sizes):
            raise ValueError("population_sizes must be unique when study is enabled")


@dataclass(frozen=True)
class PopulationStudyPoint:
    population_size: int
    best_total_value: int
    best_valid_items: int
    best_fill_ratio: float
    best_overflow_items: int
    duration_seconds: float
    fitness_key: tuple[int, int, int, int, int]
    best_individual_id: str


@dataclass(frozen=True)
class PopulationStudyResult:
    points: tuple[PopulationStudyPoint, ...]

    def __post_init__(self) -> None:
        if not self.points:
            raise ValueError("population study result must contain at least one point")

    @property
    def best_point(self) -> PopulationStudyPoint:
        return max(self.points, key=lambda point: point.fitness_key)


@dataclass(frozen=True)
class RunOutcome:
    primary_result: GAResult
    population_study: PopulationStudyResult | None = None
    exhaustive_baseline: ExhaustiveSearchResult | None = None
