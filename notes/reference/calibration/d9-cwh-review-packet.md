# D9.56 CWH 4 cm review packet

Status: **unsigned; ready for an independent reviewer. No human signature is fabricated.**
Date: 2026-11-08
Bundle: `d7-cwh-4cm-bundle.json`
Tier: `A-pilot-external` in `d9-tiered-domain-status.csv`
Manifest: `d9-cwh-review-manifest.json`

This packet covers **only** the CWH 4 cm pilot. It does not re-open the stale IDFdk or SBS bundles,
and it does not promote the CWH 2 cm bundle. D9.55 found that the CWH 4 cm pilot is the only bundle
that moves a failing non-PSP default into the BA/TPH bands on the same sample.

## 1. Bundle under review

| Field | Value |
| --- | --- |
| Bundle id | `cwh-growth-4cm-pilot-2026-11-04` |
| Version | `0.1.3` |
| Pins | `pyfvs_commit=e95172b`, `fvs_source_commit=ef5fa847`, `variant=bc`, `wrapper_version=0.21.4` |
| Domain | CWH; CAR/KAM/NEL; DBH at least 4 cm; untreated |
| Parameters | 21: BAIMULT, MORTMULT, REGDMULT |
| Ingrowth | none |
| Review | `signed_off: false`; `reviewer: "D9 CWH 4cm pilot, not signed off"` |
| SHA-256 | `sha256:4c3a068dd3c50445cfa43a541b4a7a3b1903d4f3b05f44ab731d84c6d90bfce5` |
| Bytes | 6451 |

The bundle enforces its 4 cm DBH domain. The caller still has to supply a tree list at the same
target; the bundle cannot widen or narrow a population that is already above the cutoff.

## 2. Evidence

### PSP holdouts, 4 cm

| Holdout | n | BA % | TPH % | QMD % | Matched top height % | PSP matched volume % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Arrowsmith | 38 | −2.9 | −1.3 | −1.1 | −5.3 | −4.4 |
| Fraser | 11 | −3.3 | −5.9 | +0.8 | −8.0 | −4.4 |
| Haida Gwaii | 15 | +0.6 | +7.9 | −0.5 | −3.7 | −1.7 |
| temporal ≥2000 | 252 | +3.4 | +12.1 | −5.5 | −9.0 | −5.9 |

Every PSP fold is inside the BA ±3 m2/ha or ±10 percent band, the TPH ±15 percent band, the QMD
±10 percent band, and the height ±10 percent band. PSP matched volume is inside ±10 percent. The
temporal TPH margin is the tightest at +12.1 percent.

### Independent non-PSP cohort, D9.55 same sample

| Model | n | BA % (95% CI) | TPH % (95% CI) | Site pass BA / TPH |
| --- | ---: | ---: | ---: | ---: |
| identity default | 67 | −17.8 (−21.9 to −13.4) | −9.5 (−13.8 to −4.5) | 10/61 / 37/61 |
| CWH 4 cm pilot | 67 | **+1.2 (−4.8 to +8.5)** | **+0.5 (−4.2 to +6.3)** | **30/61 / 35/61** |

The pilot is the only candidate in D9.55 whose BA and TPH bootstrap intervals both sit inside the
pre-registered bands while improving a failing default.

### Volume

The merchantability-matched comparison is the correct one:

| Cohort | `MCuM` vs matched observed |
| --- | ---: |
| Arrowsmith | −4.4% |
| Fraser | −4.4% |
| Haida Gwaii | −1.7% |
| temporal ≥2000 | −5.9% |
| non-PSP external | **−12.6%** |
| all | −7.1% |

**The external volume gap is the blocking evidence item.** It is outside the ±10 percent band and
is not explained by the merchantability cutoff; D9.33 recovered about 3.1 percentage points of the
old −18.7 percent gap, not the residual.

## 3. What a reviewer must check

1. Recompute the bundle SHA-256 and byte count against the manifest.
2. Confirm the domain: CWH only, CAR/KAM/NEL, DBH at least 4 cm, untreated. A run outside it must be
   refused, not silently calibrated.
3. Recompute or inspect the PSP table behind each row; confirm the temporal ≥2000 row is fixed
   parameter and not a refit.
4. Confirm the non-PSP table is the same sample as D9.55 (five intervals per BEC, 4 cm, corrected
   DBH denominator) and not the older 2 cm comparison.
5. Confirm the external volume row is stated as **unresolved** and is not omitted from the claim.
6. Accept, narrow, or reject the pilot. Signing would require a named reviewer and a `review` edit
   in the bundle; this packet does not do that.

## 4. Risks a sign-off would accept

- `BAIMULT 7.0` is a large structural correction, not a small growth adjustment.
- `REGDMULT 2.0` is also structural and is what fixes Fraser; it is not independently identified
  from the PSP folds.
- The candidate was selected after a 4 cm grid. The non-PSP cohort is independent, but the selection
  was not pre-registered.
- The temporal TPH margin is +12.1 percent, close to the ±15 percent limit.
- Site pass is 30/61 BA and 35/61 TPH on the external cohort; a domain mean is not a stand-level
  guarantee.
- External matched volume is −12.6 percent and unresolved.
- At least one independent reviewer and a sign-off record are still missing.

## 5. Current decision

`decision: pending`; `signed_off: false`; `reviewer: null`.

The pilot is **not** promoted to a certificate. If a reviewer accepts the BA/TPH evidence and the
volume qualification, the next action is a signed manifest and a bundle `review` update. If the
volume gap is treated as blocking, the correct decision is to narrow the claim to BA/TPH/QMD/height
and keep volume unresolved, or reject promotion until a volume-standard comparison resolves it.

## 6. Claim boundary

This is a review packet for an unsigned pilot. It does not support a yield, AAC, legal, or
whole-block claim, and it is not a certificate.
