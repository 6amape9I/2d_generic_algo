from __future__ import annotations

import json
from pathlib import Path

from knapsack2d.ga.config import GAConfig
from knapsack2d.ga.history import GenerationSnapshot, IndividualSnapshot, RunHistory
from knapsack2d.ga.individual import Individual
from knapsack2d.ga.optimizer import GAResult
from knapsack2d.models import (
    Container,
    DecodedLayout,
    FitnessBreakdown,
    Placement,
    ProblemInstance,
)
from knapsack2d.ui.presenters.history_mapper import HistoryMapper


def _build_result() -> tuple[ProblemInstance, GAResult]:
    problem = ProblemInstance(
        name="export-test",
        container=Container(4, 4),
        items=(),
    )
    breakdown = FitnessBreakdown(
        total_value=10,
        packed_items_count=1,
        valid_items_count=1,
        overflow_items_count=0,
        virtual_blocks_count=0,
        used_area_inside=4,
        fill_ratio=0.25,
    )
    layout = DecodedLayout(
        placements=[Placement("A", 0, 0, 2, 2, False, 10)],
        steps=[],
        used_solution_order=["A"],
    )
    snapshot = IndividualSnapshot(
        individual_id="ind-1",
        generation_index=0,
        rank_in_generation=1,
        chromosome_order=("A",),
        chromosome_rotations=(False,),
        fitness_breakdown=breakdown,
        decoded_layout=layout,
        origin_type="init",
        parent_ids=None,
    )
    generation = GenerationSnapshot(
        generation_index=0,
        generation_time_ms=2.0,
        best_individual_id="ind-1",
        best_total_value=10,
        avg_total_value=10,
        best_fill_ratio=0.25,
        avg_fill_ratio=0.25,
        diversity=0.0,
        best_valid_items=1,
        best_overflow_items=0,
        individuals=(snapshot,),
    )
    individual = Individual(
        individual_id="ind-1",
        generation_index=0,
        chromosome=snapshot_to_chromosome(snapshot),
        fitness_breakdown=breakdown,
        decoded_layout=layout,
        origin_type="init",
        parent_ids=None,
    )
    result = GAResult(
        best_individual=individual,
        final_population=(individual,),
        history=RunHistory(generations=[generation]),
        config=GAConfig(population_size=2, max_generations=1, stagnation_limit=1, tournament_size=2),
        duration_seconds=0.02,
    )
    return problem, result


def snapshot_to_chromosome(snapshot: IndividualSnapshot):
    from knapsack2d.ga.chromosome import Chromosome

    return Chromosome(
        order=snapshot.chromosome_order,
        rotations=snapshot.chromosome_rotations,
    )


def test_history_export_and_report_files(tmp_path: Path) -> None:
    problem, result = _build_result()
    mapper = HistoryMapper()

    history_path = tmp_path / "history.json"
    report_path = tmp_path / "report.txt"

    mapper.save_history_json(history_path, problem, result)
    mapper.save_best_report(report_path, problem, result)

    history = json.loads(history_path.read_text(encoding="utf-8"))
    report_text = report_path.read_text(encoding="utf-8")

    assert "problem" in history
    assert "ga_config" in history
    assert "saved_generations" in history
    assert "best_solution_overall" in history
    assert "Problem: export-test" in report_text
