# D9.49 MPB on high-mortality PL stands

Status: **the real MPB extension produces substantial PL kill on high-PL stands**
Date: 2026-11-08
Build: D9.46 BC MPB extension
Cases: reconstructed from `psp4-growth/intervals.csv` and raw FAIA tree detail

## 1. Cases

The D9.48 low-PL case (`4033913`, 9% PL) was a negative control and killed only 0.3% of PL.
These three intervals are post-2000 high-PL stands:

| Interval | BEC | TSA | PL trees | PL dead | Observed PL mortality |
| --- | --- | --- | ---: | ---: | ---: |
| `4025471\|1\|2001\|2014` | SBPSmk | 100 Mile | 71 | 68 | 95.8% |
| `4031394\|1\|2001\|2014` | SBSmw | Quesnel | 27 | 27 | 100% |
| `4031355\|1\|2000\|2013` | SBSmw | Quesnel | 34 | 34 | 100% |

Each was rebuilt from the start tree list and run with:

```
MPB
MPBSTART         1
BEETLES        1000
STNDSIZE        100
HABSUIT         1.0
MAXYEARS        15
END
```

## 2. Result

| Interval | MPB final live PL/ac | MPB final dead PL/ac | Dead fraction |
| --- | ---: | ---: | ---: |
| `4025471` | 355.05 | 363.29 | 50.6% |
| `4031394` | 21.37 | 164.38 | 88.5% |
| `4031355` | 35.30 | 129.81 | 78.6% |

The MPB extension now produces large PL mortality on the high-PL stands. The low-PL negative
control remains near zero. This is the first evidence that the linked extension can reach the
observed post-2000 PL range.

The MPB table in the current output ends in 2011 for these cases; the final-year fraction and
outbreak timing still need to be reconciled with the interval end year.

## 3. Interpretation

- The failure is not the MPB build or host mapping; high-PL stands respond strongly.
- The low-PL stand was the wrong calibration target.
- The remaining question is outbreak severity/timing, not whether the module can kill PL.
- The response is nonlinear; `BEETLES` alone did not move the low-PL case, but high-PL stands show
  large kill under the same module.
- Non-PL BA/TPH still need to be checked for collateral change.

## 4. Decision

- Use high-PL stands for MPB calibration; keep `4033913` as a negative control.
- Reconcile the MPB table end year with the interval end year before fitting severity.
- Calibrate one outbreak configuration on training PL stands and hold out others.
- Check non-PL BA/TPH on every run.
- Do not integrate or issue a bundle until the high-PL holdout passes.

## 5. Limits

- Three high-PL cases, all in SBPS/SBS; no IDF or BWBS holdout yet.
- The MPB output table ends at 2011; final-year mortality is unresolved.
- The BC species mapping is a first implementation.
- No damage-code data in these tree lists.
- No holdout calibration yet.

## 6. Claim boundary

This is a diagnostic MPB calibration test. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
