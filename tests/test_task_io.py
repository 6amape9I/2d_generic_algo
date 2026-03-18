from __future__ import annotations

from pathlib import Path

import pytest

from knapsack2d.task_io import load_problem_txt, save_problem_txt


def test_load_valid_task() -> None:
    problem = load_problem_txt(Path("tests/fixtures/task_valid_01.txt"))

    assert problem.name == "task_valid_01"
    assert problem.container.width == 8
    assert problem.container.height == 5
    assert len(problem.items) == 3
    assert problem.items[0].item_id == "A"
    assert problem.items[0].value == problem.items[0].width * problem.items[0].height


def test_load_duplicate_item_id_raises() -> None:
    with pytest.raises(ValueError):
        load_problem_txt(Path("tests/fixtures/task_duplicate_id.txt"))


def test_load_negative_dimensions_raises() -> None:
    with pytest.raises(ValueError):
        load_problem_txt(Path("tests/fixtures/task_negative_size.txt"))


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    source = load_problem_txt(Path("tests/fixtures/task_with_rotation.txt"))
    out_file = tmp_path / "roundtrip.txt"

    save_problem_txt(source, out_file)
    loaded = load_problem_txt(out_file)

    assert loaded == source


def test_loader_ignores_incoming_value_and_uses_area() -> None:
    problem = load_problem_txt(Path("tests/fixtures/task_with_rotation.txt"))

    for item in problem.items:
        assert item.value == item.width * item.height
