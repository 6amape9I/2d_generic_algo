from __future__ import annotations

import pytest

from knapsack2d.task_builder import ProblemBuilder


def test_builder_rejects_duplicate_item_id() -> None:
    builder = ProblemBuilder().set_name("dup").set_container(10, 5)
    builder.add_item("A", 2, 2, 5)

    with pytest.raises(ValueError):
        builder.add_item("A", 1, 1, 2)


def test_builder_requires_container_and_items() -> None:
    builder = ProblemBuilder().set_name("basic")

    with pytest.raises(ValueError):
        builder.build()

    builder.set_container(10, 5)
    with pytest.raises(ValueError):
        builder.build()


def test_remove_unknown_item_raises_key_error() -> None:
    builder = ProblemBuilder().set_name("remove").set_container(10, 5)

    with pytest.raises(KeyError):
        builder.remove_item("missing")


def test_builder_derives_value_from_area() -> None:
    problem = (
        ProblemBuilder()
        .set_name("area-value")
        .set_container(10, 5)
        .add_item("A", 3, 4, 999)
        .build()
    )

    assert problem.items[0].value == 12
