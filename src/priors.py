"""Phase 4 priors and typicality estimates for the quadratic slow-roll MVP.

This module defines a small menu of priors over the pre-IC parameterization
C=(phi_star, m) and provides Monte Carlo estimators for P(valid) under each
choice. The priors mirror the menu in ``docs/PRIORS.md``:

- P1: flat in phi_star, flat in log m
- P2: flat in phi_star, flat in log V_star (with V_star = 1/2 m^2 phi_star^2)
- P3: volume-weighted proxy using weight w = exp(3N(phi_star)) applied to P1

Usage
-----
Run ``python -m src.priors`` to print a small summary table for the default
configurations. The defaults mirror the Phase 3 scan ranges and the Phase 2
validity predicate (tensor constraint off by default).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Optional, Tuple

from . import mvp_model

# Default parameter ranges (match Phase 3 scan for consistency)
PHI_RANGE_DEFAULT: Tuple[float, float] = (6.0, 22.0)
M_RANGE_DEFAULT: Tuple[float, float] = (5e-7, 5e-5)
N_RANGE_DEFAULT: Tuple[float, float] = (50.0, 60.0)


@dataclass
class Sample:
    """A single draw from a prior distribution."""

    phi_star: float
    m: float
    weight: float = 1.0


@dataclass
class PriorResult:
    """Summary statistics for a prior's validity estimate."""

    name: str
    n_samples: int
    n_valid: int
    weight_sum: float
    weight_sum_valid: float
    p_valid: float
    mean_phi_valid: Optional[float]
    mean_m_valid: Optional[float]
    mean_N_valid: Optional[float]

    def as_dict(self) -> Dict[str, float | int | str | None]:
        return {
            "name": self.name,
            "n_samples": self.n_samples,
            "n_valid": self.n_valid,
            "weight_sum": self.weight_sum,
            "weight_sum_valid": self.weight_sum_valid,
            "p_valid": self.p_valid,
            "mean_phi_valid": self.mean_phi_valid,
            "mean_m_valid": self.mean_m_valid,
            "mean_N_valid": self.mean_N_valid,
        }


def _uniform(rng: random.Random, low: float, high: float) -> float:
    return low + (high - low) * rng.random()


def _uniform_log(rng: random.Random, low: float, high: float) -> float:
    """Sample x with log x uniform over [log low, log high]."""

    log_low = math.log(low)
    log_high = math.log(high)
    return math.exp(_uniform(rng, log_low, log_high))


def _sample_p1(
    rng: random.Random,
    phi_range: Tuple[float, float],
    m_range: Tuple[float, float],
) -> Sample:
    phi_star = _uniform(rng, *phi_range)
    m = _uniform_log(rng, *m_range)
    return Sample(phi_star=phi_star, m=m, weight=1.0)


def _sample_p2(
    rng: random.Random,
    phi_range: Tuple[float, float],
    m_range: Tuple[float, float],
) -> Sample:
    """Flat in phi_star, flat in log V_star with V_star = 1/2 m^2 phi_star^2.

    The V range is chosen so that the derived ``m`` remains within ``m_range``
    for any phi_star in ``phi_range``.
    """

    phi_star = _uniform(rng, *phi_range)

    phi_min, phi_max = phi_range
    m_min, m_max = m_range
    V_min = 0.5 * (m_min ** 2) * (phi_max ** 2)
    V_max = 0.5 * (m_max ** 2) * (phi_min ** 2)

    V_star = _uniform_log(rng, V_min, V_max)
    m = math.sqrt(2.0 * V_star) / phi_star
    return Sample(phi_star=phi_star, m=m, weight=1.0)


def _sample_p3(
    rng: random.Random,
    phi_range: Tuple[float, float],
    m_range: Tuple[float, float],
    *,
    mpl: float,
) -> Sample:
    """Volume-weighted proxy using weight w = exp(3N(phi_star))."""

    base_sample = _sample_p1(rng, phi_range, m_range)
    N_val = mvp_model.e_folds(base_sample.phi_star, mpl)
    weight = math.exp(3.0 * N_val)
    return Sample(phi_star=base_sample.phi_star, m=base_sample.m, weight=weight)


