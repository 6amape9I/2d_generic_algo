from __future__ import annotations

import random
import time
from dataclasses import dataclass

from knapsack2d.decoder import LeftBottomDecoder
from knapsack2d.fitness import FitnessEvaluator
from knapsack2d.ga.chromosome import Chromosome, to_sequence_solution
from knapsack2d.ga.config import GAConfig
from knapsack2d.ga.crossover import order_crossover
from knapsack2d.ga.history import RunHistory, build_generation_snapshot
from knapsack2d.ga.individual import Individual
from knapsack2d.ga.initializer import build_initial_chromosomes, random_chromosome
from knapsack2d.ga.mutation import apply_mutations
from knapsack2d.ga.selection import tournament_select
from knapsack2d.models import DecodedLayout, FitnessBreakdown, ProblemInstance


@dataclass(frozen=True)
class GAResult:
    best_individual: Individual
    final_population: tuple[Individual, ...]
    history: RunHistory
    config: GAConfig
    duration_seconds: float


class GeneticOptimizer:
    def __init__(
        self,
        config: GAConfig,
        decoder: LeftBottomDecoder,
        fitness_evaluator: FitnessEvaluator,
        rng: random.Random | None = None,
    ) -> None:
        self._config = config
        self._decoder = decoder
        self._fitness_evaluator = fitness_evaluator
        self._rng = rng or random.Random(config.seed)
        self._individual_counter = 0
        self._stop_requested = False
        self._evaluation_cache: dict[
            tuple[tuple[str, ...], tuple[bool, ...]],
            tuple[DecodedLayout, FitnessBreakdown],
        ] = {}

    def request_stop(self) -> None:
        self._stop_requested = True

    @property
    def stop_requested(self) -> bool:
        return self._stop_requested

    def run(self, problem: ProblemInstance) -> GAResult:
        run_start = time.perf_counter()
        history = RunHistory()

        init_start = time.perf_counter()
        initial_chromosomes = build_initial_chromosomes(
            problem=problem,
            population_size=self._config.population_size,
            random_ratio=self._config.initial_random_ratio,
            rng=self._rng,
        )
        population = [
            self._evaluate(
                problem=problem,
                chromosome=chromosome,
                generation_index=0,
                origin_type="init",
                parent_ids=None,
            )
            for chromosome in initial_chromosomes
        ]
        population = self._sort_population(population)
        init_ms = (time.perf_counter() - init_start) * 1000.0
        history.append(
            build_generation_snapshot(
                generation_index=0,
                generation_time_ms=init_ms,
                sorted_population=population,
                history_mode=self._config.history_mode,
                history_top_k=self._config.history_top_k,
            )
        )

        best_overall = population[0]
        stagnation_counter = 0

        if self._stop_requested or self._is_full_container(best_overall):
            return self._build_result(best_overall, population, history, run_start)

        for generation_index in range(1, self._config.max_generations):
            if self._stop_requested or self._is_time_limit_reached(run_start):
                break

            generation_start = time.perf_counter()
            population = self._evolve_generation(
                problem=problem,
                current_population=population,
                generation_index=generation_index,
            )
            population = self._sort_population(population)

            if population[0].fitness_key > best_overall.fitness_key:
                best_overall = population[0]
                stagnation_counter = 0
            else:
                stagnation_counter += 1

            if (
                self._config.enable_stagnation_immigrants
                and stagnation_counter >= self._config.stagnation_limit
                and not self._stop_requested
            ):
                population = self._inject_immigrants(
                    problem=problem,
                    population=population,
                    generation_index=generation_index,
                )
                population = self._sort_population(population)
                if population[0].fitness_key > best_overall.fitness_key:
                    best_overall = population[0]
                stagnation_counter = 0

            generation_ms = (time.perf_counter() - generation_start) * 1000.0
            history.append(
                build_generation_snapshot(
                    generation_index=generation_index,
                    generation_time_ms=generation_ms,
                    sorted_population=population,
                    history_mode=self._config.history_mode,
                    history_top_k=self._config.history_top_k,
                )
            )

            if self._is_full_container(best_overall):
                break
            if stagnation_counter >= self._config.stagnation_limit:
                break
            if self._is_time_limit_reached(run_start):
                break

        return self._build_result(best_overall, population, history, run_start)

    def _build_result(
        self,
        best_overall: Individual,
        population: list[Individual],
        history: RunHistory,
        run_start: float,
    ) -> GAResult:
        return GAResult(
            best_individual=best_overall,
            final_population=tuple(population),
            history=history,
            config=self._config,
            duration_seconds=time.perf_counter() - run_start,
        )

    def _evolve_generation(
        self,
        *,
        problem: ProblemInstance,
        current_population: list[Individual],
        generation_index: int,
    ) -> list[Individual]:
        next_population: list[Individual] = []
        signatures: set[tuple[tuple[str, ...], tuple[bool, ...]]] = set()

        elite_count = self._config.resolved_elite_count
        for elite in current_population[:elite_count]:
            clone = self._clone_individual(
                elite,
                generation_index=generation_index,
                origin_type="elite",
                parent_ids=(elite.individual_id,),
            )
            next_population.append(clone)
            signatures.add(self._chromosome_signature(clone.chromosome))

        while len(next_population) < self._config.population_size:
            if self._stop_requested:
                break

            parent_a = tournament_select(
                population=current_population,
                tournament_size=self._config.tournament_size,
                rng=self._rng,
            )
            parent_b = tournament_select(
                population=current_population,
                tournament_size=self._config.tournament_size,
                rng=self._rng,
            )

            if self._rng.random() < self._config.p_crossover:
                child_chromosome = order_crossover(
                    problem=problem,
                    parent1=parent_a.chromosome,
                    parent2=parent_b.chromosome,
                    rng=self._rng,
                )
                origin_type = "crossover"
            else:
                child_chromosome = parent_a.chromosome
                origin_type = "crossover"

            reference_layout = (
                parent_a.decoded_layout
                if parent_a.fitness_key >= parent_b.fitness_key
                else parent_b.decoded_layout
            )
            child_chromosome, changed = apply_mutations(
                problem=problem,
                chromosome=child_chromosome,
                rng=self._rng,
                p_order_mutation=self._config.p_order_mutation,
                p_rotation_mutation=self._config.p_rotation_mutation,
                reference_layout=reference_layout,
            )
            if changed:
                origin_type = "mutation"

            child_chromosome, origin_type = self._deduplicate_child(
                problem=problem,
                chromosome=child_chromosome,
                origin_type=origin_type,
                used_signatures=signatures,
            )

            child = self._evaluate(
                problem=problem,
                chromosome=child_chromosome,
                generation_index=generation_index,
                origin_type=origin_type,
                parent_ids=(parent_a.individual_id, parent_b.individual_id),
            )
            next_population.append(child)
            signatures.add(self._chromosome_signature(child.chromosome))

        if len(next_population) < self._config.population_size:
            for fallback in current_population:
                if len(next_population) >= self._config.population_size:
                    break
                signature = self._chromosome_signature(fallback.chromosome)
                clone = self._clone_individual(
                    fallback,
                    generation_index=generation_index,
                    origin_type="elite",
                    parent_ids=(fallback.individual_id,),
                )
                next_population.append(clone)
                signatures.add(signature)

        return next_population[: self._config.population_size]

    def _deduplicate_child(
        self,
        *,
        problem: ProblemInstance,
        chromosome: Chromosome,
        origin_type: str,
        used_signatures: set[tuple[tuple[str, ...], tuple[bool, ...]]],
    ) -> tuple[Chromosome, str]:
        signature = self._chromosome_signature(chromosome)
        if signature not in used_signatures:
            return chromosome, origin_type

        candidate = chromosome
        for _ in range(self._config.duplicate_retries):
            candidate, changed = apply_mutations(
                problem=problem,
                chromosome=candidate,
                rng=self._rng,
                p_order_mutation=1.0,
                p_rotation_mutation=1.0,
                reference_layout=None,
            )
            if not changed:
                continue
            candidate_signature = self._chromosome_signature(candidate)
            if candidate_signature not in used_signatures:
                return candidate, "mutation"

        if self._config.duplicate_random_immigrant:
            max_attempts = max(10, len(used_signatures) * 4)
            for _ in range(max_attempts):
                immigrant = random_chromosome(problem, self._rng)
                if self._chromosome_signature(immigrant) not in used_signatures:
                    return immigrant, "immigrant"

        return chromosome, origin_type

    def _inject_immigrants(
        self,
        *,
        problem: ProblemInstance,
        population: list[Individual],
        generation_index: int,
    ) -> list[Individual]:
        replace_count = max(
            1,
            int(self._config.population_size * self._config.stagnation_immigrant_fraction),
        )
        keep_count = max(1, len(population) - replace_count)
        kept = population[:keep_count]

        signatures = {self._chromosome_signature(ind.chromosome) for ind in kept}
        immigrants: list[Individual] = []
        attempts = 0
        max_attempts = max(20, replace_count * 20)
        while len(immigrants) < replace_count and attempts < max_attempts:
            if self._stop_requested:
                break
            chromosome = random_chromosome(problem, self._rng)
            signature = self._chromosome_signature(chromosome)
            attempts += 1
            if signature in signatures:
                continue
            signatures.add(signature)
            immigrants.append(
                self._evaluate(
                    problem=problem,
                    chromosome=chromosome,
                    generation_index=generation_index,
                    origin_type="immigrant",
                    parent_ids=None,
                )
            )

        return kept + immigrants

    def _clone_individual(
        self,
        individual: Individual,
        *,
        generation_index: int,
        origin_type: str,
        parent_ids: tuple[str, ...] | None,
    ) -> Individual:
        return Individual(
            individual_id=self._next_individual_id(generation_index),
            generation_index=generation_index,
            chromosome=individual.chromosome,
            fitness_breakdown=individual.fitness_breakdown,
            decoded_layout=individual.decoded_layout,
            origin_type=origin_type,
            parent_ids=parent_ids,
        )

    def _evaluate(
        self,
        *,
        problem: ProblemInstance,
        chromosome: Chromosome,
        generation_index: int,
        origin_type: str,
        parent_ids: tuple[str, ...] | None,
    ) -> Individual:
        normalized = chromosome.normalized(problem)
        signature = self._chromosome_signature(normalized)

        cached = self._evaluation_cache.get(signature)
        if cached is None:
            sequence = to_sequence_solution(problem, normalized)
            layout = self._decoder.decode(problem, sequence)
            fitness = self._fitness_evaluator.evaluate(problem, layout)
            self._evaluation_cache[signature] = (layout, fitness)
        else:
            layout, fitness = cached

        return Individual(
            individual_id=self._next_individual_id(generation_index),
            generation_index=generation_index,
            chromosome=normalized,
            fitness_breakdown=fitness,
            decoded_layout=layout,
            origin_type=origin_type,
            parent_ids=parent_ids,
        )

    def _next_individual_id(self, generation_index: int) -> str:
        self._individual_counter += 1
        return f"g{generation_index}-ind{self._individual_counter}"

    def _is_time_limit_reached(self, run_start: float) -> bool:
        if self._config.max_time_seconds is None:
            return False
        return (time.perf_counter() - run_start) >= self._config.max_time_seconds

    def _is_full_container(self, individual: Individual) -> bool:
        return individual.fitness_breakdown.fill_ratio >= 1.0

    def _chromosome_signature(
        self,
        chromosome: Chromosome,
    ) -> tuple[tuple[str, ...], tuple[bool, ...]]:
        return chromosome.order, chromosome.rotations

    def _sort_population(self, population: list[Individual]) -> list[Individual]:
        return sorted(population, key=lambda ind: ind.fitness_key, reverse=True)
