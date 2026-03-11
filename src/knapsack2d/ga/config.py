from __future__ import annotations

from dataclasses import dataclass

from knapsack2d.ga.history import HistoryMode


@dataclass(frozen=True)
class GAConfig:
    population_size: int = 60
    max_generations: int = 60
    stagnation_limit: int = 20
    max_time_seconds: float | None = None

    seed: int | None = None

    tournament_size: int = 3
    elite_count: int | None = None

    p_crossover: float = 0.9
    p_order_mutation: float = 0.35
    p_rotation_mutation: float = 0.15

    initial_random_ratio: float = 0.4

    history_mode: HistoryMode = HistoryMode.TOP_K
    history_top_k: int = 10

    duplicate_retries: int = 5
    duplicate_random_immigrant: bool = True

    enable_stagnation_immigrants: bool = False
    stagnation_immigrant_fraction: float = 0.15

    def __post_init__(self) -> None:
        if self.population_size < 2:
            raise ValueError("population_size must be >= 2")
        if self.max_generations < 1:
            raise ValueError("max_generations must be >= 1")
        if self.stagnation_limit < 1:
            raise ValueError("stagnation_limit must be >= 1")
        if self.tournament_size < 2:
            raise ValueError("tournament_size must be >= 2")
        if self.tournament_size > self.population_size:
            raise ValueError("tournament_size cannot exceed population_size")
        if not 0 <= self.p_crossover <= 1:
            raise ValueError("p_crossover must be in [0, 1]")
        if not 0 <= self.p_order_mutation <= 1:
            raise ValueError("p_order_mutation must be in [0, 1]")
        if not 0 <= self.p_rotation_mutation <= 1:
            raise ValueError("p_rotation_mutation must be in [0, 1]")
        if not 0 <= self.initial_random_ratio <= 1:
            raise ValueError("initial_random_ratio must be in [0, 1]")
        if self.history_top_k < 1:
            raise ValueError("history_top_k must be >= 1")
        if self.max_time_seconds is not None and self.max_time_seconds <= 0:
            raise ValueError("max_time_seconds must be positive")
        if self.elite_count is not None and self.elite_count < 1:
            raise ValueError("elite_count must be >= 1")
        if not 0 <= self.stagnation_immigrant_fraction <= 1:
            raise ValueError("stagnation_immigrant_fraction must be in [0, 1]")

    @property
    def resolved_elite_count(self) -> int:
        if self.elite_count is not None:
            return min(self.population_size - 1, self.elite_count)
        return max(1, self.population_size // 20)
