from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Container:
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("container dimensions must be positive")


@dataclass(frozen=True)
class Item:
    item_id: str
    width: int
    height: int
    value: int
    can_rotate: bool = True

    def __post_init__(self) -> None:
        if not self.item_id.strip():
            raise ValueError("item_id must be non-empty")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("item dimensions must be positive")
        if self.value <= 0:
            raise ValueError("item value must be positive")


@dataclass(frozen=True)
class ProblemInstance:
    name: str
    container: Container
    items: tuple[Item, ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("problem name must be non-empty")
        ids = [item.item_id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("item ids must be unique")


@dataclass(frozen=True)
class Gene:
    item_id: str
    rotated: bool = False

    def __post_init__(self) -> None:
        if not self.item_id.strip():
            raise ValueError("gene item_id must be non-empty")


@dataclass(frozen=True)
class SequenceSolution:
    genes: tuple[Gene, ...]


@dataclass(frozen=True, order=True)
class CandidatePoint:
    x: int
    y: int

    def __post_init__(self) -> None:
        if self.x < 0 or self.y < 0:
            raise ValueError("candidate point must be non-negative")


@dataclass
class Placement:
    item_id: str | None
    x: int
    y: int
    width: int
    height: int
    rotated: bool
    value: int
    is_virtual: bool = False

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("placement dimensions must be positive")
        if self.x < 0 or self.y < 0:
            raise ValueError("placement coordinates must be non-negative")
        if self.value < 0:
            raise ValueError("placement value cannot be negative")
        if self.is_virtual:
            if self.item_id is not None:
                raise ValueError("virtual placement must have item_id=None")
            if self.value != 0:
                raise ValueError("virtual placement value must be 0")


@dataclass(frozen=True)
class DecodeStep:
    gene: Gene
    tested_points: tuple[CandidatePoint, ...] = field(default_factory=tuple)
    chosen_point: CandidatePoint | None = None
    placement: Placement | None = None
    reason: str | None = None


@dataclass
class DecodedLayout:
    placements: list[Placement]
    steps: list[DecodeStep]
    used_solution_order: list[str]


@dataclass(frozen=True)
class FitnessBreakdown:
    total_value: int
    packed_items_count: int
    valid_items_count: int
    overflow_items_count: int
    virtual_blocks_count: int
    used_area_inside: int
    fill_ratio: float
