from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from knapsack2d.baseline.exhaustive import ExhaustiveSearchConfig
from knapsack2d.config import UiEnvConfig
from knapsack2d.ga.config import GAConfig
from knapsack2d.ga.history import HistoryMode
from knapsack2d.policies import VoidBlockPolicy
from knapsack2d.ui.run_models import PopulationStudyConfig
from knapsack2d.ui.widgets.settings_dialog import SettingsDialog


class ControlPanel(QWidget):
    load_task_requested = Signal()
    run_requested = Signal()
    stop_requested = Signal()
    statistics_requested = Signal()
    export_history_requested = Signal()
    export_layout_requested = Signal()
    export_report_requested = Signal()

    def __init__(self, env_config: UiEnvConfig, parent=None) -> None:
        super().__init__(parent)
        self._settings_dialog = SettingsDialog(env_config, self)

        root = QHBoxLayout(self)

        self.task_label = QLabel("Task: -")
        self.settings_summary_label = QLabel(self._settings_dialog.summary_text())

        self.settings_button = QPushButton("Settings")
        self.load_button = QPushButton("Load Task")
        self.run_button = QPushButton("Run")
        self.stop_button = QPushButton("Stop")
        self.statistics_button = QPushButton("Statistics")
        self.export_history_button = QPushButton("Export History JSON")
        self.export_layout_button = QPushButton("Export Layout PNG")
        self.export_report_button = QPushButton("Export Best Report")

        root.addWidget(self.task_label, stretch=1)
        root.addWidget(self.settings_summary_label, stretch=2)
        root.addWidget(self.settings_button)
        root.addWidget(self.load_button)
        root.addWidget(self.run_button)
        root.addWidget(self.stop_button)
        root.addWidget(self.statistics_button)
        root.addWidget(self.export_history_button)
        root.addWidget(self.export_layout_button)
        root.addWidget(self.export_report_button)

        self.stop_button.setEnabled(False)

        self.settings_button.clicked.connect(self._open_settings)
        self.load_button.clicked.connect(self.load_task_requested.emit)
        self.run_button.clicked.connect(self.run_requested.emit)
        self.stop_button.clicked.connect(self.stop_requested.emit)
        self.statistics_button.clicked.connect(self.statistics_requested.emit)
        self.export_history_button.clicked.connect(self.export_history_requested.emit)
        self.export_layout_button.clicked.connect(self.export_layout_requested.emit)
        self.export_report_button.clicked.connect(self.export_report_requested.emit)

    def set_task_name(self, name: str) -> None:
        self.task_label.setText(f"Task: {name}")

    def build_config(self) -> GAConfig:
        return self._settings_dialog.build_config()

    def population_study_config(self) -> PopulationStudyConfig:
        return self._settings_dialog.population_study_config()

    def exhaustive_config(self) -> ExhaustiveSearchConfig:
        return self._settings_dialog.exhaustive_config()

    def selected_history_mode(self) -> HistoryMode:
        return self._settings_dialog.selected_history_mode()

    def selected_void_policy(self) -> VoidBlockPolicy:
        return self._settings_dialog.selected_void_policy()

    def play_interval_ms(self) -> int:
        return self._settings_dialog.play_interval_ms()

    def set_running_state(self, is_running: bool) -> None:
        self.run_button.setEnabled(not is_running)
        self.stop_button.setEnabled(is_running)
        self.load_button.setEnabled(not is_running)
        self.settings_button.setEnabled(not is_running)

    def _open_settings(self) -> None:
        snapshot = self._settings_dialog.snapshot_state()
        if self._settings_dialog.exec() == self._settings_dialog.Accepted:
            self.settings_summary_label.setText(self._settings_dialog.summary_text())
            return
        self._settings_dialog.restore_state(snapshot)
