"""Phase 3 scanning helpers for registered inflationary models.

This module performs coarse grid scans over (phi_star, model_param) to
assess feasibility under the Phase 2 validity predicate and produces simple
diagnostic plots for the feasibility region and the induced (As, ns)
scatter.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from .ic_spec import ICTargetSpec, N_RANGE_BASELINE
from .model_registry import ModelConfig, get_model


DEFAULT_MODEL = get_model("quadratic")


def _logspace(start: float, stop: float, num: int) -> List[float]:
    """Generate logarithmically spaced values between ``start`` and ``stop``."""

    if num < 2:
        return [start]

    log_start = math.log(start)
    log_stop = math.log(stop)
    step = (log_stop - log_start) / (num - 1)
    return [math.exp(log_start + i * step) for i in range(num)]


@dataclass
class ScanPoint:
    model_name: str
    param_name: str
    phi_star: float
    param: float
    As: float
    ns: float
    r: float
    N: float
    phi_end: float
    accept: bool
    valid: bool

    @classmethod
    def from_params(
        cls,
        phi_star: float,
        param: float,
        *,
        mpl: float,
        N_range: Tuple[float, float],
        model: ModelConfig,
        target: ICTargetSpec,
    ) -> "ScanPoint":
        forward = model.forward(phi_star, param, mpl)
        accept = target.accept(forward.As, forward.ns, forward.r)
        valid = model.valid(
            phi_star,
            param,
            mpl=mpl,
            N_range=N_range,
            target=target,
        )
        return cls(
            model_name=model.name,
            param_name=model.param_name,
            phi_star=phi_star,
            param=param,
            As=forward.As,
            ns=forward.ns,
            r=forward.r,
            N=forward.N,
            phi_end=forward.phi_end,
            accept=accept,
            valid=valid,
        )


def coarse_grid(
    *,
    model: ModelConfig = DEFAULT_MODEL,
    phi_range: Tuple[float, float] | None = None,
    param_range: Tuple[float, float] | None = None,
    N_range: Tuple[float, float] = N_RANGE_BASELINE,
    n_phi: int = 40,
    n_param: int = 40,
    mpl: float = 1.0,
    target: ICTargetSpec = ICTargetSpec.mode_a(),
) -> List[ScanPoint]:
    """Evaluate a coarse grid over (phi_star, model_param).

    The grid samples ``phi_star`` linearly and the second parameter either
    linearly or logarithmically depending on ``model.param_scale``.
    """

    phi_limits = phi_range or model.default_phi_range
    param_limits = param_range or model.default_param_range

    phi_vals = [
        phi_limits[0] + i * (phi_limits[1] - phi_limits[0]) / (n_phi - 1)
        for i in range(n_phi)
    ]

    if model.param_scale == "log":
        param_vals = _logspace(param_limits[0], param_limits[1], n_param)
    else:
        param_vals = [
            param_limits[0] + i * (param_limits[1] - param_limits[0]) / (n_param - 1)
            for i in range(n_param)
        ]

    results: List[ScanPoint] = []
    for phi_star in phi_vals:
        for param_val in param_vals:
            results.append(
                ScanPoint.from_params(
                    phi_star,
                    param_val,
                    mpl=mpl,
                    N_range=N_range,
                    model=model,
                    target=target,
                )
            )
    return results


def _split_by_validity(points: Iterable[ScanPoint]) -> Tuple[List[ScanPoint], List[ScanPoint]]:
    valid: List[ScanPoint] = []
    invalid: List[ScanPoint] = []
    for point in points:
        (valid if point.valid else invalid).append(point)
    return valid, invalid


def plot_feasibility(
    points: Sequence[ScanPoint],
    *,
    target: ICTargetSpec,
    param_scale: str,
    results_dir: str = "results",
) -> Tuple[str, str]:
    """Create feasibility plots and return the saved file paths (SVG)."""

    os.makedirs(results_dir, exist_ok=True)
    valid, invalid = _split_by_validity(points)

    width, height, pad = 800, 550, 60

    def _header(title: str) -> List[str]:
        return [
            "<?xml version='1.0' encoding='UTF-8'?>",
            f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' aria-label='{title}'>",
            f"  <title>{title}</title>",
            "  <style>text{font-family:Arial,sans-serif;font-size:14px}</style>",
        ]

    def _footer() -> List[str]:
        return ["</svg>"]

    def _scatter_elements(
        xs: List[float], ys: List[float], color: str, label: str
    ) -> List[str]:
        elements = [f"  <g fill='{color}' fill-opacity='0.7' stroke='none'>"]
        for x, y in zip(xs, ys):
            elements.append(f"    <circle cx='{x:.2f}' cy='{y:.2f}' r='3' />")
        elements.append("  </g>")
        elements.append(
            f"  <text x='{width - pad}' y='{pad - 20 if label== 'valid' else pad}' text-anchor='end' fill='{color}'>■ {label}</text>"
        )
        return elements

    def _axis_labels(x_label: str, y_label: str) -> List[str]:
        return [
            f"  <text x='{width/2:.1f}' y='{height - 15}' text-anchor='middle'>{x_label}</text>",
            f"  <text x='{20}' y='{height/2:.1f}' text-anchor='middle' transform='rotate(-90, 20, {height/2:.1f})'>{y_label}</text>",
        ]

    # (phi_star, param) feasibility map (log scale optional for param)
    phi_min = min(p.phi_star for p in points)
    phi_max = max(p.phi_star for p in points)
    param_min = min(p.param for p in points)
    param_max = max(p.param for p in points)

    if param_scale == "log":
        log_param_min = math.log10(param_min)
        log_param_max = math.log10(param_max)

    def _map_phi(phi_val: float) -> float:
        return pad + (phi_val - phi_min) / (phi_max - phi_min) * (width - 2 * pad)

    def _map_param(param_val: float) -> float:
        if param_scale == "log":
            frac = (math.log10(param_val) - log_param_min) / (log_param_max - log_param_min)
        else:
            frac = (param_val - param_min) / (param_max - param_min)
        return height - pad - frac * (height - 2 * pad)

    valid_x = [_map_phi(p.phi_star) for p in valid]
    valid_y = [_map_param(p.param) for p in valid]
    invalid_x = [_map_phi(p.phi_star) for p in invalid]
    invalid_y = [_map_param(p.param) for p in invalid]

    phi_m_lines: List[str] = _header("Feasibility in (phi*, param)")
    phi_m_lines.append(f"  <rect x='{pad}' y='{pad}' width='{width-2*pad}' height='{height-2*pad}' fill='none' stroke='black' stroke-width='1' />")
    phi_m_lines.extend(_scatter_elements(invalid_x, invalid_y, "#d62728", "invalid"))
    phi_m_lines.extend(_scatter_elements(valid_x, valid_y, "#1f77b4", "valid"))
    y_label = f"{points[0].param_name} (log10)" if param_scale == "log" else points[0].param_name
    phi_m_lines.extend(_axis_labels("phi*", y_label) )
    phi_m_lines.extend(_footer())

    phi_m_path = os.path.join(results_dir, "phase3_feasibility_phi_param.svg")
    with open(phi_m_path, "w", encoding="utf-8") as f:
        f.write("\n".join(phi_m_lines))

    # (As, ns) scatter with target window (linear scale)
    ns_min_data = min(p.ns for p in points)
    ns_max_data = max(p.ns for p in points)
    As_min_data = min(p.As for p in points)
    As_max_data = max(p.As for p in points)

    ns_min = min(ns_min_data, target.ns0 - target.dns_abs)
    ns_max = max(ns_max_data, target.ns0 + target.dns_abs)
    As_min = min(As_min_data, target.As0 * (1.0 - target.dAs_frac))
    As_max = max(As_max_data, target.As0 * (1.0 + target.dAs_frac))

    def _map_ns(ns_val: float) -> float:
        return pad + (ns_val - ns_min) / (ns_max - ns_min) * (width - 2 * pad)

    def _map_As(As_val: float) -> float:
        return height - pad - (As_val - As_min) / (As_max - As_min) * (height - 2 * pad)

    valid_x_ns = [_map_ns(p.ns) for p in valid]
    valid_y_As = [_map_As(p.As) for p in valid]
    invalid_x_ns = [_map_ns(p.ns) for p in invalid]
    invalid_y_As = [_map_As(p.As) for p in invalid]

    As_ns_lines: List[str] = _header("Induced (As, ns) scatter")
    As_ns_lines.append(f"  <rect x='{pad}' y='{pad}' width='{width-2*pad}' height='{height-2*pad}' fill='none' stroke='black' stroke-width='1' />")

    # Target window rectangle
    ns_target_min = target.ns0 - target.dns_abs
    ns_target_max = target.ns0 + target.dns_abs
    As_target_min = target.As0 * (1.0 - target.dAs_frac)
    As_target_max = target.As0 * (1.0 + target.dAs_frac)
    rect_x = _map_ns(ns_target_min)
    rect_y = _map_As(As_target_max)
    rect_w = _map_ns(ns_target_max) - rect_x
    rect_h = _map_As(As_target_min) - rect_y
    As_ns_lines.append(
        f"  <rect x='{rect_x:.2f}' y='{rect_y:.2f}' width='{rect_w:.2f}' height='{rect_h:.2f}' fill='#999' fill-opacity='0.2' stroke='#666' stroke-dasharray='4,2' />"
    )

    As_ns_lines.extend(_scatter_elements(invalid_x_ns, invalid_y_As, "#d62728", "invalid"))
    As_ns_lines.extend(_scatter_elements(valid_x_ns, valid_y_As, "#1f77b4", "valid"))
    As_ns_lines.extend(_axis_labels("ns", "As"))
    As_ns_lines.extend(_footer())

    As_ns_path = os.path.join(results_dir, "phase3_scatter_As_ns.svg")
    with open(As_ns_path, "w", encoding="utf-8") as f:
        f.write("\n".join(As_ns_lines))

    return phi_m_path, As_ns_path


def run_phase3_scan(
    *,
    model: ModelConfig = DEFAULT_MODEL,
    phi_range: Tuple[float, float] | None = None,
    param_range: Tuple[float, float] | None = None,
    N_range: Tuple[float, float] = N_RANGE_BASELINE,
    n_phi: int = 40,
    n_param: int = 40,
    mpl: float = 1.0,
    target: ICTargetSpec = ICTargetSpec.mode_a(),
    results_dir: str = "results",
) -> Tuple[List[ScanPoint], Tuple[str, str]]:
    """Convenience wrapper that performs the scan and plots the results."""

    points = coarse_grid(
        model=model,
        phi_range=phi_range,
        param_range=param_range,
        N_range=N_range,
        n_phi=n_phi,
        n_param=n_param,
        mpl=mpl,
        target=target,
    )
    paths = plot_feasibility(
        points,
        target=target,
        param_scale=model.param_scale,
        results_dir=results_dir,
    )
    return points, paths


if __name__ == "__main__":
    points, paths = run_phase3_scan()
    valid_count = sum(1 for p in points if p.valid)
    total = len(points)
    print(f"Generated {total} grid points; {valid_count} are valid.")
    print("Saved plots:")
    for path in paths:
        print(f" - {path}")
