from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QSplitter,
    QTableView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from knapsack2d.baseline.exhaustive import ExhaustiveSearchResult
from knapsack2d.config import UiEnvConfig, load_ui_env_config
from knapsack2d.ga.history import GenerationSnapshot, IndividualSnapshot
from knapsack2d.ga.optimizer import GAResult
from knapsack2d.models import CandidatePoint, DecodeStep, ProblemInstance
from knapsack2d.task_io import load_problem_txt
from knapsack2d.ui.controllers.run_controller import RunController, RunRequest
from knapsack2d.ui.controllers.selection_controller import SelectionController
from knapsack2d.ui.models.gene_table_model import GeneTableModel
from knapsack2d.ui.models.generation_table_model import GenerationTableModel
from knapsack2d.ui.models.individual_table_model import IndividualTableModel
from knapsack2d.ui.models.placement_table_model import PlacementTableModel
from knapsack2d.ui.presenters.history_mapper import HistoryMapper
from knapsack2d.ui.run_models import PopulationStudyResult, RunOutcome
from knapsack2d.ui.widgets.control_panel import ControlPanel
from knapsack2d.ui.widgets.decode_steps_panel import DecodeStepsPanel
from knapsack2d.ui.widgets.individual_details_panel import IndividualDetailsPanel
from knapsack2d.ui.widgets.layout_scene import LayoutScene
from knapsack2d.ui.widgets.layout_view import LayoutView
from knapsack2d.ui.widgets.statistics_dialog import StatisticsDialog


