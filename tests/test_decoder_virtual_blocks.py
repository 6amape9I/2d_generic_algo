from __future__ import annotations

from knapsack2d.decoder import LeftBottomDecoder
from knapsack2d.models import Gene, SequenceSolution
from knapsack2d.policies import VoidBlockPolicy
from knapsack2d.task_builder import ProblemBuilder


def test_virtual_blocks_are_marked_and_id_is_none() -> None:
    problem = (
        ProblemBuilder()
        .set_name("virtual")
        .set_container(2, 6)
        .add_item("A", 2, 2, 4)
        .add_item("B", 3, 2, 5)
        .build()
    )
    decoder = LeftBottomDecoder(void_block_policy=VoidBlockPolicy.SIMPLE_BOTTOM_GAPS)

    layout = decoder.decode(
        problem,
        SequenceSolution(genes=(Gene("A"), Gene("B"))),
    )

    virtuals = [p for p in layout.placements if p.is_virtual]

    assert virtuals
    assert all(v.item_id is None for v in virtuals)
    assert all(v.value == 0 for v in virtuals)
