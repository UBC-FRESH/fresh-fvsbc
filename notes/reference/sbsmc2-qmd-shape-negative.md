# SBSmc2 QMD-based growth shape: tested, not shipped

Status: **negative result / data block.** The 0.41.7 bundle and engine 0.4.15 stay.

## 1. Why QMD

The BA-bin residual diverges at BA 40-65 (held-out over, train under). Stand QMD separates the
error better: the QMD 0-10 bin is aligned in both folds - BA over by ~21-22 m²/ha and TPH under by
566 (train) / 2,069 (test). A growth reduction there should lower BA and raise TPH together.

## 2. What was tried

A stand-level `dgf.f` term computing QMD from stand BA and trees per acre, scaling SBSmc2
diameter growth when QMD is below a threshold:

| Shape | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| shipped 0.41.7 | **7.84** | **794** | **8.10** | **609** |
| QMD < 15, ×0.7 | 8.03 | 780 | 8.02 | 611 |
| QMD < 10, ×0.5 | 7.91 | 804 | 8.16 | 601 |

No shape improves both folds. The QMD < 15 case improves held-out TPH but worsens held-out BA;
the narrower QMD < 10 case worsens both held-out measures and only improves train TPH. The engine
QMD computed from the tree list also bins stands differently from the observed-QMD column, which
makes a threshold comparison imprecise.

## 3. Data block

The remaining SBSmc2 residual (+2.2 / -323) is a fold-distribution problem, not a shape problem:

- BA 40-65 has opposite signs between folds.
- QMD 0-10 is aligned but a growth reduction there does not survive the aggregate.
- Both BA-bin and QMD-based ingress/mortality shapes have now been tested.

Further progress needs **independent held-out SBSmc2 sites** (not a re-split of the same 126) or the
measurement history that explains the dense-site discontinuities. Neither is available locally.

## Reproduce

- QMD bins: `~/workspace/bwbs-work/probe_sbsmc2_v2final/`.
- QMD shapes: `probe_sbsmc2_w32/` (QMD<15) and `probe_sbsmc2_w32b/` (QMD<10).
