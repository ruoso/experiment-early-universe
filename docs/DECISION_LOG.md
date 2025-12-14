# Decision log

## Rationale for Phase 0 choices
- **Target anchors (As0, ns0):** We lock to the Planck 2018 best-fit amplitude and tilt at the 0.05 Mpc⁻¹ pivot to stay consistent with the reference measurement set and keep later comparisons reproducible.
- **Tolerances (dAs_frac, dns_abs):** ±2% on As and ±0.004 on ns keep the acceptance window narrow enough to reflect current observational precision while allowing a few-sigma cushion for the simplified slow-roll model.
- **Tensor toggle (r_max = 0.06 or disabled):** Including r when needed enforces the prevailing observational upper limit; leaving it off preserves a clean scalar-only baseline so we can compare the impact of tensors explicitly.
- **N-range convention ([50, 60] default; [45, 65] sensitivity):** The default brackets the canonical post-inflation expansion history assumption; widening to [45, 65] tests how sensitive feasibility is to reheating/thermal history uncertainties.
- **Planck units (Mpl = 2.435e18 GeV; set Mpl=1 in formulas):** Using reduced Planck units matches the slow-roll literature and keeps symbolic expressions simple; carrying the explicit Mpl value documents the physical scale used for back-conversions.

## Phase 3 parameter scan setup
- **phi_star span (6–22)**: covers the slow-roll regime from just above the end of inflation (φ_end≈√2) up to values that keep ε, η ≪ 1 while broadening the tilt range.
- **m span (5×10⁻⁷–5×10⁻⁵, log-spaced)**: brackets the ~10⁻⁶ scale required to hit As≈2.1×10⁻⁹ across the phi_star grid and leaves room for off-target regions to visualize feasibility.
- **Grid density (40×40)**: coarse enough for a fast diagnostic sweep but sufficient to resolve the feasibility band visible in the plots.
- **Outputs**: the scan generates two SVGs under `results/` showing (phi_star, m) validity and the induced (As, ns) scatter with the target window overlay.
- **Tensor toggle off (r_max=None)**: the quadratic potential overshoots the r bound; disabling it for the Phase 3 diagnostic keeps the focus on scalar feasibility before applying tensor constraints in sensitivity checks.

## Next step
Move into **Phase 4 — Priors and typicality**: implement the prior menu in `priors.py` and integrate the validity predicate to compute P(valid) for each choice.

## Phase 4 prior choices and defaults
- **Range alignment:** match the Phase 3 grid (phi_star ∈ [6, 22], m ∈ [5×10⁻⁷, 5×10⁻⁵]) and keep the default e-fold window N ∈ [50, 60] so the prior integration is directly comparable to the feasibility scan.
- **Tensor toggle off:** retain `r_max=None` as the baseline; apply the tensor bound only in sensitivity runs since the quadratic model generically violates it.
- **P2 support window:** choose the log V_star support so that the derived m stays within [m_min, m_max] for any phi_star in range, avoiding implicit truncation and keeping the log-energy prior well defined.
- **Estimator:** use simple Monte Carlo draws (20k default) with volume weights applied only to P3 to keep the P1/P2 estimates directly comparable.

## Phase 4 sensitivity settings
- **Tensor constraint sweep:** compare the baseline scalar-only acceptance with `r_max=0.06` enabled to quantify how strongly the tensor bound suppresses validity.
- **N-range widening:** repeat the estimates with N ∈ [45, 65] to probe uncertainty from reheating/thermal history assumptions.
- **Tolerance tightening/loosening:** halve (dAs_frac=0.01, dns_abs=0.002) and scale up (dAs_frac=0.03, dns_abs=0.006) the acceptance window to see how sharply the prior mass responds to observational precision.

## Phase 5 reporting takeaways
- **Feasibility scan outcome:** Only 1 of 1,600 grid points in the Phase 3 sweep is valid (≈6.25×10⁻⁴ fraction), localized near φ*≈15 and m≈6×10⁻⁶; plots saved under `results/` visualize the narrow band.
- **Baseline typicality:** For the scalar-only baseline, P(valid) ≈ 4.5×10⁻⁴ (P1) to 6.5×10⁻⁴ (P2); volume weighting (P3) collapses support to ~10⁻⁸¹.
- **Sensitivity:** Enforcing the tensor bound removes all support; widening N to [45, 65] modestly increases P(valid) (<1×10⁻³ for P1/P2), while tighter tolerances suppress validity by ≳10× and looser tolerances yield only slight relief.

## Phase 6 decision (Model 1 vs Model 2)
- **Finding:** The plateau (Model 2) introduces a small valid band that survives the tensor ceiling (Mode B feasible), but scalar priors stay at O(10⁻⁴–10⁻³) and volume weighting still drives P(valid) ≈ 0 for both models.
- **Decision:** Treat the suppression as measure-dominated and prioritize **measure sensitivity** next (e.g., alternative volume weights / reheating assumptions) over adding more low-r models, since the plateau does not restore typicality.
