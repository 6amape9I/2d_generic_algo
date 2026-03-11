from __future__ import annotations

import random

from knapsack2d.ga.chromosome import Chromosome
from knapsack2d.models import ProblemInstance


def swap_mutation(chromosome: Chromosome, rng: random.Random) -> Chromosome:
    genes = list(zip(chromosome.order, chromosome.rotations, strict=True))
    if len(genes) < 2:
        return chromosome
    i, j = sorted(rng.sample(range(len(genes)), 2))
    genes[i], genes[j] = genes[j], genes[i]
    return _from_genes(genes)


def insert_mutation(chromosome: Chromosome, rng: random.Random) -> Chromosome:
    genes = list(zip(chromosome.order, chromosome.rotations, strict=True))
    if len(genes) < 2:
        return chromosome
    i, j = rng.sample(range(len(genes)), 2)
    gene = genes.pop(i)
    genes.insert(j, gene)
    return _from_genes(genes)


def inversion_mutation(chromosome: Chromosome, rng: random.Random) -> Chromosome:
    genes = list(zip(chromosome.order, chromosome.rotations, strict=True))
    if len(genes) < 2:
        return chromosome
    i, j = sorted(rng.sample(range(len(genes)), 2))
    genes[i : j + 1] = reversed(genes[i : j + 1])
    return _from_genes(genes)


def rotation_flip_mutation(
    problem: ProblemInstance,
    chromosome: Chromosome,
    rng: random.Random,
    flips_count: int = 1,
) -> Chromosome:
    genes = list(zip(chromosome.order, chromosome.rotations, strict=True))
    can_rotate = {item.item_id: item.can_rotate for item in problem.items}
    rotatable_positions = [
        idx for idx, (item_id, _) in enumerate(genes) if can_rotate.get(item_id, False)
    ]
    if not rotatable_positions:
        return chromosome

    flips = min(max(1, flips_count), len(rotatable_positions))
    for pos in rng.sample(rotatable_positions, flips):
        item_id, rotated = genes[pos]
        genes[pos] = (item_id, not rotated)

    mutated = _from_genes(genes)
    return mutated.normalized(problem)


def apply_mutations(
    problem: ProblemInstance,
    chromosome: Chromosome,
    rng: random.Random,
    p_order_mutation: float,
    p_rotation_mutation: float,
) -> tuple[Chromosome, bool]:
    mutated = chromosome
    changed = False

    if rng.random() < p_order_mutation:
        operator = rng.choice((swap_mutation, insert_mutation, inversion_mutation))
        candidate = operator(mutated, rng)
        if candidate != mutated:
            mutated = candidate
            changed = True

    if rng.random() < p_rotation_mutation:
        candidate = rotation_flip_mutation(problem, mutated, rng, flips_count=1)
        if candidate != mutated:
            mutated = candidate
            changed = True

    return mutated.normalized(problem), changed


def _from_genes(genes: list[tuple[str, bool]]) -> Chromosome:
    return Chromosome(
        order=tuple(item_id for item_id, _ in genes),
        rotations=tuple(rotated for _, rotated in genes),
    )
