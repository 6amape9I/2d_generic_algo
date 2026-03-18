from __future__ import annotations

from pathlib import Path

from .models import ProblemInstance
from .task_builder import ProblemBuilder


def _clean_line(raw: str) -> str:
    line = raw.lstrip("\ufeff").strip()
    if not line or line.startswith("#"):
        return ""
    if "#" in line:
        line = line.split("#", maxsplit=1)[0].strip()
    return line


def load_problem_txt(path: str | Path) -> ProblemInstance:
    file_path = Path(path)
    lines = file_path.read_text(encoding="utf-8").splitlines()

    builder = ProblemBuilder()
    in_items = False
    has_name = False
    has_container = False

    for line_number, raw in enumerate(lines, start=1):
        line = _clean_line(raw)
        if not line:
            continue

        if not in_items:
            if line.startswith("NAME "):
                name = line[5:].strip()
                builder.set_name(name)
                has_name = True
                continue
            if line.startswith("CONTAINER "):
                parts = line.split()
                if len(parts) != 3:
                    raise ValueError(f"invalid CONTAINER line at {line_number}: {line}")
                builder.set_container(int(parts[1]), int(parts[2]))
                has_container = True
                continue
            if line == "ITEMS":
                in_items = True
                continue
            raise ValueError(f"unexpected line before ITEMS at {line_number}: {line}")

        parts = line.split()
        if len(parts) == 4:
            item_id, width_s, height_s, rotate_s = parts
        elif len(parts) == 5:
            item_id, width_s, height_s, _value_s, rotate_s = parts
        else:
            raise ValueError(f"invalid ITEM line at {line_number}: {line}")

        if rotate_s not in {"0", "1"}:
            raise ValueError(f"invalid can_rotate value at {line_number}: {rotate_s}")

        width = int(width_s)
        height = int(height_s)
        builder.add_item(
            item_id=item_id,
            width=width,
            height=height,
            value=width * height,
            can_rotate=rotate_s == "1",
        )

    if not has_name:
        raise ValueError("NAME section is required")
    if not has_container:
        raise ValueError("CONTAINER section is required")
    if not in_items:
        raise ValueError("ITEMS section is required")

    return builder.build()


def save_problem_txt(problem: ProblemInstance, path: str | Path) -> None:
    file_path = Path(path)
    lines = [
        f"NAME {problem.name}",
        f"CONTAINER {problem.container.width} {problem.container.height}",
        "",
        "ITEMS",
        "# id width height area_value can_rotate",
    ]

    for item in problem.items:
        can_rotate = "1" if item.can_rotate else "0"
        lines.append(
            f"{item.item_id} {item.width} {item.height} {item.value} {can_rotate}"
        )

    file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
