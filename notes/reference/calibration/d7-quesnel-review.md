# Quesnel high-QMD candidate review packet

Status: post-hoc candidate; ready for review of the claim, **signed_off is false**
Date: 2026-11-03
Candidate: `d7-quesnel-highqmd-bundle.json`
Issues: #378, #380, #383

This packet is for the reviewer. The agent cannot sign a calibration; review and sign-off are human
responsibilities.

## 1. What is being reviewed

A candidate bundle for **Quesnel SBPSdc**, initial `QMD >= 13`, untreated:

- `BAMAX 75`, bounds 25–89 m2/ha;
- no `BAIMULT`, `MORTMULT`, or `HTGMULT`;
- pins: PyFVS `e95172b`, FVS `ef5fa847`, variant `bc`, wrapper `0.21.4`;
- domain fields `tsas: ["Quesnel TSA"]` and `qmd_min: 13.0`.

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
| TSA boundary enforced | Quesnel accepted, other TSAs refused | D7.20b |
| Provenance | records run QMD, BA, and TSA | D7.16, D7.20b |

The site-grouped and temporal thresholds are BA within ±10% and TPH within ±15%.

## 3. Review checklist

- [ ] The domain is exactly Quesnel SBPSdc, not a pooled SBPS claim.
- [ ] The TSA boundary is enforced, not just written in the note.
- [ ] The `QMD >= 13` boundary is enforced by the loader and provenance.
- [ ] `BAMAX 75` is inside the declared bounds and not selected at a bound.
- [ ] No BA/mortality/height multiplier is hidden in the bundle.
- [ ] The temporal split is time-based, not another site split.
- [ ] The test sites were not used to select `BAMAX 75`. **Currently not satisfied;** this is a post-hoc candidate.
- [ ] The 6 site-grouped folds and 6 temporal test intervals are enough for the claim.
- [ ] The `QMD < 13` sites remain validation-only.
- [ ] The claim says candidate, not certificate.
- [ ] The bundle can be re-run from its pins, checksum, and keyword set.

## 4. Known limits

- Six sites / 20 intervals at `QMD >= 13`; the temporal test has six intervals.
- The mid/dense Quesnel sites are excluded.
- The bundle is a one-period calibration; multi-cycle establishment is D8.
- The evidence excludes intervals with `dead_ba / ba0 > 0.4`; the bundle cannot enforce that filter.
- `BAMAX 75` and the QMD domain were selected on the same six sites.
- The temporal test reuses the same sites; it is not site-independent.
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
