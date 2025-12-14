"""Single-source IC target specification and acceptance helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

N_RANGE_BASELINE: Tuple[float, float] = (50.0, 60.0)
N_RANGE_SENSITIVITY: Tuple[float, float] = (45.0, 65.0)


@dataclass(frozen=True)
class ICTargetSpec:
    """Target values and tolerances for the IC acceptance region R(T)."""

    As0: float = 2.1e-9
    ns0: float = 0.965
    dAs_frac: float = 0.02
    dns_abs: float = 0.004
    r_max: Optional[float] = None
    N_range: Tuple[float, float] = N_RANGE_BASELINE

    def accept(self, As: float, ns: float, r: Optional[float] = None) -> bool:
        As_min = self.As0 * (1.0 - self.dAs_frac)
        As_max = self.As0 * (1.0 + self.dAs_frac)
        ns_min = self.ns0 - self.dns_abs
        ns_max = self.ns0 + self.dns_abs

        if not (As_min <= As <= As_max):
            return False
        if not (ns_min <= ns <= ns_max):
            return False

        if self.r_max is None:
            return True

        if r is None:
            return False

        return r <= self.r_max

    @classmethod
    def mode_a(cls, *, N_range: Tuple[float, float] = N_RANGE_BASELINE) -> "ICTargetSpec":
        """Baseline acceptance on (As, ns) only."""

        return cls(r_max=None, N_range=N_range)

    @classmethod
    def mode_b(
        cls, *, r_max: float = 0.06, N_range: Tuple[float, float] = N_RANGE_BASELINE
    ) -> "ICTargetSpec":
        """Modern acceptance with tensor ceiling."""

        return cls(r_max=r_max, N_range=N_range)
