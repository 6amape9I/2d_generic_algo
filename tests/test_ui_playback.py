from __future__ import annotations

import os
import sys

from PySide6.QtWidgets import QApplication

from knapsack2d.baseline.exhaustive import ExhaustiveSearchResult
from knapsack2d.ga.chromosome import Chromosome
from knapsack2d.ga.config import GAConfig
from knapsack2d.ga.history import GenerationSnapshot, IndividualSnapshot, RunHistory
from knapsack2d.ga.individual import Individual
from knapsack2d.ga.optimizer import GAResult
from knapsack2d.models import Container, DecodedLayout, FitnessBreakdown, Item, Placement, ProblemInstance
from knapsack2d.ui.main_window import MainWindow
from knapsack2d.ui.run_models import PopulationStudyPoint, PopulationStudyResult

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def _build_problem_and_result() -> tuple[ProblemInstance, GAResult]:
    problem = ProblemInstance(
        name="playback",
        container=Container(4, 4),
        items=(Item("A", 2, 2, 5),),
    )

    breakdown_0 = FitnessBreakdown(
        total_value=5,
        packed_items_count=1,
        valid_items_count=1,
        overflow_items_count=0,
        virtual_blocks_count=0,
        used_area_inside=4,
        fill_ratio=0.25,
        large_first_score=4,
    )
    breakdown_1 = FitnessBreakdown(
        total_value=6,
        packed_items_count=1,
        valid_items_count=1,
        overflow_items_count=0,
        virtual_blocks_count=0,
        used_area_inside=4,
        fill_ratio=0.25,
        large_first_score=4,
    )

    layout_0 = DecodedLayout(
        placements=[Placement("A", 0, 0, 2, 2, False, 5)],
        steps=[],
        used_solution_order=["A"],
    )
    layout_1 = DecodedLayout(
        placements=[Placement("A", 1, 0, 2, 2, False, 6)],
        steps=[],
        used_solution_order=["A"],
    )

    snapshot_0 = IndividualSnapshot(
        individual_id="g0-1",
        generation_index=0,
        rank_in_generation=1,
        chromosome_order=("A",),
        chromosome_rotations=(False,),
        fitness_breakdown=breakdown_0,
        decoded_layout=layout_0,
        origin_type="init",
        parent_ids=None,
    )
    snapshot_1 = IndividualSnapshot(
        individual_id="g1-1",
        generation_index=1,
        rank_in_generation=1,
        chromosome_order=("A",),
        chromosome_rotations=(False,),
        fitness_breakdown=breakdown_1,
        decoded_layout=layout_1,
        origin_type="elite",
        parent_ids=("g0-1",),
    )

    generation_0 = GenerationSnapshot(
        generation_index=0,
        generation_time_ms=1.1,
        best_individual_id="g0-1",
        best_total_value=5,
        avg_total_value=5,
        best_fill_ratio=0.25,
        avg_fill_ratio=0.25,
        diversity=0.0,
        best_valid_items=1,
        best_overflow_items=0,
        individuals=(snapshot_0,),
    )
    generation_1 = GenerationSnapshot(
        generation_index=1,
        generation_time_ms=1.1,
        best_individual_id="g1-1",
        best_total_value=6,
        avg_total_value=6,
        best_fill_ratio=0.25,
        avg_fill_ratio=0.25,
        diversity=0.0,
        best_valid_items=1,
        best_overflow_items=0,
        individuals=(snapshot_1,),
    )

    best_individual = Individual(
        individual_id="g1-1",
        generation_index=1,
        chromosome=Chromosome(order=("A",), rotations=(False,)),
        fitness_breakdown=breakdown_1,
        decoded_layout=layout_1,
        origin_type="elite",
        parent_ids=("g0-1",),
    )

    result = GAResult(
        best_individual=best_individual,
        final_population=(best_individual,),
        history=RunHistory(generations=[generation_0, generation_1]),
        config=GAConfig(population_size=2, max_generations=2, stagnation_limit=5, tournament_size=2),
        duration_seconds=0.03,
    )
    return problem, result


def test_main_window_playback_navigation() -> None:
    _app()
    window = MainWindow()

    problem, result = _build_problem_and_result()
    window.set_result(problem, result)

    assert window.generation_slider.maximum() == 1
    assert window.generation_model.rowCount() == 2
    assert window.timeline_label.text().startswith("Generation: 1/")

    window._on_next_generation()
    assert window.generation_slider.value() == 1
    assert window.timeline_label.text().startswith("Generation: 2/")

    window._on_prev_generation()
    assert window.generation_slider.value() == 0


def test_scene_selection_syncs_tables() -> None:
    _app()
    window = MainWindow()

    problem, result = _build_problem_and_result()
    window.set_result(problem, result)

    window._on_scene_placement_clicked(0)

    placement_rows = window.placement_table.selectionModel().selectedRows()
    gene_rows = window.gene_table.selectionModel().selectedRows()

    assert placement_rows and placement_rows[0].row() == 0
    assert gene_rows and gene_rows[0].row() == 0


def test_statistics_dialog_opens_with_population_study_and_baseline() -> None:
    _app()
    window = MainWindow()

    problem, result = _build_problem_and_result()
    window.set_result(
        problem,
        result,
        population_study=PopulationStudyResult(
            points=(
                PopulationStudyPoint(100, 5, 1, 0.25, 0, 0.1, (5, 1, 4, 0, 0), "g0-1"),
                PopulationStudyPoint(140, 6, 1, 0.25, 0, 0.2, (6, 1, 4, 0, 0), "g1-1"),
            )
        ),
        exhaustive_baseline=ExhaustiveSearchResult(
            status="completed",
            duration_seconds=0.1,
            evaluated_solutions=2,
            total_search_space=2,
            best_chromosome=result.best_individual.chromosome,
            best_fitness_breakdown=result.best_individual.fitness_breakdown,
            best_decoded_layout=result.best_individual.decoded_layout,
            reason=None,
        ),
    )

    window._on_statistics_requested()

    assert window.statistics_dialog.isVisible()
    assert window.statistics_dialog.charts_panel.history_generation_count == 2
    assert window.statistics_dialog.charts_panel.population_study_point_count == 2
    assert "exhaustive" in window.statistics_dialog.charts_panel.baseline_summary.text().lower()
