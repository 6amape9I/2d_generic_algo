from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable

from PySide6.QtCore import QObject, QThread, Signal, Slot

from knapsack2d.baseline.exhaustive import ExhaustiveSearchConfig, run_exhaustive_search
from knapsack2d.decoder import LeftBottomDecoder
from knapsack2d.fitness import FitnessEvaluator
from knapsack2d.ga.config import GAConfig
from knapsack2d.ga.optimizer import GAResult, GeneticOptimizer
from knapsack2d.models import ProblemInstance
from knapsack2d.policies import VoidBlockPolicy
from knapsack2d.ui.run_models import (
    PopulationStudyConfig,
    PopulationStudyPoint,
    PopulationStudyResult,
    RunOutcome,
)


@dataclass(frozen=True)
class RunRequest:
    problem: ProblemInstance
    config: GAConfig
    void_block_policy: VoidBlockPolicy
    population_study: PopulationStudyConfig | None = None
    exhaustive_search: ExhaustiveSearchConfig | None = None


def execute_run_request(
    request: RunRequest,
    *,
    stop_requested: Callable[[], bool] | None = None,
) -> RunOutcome:
    should_stop = stop_requested or (lambda: False)

    if request.population_study is not None and request.population_study.enabled:
        results: list[tuple[int, GAResult]] = []
        points: list[PopulationStudyPoint] = []

        for population_size in request.population_study.population_sizes:
            config = replace(request.config, population_size=population_size)
            result = _run_single(request.problem, config, request.void_block_policy, should_stop)
            results.append((population_size, result))
            points.append(_study_point_from_result(population_size, result))
            if should_stop():
                break

        best_result = max(
            results,
            key=lambda pair: pair[1].best_individual.fitness_key,
        )[1]
        exhaustive_result = _run_exhaustive_if_enabled(request, should_stop)
        study = PopulationStudyResult(points=tuple(points))
        return RunOutcome(
            primary_result=best_result,
            population_study=study,
            exhaustive_baseline=exhaustive_result,
        )

    result = _run_single(request.problem, request.config, request.void_block_policy, should_stop)
    exhaustive_result = _run_exhaustive_if_enabled(request, should_stop)
    return RunOutcome(
        primary_result=result,
        population_study=None,
        exhaustive_baseline=exhaustive_result,
    )


def _run_single(
    problem: ProblemInstance,
    config: GAConfig,
    void_block_policy: VoidBlockPolicy,
    stop_requested: Callable[[], bool],
) -> GAResult:
    decoder = LeftBottomDecoder(void_block_policy=void_block_policy)
    evaluator = FitnessEvaluator()
    optimizer = GeneticOptimizer(
        config=config,
        decoder=decoder,
        fitness_evaluator=evaluator,
    )
    if stop_requested():
        optimizer.request_stop()
    return optimizer.run(problem)


def _run_exhaustive_if_enabled(
    request: RunRequest,
    stop_requested: Callable[[], bool],
):
    config = request.exhaustive_search
    if config is None or not config.enabled or stop_requested():
        return None
    decoder = LeftBottomDecoder(void_block_policy=request.void_block_policy)
    evaluator = FitnessEvaluator()
    return run_exhaustive_search(request.problem, decoder, evaluator, config)


def _study_point_from_result(population_size: int, result: GAResult) -> PopulationStudyPoint:
    best = result.best_individual
    breakdown = best.fitness_breakdown
    return PopulationStudyPoint(
        population_size=population_size,
        best_total_value=breakdown.total_value,
        best_valid_items=breakdown.valid_items_count,
        best_fill_ratio=breakdown.fill_ratio,
        best_overflow_items=breakdown.overflow_items_count,
        duration_seconds=result.duration_seconds,
        fitness_key=best.fitness_key,
        best_individual_id=best.individual_id,
    )


class _GARunWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, request: RunRequest) -> None:
        super().__init__()
        self._request = request
        self._stop_requested = False

    @Slot()
    def run(self) -> None:
        try:
            outcome = execute_run_request(
                self._request,
                stop_requested=lambda: self._stop_requested,
            )
            self.finished.emit(outcome)
        except Exception as exc:  # pragma: no cover - defensive path
            self.failed.emit(str(exc))

    def request_stop(self) -> None:
        self._stop_requested = True

    @property
    def stop_requested(self) -> bool:
        return self._stop_requested


class RunController(QObject):
    run_started = Signal()
    run_finished = Signal(object, object)
    run_failed = Signal(str)
    run_stopped = Signal()
    running_state_changed = Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self._thread: QThread | None = None
        self._worker: _GARunWorker | None = None
        self._request: RunRequest | None = None

    def start(self, request: RunRequest) -> None:
        if self.is_running:
            raise RuntimeError("GA run is already in progress")

        self._request = request
        self._thread = QThread()
        self._worker = _GARunWorker(request)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.failed.connect(self._on_worker_failed)

        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._on_thread_finished)

        self.run_started.emit()
        self.running_state_changed.emit(True)
        self._thread.start()

    def request_stop(self) -> None:
        if self._worker is not None:
            self._worker.request_stop()

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.isRunning()

    @Slot(object)
    def _on_worker_finished(self, outcome: object) -> None:
        if self._request is None:
            return
        request = self._request
        if self._worker is not None and self._worker.stop_requested:
            self.run_stopped.emit()
        self.run_finished.emit(request.problem, outcome)

    @Slot(str)
    def _on_worker_failed(self, message: str) -> None:
        self.run_failed.emit(message)

    @Slot()
    def _on_thread_finished(self) -> None:
        if self._worker is not None:
            self._worker.deleteLater()
        if self._thread is not None:
            self._thread.deleteLater()
        self._worker = None
        self._thread = None
        self._request = None
        self.running_state_changed.emit(False)
