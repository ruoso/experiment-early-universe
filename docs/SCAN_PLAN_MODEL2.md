# SCAN_PLAN_MODEL2

## Objective
Mirror the Phase 3 scan used for the quadratic model while swapping in the plateau potential from `docs/MODEL2_SPEC.md`. Defaults should require no code changes to priors or acceptance logic.

## Parameter ranges
- phi_star: [4.5, 8.5] (linear spacing; 40 points baseline)
- V0: [1e-11, 1e-8] (log spacing; 40 points baseline)
- N range: [50, 60] (default) with sensitivity runs on [45, 65]

## Sampling strategy
- Maintain the same grid density as Model 1 (40x40) unless runtime constraints force coarsening.
- Use log spacing for V0 to span multiple orders of magnitude around the As target.
- Reuse the same priors (P1/P2/P3) with phi_star bounds above and V0 bounds as stated.

## Run modes
- Mode A: target on (As, ns) only (ICTargetSpec.mode_a())
- Mode B: target on (As, ns, r) with r_max=0.06 (ICTargetSpec.mode_b())

## Outputs required
- Feasibility map: `results/phase3_feasibility_phi_param.svg`
- (As, ns) scatter with acceptance overlay: `results/phase3_scatter_As_ns.svg`
- Typicality table: P(valid) for P1/P2/P3 under Mode A and Mode B
- Posterior summaries for phi_star and V0 conditional on validity

## Sanity checks before interpretation
- n_s trend follows ~1 - 2/N
- r remains ~12/N^2 and well below the Mode B ceiling
- V0 range covers As window for the sampled N-range
