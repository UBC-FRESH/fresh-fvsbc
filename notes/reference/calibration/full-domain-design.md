# Full-domain calibration design

Status: design for W2–W6; not a calibration
Date: 2026-11-02
Domain table: `domain-plan.csv`
Upstream package: `w2-upstream-package.md`
Baseline: `baseline_report.md`
Protocol: `kc-protocol.md`

This note fixes the domain grouping, the pre-registered validation design, and
the phase sequence. It is the plan W1.6 hands to W2.

## 1. The domain problem

The BC variant resolves seven BEC zones, but it does not resolve every subzone in
those zones. The W1.4 baseline found **19 supported-zone variants** whose subzone
is not in `HABTYP`; they hold **220 sites and 300 intervals**. They are not a data
problem: `ESSFdh1`, `ESSFmv1`, `IDFdh`, `SBSdh1`, and `MSxv` are valid BC BECs
that the variant cannot parse. They need the W2 extension.

The **32 unsupported-zone variants** hold **2,911 sites and 10,765 visits** in
`CWH`, `CDF`, `BWBS`, `CMA`, and `MH`. They are counted in the coverage table and
excluded from the calibration tables.

The **47 data-rich supported variants** (at least 15 sites with repeat
measurements) group into **12 calibration domains**. Ten have enough data for
capacity, mortality, and growth; two are validation-only.

## 2. The domains

| Domain | Variants | Data-rich | Sites | Intervals | Power |
| --- | ---: | ---: | ---: | ---: | --- |
| `ICHwet` | 18 | 8 | 982 | 2,414 | calibration |
| `ICHdry` | 11 | 4 | 275 | 712 | calibration |
| `IDFdk` | 6 | 4 | 490 | 915 | calibration |
| `IDFdry` | 8 | 6 | 391 | 1,094 | calibration |
| `IDFxm` | 1 | 1 | 54 | 30 | validation-only |
| `SBSwet` | 7 | 5 | 629 | 1,150 | calibration |
| `SBSdry` | 10 | 5 | 560 | 768 | calibration |
| `SBPS` | 4 | 2 | 170 | 296 | calibration |
| `ESSFwet` | 13 | 2 | 194 | 253 | calibration |
| `ESSFdry` | 12 | 3 | 119 | 240 | calibration |
| `MS` | 10 | 4 | 330 | 987 | calibration |
| `PP` | 2 | 0 | 16 | 27 | validation-only |
| `W2-subzone` | 19 | 3 | 220 | 300 | W2 extension |
| `W2-zone` | 32 | 22 | 2,911 | 0 | W2 extension |

The grouping rule is BEC zone plus subzone family, not a separate model per
variant:

- `IDFdk` is `IDFdk1`–`IDFdk5`; `IDFxm` stands alone because its capacity and
  species mix differ; `IDFdry` collects `IDFxh`, `IDFdm`, `IDFmw`, `IDFww`, and
  the `IDFxx` variants.
- `ICHwet` is `ICHmw`, `ICHmk`, `ICHmc`, and `ICHwk`; `ICHdry` is the remaining
  ICH subzones.
- `SBSwet` is `SBSmc`, `SBSmk`, `SBSmw`, and `SBSmm`; `SBSdry` is the remaining
  SBS subzones.
- `ESSFwet` is the wet `ESSF` subzones; `ESSFdry` is the rest.
- `MS` and `PP` are their own domains; `SBPS` is one domain.

The full assignment is in `domain-plan.csv`.

### Power thresholds, fixed before fitting

- **Capacity** needs at least 30 intervals and 15 repeat sites.
- **Mortality** needs at least 15 intervals and 500 dead tree records.
- **Growth** needs at least 30 intervals.
- **Validation-only** has at least 5 intervals but does not meet all three.
- **Out** has fewer than 5 intervals, or is a W2 domain.

`IDFxm` meets capacity and growth but not the mortality threshold; it is a
validation domain for mortality and a fit domain for capacity. `PP` is
validation-only at best.

## 3. Pre-registered validation

