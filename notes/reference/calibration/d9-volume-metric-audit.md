# D9.20 FVS volume column audit

Date: 2026-11-06
Issues: #447
Evidence: `runtime/cwh-volume-audit/volume-rows.csv`

## Finding

FVS exposes `MCuM` (merchantable cubic) and `TCuM` (total cubic). The PSP tree detail
exposes `VOL_MER` (gross merchantable), `VOL_NTWB` (net merchantable), and `VOL_WSV`
(whole stem).

The CWH external volume conclusion depends on which FVS column is used:

| Comparison | CWH external | CWH PSP |
| --- | ---: | ---: |
| `MCuM` vs `VOL_MER` | **−18.7%** | −6.5% to −8.1% |
| `TCuM` vs `VOL_MER` | **−0.1%** | −0.4% to +0.4% |
| `MCuM` vs `VOL_NTWB` | −13.0% | n/a |
| `TCuM` vs `VOL_WSV` | −11.6% | −5.9% |

`TCuM` matching `VOL_MER` is not expected from the documented definitions. It may be a
volume-standard effect, a field-definition mismatch, or a BC variant convention. Until it is
resolved, the CWH external volume is **unresolved**, not failed and not passed.

ICHmw2 is robust to the choice:

- `MCuM` vs `VOL_MER`: **−7.5%**
- `TCuM` vs `VOL_MER`: **+9.9%**

Both are inside ±10%.

## Decision

- CWH 4 cm remains a pilot; external volume is not a validated claim.
- ICHmw2 volume can be reported with both columns; both pass.
- Do not change either bundle's parameters.
- Do not claim volume certification from `MCuM` alone.

## Cause

The BC variant's `CFVOL` uses `TOPD = 10 cm` and `DBHMIN = 17.5 cm` (12.5 cm for lodgepole pine).
`MCuM` only counts trees above that merchantability limit. The observed `VOL_MER` is built from the
4 cm tree list and includes trees below the FVS merchantability limit. `TCuM` includes total cubic
volume for those trees, which is why it tracks `VOL_MER` in the 4 cm data.

The −18.7% CWH external gap is partly a **merchantability-limit mismatch**, not a simple model
failure. D9.33 recomputed observed volume with the FVS `DBHMIN` (17.5 cm; 12.5 cm PL) and found:

- pooled `MCuM` vs matched observed: **−7.1%** (was −10.3%);
- non-PSP external: **−12.6%** (was −18.7%);
- PSP folds: **−1.7% to −5.9%**.

The merchantability limit explains about 3.1 percentage points. The external residual is still
outside ±10%, so the CWH 4 cm pilot remains a pilot and external volume is unresolved, not passed.
`TCuM` is not a substitute for a matched comparison because it includes trees below the FVS limit.

See `d9-cwh-volume-matched.md` and `d9-cwh-volume-matched-summary.csv`.
