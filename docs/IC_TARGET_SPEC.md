# IC Target Spec (R(T))

Define the acceptance region R(T) for the primordial statistics used as
“initial conditions” for late-time structure simulations. This file is the
authoritative source for tolerances, pivot choices, and the run-mode split
used across every model.

## Baseline targets
- As0: 2.1e-9 (Planck best-fit amplitude at k = 0.05 Mpc⁻¹)
- ns0: 0.965 (Planck best-fit tilt at the same pivot)

Chosen tolerances:
- dAs_frac: 0.02 (±2% around As0)
- dns_abs: 0.004 (±0.004 around ns0)

Tensor ceiling:
- r_max: 0.06 (applied only in Mode B; set ``r_max=None`` to disable)

N-range convention:
- default: N in [50, 60]
- sensitivity: repeat with N in [45, 65]

## Run modes (frozen)

- **Mode A (baseline):** accept on (As, ns) only with ``r_max=None``
- **Mode B (modern):** accept on (As, ns) and enforce ``r <= r_max`` with
  ``r_max=0.06`` unless explicitly overridden

Planck units:
- use reduced Planck mass Mpl = 2.435e18 GeV
- set Mpl = 1 in slow-roll formulas; convert back with the stated Mpl when needed

## Acceptance function
In code, use ``ICTargetSpec`` from ``src/ic_spec.py``.

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
