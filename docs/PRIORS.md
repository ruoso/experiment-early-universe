# Priors (“Measures”) for Typicality

We model multiverse-style selection by introducing a small menu of priors over the pre-IC parameterization C=(phi_star, m).

Important: These priors are *proxies* meant to test robustness/sensitivity.

## P1: flat(phi_star) × flat(log m)
- Sample phi_star uniformly in [phi_min, phi_max]
- Sample log m uniformly in [log m_min, log m_max]
Motivation: “uninformative” scale prior on amplitude parameter.

## P2: flat(phi_star) × flat(log V_star)
Let V_star = V(phi_star).
- Sample phi_star uniformly
- Sample log V_star uniformly, then solve for m from V_star = (1/2) m^2 phi_star^2
Motivation: proxy for “random energy scale at pivot”.

## P3: volume-weighted proxy
Weight samples by w = exp(3*N(phi_star)).
Motivation: caricature of volume weighting in eternal inflation. Use with care; it can dominate results.

## Outputs to report
For each prior P_i:
- estimated P_i(valid)
- posterior summaries of phi_star, m, N for the accepted set
- sensitivity plots under:
  - r constraint on/off
  - N-range variants
  - tolerance variants

## Implementation defaults (Phase 4)
- Ranges: phi_star in [6, 22], m in [5×10⁻⁷, 5×10⁻⁵], N in [50, 60] (matches Phase 3)
- Tensor constraint: off by default (`r_max=None`) to mirror the feasibility scan baseline
- P2 support: the V_star sampling window is set so that the derived m always falls within the m-range for any phi_star in range
- Estimator: simple Monte Carlo with optional volume weights; see `src/priors.py` for a CLI summary helper

## Sensitivity variants (Phase 4)
We record the impact of toggling:
- Tensor bound on (`r_max=0.06`) vs. off (baseline)
- Wider N window: [45, 65]
- Tolerances: tighter (dAs_frac=0.01, dns_abs=0.002) and looser (dAs_frac=0.03, dns_abs=0.006)