### Primary metrics

- Annual net BA and TPH change bias by species group and DBH class.
- Next-measurement BA and TPH bias and RMSE.
- QMD, top height, and volume bias and RMSE.
- Calibration slope and intercept for observed versus predicted change.
- Envelope exceedance: above p99 and above the observed maximum.
- Parameter-at-bound indicator.

Gross mortality is not available from a no-cut, no-fire summary. W4 may add the
mortality table with a controlled fire only if the fire is held constant across
the comparison; otherwise the target is net change, stated as such.

### Holdouts

- **Spatial:** leave one TSA out, for TSAs with enough intervals.
- **Subzone:** fit `IDFdk` and test `IDFxm`, and vice versa where the sample
  allows.
- **Temporal:** fit on intervals ending before a fixed year, test after it.
- **Site-grouped:** five folds, no site in both train and test.
- **Species:** hold out a minor species group where the sample supports it.

The split is frozen before fitting. A result on the training data is a tuning
result, not a validation result.

### Acceptance thresholds

| Metric | Target |
| --- | --- |
| BA bias, independent sites | within ±3 m2/ha or 10 percent |
| TPH bias, independent sites | within 15 percent |
| Calibration slope | 0.8 to 1.2 |
| Calibration intercept | not significantly different from zero |
| Parameters at a bound | none |
| Envelope exceedance, 200-year no-cut | zero above the observed maximum; report p99 exceedance |
| Reproducibility | exact rerun from checksummed data and the recorded FVS commit |

A domain that cannot meet the thresholds narrows its claim; it does not relax the
threshold silently.

## 4. The phase sequence

| Phase | Name | Exit evidence |
| --- | --- | --- |
| W2 | Upstream coverage | A pinned PyFVS/FVS extension that resolves the five zones and the 19 subzones, or a documented go/no-go with cost and evidence |
| W3 | Full-domain baseline | The W1.4 baseline extended to every W2-resolved domain, with residual atlas and envelope flags |
| W4 | Domain calibration | Versioned bundles per domain, cross-validated, no parameter at a bound |
| W5 | Independent validation | Certificates with spatial, subzone, temporal, and site-grouped holdouts |
| W6 | Calibration release | Release, docs, CLI/API, provenance, envelope validator |

W2 is a go/no-go, not a promise. If the upstream source cannot carry a zone's
species and parameters, the programme narrows to the supported domain and says
so. See `w2-upstream-package.md`.

## 5. Effort

The KC pilot is one domain: roughly one compute day and two to three reviewer
days. The 12 calibration domains share the harness and the tables, but each needs
its own fit, holdout, and review. A realistic first pass is six to ten weeks of
compute and review for the ten calibration domains, plus the W2 upstream work,
which is a separate source-development effort. This is an estimate, not a
commitment; W2's go/no-go sets the real cost.

## 6. Risks

| Risk | Why it matters | What reduces it |
| --- | --- | --- |
| W2 is not feasible as scoped | Five zones need species and parameters the variant lacks | W2 is a bounded spike with a go/no-go and a cost |
| Domains are too coarse | A pooled fit can hide a variant that fails | Hold out variants within a domain; report per-variant residuals |
| Domains are too fine | A separate fit per variant overfits 30 intervals | Group by subzone family; use hierarchical or pooled fits |
| Gross mortality is unavailable | The no-cut summary cannot show it | Report net change; add a controlled fire only if it is held constant |
| The envelope is circular | An envelope from the training plots is not independent | Hold out sites before fitting; report the envelope's uncertainty |
| Site series is missing | The capacity default depends on it | Use a documented default and flag it; do not invent a series |
| Uneven-aged plots | FVS-BC is even-aged | Stratify by regime; do not claim a selection model |
| Reviewer time | A calibration without review is not a certificate | W5 names reviewers and records sign-off |

## 7. Claim boundary

This note does not calibrate anything. It defines the domains, the thresholds,
the holdouts, and the phase sequence. A domain certificate exists only after W5,
and only for the domain and data it names.
