# Model 2 (Plateau) Results

## Configuration
- Target spec: Mode A / Mode B from `docs/IC_TARGET_SPEC.md` (As0=2.1e-9, ns0=0.965, dAs_frac=0.02, dns_abs=0.004, r_max=0.06 for Mode B)
- N range: [50, 60]
- Parameter ranges: phi_star ∈ [4.5, 8.5]; V0 ∈ [1e-11, 1e-8]; both log-spaced in V0
- Grid: 40 × 40 coarse sweep (1,600 points)

## Phase 3 feasibility
- **Mode A (r off):** 2 / 1,600 points valid (phi*≈5.32–5.42, V0≈1.0–1.2×10⁻¹⁰), satisfying N≈53–58 and r≈0.003–0.004. Plots saved under `results/plateau_mode_a/`.
- **Mode B (r ≤ 0.06):** Identical validity set (2 / 1,600); tensor bound inactive for this model at the scanned range. Plots saved under `results/plateau_mode_b/`.

## Phase 4 typicality (20k Monte Carlo samples)
| Mode | Prior | P(valid) | Posterior means (phi*, V0, N) |
| --- | --- | --- | --- |
| A | P1 flat phi*, log V0 | 7.0×10⁻⁴ | (5.34, 1.14×10⁻¹⁰, 54.52) |
| A | P2 flat phi*, log V* | 4.0×10⁻⁴ | (5.37, 1.09×10⁻¹⁰, 55.97) |
| A | P3 volume-weighted | ~7.0×10⁻²³² | (5.43, 9.93×10⁻¹¹, 58.74) |
| B | P1 flat phi*, log V0 | 5.0×10⁻⁴ | (5.40, 1.03×10⁻¹⁰, 57.11) |
| B | P2 flat phi*, log V* | 3.5×10⁻⁴ | (5.31, 1.20×10⁻¹⁰, 53.19) |
| B | P3 volume-weighted | ~5.9×10⁻²³³ | (5.41, 1.00×10⁻¹⁰, 57.89) |

## Notes
- Plateau predictiveness is driven by the narrow phi* band delivering N within [50, 60]; the tensor ceiling is automatically satisfied (r≲0.004) across the valid region.
- Volume weighting remains catastrophically suppressive: the capped exp(3N) weights push P(valid) effectively to zero even though scalar priors give ~10⁻³ support.
