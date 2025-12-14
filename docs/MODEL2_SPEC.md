# MODEL2_SPEC — Plateau (low-r) potential

## Potential definition

\[
V(\phi) = V_0 \left(1 - e^{-\sqrt{2/3}\,\phi/M_P}\right)^2
\]

- Parameters: \(V_0\) (amplitude), \(\phi_*\) (pivot field value)
- Units: reduced Planck mass set to 1 inside the slow-roll expressions; restore with \(M_P = 2.435\times 10^{18}\) GeV if needed.

## Slow-roll ingredients

- \(\epsilon(\phi) = 2 a^2 e^{-2 a \phi} / (1 - e^{-a \phi})^2\) with \(a = \sqrt{2/3}\)
- \(\eta(\phi) = 2 a^2 (-e^{-a \phi} + 2 e^{-2 a \phi}) / (1 - e^{-a \phi})^2\)
- End of inflation: \(\epsilon(\phi_\text{end}) = 1 \Rightarrow \phi_\text{end} = a^{-1}\ln(1 + \sqrt{2}\,a)\)
- E-folds from \(\phi_\text{end}\) to \(\phi_*\):
  \[
  N(\phi_*) = \frac{1}{2a}\left[\frac{e^{a\phi_*} - e^{a\phi_\text{end}}}{a} - (\phi_* - \phi_\text{end})\right]
  \]

## Forward prediction

`predict(phi_star, V0, mpl=1.0)` returns:
- As using \(V\) and \(\epsilon\)
- ns using \(\epsilon\) and \(\eta\)
- r using \(r = 16\epsilon\)
- N using the analytic expression above

## Parameter bounds / scan guidance

- \(\phi_*\): [4.5, 8.5] spans \(N \approx 45{-}65\)
- \(V_0\): log-flat over [1e-11, 1e-8] to cover \(A_s\) around \(2.1\times 10^{-9}\)
- Sampling: log spacing in \(V_0\), linear spacing in \(\phi_*\), matching the Model 1 scan density

## Sanity checks

- Expect \(n_s \approx 1 - 2/N\)
- Expect \(r \approx 12/N^2\) (order of magnitude)

The implementation lives in `src/plateau_model.py` and conforms to the same forward/valid interface as `src/mvp_model.py`.
