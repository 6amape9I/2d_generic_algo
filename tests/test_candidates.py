from __future__ import annotations

from knapsack2d.candidates import CandidateManager
from knapsack2d.models import CandidatePoint, Placement


def test_candidate_manager_starts_from_origin() -> None:
    manager = CandidateManager()

    assert manager.next_points() == [CandidatePoint(0, 0)]


def test_candidate_manager_updates_after_placement() -> None:
    manager = CandidateManager()
    placement = Placement("A", 0, 0, 2, 2, False, 1)

    manager.add_points_from_placement(placement)

    assert manager.next_points() == [CandidatePoint(2, 0), CandidatePoint(0, 2)]


def test_candidate_manager_deduplicates_points() -> None:
    manager = CandidateManager()
    manager.add_point(CandidatePoint(0, 0))
    manager.add_point(CandidatePoint(0, 0))

    assert manager.next_points() == [CandidatePoint(0, 0)]