def _estimate_prior(
    *,
    name: str,
    sampler: Callable[[random.Random], Sample],
    n_samples: int,
    mpl: float,
    N_range: Tuple[float, float],
    As0: float,
    ns0: float,
    dAs_frac: float,
    dns_abs: float,
    r_max: float | None,
) -> PriorResult:
    rng = random.Random()
    n_valid = 0
    weight_sum = 0.0
    weight_sum_valid = 0.0
    sum_phi = 0.0
    sum_m = 0.0
    sum_N = 0.0

    for _ in range(n_samples):
        sample = sampler(rng)
        forward_result = mvp_model.forward(sample.phi_star, sample.m, mpl)
        is_valid = mvp_model.valid(
            sample.phi_star,
            sample.m,
            mpl=mpl,
            N_range=N_range,
            As0=As0,
            ns0=ns0,
            dAs_frac=dAs_frac,
            dns_abs=dns_abs,
            r_max=r_max,
        )

        weight_sum += sample.weight
        if is_valid:
            n_valid += 1
            weight_sum_valid += sample.weight
            sum_phi += sample.weight * sample.phi_star
            sum_m += sample.weight * sample.m
            sum_N += sample.weight * forward_result.N

    p_valid = weight_sum_valid / weight_sum if weight_sum > 0 else 0.0

    mean_phi_valid = sum_phi / weight_sum_valid if weight_sum_valid > 0 else None
    mean_m_valid = sum_m / weight_sum_valid if weight_sum_valid > 0 else None
    mean_N_valid = sum_N / weight_sum_valid if weight_sum_valid > 0 else None

    return PriorResult(
        name=name,
        n_samples=n_samples,
        n_valid=n_valid,
        weight_sum=weight_sum,
        weight_sum_valid=weight_sum_valid,
        p_valid=p_valid,
        mean_phi_valid=mean_phi_valid,
        mean_m_valid=mean_m_valid,
        mean_N_valid=mean_N_valid,
    )


def estimate_priors(
    *,
    n_samples: int = 20000,
    phi_range: Tuple[float, float] = PHI_RANGE_DEFAULT,
    m_range: Tuple[float, float] = M_RANGE_DEFAULT,
    N_range: Tuple[float, float] = N_RANGE_DEFAULT,
    mpl: float = 1.0,
    As0: float = mvp_model.AS0,
    ns0: float = mvp_model.NS0,
    dAs_frac: float = mvp_model.DAS_FRAC,
    dns_abs: float = mvp_model.DNS_ABS,
    r_max: float | None = None,
) -> Tuple[PriorResult, PriorResult, PriorResult]:
    """Estimate P(valid) for the three default priors via Monte Carlo."""

    def p1_sampler(rng: random.Random) -> Sample:
        return _sample_p1(rng, phi_range, m_range)

    def p2_sampler(rng: random.Random) -> Sample:
        return _sample_p2(rng, phi_range, m_range)

    def p3_sampler(rng: random.Random) -> Sample:
        return _sample_p3(rng, phi_range, m_range, mpl=mpl)

    common_kwargs = dict(
        n_samples=n_samples,
        mpl=mpl,
        N_range=N_range,
        As0=As0,
        ns0=ns0,
        dAs_frac=dAs_frac,
        dns_abs=dns_abs,
        r_max=r_max,
    )

    p1 = _estimate_prior(name="P1_flat_phi_log_m", sampler=p1_sampler, **common_kwargs)
    p2 = _estimate_prior(name="P2_flat_phi_log_V", sampler=p2_sampler, **common_kwargs)
    p3 = _estimate_prior(name="P3_volume_weighted", sampler=p3_sampler, **common_kwargs)
    return p1, p2, p3


