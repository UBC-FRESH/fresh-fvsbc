# Quesnel high-QMD candidate review packet

Status: ready for independent review; **signed_off is false**
Date: 2026-11-03
Candidate: `d7-quesnel-highqmd-bundle.json`
Issues: #378, #380, #383

This packet is for the reviewer. The agent cannot sign a calibration; review and sign-off are human
responsibilities.

## 1. What is being reviewed

A candidate bundle for **Quesnel SBPSdc**, initial `QMD >= 13`, untreated:

- `BAMAX 75`, bounds 25–89 m2/ha;
- no `BAIMULT`, `MORTMULT`, or `HTGMULT`;
- pins: PyFVS `e95172b`, FVS `ef5fa847`, variant `bc`;
- domain field `qmd_min: 13.0`.

## 2. Evidence

| Check | Result | Source |
| --- | --- | --- |
| Site-grouped BA | -2.1% | D7.13, `d7-quesnel-highqmd.md` |
| Site-grouped TPH | -6.3% | D7.13 |
| Worst site BA | 8.7% | D7.13 |
| Worst site TPH | 10.1% | D7.13 |
| Temporal test BA | +5.38% | D7.14, `d7-quesnel-bundle.md` |
| Temporal test TPH | +3.80% | D7.14 |
| Temporal test sample | 6 intervals / 6 sites | D7.14 |
| QMD boundary enforced | below 13 refused, 13 accepted | D7.15, `test_domain_enforces_qmd_min` |
| Provenance | records run QMD and bundle qmd_min | D7.16 |

The site-grouped and temporal thresholds are BA within ±10% and TPH within ±15%.

## 3. Review checklist

- [ ] The domain is exactly Quesnel SBPSdc, not a pooled SBPS claim.
- [ ] The `QMD >= 13` boundary is enforced by the loader and provenance.
- [ ] `BAMAX 75` is inside the declared bounds and not selected at a bound.
- [ ] No BA/mortality/height multiplier is hidden in the bundle.
- [ ] The temporal split is time-based, not another site split.
- [ ] The test sites were not used to select `BAMAX 75`.
- [ ] The 13 site-grouped folds and 6 temporal test intervals are enough for the claim.
- [ ] The `QMD < 13` sites remain validation-only.
- [ ] The claim says candidate, not certificate.
- [ ] The bundle can be re-run from its pins, checksum, and keyword set.

## 4. Known limits

- Six sites / 20 intervals at `QMD >= 13`; the temporal test has six intervals.
- The mid/dense Quesnel sites are excluded.
- The bundle is a one-period calibration; multi-cycle establishment is D8.
- The bundle has no independent third TSA.
- `signed_off` stays false until a reviewer signs.

## 5. Sign-off

| Field | Value |
| --- | --- |
| Reviewer | _pending_ |
| Date | _pending_ |
| Decision | _pending_ |
| Claim changes required | _pending_ |

Do not set `signed_off: true` without this table filled and the bundle regenerated with the reviewer
and date.
