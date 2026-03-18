from __future__ import annotations

from knapsack2d.candidates import CandidateManager
from knapsack2d.geometry import rects_overlap, right, top
from knapsack2d.models import (
    CandidatePoint,
    DecodedLayout,
    DecodeStep,
    Gene,
    Item,
    Placement,
    ProblemInstance,
    SequenceSolution,
)
from knapsack2d.policies import VoidBlockPolicy


class LeftBottomDecoder:
    def __init__(
        self,
        *,
        void_block_policy: VoidBlockPolicy = VoidBlockPolicy.DISABLED,
    ) -> None:
        self._void_block_policy = void_block_policy
        self._item_map_cache: dict[int, dict[str, Item]] = {}

    def decode(
        self,
        problem: ProblemInstance,
        solution: SequenceSolution,
    ) -> DecodedLayout:
        item_map = self._item_map(problem)
        candidate_manager = CandidateManager()
        placements: list[Placement] = []
        steps: list[DecodeStep] = []

        for gene in solution.genes:
            item = item_map.get(gene.item_id)
            if item is None:
                steps.append(
                    DecodeStep(
                        gene=gene,
                        tested_points=tuple(),
                        chosen_point=None,
                        placement=None,
                        reason="unknown_item",
                    )
                )
                continue

            tested_points = candidate_manager.next_points()
            placement, chosen_point = self._place_item(
                problem=problem,
                placements=placements,
                gene=gene,
                item_id=item.item_id,
                item_width=item.width,
                item_height=item.height,
                item_value=item.value,
                can_rotate=item.can_rotate,
                candidate_points=tested_points,
            )

            if placement is None:
                steps.append(
                    DecodeStep(
                        gene=gene,
                        tested_points=tested_points,
                        chosen_point=None,
                        placement=None,
                        reason="no_feasible_point",
                    )
                )
                continue

            placements.append(placement)
            candidate_manager.add_points_from_placement(placement)

            if self._void_block_policy == VoidBlockPolicy.SIMPLE_BOTTOM_GAPS:
                virtuals = self._create_bottom_gap_virtuals(
                    placement=placement,
                    placements=placements,
                )
                for virtual in virtuals:
                    placements.append(virtual)
                    candidate_manager.add_points_from_placement(virtual)

            steps.append(
                DecodeStep(
                    gene=gene,
                    tested_points=tested_points,
                    chosen_point=chosen_point,
                    placement=placement,
                    reason="placed",
                )
            )

        return DecodedLayout(
            placements=placements,
            steps=steps,
            used_solution_order=[gene.item_id for gene in solution.genes],
        )

    def _item_map(self, problem: ProblemInstance) -> dict[str, Item]:
        cache_key = id(problem)
        cached = self._item_map_cache.get(cache_key)
        if cached is None:
            cached = {item.item_id: item for item in problem.items}
            self._item_map_cache = {cache_key: cached}
        return cached

    def _place_item(
        self,
        *,
        problem: ProblemInstance,
        placements: list[Placement],
        gene: Gene,
        item_id: str,
        item_width: int,
        item_height: int,
        item_value: int,
        can_rotate: bool,
        candidate_points: tuple[CandidatePoint, ...],
    ) -> tuple[Placement | None, CandidatePoint | None]:
        rotated = gene.rotated and can_rotate
        width, height = (
            (item_height, item_width) if rotated else (item_width, item_height)
        )

        for point in candidate_points:
            if not self._is_point_usable(point, problem):
                continue

            candidate = Placement(
                item_id=item_id,
                x=point.x,
                y=point.y,
                width=width,
                height=height,
                rotated=rotated,
                value=item_value,
            )
            if any(rects_overlap(candidate, existing) for existing in placements):
                continue
            return candidate, point

        return None, None

    def _is_point_usable(self, point: CandidatePoint, problem: ProblemInstance) -> bool:
        return point.x < problem.container.width and point.y < problem.container.height

    def _create_bottom_gap_virtuals(
        self,
        *,
        placement: Placement,
        placements: list[Placement],
    ) -> list[Placement]:
        if placement.y <= 0:
            return []

        span_start = placement.x
        span_end = right(placement)
        blocked: list[tuple[int, int]] = []

        for existing in placements:
            if existing is placement:
                continue
            if existing.y >= placement.y or top(existing) <= 0:
                continue
            start = max(span_start, existing.x)
            end = min(span_end, right(existing))
            if start < end:
                blocked.append((start, end))

        free_segments = self._subtract_intervals((span_start, span_end), blocked)
        virtuals: list[Placement] = []

        for start, end in free_segments:
            width = end - start
            if width <= 0:
                continue
            candidate = Placement(
                item_id=None,
                x=start,
                y=0,
                width=width,
                height=placement.y,
                rotated=False,
                value=0,
                is_virtual=True,
            )
            if any(rects_overlap(candidate, existing) for existing in placements + virtuals):
                continue
            virtuals.append(candidate)

        return virtuals

    def _subtract_intervals(
        self,
        span: tuple[int, int],
        blocked: list[tuple[int, int]],
    ) -> list[tuple[int, int]]:
        free = [span]
        for b_start, b_end in sorted(blocked):
            updated: list[tuple[int, int]] = []
            for f_start, f_end in free:
                if b_end <= f_start or b_start >= f_end:
                    updated.append((f_start, f_end))
                    continue
                if b_start > f_start:
                    updated.append((f_start, b_start))
                if b_end < f_end:
                    updated.append((b_end, f_end))
            free = updated
        return free
