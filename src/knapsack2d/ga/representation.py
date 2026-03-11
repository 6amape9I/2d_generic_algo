from __future__ import annotations

from knapsack2d.models import Gene, SequenceSolution


def solution_from_ids(item_ids: list[str]) -> SequenceSolution:
    return SequenceSolution(genes=tuple(Gene(item_id=item_id) for item_id in item_ids))
