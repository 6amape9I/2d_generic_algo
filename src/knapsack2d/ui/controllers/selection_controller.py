from __future__ import annotations

from knapsack2d.ga.history import IndividualSnapshot
from knapsack2d.models import CandidatePoint, Container
from knapsack2d.ui.widgets.individual_details_panel import IndividualDetailsPanel
from knapsack2d.ui.widgets.layout_scene import LayoutScene


class SelectionController:
    def __init__(
        self,
        layout_scene: LayoutScene,
        details_panel: IndividualDetailsPanel,
    ) -> None:
        self._layout_scene = layout_scene
        self._details_panel = details_panel

    def select_individual(
        self,
        snapshot: IndividualSnapshot,
        container: Container,
        *,
        show_virtual: bool,
        show_overflow: bool,
        show_labels: bool,
        selected_placement_index: int | None,
        candidate_points: list[CandidatePoint] | None,
        show_candidate_points: bool,
    ) -> None:
        self._layout_scene.set_layout(
            snapshot.decoded_layout,
            container=container,
            show_virtual=show_virtual,
            show_overflow=show_overflow,
            show_labels=show_labels,
            selected_placement_index=selected_placement_index,
            candidate_points=candidate_points,
            show_candidate_points=show_candidate_points,
        )
        self._details_panel.set_snapshot(snapshot)
