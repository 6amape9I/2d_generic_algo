from __future__ import annotations

import random

from knapsack2d.ga.chromosome import Chromosome
from knapsack2d.models import ProblemInstance


def random_chromosome(problem: ProblemInstance, rng: random.Random) -> Chromosome:
    ids = [item.item_id for item in problem.items]
    rng.shuffle(ids)
    can_rotate = {item.item_id: item.can_rotate for item in problem.items}
    rotations = tuple(
        rng.choice((False, True)) if can_rotate[item_id] else False for item_id in ids
    )
    chromosome = Chromosome(order=tuple(ids), rotations=rotations)
    return chromosome.normalized(problem)


def heuristic_chromosomes(
    problem: ProblemInstance,
    rng: random.Random,
) -> list[Chromosome]:
    items = list(problem.items)
    unique: dict[tuple[tuple[str, ...], tuple[bool, ...]], Chromosome] = {}

    for ordered_items in _sorted_item_orders(items):
        order = tuple(item.item_id for item in ordered_items)
        no_rotation = Chromosome(
            order=order,
            rotations=tuple(False for _ in order),
        ).normalized(problem)
        unique[_signature(no_rotation)] = no_rotation

        random_rotation = Chromosome(
            order=order,
            rotations=tuple(
                rng.choice((False, True)) if item.can_rotate else False
                for item in ordered_items
            ),
        ).normalized(problem)
        unique[_signature(random_rotation)] = random_rotation

        canonical_rotation = Chromosome(
            order=order,
            rotations=tuple(
                item.can_rotate and item.width < item.height for item in ordered_items
            ),
        ).normalized(problem)
        unique[_signature(canonical_rotation)] = canonical_rotation

    return list(unique.values())


def build_initial_chromosomes(
    problem: ProblemInstance,
    population_size: int,
    random_ratio: float,
    rng: random.Random,
) -> list[Chromosome]:
    target_random = int(round(population_size * random_ratio))
    target_heuristic = population_size - target_random

    chromosomes: list[Chromosome] = []
    signatures: set[tuple[tuple[str, ...], tuple[bool, ...]]] = set()

    for chromosome in heuristic_chromosomes(problem, rng):
        if len(chromosomes) >= target_heuristic:
            break
        signature = _signature(chromosome)
        if signature in signatures:
            continue
        chromosomes.append(chromosome)
        signatures.add(signature)

    while len(chromosomes) < population_size:
        chromosome = random_chromosome(problem, rng)
        signature = _signature(chromosome)
        if signature in signatures:
            continue
        chromosomes.append(chromosome)
        signatures.add(signature)

    return chromosomes


def _signature(chromosome: Chromosome) -> tuple[tuple[str, ...], tuple[bool, ...]]:
    return chromosome.order, chromosome.rotations


def _sorted_item_orders(items: list) -> list[list]:
    strategies = [
        lambda item: item.value,
        lambda item: item.value / (item.width * item.height),
        lambda item: item.width * item.height,
        lambda item: max(item.width, item.height),
        lambda item: min(item.width, item.height),
    ]

    orders = []
    for key_fn in strategies:
        ordered = sorted(
            items,
            key=lambda item: (-key_fn(item), item.item_id),
        )
        orders.append(ordered)
    return orders
