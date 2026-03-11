from __future__ import annotations

import random

from knapsack2d.ga.chromosome import Chromosome
from knapsack2d.ga.individual import Individual
from knapsack2d.ga.selection import tournament_select
from knapsack2d.models import DecodedLayout, FitnessBreakdown


def make_individual(
    item_id: str,
    total_value: int,
    valid_items: int,
    used_area: int,
    overflow: int,
) -> Individual:
    return Individual(
        individual_id=item_id,
        generation_index=0,
        chromosome=Chromosome(order=(item_id,), rotations=(False,)),
        fitness_breakdown=FitnessBreakdown(
            total_value=total_value,
            packed_items_count=1,
            valid_items_count=valid_items,
            overflow_items_count=overflow,
            virtual_blocks_count=0,
            used_area_inside=used_area,
            fill_ratio=0.0,
        ),
        decoded_layout=DecodedLayout(placements=[], steps=[], used_solution_order=[]),
        origin_type="init",
        parent_ids=None,
    )


def test_tournament_selection_picks_best() -> None:
    population = [
        make_individual("A", total_value=5, valid_items=1, used_area=4, overflow=0),
        make_individual("B", total_value=9, valid_items=1, used_area=3, overflow=0),
        make_individual("C", total_value=9, valid_items=2, used_area=5, overflow=0),
    ]

    selected = tournament_select(population, tournament_size=3, rng=random.Random(7))

    assert selected.individual_id == "C"
