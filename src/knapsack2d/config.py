from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def load_env_file(path: str | Path | None = None) -> None:
    env_path = Path(path) if path is not None else Path.cwd() / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", maxsplit=1)
        os.environ.setdefault(key.strip(), value.strip())


def env_str(name: str, default: str) -> str:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return default
    return value.strip()


def env_int(name: str, default: int) -> int:
    try:
        return int(env_str(name, str(default)))
    except ValueError:
        return default


def env_float(name: str, default: float) -> float:
    try:
        return float(env_str(name, str(default)))
    except ValueError:
        return default


def env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int_tuple(name: str, default: tuple[int, ...]) -> tuple[int, ...]:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default

    values: list[int] = []
    for part in raw.split(","):
        chunk = part.strip()
        if not chunk:
            continue
        try:
            values.append(int(chunk))
        except ValueError:
            return default

    return tuple(values) if values else default


@dataclass(frozen=True)
class UiEnvConfig:
    qt_platform: str
    qt_qpa_font_dir: str
    font_family: str
    base_font_point_size: int
    min_label_pixel_size: float
    max_label_pixel_size: float
    label_padding: float
    default_task_name: str
    default_population_size: int
    default_generations: int
    default_stagnation_limit: int
    default_tournament_size: int
    default_seed: int
    default_max_time_seconds: float
    default_p_crossover: float
    default_p_order_mutation: float
    default_p_rotation_mutation: float
    default_random_ratio: float
    default_history_top_k: int
    default_play_interval_ms: int
    default_immigrant_fraction: float
    default_population_study_enabled: bool
    default_population_study_values: tuple[int, ...]
    default_exhaustive_enabled: bool
    default_exhaustive_max_items: int
    default_exhaustive_max_time_seconds: float


def load_ui_env_config() -> UiEnvConfig:
    return UiEnvConfig(
        qt_platform=env_str("QT_QPA_PLATFORM", "windows"),
        qt_qpa_font_dir=env_str("QT_QPA_FONTDIR", "C:/Windows/Fonts"),
        font_family=env_str("UI_FONT_FAMILY", "Segoe UI"),
        base_font_point_size=env_int("UI_BASE_FONT_POINT_SIZE", 10),
        min_label_pixel_size=env_float("UI_MIN_LABEL_PIXEL_SIZE", 3.0),
        max_label_pixel_size=env_float("UI_MAX_LABEL_PIXEL_SIZE", 11.0),
        label_padding=env_float("UI_LABEL_PADDING", 0.10),
        default_task_name=env_str("DEFAULT_TASK_NAME", "demo_extreme"),
        default_population_size=env_int("GA_DEFAULT_POPULATION_SIZE", 260),
        default_generations=env_int("GA_DEFAULT_GENERATIONS", 600),
        default_stagnation_limit=env_int("GA_DEFAULT_STAGNATION_LIMIT", 140),
        default_tournament_size=env_int("GA_DEFAULT_TOURNAMENT_SIZE", 3),
        default_seed=env_int("GA_DEFAULT_SEED", 42),
        default_max_time_seconds=env_float("GA_DEFAULT_MAX_TIME_SECONDS", 120.0),
        default_p_crossover=env_float("GA_DEFAULT_P_CROSSOVER", 0.9),
        default_p_order_mutation=env_float("GA_DEFAULT_P_ORDER_MUTATION", 0.35),
        default_p_rotation_mutation=env_float("GA_DEFAULT_P_ROTATION_MUTATION", 0.15),
        default_random_ratio=env_float("GA_DEFAULT_RANDOM_RATIO", 0.4),
        default_history_top_k=env_int("GA_DEFAULT_HISTORY_TOP_K", 10),
        default_play_interval_ms=env_int("UI_DEFAULT_PLAY_INTERVAL_MS", 500),
        default_immigrant_fraction=env_float("GA_DEFAULT_IMMIGRANT_FRAC", 0.15),
        default_population_study_enabled=env_bool("GA_DEFAULT_POPULATION_STUDY_ENABLED", False),
        default_population_study_values=env_int_tuple(
            "GA_DEFAULT_POPULATION_STUDY_VALUES",
            (140, 220, 320, 420, 560),
        ),
        default_exhaustive_enabled=env_bool("BASELINE_EXHAUSTIVE_ENABLED", False),
        default_exhaustive_max_items=env_int("BASELINE_EXHAUSTIVE_MAX_ITEMS", 6),
        default_exhaustive_max_time_seconds=env_float("BASELINE_EXHAUSTIVE_MAX_TIME_SECONDS", 60.0),
    )
