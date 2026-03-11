from __future__ import annotations

import json
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from knapsack2d.ga.history import GenerationSnapshot, IndividualSnapshot, RunHistory
from knapsack2d.ga.optimizer import GAResult
from knapsack2d.models import ProblemInstance


@dataclass(frozen=True)
class GenerationRow:
    generation_index: int
    best_value: int
    avg_value: float
    best_fill_percent: float
    diversity: float
    best_valid: int
    best_overflow: int
    elapsed_ms: float


@dataclass(frozen=True)
class IndividualRow:
    rank: int
    value: int
    fill_percent: float
    valid: int
    overflow: int
    origin: str
    parents: str


class HistoryMapper:
    def generation_rows(self, history: RunHistory) -> list[GenerationRow]:
        return [self._generation_row(snapshot) for snapshot in history.generations]

    def individual_rows(self, generation: GenerationSnapshot) -> list[IndividualRow]:
        rows: list[IndividualRow] = []
        for snapshot in generation.individuals:
            rows.append(self._individual_row(snapshot))
        return rows

    def build_history_export(
        self,
        problem: ProblemInstance,
        result: GAResult,
    ) -> dict[str, Any]:
        payload = {
            "problem": {
                "name": problem.name,
                "container": {
                    "width": problem.container.width,
                    "height": problem.container.height,
                },
                "items": [asdict(item) for item in problem.items],
            },
            "ga_config": asdict(result.config),
            "duration_seconds": result.duration_seconds,
            "generation_summaries": [
                {
                    "generation_index": generation.generation_index,
                    "best_total_value": generation.best_total_value,
                    "avg_total_value": generation.avg_total_value,
                    "best_fill_ratio": generation.best_fill_ratio,
                    "diversity": generation.diversity,
                    "best_valid_items": generation.best_valid_items,
                    "best_overflow_items": generation.best_overflow_items,
                    "generation_time_ms": generation.generation_time_ms,
                }
                for generation in result.history.generations
            ],
            "saved_generations": [asdict(generation) for generation in result.history.generations],
            "best_solution_overall": {
                "individual_id": result.best_individual.individual_id,
                "generation_index": result.best_individual.generation_index,
                "origin_type": result.best_individual.origin_type,
                "parent_ids": result.best_individual.parent_ids,
                "fitness_breakdown": asdict(result.best_individual.fitness_breakdown),
                "chromosome": {
                    "order": list(result.best_individual.chromosome.order),
                    "rotations": list(result.best_individual.chromosome.rotations),
                },
                "decoded_layout": asdict(result.best_individual.decoded_layout),
            },
        }
        return _json_ready(payload)

    def build_best_report(
        self,
        problem: ProblemInstance,
        result: GAResult,
    ) -> dict[str, Any]:
        best = result.best_individual
        return _json_ready(
            {
                "problem_name": problem.name,
                "duration_seconds": result.duration_seconds,
                "best_individual_id": best.individual_id,
                "best_generation_index": best.generation_index,
                "origin_type": best.origin_type,
                "parent_ids": best.parent_ids,
                "fitness_key": list(best.fitness_key),
                "fitness_breakdown": asdict(best.fitness_breakdown),
                "chromosome": {
                    "order": list(best.chromosome.order),
                    "rotations": list(best.chromosome.rotations),
                },
                "placements_count": len(best.decoded_layout.placements),
                "steps_count": len(best.decoded_layout.steps),
            }
        )

    def save_history_json(
        self,
        path: str | Path,
        problem: ProblemInstance,
        result: GAResult,
    ) -> None:
        payload = self.build_history_export(problem, result)
        Path(path).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def save_best_report(
        self,
        path: str | Path,
        problem: ProblemInstance,
        result: GAResult,
    ) -> None:
        file_path = Path(path)
        report = self.build_best_report(problem, result)

        if file_path.suffix.lower() == ".txt":
            lines = [
                f"Problem: {report['problem_name']}",
                f"Duration seconds: {report['duration_seconds']:.4f}",
                f"Best individual: {report['best_individual_id']}",
                f"Generation: {report['best_generation_index']}",
                f"Origin: {report['origin_type']}",
                f"Fitness key: {report['fitness_key']}",
                f"Fitness: {report['fitness_breakdown']}",
                f"Chromosome order: {report['chromosome']['order']}",
                f"Chromosome rotations: {report['chromosome']['rotations']}",
            ]
            file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return

        file_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _generation_row(self, snapshot: GenerationSnapshot) -> GenerationRow:
        return GenerationRow(
            generation_index=snapshot.generation_index,
            best_value=snapshot.best_total_value,
            avg_value=snapshot.avg_total_value,
            best_fill_percent=snapshot.best_fill_ratio * 100.0,
            diversity=snapshot.diversity,
            best_valid=snapshot.best_valid_items,
            best_overflow=snapshot.best_overflow_items,
            elapsed_ms=snapshot.generation_time_ms,
        )

    def _individual_row(self, snapshot: IndividualSnapshot) -> IndividualRow:
        parents = ""
        if snapshot.parent_ids:
            parents = ",".join(snapshot.parent_ids)

        breakdown = snapshot.fitness_breakdown
        return IndividualRow(
            rank=snapshot.rank_in_generation,
            value=breakdown.total_value,
            fill_percent=breakdown.fill_ratio * 100.0,
            valid=breakdown.valid_items_count,
            overflow=breakdown.overflow_items_count,
            origin=snapshot.origin_type,
            parents=parents,
        )


def _json_ready(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _json_ready(asdict(value))
    if isinstance(value, dict):
        return {str(key): _json_ready(inner) for key, inner in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_ready(inner) for inner in value]
    return value
