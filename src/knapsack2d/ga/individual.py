from __future__ import annotations

from dataclasses import dataclass

from knapsack2d.ga.chromosome import Chromosome
from knapsack2d.models import DecodedLayout, FitnessBreakdown


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
    def fitness_key(self) -> tuple[int, int, int, int]:
        breakdown = self.fitness_breakdown
        return (
            breakdown.total_value,
            breakdown.valid_items_count,
            breakdown.used_area_inside,
            -breakdown.overflow_items_count,
        )
