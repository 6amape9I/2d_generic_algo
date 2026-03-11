from __future__ import annotations

import os
import sys

from PySide6.QtWidgets import QApplication

from knapsack2d.ga.history import IndividualSnapshot
from knapsack2d.models import Container, DecodedLayout, FitnessBreakdown, Placement
from knapsack2d.ui.controllers.selection_controller import SelectionController
from knapsack2d.ui.widgets.individual_details_panel import IndividualDetailsPanel
from knapsack2d.ui.widgets.layout_scene import LayoutScene

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_selection_updates_scene_and_details() -> None:
    _app()
    scene = LayoutScene()
    details = IndividualDetailsPanel()
    controller = SelectionController(scene, details)

    snapshot = IndividualSnapshot(
        individual_id="ind-7",
        generation_index=1,
        rank_in_generation=1,
        chromosome_order=("A",),
        chromosome_rotations=(False,),
        fitness_breakdown=FitnessBreakdown(
            total_value=13,
            packed_items_count=1,
            valid_items_count=1,
            overflow_items_count=0,
            virtual_blocks_count=0,
            used_area_inside=4,
            fill_ratio=0.25,
        ),
        decoded_layout=DecodedLayout(
            placements=[Placement("A", 0, 0, 2, 2, False, 13)],
            steps=[],
            used_solution_order=["A"],
        ),
        origin_type="init",
        parent_ids=None,
    )

    controller.select_individual(
        snapshot,
        Container(4, 4),
        show_virtual=True,
        show_overflow=True,
        show_labels=True,
        selected_placement_index=None,
        candidate_points=None,
        show_candidate_points=False,
    )

    assert scene.placement_items_count() == 1
    assert details.total_value.text() == "13"
