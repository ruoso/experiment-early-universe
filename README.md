# Pre-IC Selection MVP

This repository implements a smallest-viable “walk-back from ICs” pipeline.

## Concept
We treat the late-time simulation “initial conditions” (ICs) as a small set of target statistics for the primordial Gaussian random field:
- **As**: scalar amplitude
- **ns**: scalar spectral index (tilt)
- optional: upper bound on **r** (tensor-to-scalar ratio)

Pipeline:
1. Choose a minimal pre-IC parameterization **C**.
2. Compute a forward map **F(C) -> (As, ns, r, N)** using slow-roll formulas.
3. Define a validity predicate: `Valid(C) := (F(C) in target_region) AND (N in [Nmin, Nmax])`.
4. Treat “multiverse selection” as a *family of priors* over **C** and compute the probability mass of valid configurations under each prior.

The MVP default model is single-field slow-roll with:
- Potential: `V(phi) = 1/2 * m^2 * phi^2`
- Parameters: `(phi_star, m)`, evaluated at a chosen pivot scale

## Repository layout
- `docs/`
  - `CHECKLIST.md`: end-to-end checklist for the MVP
  - `IC_TARGET_SPEC.md`: how we define the acceptance region in (As, ns, r)
  - `MODEL_SPEC.md`: the model family and formulas used for the forward map
  - `PRIORS.md`: the small menu of priors (“measures”) used in the selection test
  - `RESULTS_TEMPLATE.md`: a fill-in template for reporting results
  - `RESULTS.md`: completed report with scan/prior outputs and sensitivities
- `src/`
  - `mvp_model.py`: forward-map implementation (slow-roll) plus validity predicates for Phase 2
  - `scan.py`: coarse grid scan + feasibility plots for Phase 3
  - `priors.py`: priors over parameter space and P(valid) estimators for Phase 4
- `results/`: generated plots/tables
- `notebooks/`: optional exploratory notebooks

Run the Phase 3 feasibility scan:

```
python -m src.scan
```

The SVG plots are saved under `results/`.

Estimate P(valid) under the Phase 4 prior menu (defaults: tensor bound off, N in [50, 60]):

```
python -m src.priors
```

Run tensor/N/tolerance sensitivity sweeps with:

```
python -m src.priors --sensitivity
```

## MVP “done” criteria
- A feasible region of `(phi_star, m)` that matches `(As, ns)` within tolerances and yields `N` in range.
- A table of `P(valid)` under at least 2–3 priors, plus sensitivity to:
  - N range (e.g., 50–60 vs 45–65)
  - r constraint (on/off)
