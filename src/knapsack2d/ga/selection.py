from __future__ import annotations

import random

from knapsack2d.ga.individual import Individual


def tournament_select(
    population: list[Individual],
    tournament_size: int,
    rng: random.Random,
) -> Individual:
    if not population:
        raise ValueError("population cannot be empty")

    size = min(tournament_size, len(population))
    candidates = rng.sample(population, size)
    return max(candidates, key=lambda individual: individual.fitness_key)
