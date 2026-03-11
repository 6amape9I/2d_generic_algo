from __future__ import annotations

from knapsack2d.ga.chromosome import Chromosome
from knapsack2d.ga.individual import Individual


def order_diversity(chromosomes: list[Chromosome]) -> float:
    if len(chromosomes) < 2:
        return 0.0

    length = len(chromosomes[0].order)
    if length == 0:
        return 0.0

    pair_count = 0
    mismatch_total = 0.0
    for i in range(len(chromosomes)):
        for j in range(i + 1, len(chromosomes)):
            pair_count += 1
            mismatches = sum(
                1
                for left, right in zip(
                    chromosomes[i].order,
                    chromosomes[j].order,
                    strict=True,
                )
                if left != right
            )
            mismatch_total += mismatches / length

    return mismatch_total / pair_count if pair_count else 0.0


def average_total_value(individuals: list[Individual]) -> float:
    return sum(ind.fitness_breakdown.total_value for ind in individuals) / len(individuals)


def average_fill_ratio(individuals: list[Individual]) -> float:
    return sum(ind.fitness_breakdown.fill_ratio for ind in individuals) / len(individuals)
