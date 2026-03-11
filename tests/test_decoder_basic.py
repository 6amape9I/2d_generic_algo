from __future__ import annotations

from knapsack2d.decoder import LeftBottomDecoder
from knapsack2d.geometry import rects_overlap
from knapsack2d.models import Gene, SequenceSolution
from knapsack2d.task_builder import ProblemBuilder


def test_single_item_is_placed_at_origin() -> None:
    problem = (
        ProblemBuilder()
        .set_name("single")
        .set_container(10, 10)
        .add_item("A", 3, 2, 8)
        .build()
    )
    decoder = LeftBottomDecoder()

    layout = decoder.decode(problem, SequenceSolution(genes=(Gene("A"),)))

    assert len(layout.placements) == 1
    placement = layout.placements[0]
    assert placement.item_id == "A"
    assert (placement.x, placement.y) == (0, 0)


def test_two_items_do_not_overlap() -> None:
    problem = (
        ProblemBuilder()
        .set_name("no-overlap")
        .set_container(6, 4)
        .add_item("A", 2, 2, 5)
        .add_item("B", 2, 2, 7)
        .build()
    )
    decoder = LeftBottomDecoder()

    layout = decoder.decode(
        problem,
        SequenceSolution(genes=(Gene("A"), Gene("B"))),
    )

    real = [p for p in layout.placements if not p.is_virtual]
    assert len(real) == 2
    assert not rects_overlap(real[0], real[1])


def test_solution_order_changes_layout() -> None:
    problem = (
        ProblemBuilder()
        .set_name("order")
        .set_container(5, 4)
        .add_item("A", 3, 2, 5)
        .add_item("B", 2, 2, 7)
        .build()
    )
    decoder = LeftBottomDecoder()

    layout_ab = decoder.decode(
        problem,
        SequenceSolution(genes=(Gene("A"), Gene("B"))),
    )
    layout_ba = decoder.decode(
        problem,
        SequenceSolution(genes=(Gene("B"), Gene("A"))),
    )

    coords_ab = tuple((p.item_id, p.x, p.y) for p in layout_ab.placements if not p.is_virtual)
    coords_ba = tuple((p.item_id, p.x, p.y) for p in layout_ba.placements if not p.is_virtual)

    assert coords_ab != coords_ba
