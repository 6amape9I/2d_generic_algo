from __future__ import annotations

from knapsack2d.ga.history import GenerationSnapshot, IndividualSnapshot, RunHistory
from knapsack2d.models import DecodedLayout, FitnessBreakdown
from knapsack2d.ui.presenters.history_mapper import HistoryMapper


def test_history_mapper_maps_generations_and_individuals() -> None:
    snapshot = IndividualSnapshot(
        individual_id="ind-1",
        generation_index=0,
        rank_in_generation=1,
        chromosome_order=("A",),
        chromosome_rotations=(False,),
        fitness_breakdown=FitnessBreakdown(
            total_value=10,
            packed_items_count=1,
            valid_items_count=1,
            overflow_items_count=0,
            virtual_blocks_count=0,
            used_area_inside=4,
            fill_ratio=0.25,
        ),
        decoded_layout=DecodedLayout(placements=[], steps=[], used_solution_order=[]),
        origin_type="init",
        parent_ids=None,
    )
    generation = GenerationSnapshot(
        generation_index=0,
        generation_time_ms=12.3,
        best_individual_id="ind-1",
        best_total_value=10,
        avg_total_value=8.5,
        best_fill_ratio=0.25,
        avg_fill_ratio=0.2,
        diversity=0.1,
        best_valid_items=1,
        best_overflow_items=0,
        individuals=(snapshot,),
    )
    history = RunHistory(generations=[generation])

    mapper = HistoryMapper()
    generation_rows = mapper.generation_rows(history)
    individual_rows = mapper.individual_rows(generation)

    assert len(generation_rows) == 1
    assert generation_rows[0].best_value == 10
    assert len(individual_rows) == 1
    assert individual_rows[0].value == 10
