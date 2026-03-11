from __future__ import annotations

from knapsack2d.decoder import LeftBottomDecoder
from knapsack2d.geometry import is_fully_inside_container
from knapsack2d.models import Gene, SequenceSolution
from knapsack2d.task_builder import ProblemBuilder


def test_overflow_placement_is_kept_in_layout() -> None:
    problem = (
        ProblemBuilder()
        .set_name("overflow")
        .set_container(4, 4)
        .add_item("A", 5, 2, 10)
        .build()
    )
    decoder = LeftBottomDecoder()

    layout = decoder.decode(problem, SequenceSolution(genes=(Gene("A"),)))

    assert len(layout.placements) == 1
    placement = layout.placements[0]
    assert placement.item_id == "A"
    assert not is_fully_inside_container(placement, problem.container)
