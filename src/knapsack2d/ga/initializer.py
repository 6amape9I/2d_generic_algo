from __future__ import annotations

from random import Random

from knapsack2d.models import Gene, ProblemInstance, SequenceSolution


def random_solution(problem: ProblemInstance, rng: Random | None = None) -> SequenceSolution:
    generator = rng or Random()
    ids = [item.item_id for item in problem.items]
    generator.shuffle(ids)
    genes = tuple(Gene(item_id=item_id, rotated=False) for item_id in ids)
    return SequenceSolution(genes=genes)
