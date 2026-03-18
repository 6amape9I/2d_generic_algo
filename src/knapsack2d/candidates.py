from __future__ import annotations

from .geometry import right, top
from .models import CandidatePoint, Placement


class CandidateManager:
    def __init__(self) -> None:
        self._points: set[CandidatePoint] = set()
        self._sorted_cache: tuple[CandidatePoint, ...] | None = None
        self.reset()

    def reset(self) -> None:
        self._points = {CandidatePoint(0, 0)}
        self._sorted_cache = None

    def add_point(self, point: CandidatePoint) -> None:
        if point.x < 0 or point.y < 0:
            return
        if point not in self._points:
            self._points.add(point)
            self._sorted_cache = None

    def add_points_from_placement(self, placement: Placement) -> None:
        self._remove_points_inside_placement(placement)
        self.add_point(CandidatePoint(right(placement), placement.y))
        self.add_point(CandidatePoint(placement.x, top(placement)))

    def next_points(self) -> list[CandidatePoint]:
        if self._sorted_cache is None:
            self._sorted_cache = tuple(sorted(self._points, key=lambda p: (p.y, p.x)))
        return list(self._sorted_cache)

    def _remove_points_inside_placement(self, placement: Placement) -> None:
        x0, x1 = placement.x, right(placement)
        y0, y1 = placement.y, top(placement)
        filtered = {
            point
            for point in self._points
            if not (x0 <= point.x < x1 and y0 <= point.y < y1)
        }
        if filtered != self._points:
            self._points = filtered
            self._sorted_cache = None
