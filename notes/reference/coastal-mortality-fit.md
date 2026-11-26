# A negative result: the tree-level survival fit does not replace the mortality table

Status: **explored, not shipped.**

## What was tried

`morts.f` carries a logistic survival model (`CON`, `INVDBH`, `DBH`, `DBHSQ`, `RDBH`, `BAL`,
`SQRTBA`, `SPH`) that is fitted per BEC and species group. CWH, MH, and CDF currently borrow the ICH
tabular mortality instead. The obvious move is to fit the logistic form on the coastal PSP pairs:
685,615 tree records, 95,969 deaths, `SURVIVED = (1 - RIP)^years` with `RIP = 1/(1+exp(-linear))`.

## What came out

| Species | n | deaths | Observed survival | Fitted survival | RMSE |
| --- | ---: | ---: | ---: | ---: | ---: |
| HW | 348,316 | 50,009 | 0.856 | 0.878 | 0.328 |
| SE | 44,962 | 6,720 | 0.851 | 0.866 | 0.304 |
| PL | 4,154 | 609 | 0.853 | 0.885 | 0.330 |
| PW | 1,062 | 353 | 0.668 | 0.699 | 0.463 |
| MV | 989 | 291 | 0.706 | 0.724 | 0.397 |

## Why it is not shipped

- **It over-predicts survival by 1–3 points** even after fitting, and the RMSE is 0.30–0.46 against a
  death rate of 0.14. Tree-level survival is noisy, but the form also lacks the variables that carry
  the signal here (crown ratio, damage, species mixture).
- **The engine's effective rate is not `RIP`.** `morts.f` blends `RIP` with a stand-level rate `RZ`
  through `BA/BAMAX` and takes the larger of the two. A fit to observed survival estimates a lower
  bound, so installing it would *lower* mortality relative to the blend the engine actually applies.
- **The tabular mortality it would replace is not obviously worse.** The coastal folds sit at
  −1.2 m²/ha (CWH) and −5.1 (CDF) after the tree-count fix; a worse fitting form would put that at
  risk.

## What would change the answer

- Fit the *effective* rate: simulate the blend, or fit `RIP` only on intervals far below `BAMAX`.
- Add crown ratio and damage, which the current `LMRT` form does not carry.
- Fit per subzone with an independent holdout rather than pooling a zone.

Until then the coastal zones keep the tabular mortality and the support matrix keeps saying so.
