from __future__ import annotations

import random

from knapsack2d.ga.chromosome import Chromosome
from knapsack2d.geometry import is_fully_inside_container
from knapsack2d.models import DecodedLayout, ProblemInstance


def swap_mutation(
    chromosome: Chromosome,
    rng: random.Random,
    preferred_positions: list[int] | None = None,
) -> Chromosome:
    genes = list(zip(chromosome.order, chromosome.rotations, strict=True))
    if len(genes) < 2:
        return chromosome
    i = _pick_primary_index(len(genes), rng, preferred_positions)
    candidate_positions = [pos for pos in range(len(genes)) if pos != i]
    j = rng.choice(candidate_positions)
    if i > j:
        i, j = j, i
    genes[i], genes[j] = genes[j], genes[i]
    return _from_genes(genes)


def insert_mutation(
    chromosome: Chromosome,
    rng: random.Random,
    preferred_positions: list[int] | None = None,
) -> Chromosome:
    genes = list(zip(chromosome.order, chromosome.rotations, strict=True))
    if len(genes) < 2:
        return chromosome
    i = _pick_primary_index(len(genes), rng, preferred_positions)
    candidate_positions = [pos for pos in range(len(genes)) if pos != i]
    j = rng.choice(candidate_positions)
    gene = genes.pop(i)
    genes.insert(j, gene)
    return _from_genes(genes)


def inversion_mutation(
    chromosome: Chromosome,
    rng: random.Random,
    preferred_positions: list[int] | None = None,
) -> Chromosome:
    genes = list(zip(chromosome.order, chromosome.rotations, strict=True))
    if len(genes) < 2:
        return chromosome
    anchor = _pick_primary_index(len(genes), rng, preferred_positions)
    partner_choices = [pos for pos in range(len(genes)) if pos != anchor]
    partner = rng.choice(partner_choices)
    i, j = sorted((anchor, partner))
    genes[i : j + 1] = reversed(genes[i : j + 1])
    return _from_genes(genes)


def rotation_flip_mutation(
    problem: ProblemInstance,
    chromosome: Chromosome,
    rng: random.Random,
    flips_count: int = 1,
    preferred_item_ids: set[str] | None = None,
) -> Chromosome:
    genes = list(zip(chromosome.order, chromosome.rotations, strict=True))
    can_rotate = {item.item_id: item.can_rotate for item in problem.items}
    rotatable_positions = [
        idx for idx, (item_id, _) in enumerate(genes) if can_rotate.get(item_id, False)
    ]
    if not rotatable_positions:
        return chromosome

    preferred_positions = [
        idx
        for idx in rotatable_positions
        if preferred_item_ids is not None and genes[idx][0] in preferred_item_ids
    ]
    base_positions = preferred_positions or rotatable_positions

    flips = min(max(1, flips_count), len(base_positions))
    for pos in rng.sample(base_positions, flips):
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
    reference_layout: DecodedLayout | None = None,
) -> tuple[Chromosome, bool]:
    mutated = chromosome
    changed = False
    preferred_item_ids = _gap_neighbor_item_ids(problem, reference_layout)

    if rng.random() < p_order_mutation:
        operator = rng.choice((swap_mutation, insert_mutation, inversion_mutation))
        candidate = operator(
            mutated,
            rng,
            preferred_positions=_preferred_positions(mutated, preferred_item_ids),
        )
        if candidate != mutated:
            mutated = candidate
            changed = True

    if rng.random() < p_rotation_mutation:
        candidate = rotation_flip_mutation(
            problem,
            mutated,
            rng,
            flips_count=1,
            preferred_item_ids=preferred_item_ids,
        )
        if candidate != mutated:
            mutated = candidate
            changed = True

    return mutated.normalized(problem), changed


def _preferred_positions(chromosome: Chromosome, preferred_item_ids: set[str]) -> list[int] | None:
    if not preferred_item_ids:
        return None
    positions = [idx for idx, item_id in enumerate(chromosome.order) if item_id in preferred_item_ids]
    return positions or None


def _gap_neighbor_item_ids(
    problem: ProblemInstance,
    layout: DecodedLayout | None,
) -> set[str]:
    if layout is None:
        return set()

    width = problem.container.width
    height = problem.container.height
    occupancy: list[list[str | None]] = [[None for _ in range(width)] for _ in range(height)]
    candidate_item_ids: set[str] = set()

    for placement in layout.placements:
        if placement.is_virtual or placement.item_id is None:
            continue
        if not is_fully_inside_container(placement, problem.container):
            candidate_item_ids.add(placement.item_id)
            continue
        for y in range(placement.y, placement.y + placement.height):
            row = occupancy[y]
            for x in range(placement.x, placement.x + placement.width):
                row[x] = placement.item_id

    for y in range(height):
        for x in range(width):
            if occupancy[y][x] is not None:
                continue
            if x > 0 and occupancy[y][x - 1] is not None:
                candidate_item_ids.add(occupancy[y][x - 1])
            if x + 1 < width and occupancy[y][x + 1] is not None:
                candidate_item_ids.add(occupancy[y][x + 1])
            if y > 0 and occupancy[y - 1][x] is not None:
                candidate_item_ids.add(occupancy[y - 1][x])
            if y + 1 < height and occupancy[y + 1][x] is not None:
                candidate_item_ids.add(occupancy[y + 1][x])

    return {item_id for item_id in candidate_item_ids if item_id is not None}


def _pick_primary_index(
    length: int,
    rng: random.Random,
    preferred_positions: list[int] | None,
) -> int:
    if preferred_positions and rng.random() < 0.8:
        return rng.choice(preferred_positions)
    return rng.randrange(length)


def _from_genes(genes: list[tuple[str, bool]]) -> Chromosome:
    return Chromosome(
        order=tuple(item_id for item_id, _ in genes),
        rotations=tuple(rotated for _, rotated in genes),
    )
