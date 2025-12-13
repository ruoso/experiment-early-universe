# MVP Checklist

This checklist tracks the **smallest viable effort**: treat (As, ns, optional r) as the “IC target”, map it back to a minimal pre-IC parameter space, and compute typicality under a few priors.

## Phase 0 — Target + conventions
- [ ] Define the target region R(T) in (As, ns) and tolerances.
- [ ] Decide whether to include an r upper bound in the target (two modes recommended: on/off).
- [ ] Fix N-range convention (default: N in [50, 60]; also test [45, 65] sensitivity).
- [ ] Choose Planck units conventions (use reduced Planck mass Mpl = 2.435e18 GeV or set Mpl=1 consistently).

## Phase 1 — Forward model
- [ ] Implement slow-roll parameters epsilon(phi), eta(phi).
- [ ] Implement observables As(phi*, params), ns(phi*, params), r(phi*, params).
- [ ] Implement N(phi*) with phi_end defined by epsilon=1.
- [ ] Add a single function `forward(C)` returning dict {As, ns, r, N, phi_end}.

## Phase 2 — Validity predicate
- [ ] Implement `accept_target(As, ns, r)` for the target region R(T).
- [ ] Implement `valid(C) := accept_target(forward(C)) and N in range`.

## Phase 3 — Scanning / inference
- [ ] Choose parameter ranges for a coarse scan over C=(phi_star, m).
- [ ] Produce a feasibility plot: valid/invalid points in (phi_star, m).
- [ ] Plot induced (As, ns) scatter with target window overlay.

## Phase 4 — Priors (“measures”) and typicality
- [ ] Implement 2–3 priors over C:
  - [ ] P1: flat in phi_star, flat in log m
  - [ ] P2: flat in phi_star, flat in energy scale (proxy; see PRIORS.md)
  - [ ] P3: volume-weighted proxy: weight by exp(3N(phi_star))
- [ ] Compute P_i(valid) by Monte Carlo integration (or weighted grid integration).
- [ ] Sensitivity tests: r on/off, N-range widened, tolerances widened/narrowed.

## Phase 5 — Report
- [ ] Fill `docs/RESULTS_TEMPLATE.md`.
- [ ] Save key plots/tables under `results/` with fixed filenames.
