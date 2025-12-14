"""Phase 4 priors and typicality estimates for registered models."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Optional, Tuple

from .ic_spec import ICTargetSpec, N_RANGE_BASELINE
from .model_registry import ModelConfig, get_model

# Default configuration mirrors the quadratic model setup
DEFAULT_MODEL = get_model("quadratic")
PHI_RANGE_DEFAULT: Tuple[float, float] = DEFAULT_MODEL.default_phi_range
PARAM_RANGE_DEFAULT: Tuple[float, float] = DEFAULT_MODEL.default_param_range
N_RANGE_DEFAULT: Tuple[float, float] = N_RANGE_BASELINE


@dataclass
class Sample:
    """A single draw from a prior distribution."""

    phi_star: float
    param: float
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
    mean_param_valid: Optional[float]
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
            "mean_param_valid": self.mean_param_valid,
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
    param_range: Tuple[float, float],
) -> Sample:
    phi_star = _uniform(rng, *phi_range)
    param = _uniform_log(rng, *param_range)
    return Sample(phi_star=phi_star, param=param, weight=1.0)


def _potential_bounds(
    model: ModelConfig,
    phi_range: Tuple[float, float],
    param_range: Tuple[float, float],
    mpl: float,
) -> Tuple[float, float]:
    if model.potential is None:
        raise ValueError(f"Model {model.name} does not expose a potential for P2")

    potentials = [
        model.potential(phi, param, mpl)
        for phi in (phi_range[0], phi_range[1])
        for param in (param_range[0], param_range[1])
    ]
    potentials = [p for p in potentials if p > 0]
    if not potentials:
        raise ValueError("Potential values must be positive to define log-flat bounds")
    return min(potentials), max(potentials)


def _sample_p2(
    rng: random.Random,
    phi_range: Tuple[float, float],
    param_range: Tuple[float, float],
    *,
    model: ModelConfig,
    mpl: float,
) -> Sample:
    """Flat in phi_star, flat in log V_star using model potential."""

    if model.param_from_energy is None:
        raise ValueError(f"Model {model.name} cannot invert V->param for P2")

    phi_star = _uniform(rng, *phi_range)
    V_min, V_max = _potential_bounds(model, phi_range, param_range, mpl)
    V_star = _uniform_log(rng, V_min, V_max)
    param = model.param_from_energy(phi_star, V_star, mpl)
    return Sample(phi_star=phi_star, param=param, weight=1.0)


def _sample_p3(
    rng: random.Random,
    phi_range: Tuple[float, float],
    param_range: Tuple[float, float],
    *,
    model: ModelConfig,
    mpl: float,
) -> Sample:
    """Volume-weighted proxy using weight w = exp(3N(phi_star))."""

    base_sample = _sample_p1(rng, phi_range, param_range)
    N_val = model.e_folds(base_sample.phi_star, base_sample.param, mpl)
    # Avoid floating-point overflow for very large N by capping the exponent.
    weight = math.exp(min(3.0 * N_val, 700.0))
    return Sample(phi_star=base_sample.phi_star, param=base_sample.param, weight=weight)


def _estimate_prior(
    *,
    name: str,
    sampler: Callable[[random.Random], Sample],
    n_samples: int,
    model: ModelConfig,
    mpl: float,
    N_range: Tuple[float, float],
    target: ICTargetSpec,
) -> PriorResult:
    rng = random.Random()
    n_valid = 0
    weight_sum = 0.0
    weight_sum_valid = 0.0
    sum_phi = 0.0
    sum_param = 0.0
    sum_N = 0.0

    for _ in range(n_samples):
        sample = sampler(rng)
        forward_result = model.forward(sample.phi_star, sample.param, mpl)
        is_valid = model.valid(
            sample.phi_star,
            sample.param,
            mpl=mpl,
            N_range=N_range,
            target=target,
        )

        weight_sum += sample.weight
        if is_valid:
            n_valid += 1
            weight_sum_valid += sample.weight
            sum_phi += sample.weight * sample.phi_star
            sum_param += sample.weight * sample.param
            sum_N += sample.weight * forward_result.N

    p_valid = weight_sum_valid / weight_sum if weight_sum > 0 else 0.0

    mean_phi_valid = sum_phi / weight_sum_valid if weight_sum_valid > 0 else None
    mean_param_valid = sum_param / weight_sum_valid if weight_sum_valid > 0 else None
    mean_N_valid = sum_N / weight_sum_valid if weight_sum_valid > 0 else None

    return PriorResult(
        name=name,
        n_samples=n_samples,
        n_valid=n_valid,
        weight_sum=weight_sum,
        weight_sum_valid=weight_sum_valid,
        p_valid=p_valid,
        mean_phi_valid=mean_phi_valid,
        mean_param_valid=mean_param_valid,
        mean_N_valid=mean_N_valid,
    )


def estimate_priors(
    *,
    model: ModelConfig = DEFAULT_MODEL,
    n_samples: int = 20000,
    phi_range: Tuple[float, float] | None = None,
    param_range: Tuple[float, float] | None = None,
    N_range: Tuple[float, float] = N_RANGE_DEFAULT,
    mpl: float = 1.0,
    target: ICTargetSpec = ICTargetSpec.mode_a(),
) -> Tuple[PriorResult, PriorResult, PriorResult]:
    """Estimate P(valid) for the three default priors via Monte Carlo."""

    phi_limits = phi_range or model.default_phi_range
    param_limits = param_range or model.default_param_range

    def p1_sampler(rng: random.Random) -> Sample:
        return _sample_p1(rng, phi_limits, param_limits)

    def p2_sampler(rng: random.Random) -> Sample:
        return _sample_p2(rng, phi_limits, param_limits, model=model, mpl=mpl)

    def p3_sampler(rng: random.Random) -> Sample:
        return _sample_p3(rng, phi_limits, param_limits, model=model, mpl=mpl)

    common_kwargs = dict(
        n_samples=n_samples,
        model=model,
        mpl=mpl,
        N_range=N_range,
        target=target,
    )

    p1 = _estimate_prior(name="P1_flat_phi_log_param", sampler=p1_sampler, **common_kwargs)
    p2 = _estimate_prior(name="P2_flat_phi_log_V", sampler=p2_sampler, **common_kwargs)
    p3 = _estimate_prior(name="P3_volume_weighted", sampler=p3_sampler, **common_kwargs)
    return p1, p2, p3


def _format_result(result: PriorResult, param_label: str) -> str:
    if result.mean_phi_valid is None:
        posterior = "(no valid samples)"
    else:
        posterior = (
            f"phi*: {result.mean_phi_valid:.3f}, "
            f"{param_label}: {result.mean_param_valid:.3e}, "
            f"N: {result.mean_N_valid:.2f}"
        )

    return (
        f"{result.name}: P(valid)={result.p_valid:.4e}"
        f" (n={result.n_samples}, valid={result.n_valid}); "
        f"posterior mean {posterior}"
    )


def run_summary(  # pragma: no cover - convenience CLI
    *,
    model: ModelConfig = DEFAULT_MODEL,
    n_samples: int = 20000,
    phi_range: Tuple[float, float] | None = None,
    param_range: Tuple[float, float] | None = None,
    N_range: Tuple[float, float] = N_RANGE_DEFAULT,
    mpl: float = 1.0,
    target: ICTargetSpec = ICTargetSpec.mode_a(),
) -> Iterable[str]:
    """Yield human-readable summary lines for the three priors."""

    results = estimate_priors(
        model=model,
        n_samples=n_samples,
        phi_range=phi_range,
        param_range=param_range,
        N_range=N_range,
        mpl=mpl,
        target=target,
    )
    for result in results:
        yield _format_result(result, model.param_name)


def run_sensitivity(  # pragma: no cover - convenience CLI
    *,
    model: ModelConfig = DEFAULT_MODEL,
    n_samples: int = 20000,
    phi_range: Tuple[float, float] | None = None,
    param_range: Tuple[float, float] | None = None,
    mpl: float = 1.0,
) -> Iterable[str]:
    """Yield summary lines for a small set of sensitivity variants.

    Variants cover:
    - Tensor bound on vs. off
    - Wider N range
    - Narrower and wider tolerance bands
    """

    base_target = ICTargetSpec.mode_a()
    configs = [
        dict(name="baseline_r_off", N_range=N_RANGE_DEFAULT, target=base_target),
        dict(name="tensor_on", N_range=N_RANGE_DEFAULT, target=ICTargetSpec.mode_b()),
        dict(name="wide_N", N_range=(45.0, 65.0), target=base_target),
        dict(
            name="tight_tolerances",
            N_range=N_RANGE_DEFAULT,
            target=ICTargetSpec(As0=base_target.As0, ns0=base_target.ns0, dAs_frac=0.01, dns_abs=0.002, r_max=None),
        ),
        dict(
            name="loose_tolerances",
            N_range=N_RANGE_DEFAULT,
            target=ICTargetSpec(As0=base_target.As0, ns0=base_target.ns0, dAs_frac=0.03, dns_abs=0.006, r_max=None),
        ),
    ]

    for cfg in configs:
        results = estimate_priors(
            model=model,
            n_samples=n_samples,
            phi_range=phi_range,
            param_range=param_range,
            N_range=cfg.get("N_range", N_RANGE_DEFAULT),
            mpl=mpl,
            target=cfg.get("target", base_target),
        )
        header = f"[{cfg['name']}]"
        yield header
        for result in results:
            yield _format_result(result, model.param_name)
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