def _format_result(result: PriorResult) -> str:
    if result.mean_phi_valid is None:
        posterior = "(no valid samples)"
    else:
        posterior = (
            f"phi*: {result.mean_phi_valid:.3f}, "
            f"m: {result.mean_m_valid:.3e}, "
            f"N: {result.mean_N_valid:.2f}"
        )

    return (
        f"{result.name}: P(valid)={result.p_valid:.4e}"
        f" (n={result.n_samples}, valid={result.n_valid}); "
        f"posterior mean {posterior}"
    )


def run_summary(  # pragma: no cover - convenience CLI
    *,
    n_samples: int = 20000,
    phi_range: Tuple[float, float] = PHI_RANGE_DEFAULT,
    m_range: Tuple[float, float] = M_RANGE_DEFAULT,
    N_range: Tuple[float, float] = N_RANGE_DEFAULT,
    mpl: float = 1.0,
    As0: float = mvp_model.AS0,
    ns0: float = mvp_model.NS0,
    dAs_frac: float = mvp_model.DAS_FRAC,
    dns_abs: float = mvp_model.DNS_ABS,
    r_max: float | None = None,
) -> Iterable[str]:
    """Yield human-readable summary lines for the three priors."""

    results = estimate_priors(
        n_samples=n_samples,
        phi_range=phi_range,
        m_range=m_range,
        N_range=N_range,
        mpl=mpl,
        As0=As0,
        ns0=ns0,
        dAs_frac=dAs_frac,
        dns_abs=dns_abs,
        r_max=r_max,
    )
    for result in results:
        yield _format_result(result)


def run_sensitivity(  # pragma: no cover - convenience CLI
    *,
    n_samples: int = 20000,
    phi_range: Tuple[float, float] = PHI_RANGE_DEFAULT,
    m_range: Tuple[float, float] = M_RANGE_DEFAULT,
    mpl: float = 1.0,
) -> Iterable[str]:
    """Yield summary lines for a small set of sensitivity variants.

    Variants cover:
    - Tensor bound on vs. off
    - Wider N range
    - Narrower and wider tolerance bands
    """

    configs = [
        dict(name="baseline_r_off", N_range=N_RANGE_DEFAULT, r_max=None),
        dict(name="tensor_on", N_range=N_RANGE_DEFAULT, r_max=mvp_model.R_MAX),
        dict(name="wide_N", N_range=(45.0, 65.0), r_max=None),
        dict(
            name="tight_tolerances",
            N_range=N_RANGE_DEFAULT,
            r_max=None,
            dAs_frac=0.01,
            dns_abs=0.002,
        ),
        dict(
            name="loose_tolerances",
            N_range=N_RANGE_DEFAULT,
            r_max=None,
            dAs_frac=0.03,
            dns_abs=0.006,
        ),
    ]

    for cfg in configs:
        results = estimate_priors(
            n_samples=n_samples,
            phi_range=phi_range,
            m_range=m_range,
            N_range=cfg.get("N_range", N_RANGE_DEFAULT),
            mpl=mpl,
            As0=cfg.get("As0", mvp_model.AS0),
            ns0=cfg.get("ns0", mvp_model.NS0),
            dAs_frac=cfg.get("dAs_frac", mvp_model.DAS_FRAC),
            dns_abs=cfg.get("dns_abs", mvp_model.DNS_ABS),
            r_max=cfg.get("r_max", None),
        )
        header = f"[{cfg['name']}]"
        yield header
        for result in results:
            yield _format_result(result)
        yield ""


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    import argparse

    parser = argparse.ArgumentParser(description="Estimate P(valid) for priors")
    parser.add_argument("--n_samples", type=int, default=20000, help="Monte Carlo draws")
    parser.add_argument(
        "--sensitivity", action="store_true", help="Run tensor/N/tolerance variants",
    )
    args = parser.parse_args()

    runner = run_sensitivity if args.sensitivity else run_summary
    for line in runner(n_samples=args.n_samples):
        print(line)
