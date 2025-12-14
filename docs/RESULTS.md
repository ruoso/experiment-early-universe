# Results

## Configuration
- Target: As0=2.1e-9, ns0=0.965, dAs_frac=0.02, dns_abs=0.004, r_max=0.06 (tensor bound toggled off for priors)
- N range: [50, 60] for baseline scan and priors
- Model family: quadratic slow-roll single-field with Mpl=1 convention (Mpl=2.435e18 GeV optional)
- Parameter scan ranges: phi_star in [6.0, 22.0], m in [5e-7, 5e-5]

## Feasible region summary
- Size of scan: 1,600 grid points (40 x 40)
- Fraction valid (unweighted): 0.000625 (1 / 1600)
- Notes (e.g., degeneracies, correlations): Validity requires large phi_star with m near the lower edge; the feasible band is a narrow diagonal near phi_star ~15 and m ~6e-06.

## Typicality under priors
| Prior | P(valid) | Notes |
|---|---:|---|
| P1_flat_phi_log_m | 4.5e-4 | Posterior mean phi* ~15.0, m ~6.2e-06, N ~56 (rare but not ruled out). |
| P2_flat_phi_log_V | 6.5e-4 | Slightly higher due to energy weighting; similar posterior support. |
| P3_volume_weighted | 1.1e-81 | Volume weighting pushes toward larger N and effectively zeroes feasibility in the sampled window. |

## Sensitivity
- r constraint on/off: Enforcing r_max eliminates all valid samples in the scanned window.
- N-range: Widening to [45, 65] slightly raises P(valid) for P1/P2 (~6e-4) but volume-weighted prior remains exponentially suppressed.
- Tolerance changes: Tightening cuts drops P(valid) by ~10x (or to zero for P3); loosening gives modest increases (<2x) but keeps probabilities <1e-3.

## Plots generated (paths)
- results/phase3_feasibility_phi_m.svg
- results/phase3_scatter_As_ns.svg

## Interpretation (short)
- Typicality is low (<1e-3) under all non-volume priors and effectively zero when volume weighting is applied.
- Tensor enforcement or tighter tolerances remove all sampled support; only modest relief comes from widening N or tolerances, indicating the model is finely tuned in this configuration.
