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
