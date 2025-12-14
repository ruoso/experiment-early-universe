"""Low-r plateau model based on a Starobinsky-like potential (Model 2)."""
from __future__ import annotations

import math
from typing import Optional, Tuple

from .ic_spec import ICTargetSpec, N_RANGE_BASELINE
from .model_types import ForwardResult
from .model_utils import N_in_range


# Reduced Planck mass in GeV (Planck 2018 best-fit).
MPL_REDUCED_GEV = 2.435e18


def _a(mpl: float) -> float:
    return math.sqrt(2.0 / 3.0) / mpl


def epsilon(phi: float, *, V0: float, mpl: float = 1.0) -> float:
    """Slow-roll epsilon for V = V0 (1 - exp(-a phi))^2."""

    a = _a(mpl)
    y = math.exp(-a * phi)
    return 2.0 * (a ** 2) * (y ** 2) / (1.0 - y) ** 2


def eta(phi: float, *, V0: float, mpl: float = 1.0) -> float:
    """Slow-roll eta for V = V0 (1 - exp(-a phi))^2."""

    a = _a(mpl)
    y = math.exp(-a * phi)
    return 2.0 * (a ** 2) * (-y + 2.0 * y ** 2) / (1.0 - y) ** 2


def phi_end(mpl: float = 1.0) -> float:
    """Field value at the end of inflation from epsilon=1."""

    a = _a(mpl)
    y_end = 1.0 / (1.0 + math.sqrt(2.0) * a)
    return -(1.0 / a) * math.log(y_end)


def e_folds(phi_star: float, V0: float, mpl: float = 1.0) -> float:
    """Number of e-folds from phi_star to phi_end."""

    a = _a(mpl)
    phi_end_val = phi_end(mpl)
    prefactor = 1.0 / (2.0 * a)
    exp_term = (1.0 / a) * (math.exp(a * phi_star) - math.exp(a * phi_end_val))
    linear_term = -(phi_star - phi_end_val)
    return prefactor * (exp_term + linear_term)


def potential(phi: float, *, V0: float, mpl: float = 1.0) -> float:
    a = _a(mpl)
    return V0 * (1.0 - math.exp(-a * phi)) ** 2


def As(phi_star: float, V0: float, mpl: float = 1.0) -> float:
    eps_val = epsilon(phi_star, V0=V0, mpl=mpl)
    V = potential(phi_star, V0=V0, mpl=mpl)
    return (1.0 / (24.0 * math.pi ** 2 * mpl ** 4)) * V / eps_val


def ns(phi_star: float, V0: float, mpl: float = 1.0) -> float:
    eps_val = epsilon(phi_star, V0=V0, mpl=mpl)
    eta_val = eta(phi_star, V0=V0, mpl=mpl)
    return 1.0 - 6.0 * eps_val + 2.0 * eta_val


def r(phi_star: float, V0: float, mpl: float = 1.0) -> float:
    eps_val = epsilon(phi_star, V0=V0, mpl=mpl)
    return 16.0 * eps_val


def forward(phi_star: float, V0: float, mpl: float = 1.0) -> ForwardResult:
    phi_end_val = phi_end(mpl)
    return ForwardResult(
        As=As(phi_star, V0, mpl),
        ns=ns(phi_star, V0, mpl),
        r=r(phi_star, V0, mpl),
        N=e_folds(phi_star, V0=V0, mpl=mpl),
        phi_end=phi_end_val,
    )


def valid(
    phi_star: float,
    V0: float,
    *,
    mpl: float = 1.0,
    N_range: Tuple[float, float] = N_RANGE_BASELINE,
    target: ICTargetSpec = ICTargetSpec.mode_a(),
) -> bool:
    forward_result = forward(phi_star, V0, mpl)
    if not N_in_range(forward_result.N, N_range):
        return False
    return target.accept(forward_result.As, forward_result.ns, forward_result.r)
