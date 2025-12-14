# MVP Checklist

This checklist tracks the **smallest viable effort**: treat (As, ns, optional r) as the “IC target”, map it back to a minimal pre-IC parameter space, and compute typicality under a few priors. See `DECISION_LOG.md` for rationale behind the Phase 0 choices and the handoff into Phase 1.

## Phase 0 — Target + conventions
- [x] Define the target region R(T) in (As, ns) and tolerances (see IC_TARGET_SPEC.md for chosen values).
- [x] Decide whether to include an r upper bound in the target (two modes recommended: on/off).
- [x] Fix N-range convention (default: N in [50, 60]; also test [45, 65] sensitivity).
- [x] Choose Planck units conventions (use reduced Planck mass Mpl = 2.435e18 GeV or set Mpl=1 consistently).

## Phase 1 — Forward model
- [x] Implement slow-roll parameters epsilon(phi), eta(phi).
- [x] Implement observables As(phi*, params), ns(phi*, params), r(phi*, params).
- [x] Implement N(phi*) with phi_end defined by epsilon=1.
- [x] Add a single function `forward(C)` returning dict {As, ns, r, N, phi_end}.

## Phase 2 — Validity predicate
- [x] Implement `accept_target(As, ns, r)` for the target region R(T).
- [x] Implement `valid(C) := accept_target(forward(C)) and N in range`.

## Phase 3 — Scanning / inference
- [x] Choose parameter ranges for a coarse scan over C=(phi_star, m).
- [x] Produce a feasibility plot: valid/invalid points in (phi_star, m).
- [x] Plot induced (As, ns) scatter with target window overlay.

## Phase 4 — Priors (“measures”) and typicality
- [x] Implement 2–3 priors over C:
  - [x] P1: flat in phi_star, flat in log m
  - [x] P2: flat in phi_star, flat in energy scale (proxy; see PRIORS.md)
  - [x] P3: volume-weighted proxy: weight by exp(3N(phi_star))
- [x] Compute P_i(valid) by Monte Carlo integration (or weighted grid integration).
- [x] Sensitivity tests: r on/off, N-range widened, tolerances widened/narrowed.

## Phase 5 — Report
- [x] Fill `docs/RESULTS_TEMPLATE.md`.
- [x] Save key plots/tables under `results/` with fixed filenames.
