from __future__ import annotations

from dataclasses import dataclass

from knapsack2d.models import Gene, ProblemInstance, SequenceSolution


@dataclass(frozen=True)
class Chromosome:
    order: tuple[str, ...]
    rotations: tuple[bool, ...]

    def validate_for_problem(self, problem: ProblemInstance) -> None:
        item_ids = {item.item_id for item in problem.items}
        if len(self.order) != len(problem.items):
            raise ValueError("chromosome order length must match number of items")
        if len(self.rotations) != len(problem.items):
            raise ValueError("chromosome rotations length must match number of items")
        if len(set(self.order)) != len(self.order):
            raise ValueError("chromosome order must contain unique item_ids")
        if set(self.order) != item_ids:
            raise ValueError("chromosome must contain exactly problem item_ids")

    def normalized(self, problem: ProblemInstance) -> "Chromosome":
        self.validate_for_problem(problem)
        can_rotate_map = {item.item_id: item.can_rotate for item in problem.items}
        fixed_rotations = tuple(
            rot if can_rotate_map[item_id] else False
            for item_id, rot in zip(self.order, self.rotations, strict=True)
        )
        return Chromosome(order=self.order, rotations=fixed_rotations)


def to_sequence_solution(
    problem: ProblemInstance,
    chromosome: Chromosome,
) -> SequenceSolution:
    normalized = chromosome.normalized(problem)
    genes = tuple(
        Gene(item_id=item_id, rotated=rotated)
        for item_id, rotated in zip(normalized.order, normalized.rotations, strict=True)
    )
    return SequenceSolution(genes=genes)
