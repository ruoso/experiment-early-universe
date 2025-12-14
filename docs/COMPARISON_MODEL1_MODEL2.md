# Model Comparison: Quadratic (Model 1) vs Plateau (Model 2)

## Feasibility (Phase 3)
- **Quadratic:**
  - Mode A: 1 / 1,600 valid grid points (phi*≈15.44, m≈6.0×10⁻⁶) with r≈0.134 → outside tensor limit.
  - Mode B: 0 / 1,600 valid due to r > 0.06 everywhere.
- **Plateau:**
  - Mode A: 2 / 1,600 valid (phi*≈5.32–5.42, V0≈1.0–1.2×10⁻¹⁰) with r≈0.003–0.004.
  - Mode B: identical validity (2 / 1,600); tensor bound inactive in the scanned band.

## Typicality (Phase 4, 20k samples)
- **Quadratic:**
  - Mode A: P(valid) ≈ 1.0×10⁻⁴ (P1), 1.5×10⁻⁴ (P2); P3 collapses to ≈1.2×10⁻⁸³.
  - Mode B: P(valid) = 0 for all priors because r fails everywhere.
- **Plateau:**
  - Mode A: P(valid) ≈ 7.0×10⁻⁴ (P1), 4.0×10⁻⁴ (P2); P3 ≈ 7×10⁻²³².
  - Mode B: P(valid) ≈ 5.0×10⁻⁴ (P1), 3.5×10⁻⁴ (P2); P3 ≈ 6×10⁻²³³.

## Takeaways
- Switching to the low-r plateau model makes Mode B feasible without tightening the scan or priors; the quadratic model remains ruled out once tensors are enforced.
- Scalar priors (P1/P2) are O(10⁻⁴–10⁻³) for both models, so feasibility improves modestly but does not reach order unity.
- Volume weighting annihilates validity in both families despite the plateau’s low r, indicating the suppression is structural to the measure choice, not the potential.
