from __future__ import annotations

from .models import Container, Item, Placement


def right(p: Placement) -> int:
    return p.x + p.width


def top(p: Placement) -> int:
    return p.y + p.height


def oriented_size(item: Item, rotated: bool) -> tuple[int, int]:
    if rotated and item.can_rotate:
        return item.height, item.width
    return item.width, item.height


def rects_overlap(a: Placement, b: Placement) -> bool:
    return not (
        right(a) <= b.x
        or right(b) <= a.x
        or top(a) <= b.y
        or top(b) <= a.y
    )


def is_fully_inside_container(p: Placement, container: Container) -> bool:
    return (
        p.x >= 0
        and p.y >= 0
        and right(p) <= container.width
        and top(p) <= container.height
    )
