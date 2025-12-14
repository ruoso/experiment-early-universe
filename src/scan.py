"""Phase 3 scanning helpers for the quadratic slow-roll MVP.

This module performs coarse grid scans over (phi_star, m) to assess
feasibility under the Phase 2 validity predicate and produces simple
diagnostic plots for the feasibility region and the induced (As, ns)
scatter.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from . import mvp_model


PHI_RANGE_DEFAULT: Tuple[float, float] = (6.0, 22.0)
M_RANGE_DEFAULT: Tuple[float, float] = (5e-7, 5e-5)
N_RANGE_DEFAULT: Tuple[float, float] = (50.0, 60.0)


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
    phi_star: float
    m: float
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
        m: float,
        *,
        mpl: float,
        N_range: Tuple[float, float],
        As0: float,
        ns0: float,
        dAs_frac: float,
        dns_abs: float,
        r_max: float | None,
    ) -> "ScanPoint":
        forward = mvp_model.forward(phi_star, m, mpl)
        accept = mvp_model.accept_target(
            forward.As,
            forward.ns,
            forward.r,
            As0=As0,
            ns0=ns0,
            dAs_frac=dAs_frac,
            dns_abs=dns_abs,
            r_max=r_max,
        )
        valid = mvp_model.valid(
            phi_star,
            m,
            mpl=mpl,
            N_range=N_range,
            As0=As0,
            ns0=ns0,
            dAs_frac=dAs_frac,
            dns_abs=dns_abs,
            r_max=r_max,
        )
        return cls(
            phi_star=phi_star,
            m=m,
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
    phi_range: Tuple[float, float] = PHI_RANGE_DEFAULT,
    m_range: Tuple[float, float] = M_RANGE_DEFAULT,
    N_range: Tuple[float, float] = N_RANGE_DEFAULT,
    n_phi: int = 40,
    n_m: int = 40,
    mpl: float = 1.0,
    As0: float = mvp_model.AS0,
    ns0: float = mvp_model.NS0,
    dAs_frac: float = mvp_model.DAS_FRAC,
    dns_abs: float = mvp_model.DNS_ABS,
    r_max: float | None = None,
) -> List[ScanPoint]:
    """Evaluate a coarse grid over (phi_star, m).

    The grid samples ``phi_star`` linearly and ``m`` logarithmically to capture
    the wide dynamic range of the mass parameter while keeping runtime small.
    """

    phi_vals = [
        phi_range[0] + i * (phi_range[1] - phi_range[0]) / (n_phi - 1)
        for i in range(n_phi)
    ]
    m_vals = _logspace(m_range[0], m_range[1], n_m)

    results: List[ScanPoint] = []
    for phi_star in phi_vals:
        for m_val in m_vals:
            results.append(
                ScanPoint.from_params(
                    phi_star,
                    m_val,
                    mpl=mpl,
                    N_range=N_range,
                    As0=As0,
                    ns0=ns0,
                    dAs_frac=dAs_frac,
                    dns_abs=dns_abs,
                    r_max=r_max,
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
    As0: float = mvp_model.AS0,
    ns0: float = mvp_model.NS0,
    dAs_frac: float = mvp_model.DAS_FRAC,
    dns_abs: float = mvp_model.DNS_ABS,
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

    # (phi_star, m) feasibility map (log scale for m)
    phi_min = min(p.phi_star for p in points)
    phi_max = max(p.phi_star for p in points)
    log_m_min = math.log10(min(p.m for p in points))
    log_m_max = math.log10(max(p.m for p in points))

    def _map_phi(phi_val: float) -> float:
        return pad + (phi_val - phi_min) / (phi_max - phi_min) * (width - 2 * pad)

    def _map_m(m_val: float) -> float:
        frac = (math.log10(m_val) - log_m_min) / (log_m_max - log_m_min)
        return height - pad - frac * (height - 2 * pad)

    valid_x = [_map_phi(p.phi_star) for p in valid]
    valid_y = [_map_m(p.m) for p in valid]
    invalid_x = [_map_phi(p.phi_star) for p in invalid]
    invalid_y = [_map_m(p.m) for p in invalid]

    phi_m_lines: List[str] = _header("Feasibility in (phi*, m)")
    phi_m_lines.append(f"  <rect x='{pad}' y='{pad}' width='{width-2*pad}' height='{height-2*pad}' fill='none' stroke='black' stroke-width='1' />")
    phi_m_lines.extend(_scatter_elements(invalid_x, invalid_y, "#d62728", "invalid"))
    phi_m_lines.extend(_scatter_elements(valid_x, valid_y, "#1f77b4", "valid"))
    phi_m_lines.extend(_axis_labels("phi*", "m (log10)") )
    phi_m_lines.extend(_footer())

    phi_m_path = os.path.join(results_dir, "phase3_feasibility_phi_m.svg")
    with open(phi_m_path, "w", encoding="utf-8") as f:
        f.write("\n".join(phi_m_lines))

    # (As, ns) scatter with target window (linear scale)
    ns_min_data = min(p.ns for p in points)
    ns_max_data = max(p.ns for p in points)
    As_min_data = min(p.As for p in points)
    As_max_data = max(p.As for p in points)

    ns_min = min(ns_min_data, ns0 - dns_abs)
    ns_max = max(ns_max_data, ns0 + dns_abs)
    As_min = min(As_min_data, As0 * (1.0 - dAs_frac))
    As_max = max(As_max_data, As0 * (1.0 + dAs_frac))

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
    ns_target_min = ns0 - dns_abs
    ns_target_max = ns0 + dns_abs
    As_target_min = As0 * (1.0 - dAs_frac)
    As_target_max = As0 * (1.0 + dAs_frac)
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
    phi_range: Tuple[float, float] = PHI_RANGE_DEFAULT,
    m_range: Tuple[float, float] = M_RANGE_DEFAULT,
    N_range: Tuple[float, float] = N_RANGE_DEFAULT,
    n_phi: int = 40,
    n_m: int = 40,
    mpl: float = 1.0,
    As0: float = mvp_model.AS0,
    ns0: float = mvp_model.NS0,
    dAs_frac: float = mvp_model.DAS_FRAC,
    dns_abs: float = mvp_model.DNS_ABS,
    r_max: float | None = None,
    results_dir: str = "results",
) -> Tuple[List[ScanPoint], Tuple[str, str]]:
    """Convenience wrapper that performs the scan and plots the results."""

    points = coarse_grid(
        phi_range=phi_range,
        m_range=m_range,
        N_range=N_range,
        n_phi=n_phi,
        n_m=n_m,
        mpl=mpl,
        As0=As0,
        ns0=ns0,
        dAs_frac=dAs_frac,
        dns_abs=dns_abs,
        r_max=r_max,
    )
    paths = plot_feasibility(
        points,
        As0=As0,
        ns0=ns0,
        dAs_frac=dAs_frac,
        dns_abs=dns_abs,
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
