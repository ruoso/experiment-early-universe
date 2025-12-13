# Model Spec (MVP)

## Default model family
Single-field slow-roll inflation with:
- V(phi) = 1/2 * m^2 * phi^2

Parameterization:
- C = (phi_star, m)

Conventions:
- Use reduced Planck mass Mpl (either set Mpl=1 throughout or keep explicit Mpl).
- phi_star is the field value when the pivot scale exits the horizon.

## Slow-roll definitions
epsilon(phi) = (Mpl^2 / 2) * (V'(phi)/V(phi))^2
eta(phi)     = Mpl^2 * V''(phi)/V(phi)

End of inflation:
- phi_end defined by epsilon(phi_end)=1

E-folds:
N(phi_star) = (1/Mpl^2) * ∫_{phi_end}^{phi_star} V/V' dphi

## Observables at pivot
As ≈ (1 / (24*pi^2*Mpl^4)) * V(phi_star)/epsilon(phi_star)
ns ≈ 1 - 6*epsilon(phi_star) + 2*eta(phi_star)
r  ≈ 16*epsilon(phi_star)

## MVP workflow notes
- For this potential, (ns, r) depend mainly on phi_star; m primarily sets As.
- This is useful: it cleanly separates “shape” from “normalization” in the first MVP.
