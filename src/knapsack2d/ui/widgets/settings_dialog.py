from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from knapsack2d.baseline.exhaustive import ExhaustiveSearchConfig
from knapsack2d.config import UiEnvConfig
from knapsack2d.ga.config import GAConfig
from knapsack2d.ga.history import HistoryMode
from knapsack2d.policies import VoidBlockPolicy
from knapsack2d.ui.run_models import PopulationStudyConfig


class SettingsDialog(QDialog):
    def __init__(self, env_config: UiEnvConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("GA Settings")
        self.setModal(True)
        self.resize(720, 680)

        root = QVBoxLayout(self)
        tabs = QTabWidget()
        root.addWidget(tabs)

        ga_tab = QWidget()
        ga_layout = QVBoxLayout(ga_tab)
        ga_form = QFormLayout()
        ga_layout.addWidget(self._group_box("Population and Search", ga_form))
        tabs.addTab(ga_tab, "GA")

        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        history_form = QFormLayout()
        history_layout.addWidget(self._group_box("History and Playback", history_form))
        tabs.addTab(history_tab, "History")

        policy_tab = QWidget()
        policy_layout = QVBoxLayout(policy_tab)
        policy_form = QFormLayout()
        policy_layout.addWidget(self._group_box("Policies", policy_form))
        tabs.addTab(policy_tab, "Policies")

        study_tab = QWidget()
        study_layout = QVBoxLayout(study_tab)
        study_form = QFormLayout()
        study_layout.addWidget(self._group_box("Population Study", study_form))
        tabs.addTab(study_tab, "Population Study")

        baseline_tab = QWidget()
        baseline_layout = QVBoxLayout(baseline_tab)
        baseline_form = QFormLayout()
        baseline_layout.addWidget(self._group_box("Exhaustive Baseline", baseline_form))
        tabs.addTab(baseline_tab, "Baseline")

        self.population_spin = QSpinBox()
        self.population_spin.setRange(2, 10_000)
        self.population_spin.setValue(env_config.default_population_size)

        self.generations_spin = QSpinBox()
        self.generations_spin.setRange(1, 100_000)
        self.generations_spin.setValue(env_config.default_generations)

        self.stagnation_spin = QSpinBox()
        self.stagnation_spin.setRange(1, 100_000)
        self.stagnation_spin.setValue(env_config.default_stagnation_limit)

        self.tournament_spin = QSpinBox()
        self.tournament_spin.setRange(2, 100)
        self.tournament_spin.setValue(env_config.default_tournament_size)

        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(0, 2_147_483_647)
        self.seed_spin.setValue(env_config.default_seed)

        self.max_time_spin = QDoubleSpinBox()
        self.max_time_spin.setRange(0.0, 86400.0)
        self.max_time_spin.setDecimals(1)
        self.max_time_spin.setSingleStep(5.0)
        self.max_time_spin.setValue(env_config.default_max_time_seconds)
        self.max_time_spin.setSuffix(" s")

        self.p_crossover_spin = QDoubleSpinBox()
        self.p_crossover_spin.setRange(0.0, 1.0)
        self.p_crossover_spin.setSingleStep(0.01)
        self.p_crossover_spin.setDecimals(2)
        self.p_crossover_spin.setValue(env_config.default_p_crossover)

        self.p_order_mutation_spin = QDoubleSpinBox()
        self.p_order_mutation_spin.setRange(0.0, 1.0)
        self.p_order_mutation_spin.setSingleStep(0.01)
        self.p_order_mutation_spin.setDecimals(2)
        self.p_order_mutation_spin.setValue(env_config.default_p_order_mutation)

        self.p_rotation_mutation_spin = QDoubleSpinBox()
        self.p_rotation_mutation_spin.setRange(0.0, 1.0)
        self.p_rotation_mutation_spin.setSingleStep(0.01)
        self.p_rotation_mutation_spin.setDecimals(2)
        self.p_rotation_mutation_spin.setValue(env_config.default_p_rotation_mutation)

        self.random_ratio_spin = QDoubleSpinBox()
        self.random_ratio_spin.setRange(0.0, 1.0)
        self.random_ratio_spin.setSingleStep(0.05)
        self.random_ratio_spin.setDecimals(2)
        self.random_ratio_spin.setValue(env_config.default_random_ratio)

        self.history_mode_combo = QComboBox()
        self.history_mode_combo.addItem("best_only", HistoryMode.BEST_ONLY)
        self.history_mode_combo.addItem("top_k", HistoryMode.TOP_K)
        self.history_mode_combo.addItem("full_population", HistoryMode.FULL_POPULATION)
        self.history_mode_combo.setCurrentIndex(1)

        self.history_top_k_spin = QSpinBox()
        self.history_top_k_spin.setRange(1, 10_000)
        self.history_top_k_spin.setValue(env_config.default_history_top_k)

        self.play_interval_spin = QSpinBox()
        self.play_interval_spin.setRange(100, 5000)
        self.play_interval_spin.setSingleStep(50)
        self.play_interval_spin.setValue(env_config.default_play_interval_ms)
        self.play_interval_spin.setSuffix(" ms")

        self.void_policy_combo = QComboBox()
        self.void_policy_combo.addItem("disabled", VoidBlockPolicy.DISABLED)
        self.void_policy_combo.addItem("simple_bottom_gaps", VoidBlockPolicy.SIMPLE_BOTTOM_GAPS)

        self.enable_immigrants_checkbox = QCheckBox("Enable immigrants when best value stagnates")
        self.enable_immigrants_checkbox.setChecked(False)

        self.stagnation_immigrant_fraction_spin = QDoubleSpinBox()
        self.stagnation_immigrant_fraction_spin.setRange(0.0, 1.0)
        self.stagnation_immigrant_fraction_spin.setSingleStep(0.05)
        self.stagnation_immigrant_fraction_spin.setDecimals(2)
        self.stagnation_immigrant_fraction_spin.setValue(env_config.default_immigrant_fraction)

        self.enable_population_study_checkbox = QCheckBox(
            "Run the current task on 5 different population sizes"
        )
        self.enable_population_study_checkbox.setChecked(env_config.default_population_study_enabled)

        self.population_study_note = QLabel(
            "The main result view will show the best GA run among the study points."
        )
        self.population_study_note.setWordWrap(True)

        self.population_study_spins: list[QSpinBox] = []
        for index, value in enumerate(env_config.default_population_study_values, start=1):
            spin = QSpinBox()
            spin.setRange(2, 10_000)
            spin.setValue(value)
            self.population_study_spins.append(spin)
            study_form.addRow(f"Population #{index}", spin)

        self.enable_exhaustive_checkbox = QCheckBox(
            "Run exhaustive baseline after GA when the task is small enough"
        )
        self.enable_exhaustive_checkbox.setChecked(env_config.default_exhaustive_enabled)

        self.exhaustive_max_items_spin = QSpinBox()
        self.exhaustive_max_items_spin.setRange(1, 12)
        self.exhaustive_max_items_spin.setValue(env_config.default_exhaustive_max_items)

        self.exhaustive_max_time_spin = QDoubleSpinBox()
        self.exhaustive_max_time_spin.setRange(0.0, 86400.0)
        self.exhaustive_max_time_spin.setDecimals(1)
        self.exhaustive_max_time_spin.setSingleStep(5.0)
        self.exhaustive_max_time_spin.setValue(env_config.default_exhaustive_max_time_seconds)
        self.exhaustive_max_time_spin.setSuffix(" s")

        self.exhaustive_note = QLabel(
            "Exhaustive search enumerates every order and rotation combination. Large tasks will be skipped by the max-items guard."
        )
        self.exhaustive_note.setWordWrap(True)

        ga_form.addRow("Population", self.population_spin)
        ga_form.addRow("Generations", self.generations_spin)
        ga_form.addRow("Stagnation", self.stagnation_spin)
        ga_form.addRow("Tournament", self.tournament_spin)
        ga_form.addRow("Seed", self.seed_spin)
        ga_form.addRow("Max Time", self.max_time_spin)
        ga_form.addRow("P Crossover", self.p_crossover_spin)
        ga_form.addRow("P Order Mutation", self.p_order_mutation_spin)
        ga_form.addRow("P Rotation Mutation", self.p_rotation_mutation_spin)
        ga_form.addRow("Random Init Ratio", self.random_ratio_spin)

        history_form.addRow("History Mode", self.history_mode_combo)
        history_form.addRow("History Top K", self.history_top_k_spin)
        history_form.addRow("Play Interval", self.play_interval_spin)

        policy_form.addRow("Void Policy", self.void_policy_combo)
        policy_form.addRow("Immigrants", self.enable_immigrants_checkbox)
        policy_form.addRow("Immigrant Fraction", self.stagnation_immigrant_fraction_spin)

        study_form.addRow("Enable Study", self.enable_population_study_checkbox)
        study_form.addRow("Note", self.population_study_note)

        baseline_form.addRow("Enable Baseline", self.enable_exhaustive_checkbox)
        baseline_form.addRow("Max Items", self.exhaustive_max_items_spin)
        baseline_form.addRow("Max Time", self.exhaustive_max_time_spin)
        baseline_form.addRow("Note", self.exhaustive_note)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def summary_text(self) -> str:
        study_suffix = " | Study x5" if self.enable_population_study_checkbox.isChecked() else ""
        baseline_suffix = " | Baseline" if self.enable_exhaustive_checkbox.isChecked() else ""
        return (
            f"Pop {self.population_spin.value()} | Gen {self.generations_spin.value()} | "
            f"Seed {self.seed_spin.value()} | Hist {self.selected_history_mode().value}"
            f"{study_suffix}{baseline_suffix}"
        )

    def snapshot_state(self) -> dict[str, object]:
        state: dict[str, object] = {
            "population": self.population_spin.value(),
            "generations": self.generations_spin.value(),
            "stagnation": self.stagnation_spin.value(),
            "tournament": self.tournament_spin.value(),
            "seed": self.seed_spin.value(),
            "max_time": self.max_time_spin.value(),
            "p_crossover": self.p_crossover_spin.value(),
            "p_order_mutation": self.p_order_mutation_spin.value(),
            "p_rotation_mutation": self.p_rotation_mutation_spin.value(),
            "random_ratio": self.random_ratio_spin.value(),
            "history_mode": self.history_mode_combo.currentIndex(),
            "history_top_k": self.history_top_k_spin.value(),
            "play_interval": self.play_interval_spin.value(),
            "void_policy": self.void_policy_combo.currentIndex(),
            "enable_immigrants": self.enable_immigrants_checkbox.isChecked(),
            "immigrant_fraction": self.stagnation_immigrant_fraction_spin.value(),
            "enable_population_study": self.enable_population_study_checkbox.isChecked(),
            "enable_exhaustive": self.enable_exhaustive_checkbox.isChecked(),
            "exhaustive_max_items": self.exhaustive_max_items_spin.value(),
            "exhaustive_max_time": self.exhaustive_max_time_spin.value(),
        }
        for index, spin in enumerate(self.population_study_spins):
            state[f"population_study_{index}"] = spin.value()
        return state

    def restore_state(self, state: dict[str, object]) -> None:
        self.population_spin.setValue(int(state["population"]))
        self.generations_spin.setValue(int(state["generations"]))
        self.stagnation_spin.setValue(int(state["stagnation"]))
        self.tournament_spin.setValue(int(state["tournament"]))
        self.seed_spin.setValue(int(state["seed"]))
        self.max_time_spin.setValue(float(state["max_time"]))
        self.p_crossover_spin.setValue(float(state["p_crossover"]))
        self.p_order_mutation_spin.setValue(float(state["p_order_mutation"]))
        self.p_rotation_mutation_spin.setValue(float(state["p_rotation_mutation"]))
        self.random_ratio_spin.setValue(float(state["random_ratio"]))
        self.history_mode_combo.setCurrentIndex(int(state["history_mode"]))
        self.history_top_k_spin.setValue(int(state["history_top_k"]))
        self.play_interval_spin.setValue(int(state["play_interval"]))
        self.void_policy_combo.setCurrentIndex(int(state["void_policy"]))
        self.enable_immigrants_checkbox.setChecked(bool(state["enable_immigrants"]))
        self.stagnation_immigrant_fraction_spin.setValue(float(state["immigrant_fraction"]))
        self.enable_population_study_checkbox.setChecked(bool(state["enable_population_study"]))
        self.enable_exhaustive_checkbox.setChecked(bool(state["enable_exhaustive"]))
        self.exhaustive_max_items_spin.setValue(int(state["exhaustive_max_items"]))
        self.exhaustive_max_time_spin.setValue(float(state["exhaustive_max_time"]))
        for index, spin in enumerate(self.population_study_spins):
            spin.setValue(int(state[f"population_study_{index}"]))

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

    def play_interval_ms(self) -> int:
        return self.play_interval_spin.value()

    def population_study_config(self) -> PopulationStudyConfig:
        return PopulationStudyConfig(
            enabled=self.enable_population_study_checkbox.isChecked(),
            population_sizes=tuple(spin.value() for spin in self.population_study_spins),
        )

    def exhaustive_config(self) -> ExhaustiveSearchConfig:
        max_time = self.exhaustive_max_time_spin.value()
        return ExhaustiveSearchConfig(
            enabled=self.enable_exhaustive_checkbox.isChecked(),
            max_items=self.exhaustive_max_items_spin.value(),
            max_time_seconds=None if max_time <= 0 else max_time,
        )

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

    def _group_box(self, title: str, form: QFormLayout) -> QGroupBox:
        box = QGroupBox(title)
        box_layout = QVBoxLayout(box)
        box_layout.addLayout(form)
        box_layout.addStretch(1)
        return box
