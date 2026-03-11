from __future__ import annotations

from knapsack2d.geometry import (
    is_fully_inside_container,
    oriented_size,
    rects_overlap,
)
from knapsack2d.models import Container, Item, Placement


def test_rects_overlap_detects_intersection() -> None:
    a = Placement("A", 0, 0, 2, 2, False, 1)
    b = Placement("B", 1, 1, 2, 2, False, 1)

    assert rects_overlap(a, b)


def test_rects_touching_edges_do_not_overlap() -> None:
    a = Placement("A", 0, 0, 2, 2, False, 1)
    b = Placement("B", 2, 0, 2, 2, False, 1)

    assert not rects_overlap(a, b)


def test_oriented_size_respects_can_rotate() -> None:
    rotatable = Item("A", 3, 5, 1, can_rotate=True)
    fixed = Item("B", 3, 5, 1, can_rotate=False)

    assert oriented_size(rotatable, rotated=True) == (5, 3)
    assert oriented_size(fixed, rotated=True) == (3, 5)


def test_inside_container_check() -> None:
    container = Container(4, 4)
    inside = Placement("A", 1, 1, 2, 2, False, 1)
    outside = Placement("B", 3, 1, 2, 2, False, 1)

    assert is_fully_inside_container(inside, container)
    assert not is_fully_inside_container(outside, container)
