from __future__ import annotations

from dataclasses import dataclass, field

from .models import Container, Item, ProblemInstance


@dataclass
class ProblemBuilder:
    _name: str = "unnamed"
    _container: Container | None = None
    _items: dict[str, Item] = field(default_factory=dict)

    def set_name(self, name: str) -> "ProblemBuilder":
        cleaned = name.strip()
        if not cleaned:
            raise ValueError("problem name must be non-empty")
        self._name = cleaned
        return self

    def set_container(self, width: int, height: int) -> "ProblemBuilder":
        self._container = Container(width=width, height=height)
        return self

    def add_item(
        self,
        item_id: str,
        width: int,
        height: int,
        value: int,
        can_rotate: bool = True,
    ) -> "ProblemBuilder":
        normalized_id = item_id.strip()
        if not normalized_id:
            raise ValueError("item_id must be non-empty")
        if normalized_id in self._items:
            raise ValueError(f"duplicate item_id: {normalized_id}")
        item = Item(
            item_id=normalized_id,
            width=width,
            height=height,
            value=value,
            can_rotate=can_rotate,
        )
        self._items[normalized_id] = item
        return self

    def remove_item(self, item_id: str) -> "ProblemBuilder":
        normalized_id = item_id.strip()
        if normalized_id not in self._items:
            raise KeyError(f"item_id not found: {normalized_id}")
        del self._items[normalized_id]
        return self

    def build(self) -> ProblemInstance:
        if self._container is None:
            raise ValueError("container is not set")
        if not self._items:
            raise ValueError("at least one item is required")
        return ProblemInstance(
            name=self._name,
            container=self._container,
            items=tuple(self._items.values()),
        )
