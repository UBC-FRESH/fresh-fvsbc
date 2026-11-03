# D7.12 Quesnel site-index covariate

Status: **site index is informative but not sufficient**; no site-index rule. D7.13 finds a QMD >= 13 domain candidate.
Date: 2026-11-03
Issue: #373
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Data: 13 eligible Quesnel SBPSdc sites; public FAIB `faib_compiled_spcsmries_siteage.csv`

D7.11 left one established site at BA +35% and another at TPH -44% under a single `BAMAX`. This
tests whether measured site index explains that spread.

## 1. What was compared

For each of the 13 eligible sites:

- measured SI, median across species at the first visit;
- initial QMD and BA;
- the best `BAMAX` from the 20–80 grid by the smaller of the absolute BA/TPH percentage;
- the resulting BA and TPH residuals.

The full site table is kept in runtime because it carries site identifiers.

## 2. Result

- SI ranges from **14.2 to 21.4**; the best `BAMAX` ranges from **25 to 80**.
- SI and the best-site residual score have a rank correlation of about **-0.49**: higher SI tends to
  have smaller error.
- The relationship is not a separator:
  - one high-SI site (about 18.3) still fails BA/TPH;
  - one low-SI site (about 14.2) passes its best candidate;
  - several mid-SI sites fail in opposite directions.
- A site-index-only rule would misclassify both the high-SI failure and the low-SI pass.

## 3. Decision

**No site-index-only Quesnel rule.** SI is not a substitute for a site-level effect; it is one
covariate among QMD, BA, and unmeasured disturbance/ingrowth. D7.13 narrows the domain instead and
finds a candidate for `QMD >= 13`.

The site-to-site variation remains the block. The next model is **site-level/hierarchical capacity**:

- a site random effect or a small set of site classes;
- SI, initial QMD, and BA as covariates;
- leave-one-site-out validation;
- keep the dense `QMD < 9` site validation-only.

## 4. Claim boundary

This is a covariate screen. It does not calibrate Quesnel, change a default, or support a yield, AAC,
legal, or whole-block claim. Site index is public and usable as a covariate; FVS-BC itself still
ignores `SITECODE`, so this is a calibration-layer variable, not a variant change.
