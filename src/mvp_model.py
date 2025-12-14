"""Minimal slow-roll forward model for the quadratic potential.

This module implements the Phase 1 forward map described in
``docs/MODEL_SPEC.md`` for the MVP pipeline. The default convention sets
Mpl=1 in the formulas, but an explicit ``mpl`` value can be provided to
reintroduce physical units (defaulting to the reduced Planck mass).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

# Reduced Planck mass in GeV (Planck 2018 best-fit).
MPL_REDUCED_GEV = 2.435e18

# Baseline IC target values and tolerances (see docs/IC_TARGET_SPEC.md).
AS0 = 2.1e-9
NS0 = 0.965
DAS_FRAC = 0.02
DNS_ABS = 0.004
R_MAX = 0.06


def epsilon(phi: float, mpl: float = 1.0) -> float:
    """Slow-roll ``epsilon`` for ``V(phi) = 1/2 m^2 phi^2``.

    epsilon(phi) = 2 * (mpl / phi) ** 2
    """

    return 2.0 * (mpl / phi) ** 2


def eta(phi: float, mpl: float = 1.0) -> float:
    """Slow-roll ``eta`` for ``V(phi) = 1/2 m^2 phi^2``.

    For the quadratic potential, ``eta`` matches ``epsilon``.
    """

    return 2.0 * (mpl / phi) ** 2


def phi_end(mpl: float = 1.0) -> float:
    """Field value at the end of inflation defined by epsilon=1."""

    return math.sqrt(2.0) * mpl


def e_folds(phi_star: float, mpl: float = 1.0) -> float:
    """Number of e-folds from ``phi_star`` to ``phi_end``.

    N(phi_star) = (phi_star^2 - phi_end^2) / (4 * mpl^2)
    """

    phi_end_val = phi_end(mpl)
    return (phi_star ** 2 - phi_end_val ** 2) / (4.0 * mpl ** 2)


def As(phi_star: float, m: float, mpl: float = 1.0) -> float:
    """Scalar amplitude at the pivot scale."""

    eps_val = epsilon(phi_star, mpl)
    potential = 0.5 * m ** 2 * phi_star ** 2
    return (1.0 / (24.0 * math.pi ** 2 * mpl ** 4)) * potential / eps_val


def ns(phi_star: float, mpl: float = 1.0) -> float:
    """Scalar spectral index at the pivot scale."""

    eps_val = epsilon(phi_star, mpl)
    eta_val = eta(phi_star, mpl)
    return 1.0 - 6.0 * eps_val + 2.0 * eta_val


def r(phi_star: float, mpl: float = 1.0) -> float:
    """Tensor-to-scalar ratio at the pivot scale."""

    eps_val = epsilon(phi_star, mpl)
    return 16.0 * eps_val


@dataclass
class ForwardResult:
    As: float
    ns: float
    r: float
    N: float
    phi_end: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "As": self.As,
            "ns": self.ns,
            "r": self.r,
            "N": self.N,
            "phi_end": self.phi_end,
        }


def forward(phi_star: float, m: float, mpl: float = 1.0) -> ForwardResult:
    """Compute the forward map F(C) -> {As, ns, r, N, phi_end}.

    Parameters
    ----------
    phi_star: float
        Field value at horizon exit for the pivot scale.
    m: float
        Mass parameter in the quadratic potential.
    mpl: float, optional
        Planck mass used in the slow-roll expressions (default: 1.0).
    """

    phi_end_val = phi_end(mpl)
    result = ForwardResult(
        As=As(phi_star, m, mpl),
        ns=ns(phi_star, mpl),
        r=r(phi_star, mpl),
        N=e_folds(phi_star, mpl),
        phi_end=phi_end_val,
    )
    return result


def accept_target(
    As_val: float,
    ns_val: float,
    r_val: Optional[float] = None,
    *,
    As0: float = AS0,
    ns0: float = NS0,
    dAs_frac: float = DAS_FRAC,
    dns_abs: float = DNS_ABS,
    r_max: Optional[float] = R_MAX,
) -> bool:
    """Predicate for the IC target region R(T)."""

    As_min = As0 * (1.0 - dAs_frac)
    As_max = As0 * (1.0 + dAs_frac)
    ns_min = ns0 - dns_abs
    ns_max = ns0 + dns_abs

    if not (As_min <= As_val <= As_max):
        return False
    if not (ns_min <= ns_val <= ns_max):
        return False

    if r_max is None:
        return True

    if r_val is None:
        return False

    return r_val <= r_max


def N_in_range(N: float, N_range: Iterable[float]) -> bool:
    """Check whether N lies within [N_min, N_max]."""

    N_min, N_max = N_range
    return N_min <= N <= N_max


def valid(
    phi_star: float,
    m: float,
    *,
    mpl: float = 1.0,
    N_range: Tuple[float, float] = (50.0, 60.0),
    As0: float = AS0,
    ns0: float = NS0,
    dAs_frac: float = DAS_FRAC,
    dns_abs: float = DNS_ABS,
    r_max: Optional[float] = R_MAX,
) -> bool:
    """Validity predicate for a configuration C=(phi_star, m)."""

    forward_result = forward(phi_star, m, mpl)

    if not N_in_range(forward_result.N, N_range):
        return False

    return accept_target(
        forward_result.As,
        forward_result.ns,
        forward_result.r,
        As0=As0,
        ns0=ns0,
        dAs_frac=dAs_frac,
        dns_abs=dns_abs,
        r_max=r_max,
    )

