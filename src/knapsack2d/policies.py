from __future__ import annotations

from enum import Enum


class VoidBlockPolicy(str, Enum):
    DISABLED = "disabled"
    SIMPLE_BOTTOM_GAPS = "simple_bottom_gaps"


class OverflowPolicy(str, Enum):
    ZERO_VALUE = "zero_value"
    REJECT = "reject"
