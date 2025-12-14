"""Small shared utilities for model evaluation."""
from __future__ import annotations

from typing import Iterable


def N_in_range(N: float, N_range: Iterable[float]) -> bool:
    """Check whether N lies within [N_min, N_max]."""

    N_min, N_max = N_range
    return N_min <= N <= N_max
