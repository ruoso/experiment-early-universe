# IC Target Spec (R(T))

Define the acceptance region R(T) for the primordial statistics used as “initial conditions” for late-time structure simulations.

## Baseline targets
- As0: 2.1e-9
- ns0: 0.965

Choose tolerances:
- dAs_frac: e.g. 0.02 (±2%) or 0.05 (±5%)
- dns_abs: e.g. 0.004 (±0.004)

Optional tensor constraint:
- r_max: e.g. 0.06 (set r_max=None to disable)

## Acceptance function
A point is accepted if:
- As in [As0*(1-dAs_frac), As0*(1+dAs_frac)]
- ns in [ns0-dns_abs, ns0+dns_abs]
- if enabled: r <= r_max

## Sensitivity plan
Run two modes:
- Mode A: accept (As, ns) only
- Mode B: accept (As, ns) plus r constraint

Also test:
- tighter/looser tolerances
- N range [50, 60] vs [45, 65]
