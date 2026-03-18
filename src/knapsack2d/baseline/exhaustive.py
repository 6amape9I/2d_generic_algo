from __future__ import annotations

import math
import time
from dataclasses import dataclass
from itertools import permutations, product

from knapsack2d.decoder import LeftBottomDecoder
from knapsack2d.fitness import FitnessEvaluator
from knapsack2d.ga.chromosome import Chromosome, to_sequence_solution
from knapsack2d.ga.individual import fitness_key_for_breakdown
from knapsack2d.models import DecodedLayout, FitnessBreakdown, ProblemInstance


@dataclass(frozen=True)
class ExhaustiveSearchConfig:
    enabled: bool = False
    max_items: int = 6
    max_time_seconds: float | None = 60.0

    def __post_init__(self) -> None:
        if self.max_items < 1:
            raise ValueError("max_items must be >= 1")
        if self.max_time_seconds is not None and self.max_time_seconds <= 0:
            raise ValueError("max_time_seconds must be positive")


@dataclass(frozen=True)
class ExhaustiveSearchResult:
    status: str
    duration_seconds: float
    evaluated_solutions: int
    total_search_space: int | None
    best_chromosome: Chromosome | None
    best_fitness_breakdown: FitnessBreakdown | None
    best_decoded_layout: DecodedLayout | None
    reason: str | None = None

    @property
    def best_value(self) -> int | None:
        if self.best_fitness_breakdown is None:
            return None
        return self.best_fitness_breakdown.total_value


def run_exhaustive_search(
    problem: ProblemInstance,
    decoder: LeftBottomDecoder,
    fitness_evaluator: FitnessEvaluator,
    config: ExhaustiveSearchConfig,
) -> ExhaustiveSearchResult:
    start = time.perf_counter()
    item_count = len(problem.items)

    if item_count > config.max_items:
        return ExhaustiveSearchResult(
            status="skipped",
            duration_seconds=time.perf_counter() - start,
            evaluated_solutions=0,
            total_search_space=None,
            best_chromosome=None,
            best_fitness_breakdown=None,
            best_decoded_layout=None,
            reason=f"problem has {item_count} items; exhaustive limit is {config.max_items}",
        )

    items = tuple(problem.items)
    total_search_space = math.factorial(item_count)
    for item in items:
        total_search_space *= 2 if item.can_rotate else 1

    best_chromosome: Chromosome | None = None
    best_layout: DecodedLayout | None = None
    best_breakdown: FitnessBreakdown | None = None
    best_key: tuple[int, int, int, int, int] | None = None
    evaluated = 0

    for ordered_items in permutations(items):
        order = tuple(item.item_id for item in ordered_items)
        rotation_options = [
            (False, True) if item.can_rotate else (False,) for item in ordered_items
        ]

        for rotations in product(*rotation_options):
            if config.max_time_seconds is not None and (time.perf_counter() - start) >= config.max_time_seconds:
                return ExhaustiveSearchResult(
                    status="time_limit",
                    duration_seconds=time.perf_counter() - start,
                    evaluated_solutions=evaluated,
                    total_search_space=total_search_space,
                    best_chromosome=best_chromosome,
                    best_fitness_breakdown=best_breakdown,
                    best_decoded_layout=best_layout,
                    reason="time limit reached during exhaustive search",
                )

            chromosome = Chromosome(order=order, rotations=tuple(rotations)).normalized(problem)
            layout = decoder.decode(problem, to_sequence_solution(problem, chromosome))
            breakdown = fitness_evaluator.evaluate(problem, layout)
            key = fitness_key_for_breakdown(breakdown)
            evaluated += 1

            if best_key is None or key > best_key:
                best_chromosome = chromosome
                best_layout = layout
                best_breakdown = breakdown
                best_key = key

            if breakdown.fill_ratio >= 1.0:
                return ExhaustiveSearchResult(
                    status="fill_ratio_1",
                    duration_seconds=time.perf_counter() - start,
                    evaluated_solutions=evaluated,
                    total_search_space=total_search_space,
                    best_chromosome=best_chromosome,
                    best_fitness_breakdown=best_breakdown,
                    best_decoded_layout=best_layout,
                    reason="container filled completely",
                )

    return ExhaustiveSearchResult(
        status="completed",
        duration_seconds=time.perf_counter() - start,
        evaluated_solutions=evaluated,
        total_search_space=total_search_space,
        best_chromosome=best_chromosome,
        best_fitness_breakdown=best_breakdown,
        best_decoded_layout=best_layout,
        reason=None,
    )
