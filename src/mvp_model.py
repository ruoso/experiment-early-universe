"""Quadratic slow-roll forward model (Model 1)."""

from __future__ import annotations

import math
from typing import Optional, Tuple

# Reduced Planck mass in GeV (Planck 2018 best-fit).
MPL_REDUCED_GEV = 2.435e18

from .ic_spec import ICTargetSpec, N_RANGE_BASELINE
from .model_types import ForwardResult
from .model_utils import N_in_range


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


def valid(
    phi_star: float,
    m: float,
    *,
    mpl: float = 1.0,
    N_range: Tuple[float, float] = N_RANGE_BASELINE,
    target: ICTargetSpec = ICTargetSpec.mode_a(),
) -> bool:
    """Validity predicate for a configuration C=(phi_star, m)."""

    forward_result = forward(phi_star, m, mpl)

    if not N_in_range(forward_result.N, N_range):
        return False

    return target.accept(forward_result.As, forward_result.ns, forward_result.r)

