from __future__ import annotations

import pytest

from knapsack2d.models import CandidatePoint, Container, Placement


def test_container_dimensions_must_be_positive() -> None:
    with pytest.raises(ValueError):
        Container(width=0, height=5)


def test_virtual_placement_must_have_none_id_and_zero_value() -> None:
    with pytest.raises(ValueError):
        Placement(
            item_id="A",
            x=0,
            y=0,
            width=1,
            height=1,
            rotated=False,
            value=0,
            is_virtual=True,
        )


def test_candidate_point_non_negative() -> None:
    with pytest.raises(ValueError):
        CandidatePoint(x=-1, y=0)
