from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum

from knapsack2d.ga.individual import Individual
from knapsack2d.ga.metrics import average_fill_ratio, average_total_value, order_diversity
from knapsack2d.models import DecodedLayout, FitnessBreakdown


class HistoryMode(str, Enum):
    BEST_ONLY = "best_only"
    TOP_K = "top_k"
    FULL_POPULATION = "full_population"


@dataclass(frozen=True)
class IndividualSnapshot:
    individual_id: str
    generation_index: int
    rank_in_generation: int
    chromosome_order: tuple[str, ...]
    chromosome_rotations: tuple[bool, ...]
    fitness_breakdown: FitnessBreakdown
    decoded_layout: DecodedLayout
    origin_type: str
    parent_ids: tuple[str, ...] | None = None


@dataclass(frozen=True)
class GenerationSnapshot:
    generation_index: int
    generation_time_ms: float
    best_individual_id: str
    best_total_value: int
    avg_total_value: float
    best_fill_ratio: float
    avg_fill_ratio: float
    diversity: float
    best_valid_items: int
    best_overflow_items: int
    individuals: tuple[IndividualSnapshot, ...]


@dataclass
class RunHistory:
    generations: list[GenerationSnapshot] = field(default_factory=list)

    def append(self, snapshot: GenerationSnapshot) -> None:
        self.generations.append(snapshot)

    def to_dict(self) -> dict[str, object]:
        return {"generations": [asdict(snapshot) for snapshot in self.generations]}


def build_generation_snapshot(
    generation_index: int,
    generation_time_ms: float,
    sorted_population: list[Individual],
    history_mode: HistoryMode,
    history_top_k: int,
) -> GenerationSnapshot:
    if not sorted_population:
        raise ValueError("population cannot be empty")

    if history_mode == HistoryMode.BEST_ONLY:
        selected = sorted_population[:1]
    elif history_mode == HistoryMode.FULL_POPULATION:
        selected = sorted_population
    else:
        selected = sorted_population[: min(history_top_k, len(sorted_population))]

    snapshots = tuple(
        IndividualSnapshot(
            individual_id=individual.individual_id,
            generation_index=generation_index,
            rank_in_generation=rank,
            chromosome_order=individual.chromosome.order,
            chromosome_rotations=individual.chromosome.rotations,
            fitness_breakdown=individual.fitness_breakdown,
            decoded_layout=individual.decoded_layout,
            origin_type=individual.origin_type,
            parent_ids=individual.parent_ids,
        )
        for rank, individual in enumerate(selected, start=1)
    )

    best = sorted_population[0]
    return GenerationSnapshot(
        generation_index=generation_index,
        generation_time_ms=generation_time_ms,
        best_individual_id=best.individual_id,
        best_total_value=best.fitness_breakdown.total_value,
        avg_total_value=average_total_value(sorted_population),
        best_fill_ratio=best.fitness_breakdown.fill_ratio,
        avg_fill_ratio=average_fill_ratio(sorted_population),
        diversity=order_diversity([individual.chromosome for individual in sorted_population]),
        best_valid_items=best.fitness_breakdown.valid_items_count,
        best_overflow_items=best.fitness_breakdown.overflow_items_count,
        individuals=snapshots,
    )
