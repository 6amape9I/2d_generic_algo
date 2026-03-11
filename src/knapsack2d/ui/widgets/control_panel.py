from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QWidget,
)

from knapsack2d.ga.config import GAConfig
from knapsack2d.ga.history import HistoryMode
from knapsack2d.policies import VoidBlockPolicy


class ControlPanel(QWidget):
    load_task_requested = Signal()
    run_requested = Signal()
    stop_requested = Signal()
    export_history_requested = Signal()
    export_layout_requested = Signal()
    export_report_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        root = QHBoxLayout(self)

        controls_grid = QGridLayout()
        root.addLayout(controls_grid)

        self.population_spin = QSpinBox()
        self.population_spin.setRange(2, 10_000)
        self.population_spin.setValue(60)

        self.generations_spin = QSpinBox()
        self.generations_spin.setRange(1, 100_000)
        self.generations_spin.setValue(60)

        self.stagnation_spin = QSpinBox()
        self.stagnation_spin.setRange(1, 100_000)
        self.stagnation_spin.setValue(20)

        self.tournament_spin = QSpinBox()
        self.tournament_spin.setRange(2, 100)
        self.tournament_spin.setValue(3)

        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(0, 2_147_483_647)
        self.seed_spin.setValue(42)

        self.max_time_spin = QDoubleSpinBox()
        self.max_time_spin.setRange(0.0, 86400.0)
        self.max_time_spin.setDecimals(1)
        self.max_time_spin.setSingleStep(1.0)
        self.max_time_spin.setValue(0.0)
        self.max_time_spin.setSuffix(" s")

        self.p_crossover_spin = QDoubleSpinBox()
        self.p_crossover_spin.setRange(0.0, 1.0)
        self.p_crossover_spin.setSingleStep(0.01)
        self.p_crossover_spin.setDecimals(2)
        self.p_crossover_spin.setValue(0.9)

        self.p_order_mutation_spin = QDoubleSpinBox()
        self.p_order_mutation_spin.setRange(0.0, 1.0)
        self.p_order_mutation_spin.setSingleStep(0.01)
        self.p_order_mutation_spin.setDecimals(2)
        self.p_order_mutation_spin.setValue(0.35)

        self.p_rotation_mutation_spin = QDoubleSpinBox()
        self.p_rotation_mutation_spin.setRange(0.0, 1.0)
        self.p_rotation_mutation_spin.setSingleStep(0.01)
        self.p_rotation_mutation_spin.setDecimals(2)
        self.p_rotation_mutation_spin.setValue(0.15)

        self.random_ratio_spin = QDoubleSpinBox()
        self.random_ratio_spin.setRange(0.0, 1.0)
        self.random_ratio_spin.setSingleStep(0.05)
        self.random_ratio_spin.setDecimals(2)
        self.random_ratio_spin.setValue(0.4)

        self.history_mode_combo = QComboBox()
        self.history_mode_combo.addItem("best_only", HistoryMode.BEST_ONLY)
        self.history_mode_combo.addItem("top_k", HistoryMode.TOP_K)
        self.history_mode_combo.addItem("full_population", HistoryMode.FULL_POPULATION)

        self.history_top_k_spin = QSpinBox()
        self.history_top_k_spin.setRange(1, 10_000)
        self.history_top_k_spin.setValue(10)

        self.void_policy_combo = QComboBox()
        self.void_policy_combo.addItem("disabled", VoidBlockPolicy.DISABLED)
        self.void_policy_combo.addItem(
            "simple_bottom_gaps",
            VoidBlockPolicy.SIMPLE_BOTTOM_GAPS,
        )

        self.play_interval_spin = QSpinBox()
        self.play_interval_spin.setRange(100, 5000)
        self.play_interval_spin.setSingleStep(50)
        self.play_interval_spin.setValue(500)
        self.play_interval_spin.setSuffix(" ms")

        self.enable_immigrants_checkbox = QCheckBox("Immigrants on stagnation")
        self.enable_immigrants_checkbox.setChecked(False)

        self.stagnation_immigrant_fraction_spin = QDoubleSpinBox()
        self.stagnation_immigrant_fraction_spin.setRange(0.0, 1.0)
        self.stagnation_immigrant_fraction_spin.setSingleStep(0.05)
        self.stagnation_immigrant_fraction_spin.setDecimals(2)
        self.stagnation_immigrant_fraction_spin.setValue(0.15)

        fields = [
            ("Population", self.population_spin),
            ("Generations", self.generations_spin),
            ("Stagnation", self.stagnation_spin),
            ("Tournament", self.tournament_spin),
            ("Seed", self.seed_spin),
            ("Max Time", self.max_time_spin),
            ("P Crossover", self.p_crossover_spin),
            ("P Order Mut", self.p_order_mutation_spin),
            ("P Rot Mut", self.p_rotation_mutation_spin),
            ("Random Init", self.random_ratio_spin),
            ("History Mode", self.history_mode_combo),
            ("History Top K", self.history_top_k_spin),
            ("Void Policy", self.void_policy_combo),
            ("Play Interval", self.play_interval_spin),
            ("Immigrants", self.enable_immigrants_checkbox),
            ("Immigrant Frac", self.stagnation_immigrant_fraction_spin),
        ]

        for index, (label, widget) in enumerate(fields):
            row = index % 8
            col_block = index // 8
            controls_grid.addWidget(QLabel(label), row, col_block * 2)
            controls_grid.addWidget(widget, row, col_block * 2 + 1)

        buttons_form = QFormLayout()
        root.addLayout(buttons_form)

        self.load_button = QPushButton("Load Task")
        self.run_button = QPushButton("Run")
        self.stop_button = QPushButton("Stop")
        self.export_history_button = QPushButton("Export History JSON")
        self.export_layout_button = QPushButton("Export Layout PNG")
        self.export_report_button = QPushButton("Export Best Report")

        buttons_form.addRow(self.load_button)
        buttons_form.addRow(self.run_button)
        buttons_form.addRow(self.stop_button)
        buttons_form.addRow(self.export_history_button)
        buttons_form.addRow(self.export_layout_button)
        buttons_form.addRow(self.export_report_button)

        self.stop_button.setEnabled(False)

        self.load_button.clicked.connect(self.load_task_requested.emit)
        self.run_button.clicked.connect(self.run_requested.emit)
        self.stop_button.clicked.connect(self.stop_requested.emit)
        self.export_history_button.clicked.connect(self.export_history_requested.emit)
        self.export_layout_button.clicked.connect(self.export_layout_requested.emit)
        self.export_report_button.clicked.connect(self.export_report_requested.emit)

    def selected_history_mode(self) -> HistoryMode:
        value = self.history_mode_combo.currentData()
        if isinstance(value, HistoryMode):
            return value
        return HistoryMode.TOP_K

    def selected_void_policy(self) -> VoidBlockPolicy:
        value = self.void_policy_combo.currentData()
        if isinstance(value, VoidBlockPolicy):
            return value
        return VoidBlockPolicy.DISABLED

    def build_config(self) -> GAConfig:
        max_time = self.max_time_spin.value()
        return GAConfig(
            population_size=self.population_spin.value(),
            max_generations=self.generations_spin.value(),
            stagnation_limit=self.stagnation_spin.value(),
            max_time_seconds=None if max_time <= 0 else max_time,
            seed=self.seed_spin.value(),
            tournament_size=self.tournament_spin.value(),
            p_crossover=self.p_crossover_spin.value(),
            p_order_mutation=self.p_order_mutation_spin.value(),
            p_rotation_mutation=self.p_rotation_mutation_spin.value(),
            initial_random_ratio=self.random_ratio_spin.value(),
            history_mode=self.selected_history_mode(),
            history_top_k=self.history_top_k_spin.value(),
            enable_stagnation_immigrants=self.enable_immigrants_checkbox.isChecked(),
            stagnation_immigrant_fraction=self.stagnation_immigrant_fraction_spin.value(),
        )

    def set_running_state(self, is_running: bool) -> None:
        self.run_button.setEnabled(not is_running)
        self.stop_button.setEnabled(is_running)
        self.load_button.setEnabled(not is_running)
