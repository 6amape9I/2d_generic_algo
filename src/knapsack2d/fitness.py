from __future__ import annotations

from .geometry import is_fully_inside_container
from .models import DecodedLayout, FitnessBreakdown, ProblemInstance
from .policies import OverflowPolicy


class FitnessEvaluator:
    def __init__(
        self,
        *,
        overflow_policy: OverflowPolicy = OverflowPolicy.ZERO_VALUE,
    ) -> None:
        self._overflow_policy = overflow_policy

    def evaluate(
        self,
        problem: ProblemInstance,
        layout: DecodedLayout,
    ) -> FitnessBreakdown:
        total_value = 0
        packed_items_count = 0
        valid_items_count = 0
        overflow_items_count = 0
        virtual_blocks_count = 0
        used_area_inside = 0
        large_first_score = 0

        valid_rank = 0
        total_items = max(1, len(problem.items))

        for placement in layout.placements:
            if placement.is_virtual:
                virtual_blocks_count += 1
                continue

            packed_items_count += 1
            inside = is_fully_inside_container(placement, problem.container)
            if inside:
                area = placement.width * placement.height
                valid_items_count += 1
                total_value += placement.value
                used_area_inside += area
                large_first_score += area * (total_items - valid_rank)
                valid_rank += 1
                continue

            overflow_items_count += 1
            if self._overflow_policy == OverflowPolicy.REJECT:
                raise ValueError("overflow placement is not allowed")

        container_area = problem.container.width * problem.container.height
        fill_ratio = used_area_inside / container_area if container_area else 0.0

        return FitnessBreakdown(
            total_value=total_value,
            packed_items_count=packed_items_count,
            valid_items_count=valid_items_count,
            overflow_items_count=overflow_items_count,
            virtual_blocks_count=virtual_blocks_count,
            used_area_inside=used_area_inside,
            fill_ratio=fill_ratio,
            large_first_score=large_first_score,
        )
