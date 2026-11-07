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
