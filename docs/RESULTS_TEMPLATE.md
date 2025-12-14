# Results Template (fill this in)

## Configuration (copied from IC_TARGET_SPEC)
- Target: As0=..., ns0=..., dAs_frac=..., dns_abs=...
- Mode: A (r_max=None) or B (r_max=0.06 default)
- N range: ...
- Model family: ...
- Parameter scan ranges: phi_star in [...], param in [...]

## Model results (repeat per family)
- Model name: ...
- Feasible region summary:
  - Size of scan: ...
  - Fraction valid (unweighted): ...
  - Notes (e.g., degeneracies, correlations): ...
- Typicality under priors (P1/P2/P3):
  - Table with P(valid) and posterior means
- Sensitivity runs: Mode A vs Mode B, N-range [50,60] vs [45,65]
- Required plots:
  - results/phase3_feasibility_phi_param.svg
  - results/phase3_scatter_As_ns.svg
  - (optional) posteriors for phi_star and model param

## Comparison + interpretation
- Cross-model comparison for Mode A / Mode B
- Does typicality look robust across priors?
- If not, which assumption dominates the conclusion?
