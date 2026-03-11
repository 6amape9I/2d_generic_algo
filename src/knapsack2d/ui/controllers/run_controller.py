from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, QThread, Signal, Slot

from knapsack2d.decoder import LeftBottomDecoder
from knapsack2d.fitness import FitnessEvaluator
from knapsack2d.ga.config import GAConfig
from knapsack2d.ga.optimizer import GAResult, GeneticOptimizer
from knapsack2d.models import ProblemInstance
from knapsack2d.policies import VoidBlockPolicy


@dataclass(frozen=True)
class RunRequest:
    problem: ProblemInstance
    config: GAConfig
    void_block_policy: VoidBlockPolicy


class _GARunWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, request: RunRequest) -> None:
        super().__init__()
        self._request = request
        self._stop_requested = False
        self._optimizer: GeneticOptimizer | None = None

    @Slot()
    def run(self) -> None:
        try:
            decoder = LeftBottomDecoder(void_block_policy=self._request.void_block_policy)
            evaluator = FitnessEvaluator()
            optimizer = GeneticOptimizer(
                config=self._request.config,
                decoder=decoder,
                fitness_evaluator=evaluator,
            )
            self._optimizer = optimizer
            if self._stop_requested:
                optimizer.request_stop()
            result = optimizer.run(self._request.problem)
            self.finished.emit(result)
        except Exception as exc:  # pragma: no cover - defensive path
            self.failed.emit(str(exc))

    def request_stop(self) -> None:
        self._stop_requested = True
        if self._optimizer is not None:
            self._optimizer.request_stop()

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
    def _on_worker_finished(self, result: object) -> None:
        if self._request is None:
            return
        request = self._request
        if self._worker is not None and self._worker.stop_requested:
            self.run_stopped.emit()
        self.run_finished.emit(request.problem, result)

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
