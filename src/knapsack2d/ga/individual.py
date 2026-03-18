from __future__ import annotations

from dataclasses import dataclass

from knapsack2d.ga.chromosome import Chromosome
from knapsack2d.models import DecodedLayout, FitnessBreakdown


def fitness_key_for_breakdown(breakdown: FitnessBreakdown) -> tuple[int, int, int, int, int]:
    return (
        breakdown.total_value,
        breakdown.large_first_score,
        breakdown.valid_items_count,
        breakdown.used_area_inside,
        -breakdown.overflow_items_count,
    )


@dataclass(frozen=True)
class Individual:
    individual_id: str
    generation_index: int
    chromosome: Chromosome
    fitness_breakdown: FitnessBreakdown
    decoded_layout: DecodedLayout
    origin_type: str
    parent_ids: tuple[str, ...] | None = None

    @property
    def fitness_key(self) -> tuple[int, int, int, int, int]:
        return fitness_key_for_breakdown(self.fitness_breakdown)