class MainWindow(QMainWindow):
    def __init__(self, ui_env: UiEnvConfig | None = None) -> None:
        super().__init__()
        self._ui_env = ui_env or load_ui_env_config()

        self.setWindowTitle("2D Knapsack GA")
        self.resize(1840, 1040)

        self._problem: ProblemInstance | None = None
        self._problem_path: Path | None = None
        self._result: GAResult | None = None
        self._population_study: PopulationStudyResult | None = None
        self._exhaustive_baseline: ExhaustiveSearchResult | None = None
        self._mapper = HistoryMapper()

        self._current_generation_index = -1
        self._current_generation: GenerationSnapshot | None = None
        self._current_individual: IndividualSnapshot | None = None
        self._selected_placement_index: int | None = None
        self._selected_step_index: int = -1
        self._events_suspended = False

        self._play_timer = QTimer(self)
        self._play_timer.timeout.connect(self._on_play_tick)

        self.run_controller = RunController()

        self.control_panel = ControlPanel(self._ui_env)
        self.statistics_dialog = StatisticsDialog(self)

        self.generation_model = GenerationTableModel()
        self.generation_table = QTableView()
        self.generation_table.setModel(self.generation_model)

        self.individual_model = IndividualTableModel()
        self.individual_table = QTableView()
        self.individual_table.setModel(self.individual_model)

        self.layout_scene = LayoutScene(self._ui_env)
        self.layout_view = LayoutView()
        self.layout_view.setScene(self.layout_scene)

        self.details_panel = IndividualDetailsPanel()
        self.gene_model = GeneTableModel()
        self.gene_table = QTableView()
        self.gene_table.setModel(self.gene_model)

        self.placement_model = PlacementTableModel()
        self.placement_table = QTableView()
        self.placement_table.setModel(self.placement_model)

        self.decode_steps_panel = DecodeStepsPanel()

        self.show_virtual_checkbox = QCheckBox("Show virtual")
        self.show_virtual_checkbox.setChecked(True)
        self.show_overflow_checkbox = QCheckBox("Show overflow")
        self.show_overflow_checkbox.setChecked(True)
        self.show_labels_checkbox = QCheckBox("Show labels")
        self.show_labels_checkbox.setChecked(True)
        self.show_candidate_points_checkbox = QCheckBox("Show candidate points")
        self.show_candidate_points_checkbox.setChecked(False)
        self.pan_mode_checkbox = QCheckBox("Pan mode")
        self.pan_mode_checkbox.setChecked(True)

        self.zoom_fit_button = QPushButton("Fit")
        self.zoom_reset_button = QPushButton("Reset Zoom")

        self.prev_generation_button = QPushButton("Prev")
        self.next_generation_button = QPushButton("Next")
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.generation_slider = QSlider(Qt.Horizontal)
        self.generation_slider.setRange(0, 0)
        self.timeline_label = QLabel("Generation: -")

        self.selection_controller = SelectionController(
            layout_scene=self.layout_scene,
            details_panel=self.details_panel,
        )

        self._build_layout()
        self._configure_tables()
        self._wire_signals()
        self._load_default_task()

        if self._problem is None:
            self.statusBar().showMessage("Load a task (.txt) and run GA")

    def set_result(
        self,
        problem: ProblemInstance,
        result: GAResult,
        *,
        population_study: PopulationStudyResult | None = None,
        exhaustive_baseline: ExhaustiveSearchResult | None = None,
    ) -> None:
        self._problem = problem
        self._result = result
        self._population_study = population_study
        self._exhaustive_baseline = exhaustive_baseline
        self.control_panel.set_task_name(problem.name)

        generations = list(result.history.generations)
        self.generation_model.set_generations(generations)
        self.statistics_dialog.set_history(result.history)
        self.statistics_dialog.set_population_study(population_study)
        self.statistics_dialog.set_baseline_comparison(result, exhaustive_baseline)

        if not generations:
            self._clear_generation_selection()
            self.statusBar().showMessage("Run finished with empty history")
            return

        with self._suspend_events():
            self.generation_slider.setRange(0, len(generations) - 1)
        self._select_generation_index(0, sync_table=True, sync_slider=True)

        best = result.best_individual.fitness_breakdown.total_value
        study_suffix = ""
        if population_study is not None:
            study_suffix = f" Best study population: {population_study.best_point.population_size}."
        baseline_suffix = ""
        if exhaustive_baseline is not None:
            baseline_suffix = f" Exhaustive: {exhaustive_baseline.status}."
        self.statusBar().showMessage(
            f"Run finished. Best total value: {best}. Duration: {result.duration_seconds:.3f}s.{study_suffix}{baseline_suffix}"
        )

    def _build_layout(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.addWidget(self.control_panel)

        main_splitter = QSplitter(Qt.Horizontal)

        render_block = QWidget()
        render_layout = QVBoxLayout(render_block)

        view_toolbar = QHBoxLayout()
        view_toolbar.addWidget(self.zoom_fit_button)
        view_toolbar.addWidget(self.zoom_reset_button)
        view_toolbar.addWidget(self.pan_mode_checkbox)
        view_toolbar.addWidget(self.show_virtual_checkbox)
        view_toolbar.addWidget(self.show_overflow_checkbox)
        view_toolbar.addWidget(self.show_labels_checkbox)
        view_toolbar.addWidget(self.show_candidate_points_checkbox)
        view_toolbar.addStretch(1)

        legend = QLabel(
            "Legend: blue=valid, red dashed=overflow (0 value), gray=virtual blocks"
        )

        timeline_widget = QWidget()
        timeline_layout = QHBoxLayout(timeline_widget)
        timeline_layout.addWidget(self.prev_generation_button)
        timeline_layout.addWidget(self.next_generation_button)
        timeline_layout.addWidget(self.play_button)
        timeline_layout.addWidget(self.pause_button)
        timeline_layout.addWidget(self.generation_slider, stretch=1)
        timeline_layout.addWidget(self.timeline_label)

        render_layout.addLayout(view_toolbar)
        render_layout.addWidget(legend)
        render_layout.addWidget(self.layout_view, stretch=1)
        render_layout.addWidget(timeline_widget)

        info_splitter = QSplitter(Qt.Vertical)

        tables_widget = QWidget()
        tables_layout = QVBoxLayout(tables_widget)
        tables_layout.addWidget(QLabel("Generations"))
        tables_layout.addWidget(self.generation_table)
        tables_layout.addWidget(QLabel("Individuals"))
        tables_layout.addWidget(self.individual_table)

        right_tabs = QTabWidget()
        right_tabs.addTab(self.details_panel, "Details")
        right_tabs.addTab(self.gene_table, "Genes")
        right_tabs.addTab(self.placement_table, "Placements")
        right_tabs.addTab(self.decode_steps_panel, "Decode Steps")

        info_splitter.addWidget(tables_widget)
        info_splitter.addWidget(right_tabs)
        info_splitter.setStretchFactor(0, 0)
        info_splitter.setStretchFactor(1, 1)
        info_splitter.setSizes([360, 520])

        main_splitter.addWidget(render_block)
        main_splitter.addWidget(info_splitter)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 0)
        main_splitter.setSizes([1180, 620])

        root_layout.addWidget(main_splitter, stretch=1)
        self.setCentralWidget(root)

    def _configure_tables(self) -> None:
        for table in (
            self.generation_table,
            self.individual_table,
            self.gene_table,
            self.placement_table,
            self.decode_steps_panel.table,
        ):
            table.setSelectionBehavior(QAbstractItemView.SelectRows)
            table.setSelectionMode(QAbstractItemView.SingleSelection)
            table.setAlternatingRowColors(True)
            table.setSortingEnabled(False)
            header = table.horizontalHeader()
            header.setStretchLastSection(True)

    def _wire_signals(self) -> None:
        self.control_panel.load_task_requested.connect(self._on_load_task_requested)
        self.control_panel.run_requested.connect(self._on_run_requested)
        self.control_panel.stop_requested.connect(self._on_stop_requested)
        self.control_panel.statistics_requested.connect(self._on_statistics_requested)
        self.control_panel.export_history_requested.connect(self._on_export_history_requested)
        self.control_panel.export_layout_requested.connect(self._on_export_layout_requested)
        self.control_panel.export_report_requested.connect(self._on_export_report_requested)

        self.run_controller.run_started.connect(self._on_run_started)
        self.run_controller.run_finished.connect(self._on_run_finished)
        self.run_controller.run_failed.connect(self._on_run_failed)
        self.run_controller.run_stopped.connect(self._on_run_stopped)
        self.run_controller.running_state_changed.connect(self.control_panel.set_running_state)

        self.generation_table.selectionModel().selectionChanged.connect(
            lambda *_: self._on_generation_selected()
        )
        self.individual_table.selectionModel().selectionChanged.connect(
            lambda *_: self._on_individual_selected()
        )
        self.placement_table.selectionModel().selectionChanged.connect(
            lambda *_: self._on_placement_selected()
        )
        self.gene_table.selectionModel().selectionChanged.connect(
            lambda *_: self._on_gene_selected()
        )
        self.decode_steps_panel.step_selected.connect(self._on_decode_step_selected)

        self.layout_scene.placement_clicked.connect(self._on_scene_placement_clicked)
        self.layout_scene.empty_clicked.connect(self._on_scene_empty_clicked)

        self.show_virtual_checkbox.toggled.connect(self._on_view_flags_changed)
        self.show_overflow_checkbox.toggled.connect(self._on_view_flags_changed)
        self.show_labels_checkbox.toggled.connect(self._on_view_flags_changed)
        self.show_candidate_points_checkbox.toggled.connect(self._on_view_flags_changed)
        self.pan_mode_checkbox.toggled.connect(self.layout_view.set_pan_enabled)

        self.zoom_fit_button.clicked.connect(self.layout_view.fit_container)
        self.zoom_reset_button.clicked.connect(self.layout_view.reset_zoom)

        self.prev_generation_button.clicked.connect(self._on_prev_generation)
        self.next_generation_button.clicked.connect(self._on_next_generation)
        self.play_button.clicked.connect(self._on_play_requested)
        self.pause_button.clicked.connect(self._on_pause_requested)
        self.generation_slider.valueChanged.connect(self._on_generation_slider_changed)

    def _load_default_task(self) -> None:
        default_path = Path.cwd() / "data" / "tasks" / f"{self._ui_env.default_task_name}.txt"
        if default_path.exists():
            self._load_problem_file(default_path, announce=False)

    def _load_problem_file(self, path: str | Path, *, announce: bool = True) -> None:
        file_path = Path(path)
        problem = load_problem_txt(file_path)
        self._problem = problem
        self._problem_path = file_path
        self.control_panel.set_task_name(problem.name)
        if announce:
            self.statusBar().showMessage(
                f"Loaded task '{problem.name}' with {len(problem.items)} items"
            )
        else:
            self.statusBar().showMessage(
                f"Default task loaded: '{problem.name}' with {len(problem.items)} items"
            )

    def _on_load_task_requested(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Task",
            str(self._problem_path.parent) if self._problem_path else str(Path.cwd() / "data" / "tasks"),
            "Task files (*.txt);;All files (*)",
        )
        if not path:
            return

        try:
            self._load_problem_file(path)
        except Exception as exc:
            QMessageBox.critical(self, "Load Error", f"Failed to load task:\n{exc}")

    def _on_run_requested(self) -> None:
        if self._problem is None:
            QMessageBox.warning(self, "No task", "Load a task before starting GA.")
            return

        try:
            config = self.control_panel.build_config()
            population_study = self.control_panel.population_study_config()
            exhaustive_config = self.control_panel.exhaustive_config()
        except Exception as exc:
            QMessageBox.critical(self, "Invalid Config", str(exc))
            return

        request = RunRequest(
            problem=self._problem,
            config=config,
            void_block_policy=self.control_panel.selected_void_policy(),
            population_study=population_study,
            exhaustive_search=exhaustive_config,
        )

        try:
            self.run_controller.start(request)
        except RuntimeError as exc:
            QMessageBox.warning(self, "Run in progress", str(exc))

    def _on_stop_requested(self) -> None:
        self.run_controller.request_stop()
        self.statusBar().showMessage("Stop requested. Waiting for the current run to finish.")

    def _on_statistics_requested(self) -> None:
        if self._result is None:
            QMessageBox.warning(self, "No results", "Run GA before opening statistics.")
            return
        self.statistics_dialog.show()
        self.statistics_dialog.raise_()
        self.statistics_dialog.activateWindow()

    def _on_run_started(self) -> None:
        self.statusBar().showMessage("GA is running...")

    def _on_run_finished(self, problem: object, outcome: object) -> None:
        if not isinstance(problem, ProblemInstance) or not isinstance(outcome, RunOutcome):
            QMessageBox.critical(self, "Run Error", "Unexpected run result payload.")
            return
        self.set_result(
            problem,
            outcome.primary_result,
            population_study=outcome.population_study,
            exhaustive_baseline=outcome.exhaustive_baseline,
        )

    def _on_run_failed(self, error: str) -> None:
        QMessageBox.critical(self, "Run Failed", error)
        self.statusBar().showMessage("GA run failed")

    def _on_run_stopped(self) -> None:
        self.statusBar().showMessage("GA was stopped by user request")

    def _on_generation_selected(self) -> None:
        if self._events_suspended:
            return
        rows = self.generation_table.selectionModel().selectedRows()
        if not rows:
            return
        self._select_generation_index(rows[0].row(), sync_slider=True)

    def _on_generation_slider_changed(self, value: int) -> None:
        if self._events_suspended:
            return
        self._select_generation_index(value, sync_table=True)

    def _select_generation_index(
        self,
        index: int,
        *,
        sync_table: bool = False,
        sync_slider: bool = False,
    ) -> None:
        if self._result is None:
            return

        generations = self._result.history.generations
        if not generations or index < 0 or index >= len(generations):
            return

        self._current_generation_index = index
        self._current_generation = generations[index]

        if sync_table:
            self._select_table_row(self.generation_table, index)
        if sync_slider:
            with self._suspend_events():
                self.generation_slider.setValue(index)

        self.timeline_label.setText(f"Generation: {index + 1}/{len(generations)}")

        individuals = list(self._current_generation.individuals)
        self.individual_model.set_individuals(individuals)

        if not individuals:
            self._current_individual = None
            self._selected_placement_index = None
            self._selected_step_index = -1
            self.gene_model.clear()
            self.placement_model.clear()
            self.decode_steps_panel.set_steps([])
            self.layout_scene.clear()
            return

        self._select_individual_row(0, sync_table=True)

    def _on_individual_selected(self) -> None:
        if self._events_suspended:
            return
        rows = self.individual_table.selectionModel().selectedRows()
        if not rows:
            return
        self._select_individual_row(rows[0].row(), sync_table=False)

    def _select_individual_row(self, row: int, *, sync_table: bool) -> None:
        if self._current_generation is None:
            return

        individuals = list(self._current_generation.individuals)
        if row < 0 or row >= len(individuals):
            return

        self._current_individual = individuals[row]
        self._selected_placement_index = None
        self._selected_step_index = -1

        if sync_table:
            self._select_table_row(self.individual_table, row)

        if self._problem is None:
            return

        self.gene_model.set_individual(self._problem, self._current_individual)
        self.placement_model.set_placements(self._current_individual.decoded_layout.placements)
        self.decode_steps_panel.set_steps(self._current_individual.decoded_layout.steps)
        self._render_current_individual(fit_view=True)

    def _on_scene_placement_clicked(self, index: int) -> None:
        self._set_selected_placement(index, source="scene")

    def _on_scene_empty_clicked(self) -> None:
        self._set_selected_placement(None, source="scene")

    def _on_placement_selected(self) -> None:
        if self._events_suspended:
            return
        rows = self.placement_table.selectionModel().selectedRows()
        if not rows:
            self._set_selected_placement(None, source="table")
            return
        self._set_selected_placement(rows[0].row(), source="table")

    def _on_gene_selected(self) -> None:
        if self._events_suspended:
            return
        rows = self.gene_table.selectionModel().selectedRows()
        if not rows:
            return

        gene_row = rows[0].row()
        item_id = self.gene_model.item_id_at(gene_row)
        placement_row = self.placement_model.row_for_item_id(item_id)
        self._set_selected_placement(placement_row, source="gene")

    def _on_decode_step_selected(self, step_index: int) -> None:
        self._selected_step_index = step_index
        step = self._current_decode_step()
        if step is not None and step.placement is not None:
            row = self.placement_model.row_for_placement(step.placement)
            self._set_selected_placement(row, source="step", rerender=False)
        else:
            self._set_selected_placement(None, source="step", rerender=False)

        self._render_current_individual(fit_view=False)

    def _set_selected_placement(
        self,
        row: int | None,
        *,
        source: str,
        rerender: bool = True,
    ) -> None:
        self._selected_placement_index = row

        if source != "table":
            if row is None:
                with self._suspend_events():
                    self.placement_table.clearSelection()
            else:
                self._select_table_row(self.placement_table, row)

        placement = self.placement_model.placement_at(row) if row is not None else None

        if source != "gene":
            gene_row = self.gene_model.row_for_item_id(
                placement.item_id if placement is not None else None
            )
            if gene_row is None:
                with self._suspend_events():
                    self.gene_table.clearSelection()
            else:
                self._select_table_row(self.gene_table, gene_row)

        if rerender:
            self._render_current_individual(fit_view=False)

    def _on_view_flags_changed(self) -> None:
        self._render_current_individual(fit_view=False)

    def _render_current_individual(self, *, fit_view: bool) -> None:
        if self._problem is None or self._current_individual is None:
            return

        candidate_points = self._current_candidate_points()

        self.selection_controller.select_individual(
            snapshot=self._current_individual,
            container=self._problem.container,
            show_virtual=self.show_virtual_checkbox.isChecked(),
            show_overflow=self.show_overflow_checkbox.isChecked(),
            show_labels=self.show_labels_checkbox.isChecked(),
            selected_placement_index=self._selected_placement_index,
            candidate_points=candidate_points,
            show_candidate_points=self.show_candidate_points_checkbox.isChecked(),
        )

        if fit_view:
            self.layout_view.fit_container()

    def _current_candidate_points(self) -> list[CandidatePoint] | None:
        if not self.show_candidate_points_checkbox.isChecked():
            return None
        step = self._current_decode_step()
        if step is None:
            return None
        return list(step.tested_points)

    def _current_decode_step(self) -> DecodeStep | None:
        if self._selected_step_index < 0:
            return None
        return self.decode_steps_panel.model.step_at(self._selected_step_index)

    def _on_prev_generation(self) -> None:
        if self._result is None:
            return
        current = self.generation_slider.value()
        if current > self.generation_slider.minimum():
            self.generation_slider.setValue(current - 1)

    def _on_next_generation(self) -> None:
        if self._result is None:
            return
        current = self.generation_slider.value()
        if current < self.generation_slider.maximum():
            self.generation_slider.setValue(current + 1)

    def _on_play_requested(self) -> None:
        if self._result is None:
            return
        self._play_timer.start(self.control_panel.play_interval_ms())

    def _on_pause_requested(self) -> None:
        self._play_timer.stop()

    def _on_play_tick(self) -> None:
        current = self.generation_slider.value()
        if current >= self.generation_slider.maximum():
            self._play_timer.stop()
            return
        self.generation_slider.setValue(current + 1)

    def _on_export_history_requested(self) -> None:
        if self._problem is None or self._result is None:
            QMessageBox.warning(self, "No results", "Run GA before exporting history.")
            return

        default_name = f"{self._problem.name}_history.json"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export History JSON",
            str(Path.cwd() / default_name),
            "JSON files (*.json)",
        )
        if not path:
            return

        try:
            self._mapper.save_history_json(
                path,
                self._problem,
                self._result,
                population_study=self._population_study,
                exhaustive_baseline=self._exhaustive_baseline,
            )
        except Exception as exc:
            QMessageBox.critical(self, "Export Error", str(exc))
            return

        self.statusBar().showMessage(f"History exported to {path}")

    def _on_export_layout_requested(self) -> None:
        if self._current_individual is None:
            QMessageBox.warning(self, "No selection", "Select an individual to export layout.")
            return

        default_name = f"{self._current_individual.individual_id}_layout.png"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Layout PNG",
            str(Path.cwd() / default_name),
            "PNG files (*.png)",
        )
        if not path:
            return

        try:
            self.layout_scene.save_png(path)
        except Exception as exc:
            QMessageBox.critical(self, "Export Error", str(exc))
            return

        self.statusBar().showMessage(f"Layout exported to {path}")

    def _on_export_report_requested(self) -> None:
        if self._problem is None or self._result is None:
            QMessageBox.warning(self, "No results", "Run GA before exporting report.")
            return

        default_name = f"{self._problem.name}_best_report.json"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Best Report",
            str(Path.cwd() / default_name),
            "JSON files (*.json);;Text files (*.txt)",
        )
        if not path:
            return

        try:
            self._mapper.save_best_report(path, self._problem, self._result)
        except Exception as exc:
            QMessageBox.critical(self, "Export Error", str(exc))
            return

        self.statusBar().showMessage(f"Best report exported to {path}")

    def _select_table_row(self, table: QTableView, row: int) -> None:
        model = table.model()
        if model is None:
            return
        if row < 0 or row >= model.rowCount():
            return
        with self._suspend_events():
            table.selectRow(row)

    def _clear_generation_selection(self) -> None:
        self._current_generation_index = -1
        self._current_generation = None
        self._current_individual = None
        self._selected_placement_index = None
        self._selected_step_index = -1
        with self._suspend_events():
            self.generation_slider.setRange(0, 0)
            self.generation_slider.setValue(0)
            self.generation_table.clearSelection()
            self.individual_table.clearSelection()
        self.gene_model.clear()
        self.placement_model.clear()
        self.decode_steps_panel.set_steps([])
        self.layout_scene.clear()
        self.timeline_label.setText("Generation: -")

    @contextmanager
    def _suspend_events(self):
        previous = self._events_suspended
        self._events_suspended = True
        try:
            yield
        finally:
            self._events_suspended = previous

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt API
        self._play_timer.stop()
        if self.run_controller.is_running:
            self.run_controller.request_stop()
        self.statistics_dialog.close()
        super().closeEvent(event)
