# Replacing FVS-BC's weak mortality and ingress submodels

**A model comparison and core-function design for PSP-calibrated projection across BC BEC zones**

Status: design report / literature deep dive. Tracked reference note.
Date: 2026-11-07.
Audience: FVS-BC calibration programme (W2/W4/W5), biometric reviewer, variant engineer.

---

## 0. Bottom line

1. **FVS-BC's mortality is not a model of mortality; it is a small lookup table plus a density cap.** The BC variant uses a 5 basal-area-class × 4 DBH-class table for nine species groups, with only two BEC classes (ICH and IDF; SBPS mapped to IDF, SBS to ICH except `SBSdw2`), a four-entry site-series logistic for four minor species, and a maximum-basal-area adjustment that dominates near capacity. The tabular and site-series paths have **no site index, no climate, no crown-ratio term, no growth term, no species-specific competition, and no stochasticity**; the legacy `LV2ATV` path has a site-potential multiplier and a growth term, but it is not the main BC path (code audit: `canada/bc/morts.f`, `BCPLOT.F77`). The model is deterministic: `WKI = P·(1−(1−RIPP)^FINT)`.
2. **FVS-BC has no automatic ingress.** `ESTAB` only adds trees when a `PLANT` or `NATURAL` keyword is present (`MODE=1`); the "best tree" code is disabled. The current wrapper injects natural regeneration as a **BEC × species annual rate table** (optionally with initial-BA and QMD ranges; `fresh_fvsbc/ingrowth.py`, `d7-all-recruitment.csv`). This is exactly the hand-tuned-domain approach the programme is trying to escape.
3. **Missing ingress and wrong mortality are confounded.** If recruitment is absent, a calibration that matches basal area must lower mortality (or raise growth) to compensate. A multiplier fit cannot identify which submodel is wrong. The fix must be structural: fit mortality on tree-level survival, fit ingress on recruitment counts, then check the joint stand trajectory.
4. **The literature is unusually clear on the model forms.** Mortality: a discrete-time survival model with individual growth and competition covariates, regional/site effects, and (where data allow) climate (Hülsmann et al. 2017; Monserud & Sterba 1999; SILVA, MOSES, SORTIE). Ingress: a two-part/hurdle or zero-inflated negative-binomial count model with an explicit seed-source/parent-tree term, overdispersion, and a real probability of zero (Lappi & Pukkala 2020; Li et al. 2011; Zhang et al. 2012; BWINPro; SORTIE/BC).
5. **The project's own pilot already shows the direction.** A continuous-covariate, species-interaction survival model (14 parameters) beat a 23-parameter species × BA-class model on AIC by 196 points and on cross-validated log loss (0.4854 vs 0.4878). But a TSA holdout exposed regional over-prediction (100 Mile House: predicted 0.0201 vs observed 0.0148 per year), which is a direct argument for hierarchical site/region effects. A naive year term failed the temporal holdout badly (over-prediction 1.6–5×). Project evidence: `mort-calib/validation/model_comparison.csv`, `validation.json`, `temporal/temporal_validation.json`.
6. **Recommended core functions, not multipliers:**
   - `BCMORT`: hierarchical discrete-time survival (complementary log-log), with DBH, BAL, BA, relative DBH, recent growth, crown ratio, site index, climate moisture, species effects, and BEC/site random intercepts. Optional two-component background + stress hazard. Optional stochastic thinning that preserves the expectation.
   - `BCINGR`: hurdle/ZINB recruitment with a stand-level seed-rain index computed from the tree list (fecundity × crown area, with a dispersal/viability weight and an external seed-rain term), presence and count equations, species composition drawn from expected recruitment, and establishment at a defined size threshold.
   - **Architecture:** keep the `MORTS`/`ESTAB` entry points and all existing keywords; load coefficients from a versioned external bundle; expose diagnostics tables; add a domain/envelope guard; prototype the ingress model through the FVS ES1/ES2 external-model interface before porting to Fortran.
7. **Do not calibrate separate models per BEC variant.** Use partial pooling across BEC zones/site series and species. This is how the five data-poor zones (CWH, CDF, BWBS, MH, CMA) can be represented with honest uncertainty instead of either a wrong ICH/IDF table or a blanket "no-go".
8. **Phasing:** mortality v1 (empirical, no climate) → mortality v2 (growth/CR/SI/climate, stochastic) → ingress v1 (seed source, no climate) → ingress v2 (climate, disturbance, advance regeneration) → joint calibration and independent validation → release.
9. **The strongest single pieces of evidence** are: Hülsmann et al. (2017) for growth/competition covariates and regional calibration; Lappi & Pukkala (2020) for ZINB ingress and its overdispersion/zero structure; Díaz-Yáñez et al. (2024) for the fact that most models over-estimate recruitment and produce too few zeros, and that complexity does not buy accuracy; Bugmann et al. (2019) for the size of mortality-submodel uncertainty; and the project's own AIC/holdout results.
10. **Unverified claims are marked `[UNVERIFIED]`** throughout, especially exact equations in proprietary or thinly documented models (TASS, MGM, parts of SILVA/BWINPro/MOSES/PICUS regeneration).

---

## 1. Scope, method, evidence standard

### 1.1 What was reviewed

Twelve independent-tree or individual-based systems, chosen to span the design space:

| Class | Systems |
| --- | --- |
| Distance-dependent empirical / hybrid (Europe) | SILVA, BWINPro/TreeGrOSS, MOSES, PICUS |
| Spatially explicit individual-based (North America / process) | SORTIE-ND / SORTIE/BC, iLand |
| Individual-based gap / tropical | FORMIND |
| BC operational / provenance | TASS/TIPSY, PrognosisBC / FVS-BC |
| Distance-independent boreal mixedwood | MGM |
| Distance-independent PNW empirical benchmark | Organon |
| FVS's only full establishment model (benchmark) | Prognosis / FVS establishment model (Ferguson–Carlson) |

### 1.2 Evidence standard

- **Primary**: peer-reviewed paper or model documentation read directly (PDF or publisher page).
- **Secondary**: a review or a citing paper that describes the model, where the primary was inaccessible.
- **Code audit**: the actual FVS-BC source in `.opencode/tmp/opencode/fvs-src/canada/bc/`.
- **Project evidence**: the calibration artifacts under `.opencode/tmp/opencode/mort-calib/` and `d7-*`.
- **`[UNVERIFIED]`**: I could not confirm the exact equation or parameterization from a primary source. These are design risks, not claims.

### 1.3 What this report does not do

- It does not fit a new model. It specifies the model forms, covariates, calibration design, and acceptance gates.
- It does not claim that any single published model is "correct" for BC. The BC 2021 review is explicit that **none of TASS, TIPSY, VDYP, PrognosisBC, MGM or SORTIE had recent (last 10 years) validation in BC** and that documentation of calibration data is thin (Forest Analysis Ltd. 2021). The design therefore treats published models as **structure donors**, not as parameter sources.
- It does not propose a new keyword multiplier. Existing multipliers remain as overrides, but they are not the calibration mechanism.

---

## 2. What FVS-BC actually does: a code-level audit

This section is important because the design must replace real code, not a stylized description.

### 2.1 Mortality (`canada/bc/morts.f`)

`MORTS` is called from `GRINCR` after growth. It has three mortality paths:

**(a) Legacy `LV2ATV` path (old PrognosisBC / Hamilton form).**

```
RIP = 2.76253 + 0.222310*SQRT(D) - 0.0460508*SQRT(BA)
    + 11.2007*G - 0.554421/D + B5
    + 0.246301*RELDBH + 6.07129*G/D
RIP = 1/(1+EXP(RIP))          ! survival
RIP = RIP * POTENT            ! site potential multiplier
```

where `G` is periodic basal-area increment, `RELDBH = D/AVED`, and `B5` is a species constant. This path has growth and relative size but is a legacy calibration and is not the main BC path.

**(b) Tabular `FMRT` path** for species groups PW, LW, FD, BG, HW, CW, PL, SE, PY (and OC mapped to FD). The table is 5 BA classes (`<20, 20–30, 30–40, 40–50, 50+ m²/ha`) × 4 DBH classes (`<10, 10–25, 25–40, 40+ cm`) of **annual percent mortality**, separately for ICH and IDF only. Several species simply copy the ICH table into IDF (PW, LW, BG, HW, CW, SE, PY). `SBPS` is mapped to IDF; `SBS` to ICH except `SBSdw2`; `ESSF`/`MS` use the V2/ICH default. This is the "hand-tuned domain" in its purest form.

**(c) Site-series logistic `LMRT` path** for species 11, 12, 13, 15 (EP, AT, AC, OH), with only four entries: `ICH/all`, `IDF/all`, `SBPS/all`, `SBS/all`. The linear predictor is

```
RIP = CON + INVDBH/D + DBH*D + DBHSQ*D^2 + RDBH*RELDBH
    + BAL*BAL + SQRTBA*SQRT(BA) + SPH*SPH
RIP = 1 - 1/(1+EXP(RIP))      ! mortality
```

If no BEC string matches, `MORT%FIT(ISPC)=.FALSE.` and the code sets `RIP=99`, which after the inverse-logit is essentially **certain mortality**. The `BCPLOT` structure confirms the covariate set: `CON, INVDBH, DBH, DBHSQ, RDBH, BAL, SQRTBA, SPH`. There is **no SI, no climate, no crown ratio, and no growth term** in the tabular/LMRT paths; the legacy `LV2ATV` path has `G` and a `POTENT` site multiplier, but it is the old PrognosisBC calibration.

**(d) Maximum-basal-area adjustment.**

```
RZ  = 1 - (1 - (T - TB)/T)^0.1          ! 10-yr BA projection
RIPP = (BA*RZ + (BAMAX - BA)*RIP)/BAMAX
RIPP = MAX(RIPP, RIP)
```

Near `BAMAX`, the density cap dominates and the underlying hazard matters less. This can hide a wrong hazard and makes the model behave like a self-thinning boundary rather than a mortality process.

**(e) Application.** Deterministic:

```
WKI = P * (1 - (1 - RIPP)^FINT) * X
```

`X` includes `XMORT` multipliers, `FIXMORT`, `SIZCAP`, and a 20-year post-disturbance establishment exemption. There is **no random draw** and therefore no variance, no natural variability, and no way to represent a stochastic survival process.

**(f) Climate.** `MORTS` calls `CLMORTS` after the tree loop, but in the BC variant this is the no-op stub in `base/exclim.f` (`ENTRY CLMORTS; RETURN`) unless the climate extension is linked. The core BC mortality has no climate response.

**Consequences for PSP tracking:**

- The BEC domain is encoded in the coefficient table, not in a response function. Adding a zone means adding a table; a wrong table is worse than no table.
- The BA/DBH class boundaries produce discontinuities; a tree crossing 25 cm or a stand crossing 30 m²/ha changes hazard discontinuously.
- Site quality is absent. Two stands with the same BA/DBH but SI 15 vs 25 get the same hazard.
- Competition is only total BA/BAL/SPH; there is no species-specific competition and no crown ratio.
- The density cap can compensate for a biased hazard, so a calibration that matches BA does not prove the mortality model is right.
- Deterministic application cannot represent the binomial nature of death, and it cannot produce uncertainty bands for PSP intervals.

### 2.2 Ingress (`canada/bc/estab.f`)

`ESTAB` is the PROGNOSIS regeneration-establishment model, but in the BC variant it is essentially **keyword-driven**:

- `MODE=1` only when a `PLANT` or `NATURAL` keyword is found (`OPFIND` on activities 430/431/491/493/492).
- If no keyword, the code branches to `227` and adds no trees.
- The "best tree" logic is explicitly disabled: *"PICKING BEST TREES USED TO BE DONE HERE."*
- `NATURAL` requires the user to supply species, trees/acre, height, age, shade code; the model does not derive recruitment from the stand.
- The wrapper's `fresh_fvsbc/ingrowth.py` generates `NATURAL` lines from a table of **annual recruitment rates by BEC and species group**, optionally with initial-BA and QMD ranges. The rates are data, not a model. The `d7-all-recruitment.csv` shows the observed `new_total` and species breakdown used to build that table.

**Consequences:**

- There is no seed source, no parent-tree effect, no dispersal, no seedbed, no light response, no zero-inflation, no overdispersion, and no climate effect.
- Recruitment is a constant rate within a BEC × species cell; it cannot respond to a partial cut, a mortality event, a change in composition, or a drought.
- The flat rate is inserted as a `NATURAL` pulse, so establishment timing is an artifact of the cycle length.
- Because ingress is absent unless the user asks for it, any PSP calibration that ignores ingress will attribute the missing stems to survival, biasing mortality downward.

### 2.3 Architecture

- `MORTS`/`MORCON` are the mortality entry points; `ESTAB`/`ESINIT` are the establishment entry points.
- Parameters are compiled Fortran `DATA` statements and a `MORT%` structure keyed by a 15-character BEC `PrettyName`.
- The FVS base has an **external regeneration model interface** (`AddTrees`, ES1/ES2 files; Robinson 2008) that lets a stand-state file be passed to an external executable and a recruitment file read back. The BC variant does not currently use it, but it is the cleanest prototype path.
- There is no per-tree mortality or per-species recruitment diagnostic output; calibration must infer from aggregate BA/TPH.

**This is the architectural problem:** the submodels are parameter tables compiled into the variant. The proposed design makes them **functions with externally loaded, versioned parameters**, so a new BEC or species is a data/parameter task, not a code fork.

---

## 3. Comparison table

Legend: **DD** = distance-dependent; **DI** = distance-independent; **S** = stochastic; **D** = deterministic. "Better than FVS-BC" means a specific structural feature, not a claim of superior BC validation (which generally does not exist).

| Model / system | Architecture | Mortality logic | Ingress logic | Calibration / validation | Known failure modes | Genuinely better than FVS-BC |
| --- | --- | --- | --- | --- | --- | --- |
| **SILVA** (Pretzsch, Biber & Ďurský 2002) | DD, individual tree, 5-yr, age-independent; potential growth × competition modifier; static crown; site via climate/site dose-response | Logistic **survival** probability from tree dimension and expected basal-area increase: `P = 1/(1+exp(−(a0 + a1·d + a2·(i_g/dbh) + a3·(h/dbh) + a4·SI + …)))`; stochastic survival. Includes **SI and growth**; direct climate mortality is not documented in the reviewed sources `[UNVERIFIED]`. | Natural regeneration was a later/ongoing submodel in v2.2 [UNVERIFIED exact form]; many applications use planting or ingrowth input. A citing paper describes seedling establishment related to biotic factors. | Long-term research plots in southern Germany; extensive stand/enterprise/region evaluations; one secondary evaluation reports ~5% per-decade under-estimation of diameter `[secondary]`. | Coarse for minor species; regeneration not a validated core in v2.2; potential-growth ceiling; regional calibration. | **Growth- and SI-dependent survival**; explicit stochasticity; a compact, interpretable hazard. This is the closest European analogue to the proposed `BCMORT` v1. |
| **BWINPro / TreeGrOSS** (Nagel 1999; Nagel et al. 2002; Nagel & Schmidt 2006; Hansen & Nagel 2014) | DI (optional spatial variant), individual tree, 5-yr; potential height growth; static crown; SI | Modern TreeGrOSS: **density-dependent mortality via maximum density** (extended C-D rule, Sterba 1981; Doebbeler 2004) plus age-related mortality; trees whose influence zone exceeds crown closure are selected; 95%/99% survival thresholds. Earlier BWINPro may use a logistic form [UNVERIFIED exact version]. | **Regeneration layers** of small "placeholder" trees; ingrowth on 500 m² grid cells. Presence: `pE = p0·c66Kl^p1`; if `U > pE`, stop. Count: `nE = exp(p0 + p1·c66Kl)`. Species drawn randomly from leading species × c66Kl. Placeholders: age 5, DBH 0.5 cm, H 0.5 m; become trees at 7 cm. Density-dependent mortality of placeholders under shade. | Long-term German thinning/PSP trials; NW-FVA operational inventory data; evaluated against stand-growth principles (Vospernik 2017). | Max density exceeded on some species/sites; young-stand behavior; species-specific parameter availability; regeneration model is regional (NW Germany). | **A calibrated hurdle ingress model** (presence × count) driven by light/canopy closure and overstory composition; **density-dependent mortality without a lookup table**. The ingress logic is directly portable to DI FVS. |
| **MOSES** (Hasenauer 1994; Hasenauer et al. 2006; Thurnher, Klopf & Hasenauer 2017) | DD, individual tree; potential diameter and height growth; dynamic crown; spatial competition index; SI | **Monserud–Sterba logistic** probability of death over 5 years: `p_i = [1 + exp(a0 + a1·CIR + a2·CR + a3·dbh + a4/dbh)]^{-1}`; random draw `rnd > p_i` → survives. Includes **competition index, crown ratio, DBH, 1/DBH**. | Regeneration model exists in the MOSES framework [UNVERIFIED exact process]; in practice regeneration/ingrowth is often an input layer. | Austrian and European long-term plots; evaluated in Vospernik (2017) and model comparisons; open-grown crown ratio constrained to 1. | Crown ratio = 1 for open-grown by constraint; young-stand behavior; max density exceeded in some evaluations; regeneration not a validated process core. | **Crown ratio + competition + size in a stochastic survival model**; simple, transferable functional form. This is the cleanest precedent for a tree-level hazard with CR. |
| **PICUS** (Lexer & Hönninger 2001; Seidl et al. 2005, 2008) | Spatially explicit 3-D patch model, monthly, individual trees; climate, soil water, C/N; light | Background (max age) + **stress from negative leaf-mass increment over successive years**; alternative PROGNAUS empirical `f(dbh, crown ratio, BAL)`. Mortality is a process response, not a lookup table. | Regeneration and mortality retained from the gap-model approach of Lexer & Hönninger (2001): seed availability from parent trees + establishment probability conditioned on light, temperature, water/nutrients [UNVERIFIED exact equation]. | Tested against Austrian growth/yield data; PNV and climate-response comparisons; process evaluation. | **Recruitment over-estimation and high variability** in the Díaz-Yáñez et al. (2024) 15-model comparison (PICUS was the largest over-estimator); parameter-heavy; monthly step. | **Climate/water-stress mortality** and **light/water-gated establishment**; a process alternative to empirical hazards. Use as a structural donor for the stress component, not as a BC parameter source. |
| **SORTIE-ND / SORTIE/BC** (Pacala et al. 1996; Coates et al. 2003; Kobe & Coates 1997) | Spatially explicit, individual-based, 5-yr; light-mediated; seedlings, saplings, adults | Juvenile survival is a species-specific function of **recent radial growth** (Kobe et al. 1995; Kobe & Coates 1997); adult mortality from size/senescence plus a **user-specified random background**; self-thinning optional. Growth and resource models deterministic; **mortality and recruitment stochastic** (Pacala et al. 1996). | **Parent-tree proximity, size and abundance** + seedbed substrate favourability under four canopy-openness classes (full canopy, partial canopy, large gaps, clearcuts; Ribbens et al. 1994; LePage et al. 2000). Explicit seed dispersal; stochastic. | SORTIE/BC parameterized for SBSmc2 and ICHmc2 (Date Creek, Kispiox); light submodel validated; **limited calibration/testing in BC**, no climate inputs in BC; requires spatial tree list or generates random locations. | Data-hungry; limited BC transferability across site series; no climate in BC; adult mortality less developed than juvenile; spatial initialization. | **The best explicit parent-tree + seedbed recruitment model in the comparison**, and **growth-based juvenile mortality**. This is the strongest structural argument that FVS ingress must be seed-source-dependent, not a flat rate. |
| **iLand** (Seidl et al. 2012; Rammer et al. 2024; iLand book) | Individual-based, landscape, annual time step with sub-annual integration; process C allocation; 3-D light; climate/soil | Background (max age) + **stress from negative carbon balance / carbon starvation**, with a lag; alternative minimum absolute/relative diameter increment; disturbance mortality (wind, fire, bark beetle). | **Seed production** (fecundity per m² crown), **dispersal kernel**, seed-year interval and non-seed-year fraction; **establishment probability** limited by light, temperature, water; sapling self-thinning (`sapReinekesR`); serotiny. | Evaluated against Austrian permanent plots, self-thinning, PNV, and 150-species parameter sets (Thom et al. 2024); recruitment over-estimated in Díaz-Yáñez et al. (2024). | Complex, parameter-heavy; recruitment still over-estimated; climate/soil data requirements; process parameters not identifiable from short PSP series. | **A complete, climate-sensitive seed-to-establishment chain**; the best template for `BCINGR` v2. The model's own evaluation shows that complexity alone does not fix recruitment bias. |
| **FORMIND** (Köhler & Huth 1998; Fischer et al. 2016) | Individual/cohort gap model, 20 m × 20 m patches, 1-yr; plant functional types | **Stochastic background mortality** from a mean annual rate (typically ~2%/yr); `NPP < 0` → death (or increased probability); crowding increases mortality; falling large trees damage neighbors. | Seeds from **mother trees within the stand or external seed rain**; dispersal between patches; **light-gated germination**; seedbank with seed mortality; recruitment limitation. | Sabah permanent plots (Köhler et al. 2001); tropical forest; extensive logging/scenario work. | Tropical PFT structure; not directly transferable to BC species; background rate is a calibration parameter; recruitment limitation sensitive to dispersal assumptions. | **Explicit seed pool, seedbank, light-gated germination and recruitment limitation**; a clear demonstration that mortality can be stochastic and size/competition-dependent. Structural donor for ingress, not a BC parameter source. |
| **TASS / TIPSY** (Mitchell 1975; Di Lucca 1999; Goudie et al. 2026; Forest Analysis Ltd. 2021) | Spatially explicit, crown-driven individual tree; BC operational; TASS III light model | Crown competition/light-driven mortality; TASS III light regulates growth and mortality; self-thinning. Exact equation is proprietary/undocumented [UNVERIFIED]. | **Does not predict ingress beyond the establishment period** (BC review, p. 5). TIPSY is a stand-level yield-table interpolation with no mixed-species interactions. | Calibrated on detailed stem/crown analysis of research plots in relatively pest-free stands, plus 150+ year PSPs for older ages; yields close to site/species potential; **no recent independent validation** and little documentation. | No ongoing ingress; limited species/mixtures (TASS III public: lodgepole pine/white spruce); proprietary; OAFs coarse and region-independent; not calibrated for all BC species. | **Crown/light realism and a long BC calibration history.** Its weakness is precisely the one FVS-BC must fix: recruitment stops at establishment. |
| **PrognosisBC / FVS-BC** (Stage 1973; Wykoff et al. 1982; Hamilton & Edwards 1976; Temesgen Hailemariam 2001 [unpublished]; Zumrawi 2004) | DI, individual tree, 5/10-yr; FVS keyword system | Tabular ICH/IDF table (5 BA × 4 DBH classes), four-entry site-series logistic for minor species, BA-max/SDI cap; deterministic expected mortality; no SI/climate/CR/growth in the tabular/LMRT paths; no species-specific competition. | PROGNOSIS establishment model, but BC uses **`PLANT`/`NATURAL` keywords only**; no automatic seed-source ingress; regeneration imputation models (Zumrawi 2004) are an external imputation approach, not a process model. | BC calibration for ICH/IDF, legacy ESSF/MS/PP, partial SBS/SBPS; project PSP baseline shows over-prediction in SBPS/SBS; no recent independent validation (BC 2021 review). | Coarse BEC domains; discontinuities; no SI/climate; missing ingress confounded with mortality; deterministic; five zones unsupported. | **The baseline to beat.** Its weaknesses define the requirements. |
| **MGM** (Mixedwood Growth Model; Forest Analysis Ltd. 2021; U. Alberta) | DI, individual tree, aspatial; height-driven; species-specific competition; climate moisture index | Survival based on social status/competition; competition adjustment **varies with the species of competing trees**; dominant trees more likely to survive. Exact equation [UNVERIFIED]. | Not a core process model in the reviewed documentation; likely planting/ingrowth input [UNVERIFIED]. | Calibrated in Alberta with some BC SBS/SWBS work; current calibration includes BC PSP data (2020 release); not independently validated in BC. | Aspatial; requires homogeneous strata; limited BC validation; regeneration not a strength. | **Species-specific competition and a climate moisture index** in a DI framework. This is a direct precedent for adding species identity to FVS competition terms. |
| **Organon** (Hann, Marshall & Hanus 2006) | DI, individual tree, PNW; empirical | 5-yr mortality probability `PM5 = f(DBH, crown ratio, BAL, …)`; reanalysis of SMC-ORGANON equations; strong Douglas-fir calibration. | No natural recruitment; planting/ingrowth input. | Long-term SMC/PSP plots; extensive Douglas-fir validation. | PNW-specific; no ingress; species coverage. | **A well-validated empirical mortality form with crown ratio and BAL** for a major BC species (Douglas-fir). Useful as a coefficient/benchmark donor, not as a full BC model. |
| **FVS establishment model** (Ferguson & Carlson 1993; Ferguson et al. 1986) | DI, plot-level regeneration establishment | n/a | Species-specific probability and amount of establishment as a function of **habitat type, site preparation, canopy openness, overstory, and existing regeneration**; 12,128 plots in 537 stands; the only full-featured FVS regeneration model. | Large stratified sample in the northern Rocky Mountains; operational in several FVS variants. | Regional (Inland Empire); data-hungry; not BC; "all-or-none" regeneration is hard to observe. | **Proof that FVS can host a real regeneration model**, and a benchmark for the data volume required. Its structure (presence × amount, habitat/site prep/canopy) is a template for `BCINGR`. |

### 3.1 Cross-cutting reading of the table

- **Mortality forms cluster into three families:** (i) empirical logistic survival with size + competition + growth (SILVA, MOSES, Organon), (ii) density/self-thinning thresholds (BWINPro, FVS-BC's BA cap), and (iii) process stress/carbon balance (PICUS, iLand, FORMIND). The empirical family is the best fit for PSP data; the process family is best for climate scenarios but needs more parameters than BC PSP can identify.
- **Ingress forms cluster into two families:** (i) explicit seed-source/dispersal/seedbed models (SORTIE, iLand, FORMIND) and (ii) stand-level hurdle/count models driven by overstory/light (BWINPro, FVS establishment). FVS is distance-independent and lacks coordinates, so the **stand-level hurdle model with a seed-rain index** is the pragmatic bridge: it retains parent-tree dependence without requiring a spatial grid.
- **No model in the table has both a strong BC calibration and a strong recruitment model.** TASS has BC calibration but no ingress; SORTIE/BC has ingress but limited BC calibration and no climate; FVS-BC has neither. This is the gap the programme is filling. The design should borrow structure, not authority.

---

## 4. Model-by-model notes (citations, logic, data, failure modes)

### 4.1 SILVA

**Citations.** Pretzsch, H., Biber, P., Ďurský, J. 2002. The single tree-based stand simulator SILVA: construction, application and evaluation. *Forest Ecology and Management* 162:3–21. DOI [10.1016/S0378-1127(02)00047-6](https://doi.org/10.1016/S0378-1127(02)00047-6). Design lineage: Pretzsch (1992), Kahn & Pretzsch (1997); evaluation: Pretzsch (2002). Secondary: Vospernik (2017).

**Mortality.** SILVA calculates a **survival probability** with a logit function of tree dimension and expected basal-area increase. The published form is

```
P_surv = 1 / (1 + exp(−(a0 + a1·d + a2·(i_g/dbh) + a3·(h/dbh) + a4·SI + …)))
```

where `i_g` is basal-area increment, `h/dbh` is the height–diameter ratio, and `SI` is site index. A random draw determines survival. This is a compact, interpretable hazard with **growth, size, stem form and site quality** — four things FVS-BC's tabular path lacks. `[VERIFIED: primary abstract/equation snippet; full paper not accessible]`.

**Ingress.** SILVA 2.2's "ongoing development" included natural-regeneration submodels; the classic model is often initialized by planting or ingrowth. A citing paper describes SILVA v2.2 as relating seedling establishment to biotic factors. I could not verify a seed-dispersal kernel or a parent-tree fecundity function. `[UNVERIFIED]`. Do not treat SILVA as an ingress donor.

**Data / calibration.** Long-term research plots in pure and mixed stands, mainly southern Germany; stand-, enterprise- and region-level evaluations. One evaluation reports ~5% relative under-estimation of diameter per decade.

**Failure modes.** Potential-growth ceiling; regional calibration; minor species; regeneration not a validated core; static crown. **Better than FVS-BC:** growth- and SI-dependent survival, stochasticity, and a hazard that responds continuously to size/growth rather than a BA/DBH class table.

### 4.2 BWINPro / TreeGrOSS

**Citations.** Nagel, J. 1999. *Konzeption und Standortsanalyse des waldbaulichen Entscheidungsmodells BWINPro.* Dissertation, Universität Göttingen. Nagel, J., Albert, M., Schmidt, M. 2002. Das waldbauliche Prognose- und Entscheidungsmodell BWINPro 6.1. *Forst und Holz* 57:1–8. Nagel, J., Schmidt, M. 2006. The silvicultural decision support system BWINPro. In: Hasenauer, H. (ed.), *Sustainable Forest Management: Growth Models for Europe*, Springer, pp. 59–63. DOI [10.1007/3-540-31304-4_4](https://doi.org/10.1007/3-540-31304-4_4). Implementation: Hansen, J., Nagel, J. 2014. *Waldwachstumskundliche Softwaresysteme auf Basis von TreeGrOSS.* Beiträge aus der NW-FVA, Band 11. [PDF](https://www.nw-fva.de/fileadmin/nwfva/publikationen/pdf/hansen_2014_waldwachstumskundliche.pdf).

**Mortality.** The modern TreeGrOSS implementation combines **density-dependent mortality via maximum density** (extended competition–density rule, Sterba 1981; Doebbeler 2004) with **age-related mortality**. The maximum density is a function of top height; trees whose influence zone exceeds crown closure are selected, with 95% (secondary species) / 99% (main species) survival thresholds. This is a **threshold/self-thinning** model, not a logistic hazard. Earlier BWINPro versions may use a different logistic form `[UNVERIFIED exact version]`.

**Ingress.** This is one of the most directly portable designs in the comparison. Ingrowth is handled through **regeneration layers** of small placeholder trees on a 500 m² grid:

```
pE = p0 * c66Kl^p1                 # probability that regeneration occurs
if U(0,1) > pE: nE = 0
else:           nE = exp(p0 + p1*c66Kl)
species ~ categorical(leading species, c66Kl)
placeholder: age 5, DBH 0.5 cm, H 0.5 m, crown width 2.52 m
```

`c66Kl` is a crown-closure/light class (0.2 width, max 2.5), computed from the crown cover of all trees over the cell. Placeholders suffer density-dependent mortality under shade and become trees at 7 cm DBH. This is a **hurdle model** (presence × count) with a **light/overstory driver** and **random species composition** — exactly the kind of stand-level approximation FVS can use.

**Data / calibration.** Long-term German thinning and PSP trials; NW-FVA operational inventory data (500 m² circles); evaluated against stand-growth principles (Vospernik 2017).

**Failure modes.** Maximum density exceeded on some species/sites; young-stand behavior; parameter availability; regeneration model is regional to NW Germany; the placeholder crown width is a modeling artifact. **Better than FVS-BC:** a calibrated presence/count ingress model with light and overstory dependence; density-dependent mortality that is not a BEC lookup table.

### 4.3 MOSES

**Citations.** Hasenauer, H. 1994. *Ein Einzelbaumwachstumsmodell für einen ungleichaltrigen Fichtenbestand.* Dissertation, Universität für Bodenkultur Wien. Hasenauer, H., Kindermann, G., Steinmetz, P. 2006. The tree growth model MOSES 3.0. In: Hasenauer, H. (ed.), *Sustainable Forest Management: Growth Models for Europe*, Springer, pp. 64–70. Thurnher, C., Klopf, M., Hasenauer, H. 2017. MOSES – A tree growth simulator for modelling stand response in Central Europe. *Ecological Modelling* 352:58–76. DOI [10.1016/j.ecolmodel.2017.01.013](https://doi.org/10.1016/j.ecolmodel.2017.01.013).

**Mortality.** MOSES uses the **Monserud–Sterba logistic** probability of death over five years (Monserud & Sterba 1999; cited as 1998 in the implementation):

```
p_i = [1 + exp(a0 + a1·CIR + a2·CR + a3·dbh + a4/dbh)]^{-1}
if rnd > p_i: tree survives
```

where `CIR` is the competition index after crown release and `CR` is crown ratio. This is a direct, well-documented precedent for **crown ratio + competition + size + inverse size** in a stochastic survival model. `[VERIFIED: BOKU thesis/implementation description]`.

**Ingress.** MOSES has a regeneration model in its framework, and its data model carries a "regeneration" layer, but the reviewed implementation treats regeneration largely as an input/initialization layer rather than a validated seed-dispersal process. Exact equations `[UNVERIFIED]`. Do not use MOSES as the ingress donor.

**Data / calibration.** Austrian and European long-term plots; evaluated in Vospernik (2017) and model comparisons; open-grown crown ratio constrained to 1.

**Failure modes.** Crown ratio = 1 for open-grown by constraint; young-stand behavior; max density exceeded in some evaluations; regeneration not a validated core. **Better than FVS-BC:** crown ratio and competition in a stochastic hazard; a simple form that can be fitted to PSP data with modest sample sizes.

### 4.4 PICUS

**Citations.** Lexer, M.J., Hönninger, K. 2001. A modified 3D-patch model for spatially explicit simulation of vegetation composition in heterogeneous landscapes. *Forest Ecology and Management* 144:43–65. DOI [10.1016/S0378-1127(00)00386-8](https://doi.org/10.1016/S0378-1127(00)00386-8). Seidl, R., Rammer, W., Lasch, P., Badeck, F.-W., Lexer, M.J. 2008. Does conversion of even-aged, secondary coniferous forests affect carbon sequestration? A simulation study under changing environmental conditions. *Silva Fennica* 42:369–386. [PDF](https://silvafennica.fi/pdf/243). Seidl, R., Rammer, W., Scheller, R.M., Spies, T.A. 2012. An individual-based process model to simulate landscape-scale forest ecosystem dynamics. *Ecological Modelling* 231:87–100. DOI [10.1016/j.ecolmodel.2012.02.015](https://doi.org/10.1016/j.ecolmodel.2012.02.015).

**Mortality.** Background (maximum age) plus **stress from negative leaf-mass increment over successive years**; alternative PROGNAUS empirical `f(dbh, crown ratio, BAL)`. Mortality is a process response, not a table.

**Ingress.** Regeneration and mortality are retained from the gap-model approach of Lexer & Hönninger (2001): seed availability from parent trees plus establishment probability conditioned on light, temperature, water and nutrients. The exact equation is in the 2001 paper, which I did not read directly; treat the form as `[UNVERIFIED]`.

**Data / calibration.** Tested against Austrian growth/yield data; PNV and climate-response comparisons. In the Díaz-Yáñez et al. (2024) 15-model regeneration comparison, **PICUS had the largest recruitment over-estimation and the largest variability** — a cautionary result, not a recommendation.

**Failure modes.** Recruitment over-estimation; parameter-heavy; monthly step; process parameters hard to identify from PSP. **Better than FVS-BC:** climate/water-stress mortality and light/water-gated establishment. Use as a structural donor for the stress component, not as a BC parameter source.

### 4.5 SORTIE-ND / SORTIE-BC

**Citations.** Pacala, S.W., Canham, C.D., Saponara, J., Silander, J.A., Kobe, R.K., Ribbens, E. 1996. Forest models defined by field measurements: estimation, error analysis and dynamics. *Ecological Monographs* 66:1–43. DOI [10.2307/2963479](https://doi.org/10.2307/2963479). Coates, K.D., Canham, C.D., Beaudet, M., Sachs, D.L., Messier, C. 2003. Use of a spatially explicit individual-tree model (SORTIE/BC) to explore the implications of patchiness in structurally complex forests. *Forest Ecology and Management* 186:297–310. DOI [10.1016/S0378-1127(03)00301-3](https://doi.org/10.1016/S0378-1127(03)00301-3). Kobe, R.K., Coates, K.D. 1997. Models of sapling mortality as a function of growth to characterize interspecific variation in shade tolerance of eight tree species of northwestern British Columbia. *Canadian Journal of Forest Research* 27:227–236. DOI [10.1139/x96-182](https://doi.org/10.1139/x96-182). Ribbens, E., Silander, J.A., Pacala, S.W. 1994. Seedling recruitment in forests: calibrating models to predict patterns of tree seedling dispersion. *Ecology* 75:1794–1806. DOI [10.2307/1939638](https://doi.org/10.2307/1939638).

**Mortality.** Juvenile survival is a species-specific function of **recent radial growth** (Kobe et al. 1995; Kobe & Coates 1997); adult mortality is size/senescence plus a **user-specified random background**; self-thinning functions are optional. Pacala et al. (1996) state explicitly that growth and resource models are deterministic while **mortality and recruitment are stochastic**. Parameters should be estimated from local remeasured plots.

**Ingress.** The number and spatial distribution of seedlings from **parent-tree proximity, size and abundance** (Ribbens et al. 1994) plus **seedbed substrate favourability under four canopy-openness classes** (full canopy, partial canopy, large gaps, clearcuts; LePage et al. 2000). Stochastic. This is the clearest published statement that recruitment must depend on the parent trees and the seedbed, not on a stand-average rate.

**Data / calibration.** SORTIE/BC parameterized for SBSmc2 and ICHmc2 (Date Creek, Kispiox); light submodel validated; **limited calibration/testing in BC**, no climate inputs in BC, requires a spatial tree list or generates random locations. The BC 2021 review calls the recruitment model a genuine strength and the BC calibration a weakness.

**Failure modes.** Data-hungry; limited transferability across site series; no climate in BC; adult mortality less developed than juvenile; spatial initialization. **Better than FVS-BC:** the best explicit parent-tree + seedbed recruitment model in the comparison, and growth-based juvenile mortality.

### 4.6 iLand

**Citations.** Seidl, R., Rammer, W., Scheller, R.M., Spies, T.A. 2012. An individual-based process model to simulate landscape-scale forest ecosystem dynamics. *Ecological Modelling* 231:87–100. DOI [10.1016/j.ecolmodel.2012.02.015](https://doi.org/10.1016/j.ecolmodel.2012.02.015). Rammer, W., Thom, D., Baumann, M., Braziunas, K.H., Dollinger, C., Kerber, J., et al. 2024. The individual-based forest landscape and disturbance model iLand: overview, progress, and outlook. *Ecological Modelling* 495:110785. DOI [10.1016/j.ecolmodel.2024.110785](https://doi.org/10.1016/j.ecolmodel.2024.110785). Model book: [iland-model.org/downloads/iland-book.pdf](https://iland-model.org/downloads/iland-book.pdf). Parameters: Thom et al. (2024), [PDF](https://depts.washington.edu/bjhlab/wordpress/wp-content/uploads/2024/10/Thom_etal_2024_DiB_iLandParameters.pdf).

**Mortality.** Background (maximum age) plus **stress from negative carbon balance / carbon starvation**, with a lag; alternative minimum absolute/relative diameter increment; disturbance mortality (wind, fire, bark beetle). The iLand book describes stress as the dominant factor: a tree dies when it cannot capture enough energy to maintain itself, from light limitation or depleted reserves.

**Ingress.** Seeds are produced (fecundity per m² crown), dispersed (kernel), and established with probabilities limited by light, temperature and water; seed-year interval and non-seed-year fraction; sapling self-thinning (`sapReinekesR`); serotiny. This is a complete climate-sensitive seed-to-establishment chain.

**Data / calibration.** Austrian permanent plots, self-thinning, PNV, 150-species parameter sets; recruitment over-estimated in the Díaz-Yáñez et al. (2024) comparison.

**Failure modes.** Complex and parameter-heavy; recruitment still over-estimated; climate/soil data requirements; process parameters not identifiable from short PSP series. **Better than FVS-BC:** a complete seed-to-establishment chain and a mechanistic stress mortality. Use as the template for `BCINGR` v2 and the stress component of `BCMORT` v2.

### 4.7 FORMIND

**Citations.** Köhler, P., Huth, A. 1998. The effects of tree species grouping in tropical rainforest modelling: simulations with the individual-based model Formind. *Ecological Modelling* 109:301–321. DOI [10.1016/S0304-3800(98)00066-0](https://doi.org/10.1016/S0304-3800(98)00066-0). Köhler, P., Ditzer, T., Ong, R., Huth, A. 2001. Comparison of measured and modelled growth on permanent plots in Sabah's rain forests. *Forest Ecology and Management* 144:101–111. DOI [10.1016/S0378-1127(00)00364-9](https://doi.org/10.1016/S0378-1127(00)00364-9). Fischer, R., Bohn, F., Dantas de Paula, M., Dislich, C., Groeneveld, J., Gutiérrez, A.G., et al. 2016. Lessons learned from applying a forest gap model to understand ecosystem and carbon dynamics of complex tropical forests. *Ecological Modelling* 326:124–133. DOI [10.1016/j.ecolmodel.2015.11.018](https://doi.org/10.1016/j.ecolmodel.2015.11.018). Köhler, P., Huth, A. 2007. Impacts of recruitment limitation and canopy disturbance on tropical tree species richness. *Ecological Modelling* 203:511–517. DOI [10.1016/j.ecolmodel.2006.11.023](https://doi.org/10.1016/j.ecolmodel.2006.11.023).

**Mortality.** Background mortality is **stochastic from a mean annual rate** (typically ~2%/yr); `NPP < 0` causes death (or an increased probability); crowded patches have increased mortality; falling large trees damage neighbors.

**Ingress.** Seeds from **mother trees within the stand or external seed rain**; dispersal between patches; **light-gated germination**; seedbank with seed mortality; recruitment limitation. This is a clear, compact process model for a seed pool.

**Data / calibration.** Sabah permanent plots; tropical forest; extensive logging/scenario work. Not directly transferable to BC species, but the structure is.

**Failure modes.** Tropical PFT structure; not BC; background rate is a calibration parameter; recruitment limitation sensitive to dispersal assumptions. **Better than FVS-BC:** explicit seed pool, seedbank, light-gated germination and recruitment limitation; stochastic, competition-dependent mortality.

### 4.8 TASS / TIPSY

**Citations.** Mitchell, K.J. 1975. Dynamics and simulated yield of Douglas-fir. *Forest Science Monograph* 17. Di Lucca, C.M. 1999. TASS/SYLVER/TIPSY: systems for predicting the impact of silvicultural practices on yield, lumber value, economic return and other benefits. *Stand Density Management Conference*, Edmonton, Alberta, pp. 7–16. Goudie, J.W., Cameron, I.R., Bealle Statland, C., Polsson, K., Parish, R. 2026. Development of the Tree and Stand Simulator (TASS) Version 3.0. Preprint. DOI [10.13140/RG.2.2.25369.68962](https://doi.org/10.13140/RG.2.2.25369.68962). García, O. 2005. TADAM: a dynamic whole-stand approximation for the TASS growth model. *The Forestry Chronicle* 81:575–581. DOI [10.5558/tfc81575-4](https://doi.org/10.5558/tfc81575-4). BC review: Forest Analysis Ltd. (2021), [PDF](https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/stewardship/forest-analysis-inventory/growth-yield/modelreview_finalreport_march_2021.pdf).

**Mortality.** Crown competition/light-driven; TASS III has a light model that regulates growth and mortality; self-thinning. The exact equation is proprietary/undocumented `[UNVERIFIED]`. The BC review notes that TASS is calibrated on detailed stem/crown analysis of research plots in relatively pest-free stands, and that its yields are close to the potential of a site/species/management regime.

**Ingress.** **TASS does not predict ingress beyond the establishment period** (BC review, p. 5). TIPSY is a stand-level yield-table interpolation; mixed-species yields are a weighted average of pure-species tables with no species interactions.

**Data / calibration.** Detailed stem and crown analysis; research plots from ~1960 onward; 150+ year PSPs for older ages; TASS III public for lodgepole pine/white spruce. **No recent independent validation; little documentation of calibration data; not calibrated for all BC species/mixtures.**

**Failure modes.** No ongoing ingress; limited species/mixtures; proprietary; coarse OAFs; no recent validation. **Better than FVS-BC:** crown/light realism and a long BC calibration history. Its weakness is exactly the gap FVS-BC must fill.

### 4.9 PrognosisBC / FVS-BC

**Citations.** Stage, A.R. 1973. *Prognosis model for stand development.* USDA Forest Service Research Paper INT-137. Wykoff, W.R., Crookston, N.L., Stage, A.R. 1982. *User's guide to the Stand Prognosis Model.* USDA Forest Service General Technical Report INT-133. Hamilton, D.A., Edwards, B.M. 1976. *Modeling the probability of individual tree mortality.* USDA Forest Service Research Paper INT-185. Crookston, N.L., Dixon, G.E. 2005. The Forest Vegetation Simulator: a review of its structure, content, and applications. *Computers and Electronics in Agriculture* 49:60–80. DOI [10.1016/j.compag.2005.02.003](https://doi.org/10.1016/j.compag.2005.02.003). Temesgen Hailemariam (UBC Faculty of Forestry), 2001. Mortality model for PrognosisBC. Unpublished report (cited in `canada/bc/morts.f` as "fitted by Temesgen Hailemariam, December 8, 2001"; the name is a single person, not two authors). Zumrawi, A.A. 2004. Regeneration imputation models for complex stands of southeastern British Columbia. *The Forestry Chronicle* 80:271–278. DOI [10.5558/tfc80271-2](https://doi.org/10.5558/tfc80271-2).

**Mortality.** As audited in §2.1: tabular ICH/IDF, four-entry site-series logistic, BA-max/SDI cap, deterministic. The current source's comment says the site-series logistic was fitted by Temesgen Hailemariam (UBC) in 2001, but the `LMRT` table only contains four BEC strings.

**Ingress.** As audited in §2.2: keyword-driven `PLANT`/`NATURAL`; no automatic seed-source ingress. Zumrawi's regeneration imputation models are an external imputation approach for complex stands, not a process model. The wrapper's flat BEC × species rate table is the current operational substitute.

**Data / calibration.** BC calibration for ICH/IDF, legacy ESSF/MS/PP, partial SBS/SBPS; project PSP baseline shows over-prediction in SBPS/SBS; no recent independent validation. The project has 4,430 sites and 13,191 visits in the seven supported zones, 9,186 intervals, 1,031,828 tree-survival rows and 54,269 damage-coded rows (project summary). The five missing zones (CWH, CDF, BWBS, MH, CMA) have 32 variants, 2,911 sites and 10,765 visits but lack species/model tables.

**Failure modes.** Coarse BEC domains; discontinuities; no SI/climate; missing ingress confounded with mortality; deterministic; five zones unsupported. **Better than FVS-BC:** the proposed functions below.

### 4.10 MGM

**Citations.** Forest Analysis Ltd. 2021 (BC review); MGM project, [mgm.ualberta.ca](https://mgm.ualberta.ca/). The BC review describes MGM as a deterministic, distance-independent, individual-tree model for boreal mixedwoods (white spruce, trembling aspen, lodgepole pine, jack pine, black spruce), height-driven, with species-specific competition and a climate moisture index; calibrated in Alberta with some BC SBS/SWBS work and current BC PSP data (2020 release). Exact mortality/ingress equations are not in the review `[UNVERIFIED]`.

**Why it matters.** MGM is the clearest DI precedent for **competition that varies with the species of the competitor** — something FVS-BC lacks (the BC review notes FVS growth is affected by the presence and size of competitors but not their species). It also includes a climate moisture index. It is not a recruitment model.

### 4.11 Organon

**Citation.** Hann, D.W., Marshall, D.D., Hanus, M.L. 2006. *Reanalysis of the SMC-ORGANON equations for diameter-growth rate, height-growth rate, and mortality rate of Douglas-fir.* Forest Research Laboratory, Oregon State University, Research Contribution 49.

**Why it matters.** A well-validated empirical 5-year mortality equation for Douglas-fir with DBH, crown ratio and BAL. It is a coefficient/benchmark donor for the most important BC interior species, not a full BC model. No natural recruitment.

### 4.12 FVS establishment model (Ferguson–Carlson)

**Citation.** Ferguson, D.E., Carlson, C.E. 1993. *Predicting regeneration establishment with the Prognosis model.* USDA Forest Service Research Paper INT-467. DOI [10.5962/bhl.title.68938](https://doi.org/10.5962/bhl.title.68938). Also Ferguson et al. (1986) and Robinson (2008).

**Why it matters.** It is the only full-featured regeneration model in FVS and it establishes the data requirement: **12,128 plots in 537 stands** to model 10 conifer species across five habitat-type series, site preparation, canopy openness and existing regeneration. It uses a presence × amount structure, which is the same hurdle logic proposed here. It is regional (Inland Empire) and not BC, but it proves FVS can host a real regeneration model and shows the sample size needed.

---

## 5. Cross-cutting evidence

### 5.1 Mortality: what actually predicts death

**Hülsmann, Bugmann & Brang (2017)** systematically applied 46 inventory-based mortality models to ~80,000 independent records from 54 strict forest reserves in Germany and Switzerland (11 species). Key results:

- Mortality rates were predicted with **higher accuracy when individual-tree growth and/or competition covariates were included**.
- Models applied **within the same ecological zone** performed better.
- **Classification** of dead vs. living trees was improved mainly by **growth variables**.
- Management intensity, census interval and calibration dataset size did **not** strongly influence performance.
- Recommendation: for a restricted spatial extent and current climate, calibrate on **regional data, even if small**; for wider applicability and climate sensitivity, address spatial variability explicitly.

This is the single strongest justification for (i) adding growth and competition to FVS-BC mortality, and (ii) using BEC/site random effects rather than one global table.

**Monserud & Sterba (1999)** fitted a logistic mortality model for six Austrian species and found the **same general form** for all species, with basal area in larger trees (BAL) and crown ratio as key predictors. This supports a common functional form with species-specific coefficients, rather than a separate bespoke model per species.

**SILVA** uses DBH, `i_g/dbh`, `h/dbh` and SI; **MOSES** uses competition index, crown ratio, DBH and 1/DBH; **SORTIE** uses recent radial growth; **Organon** uses DBH, crown ratio and BAL. Four independent lineages converge on the same covariate set: **size, competition, vigor/growth, and site**.

**Bugmann et al. (2019)** ran 15 dynamic vegetation models with at least two mortality formulations each. Most matched historical data similarly, but diverged by **10–40% in basal area and stem number per century under current climate and 20–170% under climate change**. The paper explicitly warns that **overfitting to short-term data** is a major problem and that empirical mortality formulations may exceed their range under future climate. This is the case for (i) reporting uncertainty, (ii) validating on temporal holdout, and (iii) treating climate terms as a separate, guarded extension rather than a free year multiplier.

**Canham & Murphy (2017)** show climate effects on sapling and canopy-tree survival across species; this supports climate covariates in the background hazard, but the effect sizes are species-specific and should not be assumed transferable to BC without local calibration.

### 5.2 Ingress: what actually predicts recruitment

**Lappi & Pukkala (2020)** fitted zero-inflated negative-binomial (ZINB) ingrowth models to Finnish NFI permanent plots. Key numbers:

- Ingrowth was **over-dispersed** relative to Poisson and had **many zeros**.
- The probability of "extra zeros" averaged **0.68 for Scots pine, 0.22 for spruce, 0.21 for birch** in the fixed-effects models.
- The overdispersion parameter `α` was **2.28–3.19** — large.
- Predictors: species-specific and total basal area, temperature sum, fertility class.
- Fixed-effects models were unbiased; **mixed-effects models had larger likelihood but produced biased marginal predictions**. This is a crucial warning for calibration: random effects are useful for site-level inference, but the marginal prediction must be checked, and fixed effects may be preferable for operational projection.
- The authors also show that ignoring plot area and exposure time produces biased predictions (the earlier Pukkala et al. 2013 model under-predicted by 3–10× in average ingrowth).

**Li, Weiskittel & Kershaw (2011)** modeled annualized occurrence, frequency and composition of ingrowth in the Acadian Forest with mixed-effects zero-inflated Poisson/NB models. **Zhang et al. (2012)** compared negative-binomial mixture models and found ZINB performed well. **Zell et al. (2019)** modeled ingrowth for empirical forest prediction systems in Switzerland; **Flury et al. (2024)** show soil- and climate-dependent ingrowth inference. The consistent finding: **recruitment is a zero-inflated, over-dispersed count process with species-specific responses to overstory and climate.**

**BWINPro/TreeGrOSS** implements a simple hurdle model (`pE` then `nE`) driven by crown closure/light and leading species. This is the most directly portable stand-level design for FVS.

**SORTIE/BC** implements an explicit parent-tree + seedbed model. The BC 2021 review calls the recruitment model a genuine strength and notes it was calibrated with Date Creek data. This is the strongest argument that **parent-tree/seed-source dependence is not optional** if the model is to respond to partial cutting and mortality.

**Díaz-Yáñez et al. (2024)** compared 15 models of forest dynamics at 200 European sites. Key results:

- **Most models over-estimated recruitment**; SIBYLA, Landis-II and aDGVM2 were at the low end.
- The observed data had **4% of samples with no recruitment**; only three models produced a larger proportion of zeros, and most produced **far too few zeros** (0.01–2.39%).
- Increasing complexity in regeneration modules was **not related** to higher accuracy.
- Individual model design mattered more than scale (stand/landscape/global) or approach (empirical/process).
- Light effects were captured better than temperature and soil moisture.

This is the strongest evidence for a **parsimonious hurdle/ZINB model with an explicit zero process**, validated on the marginal distribution, not just the mean. It also warns against assuming that a more complex seed-dispersal model will automatically be better.

### 5.3 The project's own evidence

From `mort-calib/validation/model_comparison.csv` (IDFdk3/IDFxm, 45,834 tree rows, 186 sites):

| Model | Parameters | AIC | BIC | CV log loss | CV Brier |
| --- | ---: | ---: | ---: | ---: | ---: |
| continuous species BA | 14 | 44,384.8 | 44,507.1 | **0.48535** | 0.12167 |
| continuous common BA | 8 | 44,617.5 | 44,687.4 | 0.48719 | 0.12165 |
| species × BA class | 23 | 44,581.1 | 44,781.9 | 0.48784 | 0.12165 |

- The continuous species-BA model beats the 23-parameter class model by **196 AIC points** and **0.0025 CV log loss** with **9 fewer parameters**. This is direct evidence that continuous covariates + species interactions are a better use of parameters than a coarse table.
- The TSA holdout shows the limits of a single global model: 100 Mile House predicted 0.0201 vs observed 0.0148 per year (35.6% high); Williams Lake predicted 0.01435 vs observed 0.01449 (1% low). A BEC/site random effect is needed.
- The temporal holdout is much worse than random CV: log loss 1.28 (train 1993–2004, test 2008–2013) and 1.03 (train 1993–2008, test 2013), with the model under-predicting the later period (0.0104 vs 0.0167; 0.0108 vs 0.0124). A naive year term over-corrects and over-predicts (0.0275 vs 0.0167; 0.0627 vs 0.0124). **A free year multiplier is not a climate model.** Climate covariates must be validated on a temporal holdout.
- The baseline backtest (project summary) over-predicts BA in SBPS/SBS, consistent with a mortality/ingress structural error. Because ingress is missing, the direction of the mortality bias is not identifiable from BA alone; this is why the joint design matters.

---

## 6. Design proposal: FVS core-function upgrades

### 6.1 Principles

1. **Separate the processes, then join them.** Fit mortality on tree-level survival, ingress on recruitment counts, then check the joint BA/TPH trajectory. Do not use one multiplier to fix both.
2. **Functions, not tables.** The response is a function of measurable covariates; BEC/species enter as hierarchical effects, not as separate compiled tables.
3. **Partial pooling.** Borrow strength across BEC zones, site series and species; report uncertainty; flag data-poor domains instead of silently substituting a wrong table.
4. **Parsimony first.** Add growth, crown ratio, SI and climate only if they improve a pre-registered holdout. The literature shows complexity is not correlated with accuracy (Díaz-Yáñez et al. 2024).
5. **Guard the domain.** Clamp, flag and report; never silently extrapolate or fall back to a wrong BEC table.
6. **Keep FVS compatible.** Keep `MORTS`, `MORCON`, `ESTAB`, `PLANT`, `NATURAL`, `MORTMULT`, `FIXMORT`, `SIZCAP`, `BAIMULT`; add new behavior behind a bundle switch.
7. **Diagnostics are part of the model.** Per-tree mortality probability and per-species recruitment components must be written to the FVS database for calibration/validation.

#### 6.1.1 Why not multipliers

The existing calibration lever is a multiplier (`MORTMULT`, `BAIMULT`, the wrapper's bundle scale). A multiplier is a scalar on a fixed hazard shape. It cannot fix:

- **Wrong shape:** no SI, no growth term, no crown ratio, and discontinuities at the 10/25/40 cm and 20/30/40/50 m²/ha class boundaries. A scalar shifts the level but leaves the shape wrong.
- **Wrong domain:** the ICH/IDF table cannot represent an SBPS or SBS stand except by mapping it to ICH/IDF. A multiplier makes the wrong table fit better on average, which is worse than an honest uncertainty.
- **Confounding:** a multiplier fitted to BA trajectories absorbs missing ingress and growth error. The KC pilot's PL multiplier at its bound is the signature of structural misspecification, not a calibrated parameter.
- **No response:** a multiplier cannot represent a drought year, a partial cut, a change in species composition, or a post-disturbance seed pulse.

The proposed functions replace the **shape** of the response. Multipliers remain as explicit overrides, logged and reported, but they are not the calibration mechanism. This is the difference between "tune the table" and "model the process."

The "hand-tuned domain" problem is architectural: `FMRT`/`LMRT` encode BEC knowledge as compiled constants, so a new zone requires a new table. The proposed model encodes BEC/site knowledge as random effects and covariates, so a new zone is a data/prior task, with uncertainty.

### 6.2 Mortality core function (`BCMORT`)

#### 6.2.1 Model form

**Primary form: discrete-time survival with a complementary log-log link.**

For tree `i` in plot `p`, interval `t` of length `Δt` years. `BAL_ip` is the basal area of trees larger than the target tree (m²/ha); `BA_p` is total stand basal area; `QMD_p` is quadratic mean diameter.

```
η_ip = β0 + β_sp[sp]
     + f_dbh(dbh_ip)
     + β_bal · BAL_ip / 10
     + β_ba · BA_p / 10
     + β_ba2 · (BA_p / 10)^2
     + β_rel · (dbh_ip / QMD_p)
     + u_bec[BEC_p] + u_site[site_p]

p_ann = 1 − exp(−exp(η_ip))
p_int = 1 − (1 − p_ann)^Δt
```

`f_dbh` can be `β1·log(dbh) + β2·log(dbh)^2`, or `β1·dbh + β2·dbh^2 + β3/dbh` to capture the U-shape / increasing senescence. The cloglog is the discrete-time proportional-hazards analogue and handles unequal PSP intervals via the `log(Δt)` offset; it is also the form used in the project's pilot. The traditional FVS/Hamilton form `p = 1 − (1 + exp(−η))^{−Δt}` (proportional odds) is a sensitivity check, not the primary.

**Why not a single logistic on BA/DBH classes?** Because it cannot represent continuous size/growth/site effects, it produces discontinuities, and it forces every BEC into a table. The pilot's AIC result is a direct test: continuous covariates win.

#### 6.2.2 Covariates

| Block | Covariates | Rationale / evidence |
| --- | --- | --- |
| Size | DBH, log(DBH), DBH², 1/DBH | U-shaped/senescence hazard; Monserud & Sterba 1999; SILVA; MOSES. |
| Competition | BAL (total and species-specific), total BA, relative DBH = DBH/QMD, SDI | Hülsmann et al. 2017; Monserud & Sterba 1999; Organon; MGM species-specific competition. |
| Vigor | Recent radial growth `DG`, growth ratio `DG/DBH` or `DG/DG_pot`, crown ratio `CR` | Hülsmann et al. 2017 (growth is the key discriminator); SORTIE/Kobe–Coates; MOSES; SILVA; Organon. |
| Site | Site index `SI` (or BEC site-series productivity proxy), elevation, slope/aspect, soil moisture/nutrient regime | SILVA; MOSES; Hülsmann et al. 2017 (regional calibration). FVS-BC currently has none. |
| Climate | Climatic moisture deficit `CMI`, degree days `DD5`, drought-year indicator | Bugmann et al. 2019; Canham & Murphy 2017; iLand/PICUS. Add only after temporal validation. |
| Species | Species intercepts and (optionally) slopes for BAL/growth; or species groups | Monserud & Sterba 1999 (same form, species-specific coefficients); partial pooling. |
| Disturbance | Recent harvest/fire/insect flag, windthrow, root disease | FVS extensions; prevents the base hazard from absorbing disturbance. |
| Random effects | BEC zone/subzone, site series, TSA/region, plot; optionally year | TSA holdout in the pilot; Hülsmann et al. 2017; Bugmann et al. 2019. |

**Mixedwoods, young stands, and uneven-aged structure.** The current tabular model has no small-tree class below 2.5 cm and no species-specific competition. FVS-BC is also an even-aged variant; the KC pilot stand is uneven-aged, which the pilot explicitly does not validate. The new model should:
- Include a small-tree hazard for `0.5 ≤ DBH < 10 cm`, with species-specific shade tolerance and size terms.
- Use species-specific BAL (or at least conifer/broadleaf groups) so that a hemlock suppressed by cedar differs from a pine suppressed by pine (MGM's lesson).
- Include a `CR` term where available; if CR is missing, use a species-specific proxy from DBH/height/BA and flag it.
- Include a "release" term for stands that have recently dropped below a density threshold; otherwise the model cannot represent the post-thinning response.

#### 6.2.3 Two-component hazard (v2, only if justified)

```
# Background: senescence, site, climate
η_bg = b0[sp] + b_dbh·log(dbh) + b_dbh2·log(dbh)^2
     + b_si·(SI − SI_ref)/10
     + b_cmi·(CMI − CMI_ref)
     + b_dd·(DD5 − DD5_ref)/100
     + u_bec + u_site
p_bg = 1 − exp(−exp(η_bg))

# Stress: density, relative size, growth, crown
η_st = c0[sp] + c_bal·BAL/10 + c_ba·BA/10 + c_rel·relDBH
     + c_gr·log(growth_ratio + 0.01) + c_cr·(CR − CR_ref)
p_st = 1 − exp(−exp(η_st))

p_ann = 1 − (1 − p_bg)·(1 − p_st)
```

This is a competing-risk form (background vs. stress) in the spirit of iLand, PICUS and 4C. It lets the background be calibrated on old-growth/PSP and the stress component on density/growth, and it gives a natural way to add climate to the background without letting a free year term absorb everything. **Do not start here.** Fit the single cloglog first; adopt the two-component form only if the single form fails the holdout in a structured way (e.g., old-growth mortality too low, density response too weak).

#### 6.2.4 Stochasticity

FVS tree records represent many trees (`PROB` = trees/acre). A Bernoulli draw per record is wrong. Use one of:

```
expected = PROB · (1 − (1 − p_ann)^FINT)
if stochastic:
    # stochastic rounding preserves the expectation
    dead = floor(expected) + Bernoulli(frac(expected))
    # or, if PROB is an integer count:
    dead ~ Binomial(PROB, 1 − (1 − p_ann)^FINT)
else:
    dead = expected
WK2(I) = min(dead, PROB)
```

Use **common random numbers**: seed the RNG by `(stand_id, tree_id, cycle)` so scenario comparisons share draws and Monte Carlo noise cancels. Report both the deterministic expected value (operational default) and the stochastic distribution (uncertainty). Do not use stochasticity to hide bias; it is a variance model, not a calibration fix.

#### 6.2.5 Calibration

- **Data:** tree-level remeasurement rows with species, DBH, height, crown ratio (if available), status (live/dead), interval length, plot ID, BEC, site series, SI, BA/BAL, climate. The project has ~1.03M tree-survival rows and 9,186 intervals in the seven supported zones.
- **Likelihood:** cloglog GLM/GLMM with `log(Δt)` offset; species-specific fixed effects; random intercepts for BEC/site/TSA; Bayesian or penalized ML.
- **Priors/penalties:** standardize covariates; `Normal(0, 1)` on fixed effects; `HalfNormal(1)` on random-effect SDs; regularize species effects toward a species-trait mean (shade tolerance, drought tolerance, max age, wood density) to borrow strength for minor species.
- **Model comparison:** AIC/BIC, cross-validated log loss and Brier, calibration slope/intercept, AUC; PSIS-LOO/WAIC for Bayesian fits.
- **Identifiability:** profile likelihood or posterior intervals; check the correlation between BA and BAL, between SI and BEC, and between climate and year; do not include both a free year term and a climate term.
- **Calibration vs. overfitting:** pre-register covariates; limit parameters per domain; use leave-one-TSA-out, leave-one-BEC-out, temporal holdout, and site-grouped 5-fold; no parameter at a bound; report the full uncertainty.

### 6.3 Ingress core function (`BCINGR`)

#### 6.3.1 Model form

**Two-part hurdle (a zero-inflated count model; the ZINB is the alternative single-equation form), with an explicit seed-rain index.**

For species `sp` in stand `s`, interval `Δt`:

**(1) Seed rain from the tree list (stand-level approximation to a seed-shadow model).**

```
S_sp = ( Σ_j fec_sp(dbh_j) · crown_area_j · w_disp_sp ) / A_ha
     + S_ext_sp
```

- `fec_sp(dbh)` = 0 below a species-specific maturity DBH; rises to a plateau (e.g., `fec0 · (dbh/maturity_dbh)^γ`).
- `crown_area_j` from the FVS crown-width model.
- `w_disp_sp` = a stand-level dispersal/viability weight (the fraction of seed that reaches a receptive microsite within the stand); for a distance-independent model this is the integral of the dispersal kernel over the stand, not a per-tree distance.
- `S_ext_sp` = external seed rain (seed bank, edge, regional source); allows a species with no local parent to establish, but at a lower rate.
- For serotinous species (PL), add a post-fire seed-release pulse.
- For suckering species (AT, AC), add a root/stump sprout term (keep `ESUCKR`).

**(2) Presence / zero process.**

```
η_pi = a0[sp] + a1[sp]·log1p(S_sp) + a2[sp]·(BA/10)
     + a3[sp]·(BA_sp/10) + a4[sp]·(SI − SI_ref)/10
     + a5[sp]·(CMI − CMI_ref) + a6[sp]·light
     + u_bec[BEC]
π_sp = logistic(η_pi)
```

**(3) Count process (negative binomial).**

```
η_mu = b0[sp] + b1[sp]·log1p(S_sp) + b2[sp]·(BA/10)
     + b3[sp]·(BA_sp/10) + b4[sp]·(SI − SI_ref)/10
     + b5[sp]·(CMI − CMI_ref) + b6[sp]·light
     + log(Δt) + log(A_ha)
μ_sp = exp(η_mu)
N_sp ~ NB(μ_sp, α_sp)      # Var = μ + α·μ²
```

**(4) Hurdle draw.**

```
if U(0,1) < π_sp:
    N_sp = NB(μ_sp, α_sp)
else:
    N_sp = 0
```

**(5) Establishment filter and timing.**

```
N_sp = N_sp · g_est(sp, light, substrate, browse)
```

`g_est` is a species-specific establishment suitability (0–1), driven by light/canopy openness, seedbed substrate (BEC site series proxy), and browse. In the distance-independent case, `light` can be a function of BA and canopy composition; in a spatial mode, use canopy openness. Recruits enter at a defined threshold: `H = 1.3 m`, `DBH = 0.5–1.0 cm`, `ABIRTH = 5`, at the end of the cycle (or split across the cycle to avoid a pulse).

**Species composition.** Draw the species of each recruit from a multinomial with probabilities proportional to `π_sp · μ_sp` (expected recruitment by species). This makes composition respond to seed source, overstory and site, rather than a fixed ratio.

#### 6.3.2 Why this form

- **Zero-inflation is real.** 4% of observed samples have zero recruitment (Díaz-Yáñez et al. 2024); the ZINB literature shows extra-zero probabilities of 0.21–0.68 and overdispersion α 2.28–3.19 (Lappi & Pukkala 2020). A Poisson or normal model cannot represent this.
- **Parent-tree dependence is real.** SORTIE/BC's recruitment is a function of parent-tree proximity, size and abundance plus seedbed (Coates et al. 2003); iLand and FORMIND use fecundity + dispersal. A flat BEC × species rate cannot respond to partial cutting or mortality.
- **A stand-level seed index is the right compromise for DI FVS.** FVS has no x/y coordinates, so a full kernel is impossible; but the tree list has species, DBH and crown width, so a stand-level seed-rain integral is computable. This preserves the response to composition/size structure without a spatial grid.
- **A hurdle is simpler than a full ZINB and easier to explain.** The two parts have separate interpretations (does recruitment occur? how much?), which is useful for diagnostics and for the "all-or-none" nature of regeneration (Robinson 2008). BWINPro uses exactly this structure.
- **Climate/soil effects are species-specific and should be added last.** Flury et al. (2024) show soil- and climate-dependent ingrowth; Lappi & Pukkala (2020) show temperature-sum effects. But the Díaz-Yáñez et al. (2024) result warns that added complexity does not guarantee accuracy. Add climate only after the seed-source + overstory model is validated.

#### 6.3.3 Data requirements and the hard part

- **Recruitment counts by species** at a defined size threshold, plot area, interval, overstory composition/BA, BEC, SI, climate, disturbance. The project's `d7-all-recruitment.csv` has `new_total` and species breakdown; the PSP archive may not measure seedlings below the tally threshold. This is the main data risk.
- **Observation model:** if small trees are only detected above a threshold, the "zero" is a detection zero, not a biological zero. Use a threshold/detection model or restrict the response to the tally threshold; do not treat unobserved seedlings as absent.
- **Augmentation:** use independent regeneration plots (BC YSM/SEP, Date Creek, SORTIE/BC parameter data) to anchor the seed-source and establishment relationships; use the PSP for the overstory/climate response.
- **Sample size:** the FVS establishment model needed 12,128 plots in 537 stands for 10 species. BC PSP has 4,430 sites in seven zones, which is enough for a hierarchical model with species groups, but not for a separate model per species × BEC. Partial pooling is essential.

### 6.4 Architecture: where the functions live and how to keep FVS compatible

#### 6.4.1 Code placement

| Component | Placement | Compatibility |
| --- | --- | --- |
| Mortality | Replace the body of `MORTS`; add `BCMORT` module; keep `MORCON` entry | All existing keywords (`MORTMULT`, `FIXMORT`, `SIZCAP`) still work; new bundle is opt-in. |
| Ingress | New `BCINGR` called from `GRINCR` (after mortality) or `ESTAB`; keep `ESTAB` for `PLANT`/`NATURAL` | `PLANT`/`NATURAL` unchanged; add `INGROW` on/off and `NATURAL` auto mode. |
| Parameters | External bundle (JSON/SQLite/NetCDF) loaded at `MORCON`/`ESINIT` | No recompile for calibration; bundle version/checksum recorded. |
| Prototype | ES1/ES2 external model via `AddTrees` (Robinson 2008) | Develop/test the ingress model in R/Python before porting to Fortran. |
| Diagnostics | New SQLite tables `FVS_MortalityDiag`, `FVS_IngrowthDiag` | Per-tree p, expected dead, seed rain, π, μ, N, applied value, flags. |
| Domain guard | New `BCDOMAIN` check at initialization and each cycle | Flag/refuse out-of-domain BEC/SI/CMI; no silent fallback. |

#### 6.4.2 Parameter bundle schema

```
{
  "model_id": "bc-mort-hcloglog",
  "version": "1.0.0",
  "domain": {"bec_zones": [...], "si_range": [..], "cmi_range": [..]},
  "species": ["PW","LW","FD",...],
  "fixed_effects": {"intercept": ..., "logdbh": ..., "bal": ..., ...},
  "species_effects": {"FD": {...}, "PL": {...}, ...},
  "random_effects": {"bec": {"sd": ..., "values": {...}}, "site": {"sd": ...}},
  "covariance": [...],
  "refs": {"si_ref": ..., "cmi_ref": ..., "dd5_ref": ...},
  "checksum": "..."
}
```

The ingress bundle has the same structure plus `fecundity`, `maturity_dbh`, `dispersal_weight`, `alpha`, `presence_coefficients`, `count_coefficients`.

#### 6.4.3 Guardrails

- **Domain:** if BEC/SI/CMI is outside the calibration envelope, use the hierarchical prior mean and set `OUT_OF_DOMAIN=1`; the wrapper refuses or flags the run. This is the project's "no plausible-wrong-number" rule.
- **Monotonicity:** assert that `p` increases with BAL/BA and decreases with growth/SI within the calibration range; if a fitted coefficient violates the expected sign, treat it as a failure signal, not a result.
- **Bounds:** `0 ≤ p_ann ≤ 0.99`; `N ≥ 0`; `PROB ≥ 0`; no NaN/Inf.
- **Conservation:** `Σ dead ≤ Σ PROB`; `Σ recruits ≤ MAXTRE`; no negative `PROB`.
- **Reproducibility:** bundle checksum, RNG seed, FVS/PyFVS pin, input checksum.
- **Override logging:** `MORTMULT`/`FIXMORT`/`SIZCAP`/`BAIMULT` are logged as overrides, not calibration parameters.

#### 6.4.4 Why this is better than the current architecture

- Adding a BEC zone becomes a matter of adding plots/priors, not a new compiled table.
- The five data-poor zones can be represented with partial pooling and wider uncertainty, instead of a wrong ICH/IDF table or a blanket no-go.
- Calibration artifacts are versioned data, not source-code edits; this is essential for the project's bundle/reproducibility contract.
- Diagnostics make the model auditable: you can see whether a BA error comes from mortality or ingress.

### 6.5 Calibration and validation design

#### 6.5.1 Data

| Process | Response | Covariates | Minimum data |
| --- | --- | --- | --- |
| Mortality | Live/dead at remeasurement | Species, DBH, H, CR, DG, BAL, BA, QMD, SI, BEC, site series, climate, disturbance | Tree-level survival rows with interval length; ~1M rows in seven zones (project). |
| Ingress | New stems crossing threshold, by species | Species, count, plot area, interval, overstory BA/composition, SI, BEC, climate, disturbance | Plot-level recruitment counts; the project's `d7-all-recruitment.csv`; augment with regeneration plots. |

Two data-handling rules are non-negotiable:

1. **Missing is not dead.** A tree absent from a remeasurement is not a mortality observation unless it is confirmed dead. Treating absence as death biases mortality upward and ingress downward. Use the PSP status field; keep "missing" as a separate category or censor it.
2. **Disturbance is not background.** The project has 54,269 damage-coded rows. Use them to flag insect, disease, fire and wind events; fit the base hazard on the non-disturbance subset and enter disturbance as a separate term. Otherwise the climate/competition coefficients absorb disturbance and will not transfer.

The interval length enters as a `log(Δt)` offset in the mortality model and as `log(Δt) + log(A_ha)` offsets in the ingress model; plot area must be the actual measured area, not a nominal expansion factor.

#### 6.5.2 Fitting sequence

1. **Mortality v1:** cloglog with DBH, BAL, BA, species; BEC random intercept. No climate, no CR, no growth. This is the "safe" model; it should already beat the table.
2. **Mortality v2:** add growth, CR, SI, climate; optional two-component hazard. Ablate each addition.
3. **Ingress v1:** hurdle/ZINB with seed rain, BA, BA_sp, species, BEC; no climate.
4. **Ingress v2:** add climate, disturbance pulses, advance regeneration, serotiny/suckering.
5. **Joint:** simulate PSP intervals with the fitted mortality + ingress; compute BA/TPH/QMD/top-height trajectories; build a residual atlas by BEC/TSA/species/size/density; iterate only if a structural error is identified (not by tuning multipliers).

#### 6.5.3 Metrics and gates

| Metric | Target / gate |
| --- | --- |
| Mortality log loss / Brier | ≤ current pilot (0.485 / 0.122) on held-out sites; lower is better. |
| Calibration slope / intercept | Slope 0.8–1.2; intercept not significantly different from 0. |
| Mortality discrimination (AUC) | Report; do not optimize alone (class imbalance). |
| Stand BA bias | Within ±3 m²/ha or 10% of observed, whichever is larger. |
| TPH bias | Within 15%. |
| Mortality slope (observed vs predicted) | 0.8–1.2. |
| Envelope exceedance | Zero predictions above the observed maximum; report p99. |
| Recruitment zero frequency | Within ±5 percentage points of observed. |
| Recruitment marginal distribution | Chi-square/p-value not rejected; report mean, variance, zeros. |
| Species composition | Bray–Curtis dissimilarity no worse than the flat-rate baseline. |
| Parameter at bound | Zero; a bound is a failure signal. |
| Temporal holdout | No worse than random CV by more than a pre-registered margin. |
| Out-of-domain runs | Flagged or refused; no silent fallback. |

#### 6.5.4 Holdouts

- Leave-one-TSA-out (the pilot already shows why).
- Leave-one-BEC-variant-out.
- Temporal holdout: train early, test late; train late, test early (if data allow).
- Site-grouped 5-fold.
- Species holdout for species with sufficient support.
- No site in both training and test.

#### 6.5.5 Avoiding overfitting

- **Pre-register** covariates, functional forms, and thresholds before fitting (the project's W1.6 design already does this).
- **Limit parameters** per domain; prefer 8–14 fixed effects plus a small number of random-effect SDs.
- **Partial pooling** across BEC/site/species; do not fit separate models per BEC variant.
- **Regularizing priors**; species effects shrunk to trait-based means.
- **Ablation:** each added covariate must improve the pre-registered holdout; otherwise drop it.
- **No free year term.** Use climate covariates; validate temporally. The pilot's year term over-corrected.
- **Marginal prediction check.** Lappi & Pukkala (2020) found mixed-effects ingrowth models had better likelihood but biased marginal predictions. Report both conditional and marginal predictions; prefer fixed effects for operational projection if the marginal is biased.
- **Uncertainty:** report posterior/CI intervals; do not present a point estimate as a certificate.
- **Model comparison:** AIC/BIC, CV log loss/Brier, PSIS-LOO/WAIC; not R² alone.

---

## 7. Pseudocode

### 7.1 Mortality (`BCMORT` / `MORTS` replacement)

```text
SUBROUTINE BCMORT
  ! Called from MORTS after growth; all arrays are FVS standard.
  ! bundle = MORT_BUNDLE loaded in MORCON; if absent, call LEGACY_MORTS and return.

  BA   = total stand basal area (m2/ha)
  QMD  = quadratic mean diameter (cm)
  SI   = site index for the plot (m @ 50 yr BH age) or BEC proxy
  CMI  = climatic moisture deficit for the interval
  DD5  = degree days > 5 C for the interval

  DO ispc = 1, MAXSP
    DO i = first tree of species, last tree of species
      d    = max(DBH(i), 0.5)
      bal  = BAL(i)                      ! basal area of trees larger than i
      rel  = d / max(QMD, 1.0)
      gr   = DG(i) / max(DBH(i), 0.5)    ! recent relative growth
      cr   = crown_ratio(i)              ! if missing, species proxy

      ! standardize
      z_dbh = (log(d) - mu_logdbh) / sd_logdbh
      z_bal = (bal/10 - mu_bal) / sd_bal
      z_ba  = (BA/10  - mu_ba ) / sd_ba
      z_rel = (rel    - mu_rel) / sd_rel
      z_gr  = (gr     - mu_gr ) / sd_gr
      z_cr  = (cr     - mu_cr ) / sd_cr
      z_si  = (SI     - si_ref) / 10
      z_cmi = (CMI    - cmi_ref)
      z_dd  = (DD5    - dd5_ref) / 100

      ! v1: single cloglog
      eta = b0 + b_sp(ispc) + b_logdbh*z_dbh + b_logdbh2*z_dbh**2
          + b_bal*z_bal + b_ba*z_ba + b_ba2*z_ba**2 + b_rel*z_rel
          + b_gr*z_gr + b_cr*z_cr + b_si*z_si + b_cmi*z_cmi + b_dd*z_dd
          + u_bec(BEC) + u_site(SITE_ID)

      eta = clamp(eta, -20, 20)
      p_ann = 1.0 - exp(-exp(eta))
      p_ann = clamp(p_ann, 0.0, 0.99)
      p_int = 1.0 - (1.0 - p_ann)**FINT

      ! stochastic thinning (optional; preserves expectation)
      expected = PROB(i) * p_int
      if (STOCHASTIC) then
        dead = floor(expected) + bernoulli(frac(expected), rng(i,icycle))
      else
        dead = expected
      end if
      WK2(i) = min(dead, PROB(i))

      ! diagnostics
      write MORTDIAG(tree=i, ispc=ispc, p_ann=p_ann, p_int=p_int,
                     expected=expected, dead=WK2(i), eta=eta,
                     bal=bal, ba=BA, si=SI, cmi=CMI, flag=domain_flag)
    END DO
  END DO

  ! preserve legacy overrides
  CALL APPLY_FIXMORT
  CALL APPLY_SIZCAP
  CALL APPLY_XMMULT
END SUBROUTINE
```

### 7.2 Ingress (`BCINGR`)

```text
SUBROUTINE BCINGR(dt)
  ! Called at the end of the growth cycle, after mortality.
  ! Adds new tree records at the 1.3 m / 0.5-1.0 cm threshold.

  BA    = total stand basal area (m2/ha)
  BA_sp = species-specific basal area (m2/ha)
  SI    = site index or BEC proxy
  CMI   = climatic moisture deficit
  light = light proxy: exp(-k * BA/10) or canopy openness if available

  DO ispc = 1, MAXSP
    S = 0.0
    DO j = 1, ITRN
      if (ISP(j) == ispc .and. DBH(j) >= maturity_dbh(ispc)) then
        fec  = fec0(ispc) * (DBH(j)/maturity_dbh(ispc))**fec_exp(ispc)
        S    = S + fec * crown_area(j)
      end if
    END DO
    S = S / A_ha * dispersal_weight(ispc) + external_seed(ispc)

    ! presence
    eta_pi = a0(ispc) + a1(ispc)*log1p(S) + a2(ispc)*(BA/10)
           + a3(ispc)*(BA_sp/10) + a4(ispc)*(SI-si_ref)/10
           + a5(ispc)*(CMI-cmi_ref) + a6(ispc)*light
           + u_bec_ing(BEC)
    pi = logistic(eta_pi)

    ! count
    eta_mu = b0(ispc) + b1(ispc)*log1p(S) + b2(ispc)*(BA/10)
           + b3(ispc)*(BA_sp/10) + b4(ispc)*(SI-si_ref)/10
           + b5(ispc)*(CMI-cmi_ref) + b6(ispc)*light
           + log(dt) + log(A_ha)
    mu = exp(eta_mu)

    if (bernoulli(pi, rng_ing(ispc, icycle))) then
      N = negative_binomial(mu, alpha(ispc), rng_ing(ispc, icycle))
      N = N * g_est(ispc, light, substrate, browse)
    else
      N = 0
    end if

    ! convert to FVS tree records
    DO k = 1, N
      ITRN = ITRN + 1
      ISP(ITRN)  = ispc
      PROB(ITRN) = 1.0 / ACRtoHA          ! 1 tree/ha -> trees/acre
      DBH(ITRN)  = 0.5 + uniform(0, 0.5)
      HT(ITRN)   = 1.3 + uniform(0, 0.5)
      ABIRTH(ITRN) = 5.0
      ITRE(ITRN) = plot_index
      IESTAT(ITRN) = 0
      ! initialize crown, DG, etc. via existing REGENT / CWCALC calls
    END DO

    write INGRDIAG(ispc=ispc, S=S, pi=pi, mu=mu, N=N, BA=BA,
                   BA_sp=BA_sp, SI=SI, CMI=CMI, flag=domain_flag)
  END DO
END SUBROUTINE
```

### 7.3 Calibration loop (R/Python, outside Fortran)

```text
for domain in preregistered_domains:
    train, test = holdout(domain)          # TSA / BEC / temporal / site-grouped
    mort = fit_cloglog(train.survival,
                       y = dead,
                       x = [logdbh, logdbh^2, bal, ba, ba^2, rel, gr, cr, si, cmi],
                       offset = log(years),
                       random = [bec, site],
                       priors = regularizing)
    ingr = fit_hurdle_nb(train.recruitment,
                         y = new_stems,
                         x = [log1p(S), ba, ba_sp, si, cmi, light],
                         offset = log(area) + log(years),
                         random = [bec, site])
    pred = simulate(mort, ingr, test.initial_state, test.years)
    report(bias, rmse, slope, intercept, log_loss, brier,
           zero_frequency, marginal_counts, composition,
           envelope_exceedance, parameter_at_bound)
    if not pass(gates): revise_structure()   # not multiplier tuning
```

---

## 8. Phased implementation and validation plan

| Phase | Scope | Deliverable | Gate / evidence | Est. |
| --- | --- | --- | --- | --- |
| **0. Freeze and pre-register** | Freeze PSP snapshot, pins, checksums; confirm 12 domains; pre-register metrics/thresholds | Data manifest; pre-registration note | Independent biometric sign-off; no result-dependent changes | 1–2 wk |
| **1. Mortality v1** | Cloglog with DBH, BAL, BA, species; BEC random intercept; no climate/CR/growth | `bc-mort-hcloglog` v1 bundle; diagnostics table | CV log loss ≤ 0.485; TSA holdout bias reduced vs current; no parameter at bound | 3–4 wk |
| **2. Mortality v2** | Add growth, CR, SI, climate; optional two-component hazard; stochastic mode | v2 bundle; ablation table | Temporal holdout improves; calibration slope 0.8–1.2; BA bias within ±3 m²/ha or 10% | 4–6 wk |
| **3. Ingress v1** | Hurdle/ZINB with stand-level seed rain, BA, BA_sp, species, BEC; no climate | `bc-ingr-hurdle` v1 bundle | Zero frequency within ±5 pp; mean recruitment within 15%; marginal distribution not rejected | 4–6 wk |
| **4. Ingress v2** | Climate, disturbance pulses, advance regeneration, serotiny/suckering | v2 bundle | Temporal/TSA holdout improves; composition no worse than flat-rate baseline | 4–6 wk |
| **5. Joint calibration and validation** | Simulate PSP intervals; residual atlas; joint metrics; independent holdout | Validation report; certificates per domain | BA/TPH bias gates; mortality slope 0.8–1.2; zero envelope exceedance; no site in train/test | 4–6 wk |
| **6. Release** | Bundle selection by BEC/domain; provenance; envelope validator; docs | Pinned release; claim boundary | Reproducible from checksums/pins; out-of-domain runs flagged/refused | 2–4 wk |

**Sequencing rationale.** Mortality v1 is first because tree-level survival is directly observed and not confounded by ingress. Ingress v1 is next because it is the missing process; fitting it before mortality v2 prevents the mortality model from absorbing missing recruitment. Joint calibration is last because it is a check, not a fitting shortcut.

---

## 9. Strongest evidence for each recommendation

| Recommendation | Strongest evidence |
| --- | --- |
| Replace the tabular/BA-cap mortality with a covariate survival model | Hülsmann et al. (2017): growth/competition covariates and regional calibration improve prediction across 46 models and ~80k records. Project pilot: continuous species-BA model beats 23-parameter species × BA-class model by 196 AIC and 0.0025 CV log loss. |
| Add growth and crown ratio | Hülsmann et al. (2017): growth variables are the key discriminator between dead and living trees. SORTIE/Kobe–Coates: juvenile survival is a function of recent radial growth. MOSES and Organon: crown ratio is a core predictor. |
| Add site index | SILVA: SI is in the survival logit. Hülsmann et al. (2017): regional/ecological context matters. FVS-BC code audit: no SI in the tabular/LMRT mortality structure; only the legacy path has a site-potential multiplier. |
| Add BEC/site random effects (partial pooling) | Project TSA holdout: 100 Mile House over-predicted 0.0201 vs 0.0148. Hülsmann et al. (2017): regional models outperform transferred models. Bugmann et al. (2019): spatial variability must be addressed explicitly. |
| Add climate, but guard it | Bugmann et al. (2019): mortality submodels diverge 10–40%/century under current climate and 20–170% under climate change. Project temporal holdout: naive year term over-predicts 1.6–5×. Canham & Murphy (2017): climate effects on survival are species-specific. |
| Make mortality stochastic (optional) | Pacala et al. (1996): SORTIE mortality and recruitment are stochastic. MOSES: random draw. FORMIND: stochastic background. But stochasticity is a variance model, not a bias fix; default to expected value for operations. |
| Use a hurdle/ZINB ingress model | Lappi & Pukkala (2020): ZINB, extra-zero probability 0.21–0.68, α 2.28–3.19. Li et al. (2011), Zhang et al. (2012), Zell et al. (2019). Díaz-Yáñez et al. (2024): 4% observed zeros; most models produce too few. |
| Make ingress parent-tree/seed-source dependent | SORTIE/BC (Coates et al. 2003): recruitment from parent-tree proximity, size, abundance and seedbed. iLand: fecundity + dispersal + establishment. FORMIND: mother trees/external seed rain. A constant BEC × species rate cannot respond to partial cutting or mortality. |
| Use a stand-level seed-rain index for DI FVS | FVS has no x/y coordinates; the tree list has species, DBH and crown width. A stand-level fecundity × crown-area integral preserves composition/size response without a spatial grid. BWINPro's `pE`/`nE` hurdle is the simplest precedent. |
| Keep FVS compatible via bundles and entry points | Robinson (2008): FVS can host external regeneration models via ES1/ES2 and `AddTrees`. The `MORTS`/`ESTAB` entry points and existing keywords can be preserved. The project's bundle/provenance contract already requires versioned data. |
| Avoid per-BEC models and free year terms | Bugmann et al. (2019): overfitting to short-term data is a major problem. Lappi & Pukkala (2020): mixed models can have better likelihood but biased marginal predictions. Project temporal holdout: year term fails. Pre-registration and partial pooling are the safeguards. |
| Add diagnostics | The current FVS-BC has no per-tree mortality or per-species recruitment output; calibration must infer from aggregate BA/TPH. Diagnostics are required to separate mortality from ingress error. |

---

## 10. Risks, unverified claims, and what would change the design

### 10.1 Risks

1. **PSP recruitment data may be too sparse or detection-limited.** Seedlings below the tally threshold are not observed; "zero" may be a detection zero. Mitigation: restrict the response to the tally threshold; model detection; augment with independent regeneration plots; treat the smallest size class as latent.
2. **Climate extrapolation.** Future climate may be outside the calibration envelope; a fitted climate coefficient can extrapolate badly. Mitigation: clamp, flag, report; use hierarchical climate coefficients; do not claim no-analog prediction.
3. **Identifiability of mortality vs. ingress.** Both affect BA/TPH. Mitigation: fit mortality on tree-level survival first, ingress on recruitment counts, then joint check; profile likelihood; do not tune multipliers.
4. **Overfitting across many BEC × species cells.** Mitigation: partial pooling, regularizing priors, pre-registration, leave-one-BEC-out, temporal holdout.
5. **Fortran integration risk.** Mitigation: keep entry points, load bundles externally, prototype via ES1/ES2, add regression tests against the legacy path.
6. **Data-poor zones.** CWH, CDF, BWBS, MH, CMA lack species/model tables. Mitigation: hierarchical borrowing across zones/species; report wider uncertainty; do not claim a calibrated domain without independent validation.

### 10.2 Unverified claims

- **SILVA natural regeneration**: v2.2 had regeneration submodels under development; the exact seed/dispersal/establishment form is `[UNVERIFIED]`. Do not use SILVA as an ingress donor.
- **BWINPro mortality**: the modern TreeGrOSS implementation uses maximum density + crown closure; earlier BWINPro versions may use a logistic form. The exact original equation is `[UNVERIFIED]`.
- **MOSES regeneration**: a regeneration model exists in the framework, but the reviewed implementation treats it largely as an input layer. Exact equations `[UNVERIFIED]`.
- **PICUS regeneration**: retained from Lexer & Hönninger (2001); the exact equation was not read directly. `[UNVERIFIED]`.
- **TASS mortality**: proprietary/undocumented; the BC review describes light-driven mortality but not the equation. `[UNVERIFIED]`.
- **MGM mortality/ingress**: described in the BC review at a high level; exact equations `[UNVERIFIED]`.
- **Species-specific ingress for all 15 BC species**: likely only feasible for well-represented species; minor species will need pooling/traits. `[UNVERIFIED]` until the PSP recruitment counts are tabulated.
- **The exact PSP recruitment sample size**: the project has ~1M survival rows, but recruitment counts are a smaller and less certain subset. `[UNVERIFIED]` until audited.

### 10.3 What would change the design

- If the PSP recruitment audit shows too few observations for a species-specific hurdle model, collapse to species groups/PFTs and use traits; do not fit 15 separate models.
- If the temporal holdout shows that climate covariates do not transfer, keep the climate term out of the operational model and provide a scenario-only sensitivity module.
- If the joint check shows that mortality and ingress are not separately identifiable even with tree-level data, use a joint Bayesian model with informative priors and report the posterior correlation; do not pretend the point estimates are independent.
- If the Fortran integration proves too costly, implement the ingress model as an external ES1/ES2 model and keep the FVS core unchanged; this is a legitimate architectural outcome, not a failure.

---

## 11. References

**FVS / BC**

- Stage, A.R. 1973. *Prognosis model for stand development.* USDA Forest Service Research Paper INT-137.
- Wykoff, W.R., Crookston, N.L., Stage, A.R. 1982. *User's guide to the Stand Prognosis Model.* USDA Forest Service General Technical Report INT-133.
- Hamilton, D.A., Edwards, B.M. 1976. *Modeling the probability of individual tree mortality.* USDA Forest Service Research Paper INT-185.
- Crookston, N.L., Dixon, G.E. 2005. The Forest Vegetation Simulator: a review of its structure, content, and applications. *Computers and Electronics in Agriculture* 49:60–80. https://doi.org/10.1016/j.compag.2005.02.003
- Temesgen Hailemariam (UBC Faculty of Forestry), 2001. Mortality model for PrognosisBC. Unpublished report. (Cited in `canada/bc/morts.f`; `[UNVERIFIED]` publication status. The name is a single person, not two authors.)
- Zumrawi, A.A. 2004. Regeneration imputation models for complex stands of southeastern British Columbia. *The Forestry Chronicle* 80:271–278. https://doi.org/10.5558/tfc80271-2
- Robinson, D.C.E. 2008. Development of external regeneration models for FVS: another wrench in the toolkit. In: Havis, R.N., Crookston, N.L. (comps.), *Third Forest Vegetation Simulator Conference*, RMRS-P-54, pp. 225–237. https://research.fs.usda.gov/download/treesearch/30983.pdf
- Ferguson, D.E., Carlson, C.E. 1993. *Predicting regeneration establishment with the Prognosis model.* USDA Forest Service Research Paper INT-467. https://doi.org/10.5962/bhl.title.68938
- Forest Analysis Ltd. 2021. *Growth and Yield Modelling Systems for BC – a Review.* https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/stewardship/forest-analysis-inventory/growth-yield/modelreview_finalreport_march_2021.pdf
- BC Ministry of Forests. TASS page. https://www2.gov.bc.ca/gov/content/industry/forestry/managing-our-forest-resources/forest-inventory/growth-and-yield-modelling/tree-and-stand-simulator-tass

**SILVA**

- Pretzsch, H., Biber, P., Ďurský, J. 2002. The single tree-based stand simulator SILVA: construction, application and evaluation. *Forest Ecology and Management* 162:3–21. https://doi.org/10.1016/S0378-1127(02)00047-6
- Pretzsch, H. 2009. *Forest Dynamics, Growth and Yield.* Springer. (SILVA chapter.)
- Vospernik, S. 2017. Possibilities and limitations of individual-tree growth models – A review on model evaluations. *Die Bodenkultur* 68:103–112. https://doi.org/10.1515/boku-2017-0010

**BWINPro / TreeGrOSS**

- Nagel, J. 1999. *Konzeption und Standortsanalyse des waldbaulichen Entscheidungsmodells BWINPro.* Dissertation, Universität Göttingen.
- Nagel, J., Albert, M., Schmidt, M. 2002. Das waldbauliche Prognose- und Entscheidungsmodell BWINPro 6.1. *Forst und Holz* 57:1–8.
- Nagel, J., Schmidt, M. 2006. The silvicultural decision support system BWINPro. In: Hasenauer, H. (ed.), *Sustainable Forest Management: Growth Models for Europe*, Springer, pp. 59–63. https://doi.org/10.1007/3-540-31304-4_4
- Hansen, J., Nagel, J. 2014. *Waldwachstumskundliche Softwaresysteme auf Basis von TreeGrOSS – Anwendung und theoretische Grundlagen.* Beiträge aus der NW-FVA, Band 11. https://www.nw-fva.de/fileadmin/nwfva/publikationen/pdf/hansen_2014_waldwachstumskundliche.pdf
- Sterba, H. 1981. (Competition–density rule.) As cited in Hansen & Nagel (2014).
- Doebbeler, H. 2004. (Maximum density functions.) As cited in Hansen & Nagel (2014).

**MOSES**

- Hasenauer, H. 1994. *Ein Einzelbaumwachstumsmodell für einen ungleichaltrigen Fichtenbestand.* Dissertation, Universität für Bodenkultur Wien.
- Hasenauer, H., Kindermann, G., Steinmetz, P. 2006. The tree growth model MOSES 3.0. In: Hasenauer, H. (ed.), *Sustainable Forest Management: Growth Models for Europe*, Springer, pp. 64–70.
- Thurnher, C., Klopf, M., Hasenauer, H. 2017. MOSES – A tree growth simulator for modelling stand response in Central Europe. *Ecological Modelling* 352:58–76. https://doi.org/10.1016/j.ecolmodel.2017.01.013

**PICUS**

- Lexer, M.J., Hönninger, K. 2001. A modified 3D-patch model for spatially explicit simulation of vegetation composition in heterogeneous landscapes. *Forest Ecology and Management* 144:43–65. https://doi.org/10.1016/S0378-1127(00)00386-8
- Seidl, R., Rammer, W., Lasch, P., Badeck, F.-W., Lexer, M.J. 2008. Does conversion of even-aged, secondary coniferous forests affect carbon sequestration? A simulation study under changing environmental conditions. *Silva Fennica* 42:369–386. https://silvafennica.fi/pdf/243
- Seidl, R., Rammer, W., Scheller, R.M., Spies, T.A. 2012. An individual-based process model to simulate landscape-scale forest ecosystem dynamics. *Ecological Modelling* 231:87–100. https://doi.org/10.1016/j.ecolmodel.2012.02.015

**SORTIE**

- Pacala, S.W., Canham, C.D., Saponara, J., Silander, J.A., Kobe, R.K., Ribbens, E. 1996. Forest models defined by field measurements: estimation, error analysis and dynamics. *Ecological Monographs* 66:1–43. https://doi.org/10.2307/2963479
- Coates, K.D., Canham, C.D., Beaudet, M., Sachs, D.L., Messier, C. 2003. Use of a spatially explicit individual-tree model (SORTIE/BC) to explore the implications of patchiness in structurally complex forests. *Forest Ecology and Management* 186:297–310. https://doi.org/10.1016/S0378-1127(03)00301-3
- Kobe, R.K., Coates, K.D. 1997. Models of sapling mortality as a function of growth to characterize interspecific variation in shade tolerance of eight tree species of northwestern British Columbia. *Canadian Journal of Forest Research* 27:227–236. https://doi.org/10.1139/x96-182
- Ribbens, E., Silander, J.A., Pacala, S.W. 1994. Seedling recruitment in forests: calibrating models to predict patterns of tree seedling dispersion. *Ecology* 75:1794–1806. https://doi.org/10.2307/1939638

**iLand**

- Seidl, R., Rammer, W., Scheller, R.M., Spies, T.A. 2012. (Above.) https://doi.org/10.1016/j.ecolmodel.2012.02.015
- Rammer, W., Thom, D., Baumann, M., Braziunas, K.H., Dollinger, C., Kerber, J., et al. 2024. The individual-based forest landscape and disturbance model iLand: overview, progress, and outlook. *Ecological Modelling* 495:110785. https://doi.org/10.1016/j.ecolmodel.2024.110785
- iLand model book. https://iland-model.org/downloads/iland-book.pdf
- Thom, D., et al. 2024. Parameters of 150 temperate and boreal tree species and provenances for iLand. https://depts.washington.edu/bjhlab/wordpress/wp-content/uploads/2024/10/Thom_etal_2024_DiB_iLandParameters.pdf

**FORMIND**

- Köhler, P., Huth, A. 1998. The effects of tree species grouping in tropical rainforest modelling: simulations with the individual-based model Formind. *Ecological Modelling* 109:301–321. https://doi.org/10.1016/S0304-3800(98)00066-0
- Köhler, P., Ditzer, T., Ong, R., Huth, A. 2001. Comparison of measured and modelled growth on permanent plots in Sabah's rain forests. *Forest Ecology and Management* 144:101–111. https://doi.org/10.1016/S0378-1127(00)00364-9
- Fischer, R., Bohn, F., Dantas de Paula, M., Dislich, C., Groeneveld, J., Gutiérrez, A.G., et al. 2016. Lessons learned from applying a forest gap model to understand ecosystem and carbon dynamics of complex tropical forests. *Ecological Modelling* 326:124–133. https://doi.org/10.1016/j.ecolmodel.2015.11.018
- Köhler, P., Huth, A. 2007. Impacts of recruitment limitation and canopy disturbance on tropical tree species richness. *Ecological Modelling* 203:511–517. https://doi.org/10.1016/j.ecolmodel.2006.11.023

**TASS / TIPSY**

- Mitchell, K.J. 1975. Dynamics and simulated yield of Douglas-fir. *Forest Science Monograph* 17.
- Di Lucca, C.M. 1999. TASS/SYLVER/TIPSY: systems for predicting the impact of silvicultural practices on yield, lumber value, economic return and other benefits. *Stand Density Management Conference*, Edmonton, Alberta, pp. 7–16.
- Goudie, J.W., Cameron, I.R., Bealle Statland, C., Polsson, K., Parish, R. 2026. Development of the Tree and Stand Simulator (TASS) Version 3.0. Preprint. https://doi.org/10.13140/RG.2.2.25369.68962
- García, O. 2005. TADAM: a dynamic whole-stand approximation for the TASS growth model. *The Forestry Chronicle* 81:575–581. https://doi.org/10.5558/tfc81575-4

**MGM / Organon**

- Mixedwood Growth Model. https://mgm.ualberta.ca/
- Hann, D.W., Marshall, D.D., Hanus, M.L. 2006. *Reanalysis of the SMC-ORGANON equations for diameter-growth rate, height-growth rate, and mortality rate of Douglas-fir.* Forest Research Laboratory, Oregon State University, Research Contribution 49.

**Mortality / regeneration synthesis**

- Bugmann, H., Seidl, R., Hartig, F., Bohn, F., Brůna, J., Cailleret, M., et al. 2019. Tree mortality submodels drive simulated long-term forest dynamics: assessing 15 models from the stand to global scale. *Ecosphere* 10:e02616. https://doi.org/10.1002/ecs2.2616
- Díaz-Yáñez, O., Käber, Y., Anders, T., Bohn, F., Braziunas, K.H., Brůna, J., et al. 2024. Tree regeneration in models of forest dynamics: a key priority for further research. *Ecosphere* 15:e4807. https://doi.org/10.1002/ecs2.4807
- Hülsmann, L., Bugmann, H., Brang, P. 2017. How to predict tree death from inventory data – lessons from a systematic assessment of European tree mortality models. *Canadian Journal of Forest Research* 47:890–900. https://doi.org/10.1139/cjfr-2016-0224
- Monserud, R.A., Sterba, H. 1999. Modeling individual tree mortality for Austrian forest species. *Forest Ecology and Management* 113:109–123. https://doi.org/10.1016/S0378-1127(98)00419-8
- Canham, C.D., Murphy, L. 2017. The demography of tree species response to climate: sapling and canopy tree survival. *Ecosphere* 8:e01701. https://doi.org/10.1002/ecs2.1701
- Lappi, J., Pukkala, T. 2020. Analyzing ingrowth using zero-inflated negative binomial models. *Silva Fennica* 54:10370. https://doi.org/10.14214/sf.10370
- Li, R., Weiskittel, A.R., Kershaw, J.A. 2011. Modeling annualized occurrence, frequency, and composition of ingrowth using mixed-effects zero-inflated models and permanent plots in the Acadian Forest Region of North America. *Canadian Journal of Forest Research* 41:2077–2089. https://doi.org/10.1139/x11-117
- Zhang, X., Lei, Y., Cai, D., Liu, F. 2012. Predicting tree recruitment with negative binomial mixture models. *Forest Ecology and Management* 270:209–215. https://doi.org/10.1016/j.foreco.2012.01.028
- Zell, J., Rohner, B., Thürig, E., Stadelmann, G. 2019. Modeling ingrowth for empirical forest prediction systems. *Forest Ecology and Management* 433:771–779. https://doi.org/10.1016/j.foreco.2018.11.052
- Flury, R., Portier, J., Rohner, B., Baltensweiler, A., Di Bella Meusburger, K., Scherrer, D. 2024. Soil and climate-dependent ingrowth inference: broadleaves on their slow way to conquer Swiss forests. *Ecography* 2024:e07174. https://doi.org/10.1111/ecog.07174
- Vanclay, J.K. 1994. *Modelling Forest Growth and Yield: Applications to Mixed Tropical Forests.* CABI.
- Weiskittel, A.R., Hann, D.W., Kershaw, J.A., Vanclay, J.K. 2011. *Forest Growth and Yield Modeling.* Wiley.
- Herbert, C., Fried, J.S., Butsic, V. 2023. Validation of Forest Vegetation Simulator model finds overprediction of carbon growth in California. *Forests* 14:604. https://doi.org/10.3390/f14030604

**Project evidence (internal, not published)**

- `canada/bc/morts.f`, `estab.f`, `BCPLOT.F77`, `PRGPRM.F77`, `blkdat.f` in `.opencode/tmp/opencode/fvs-src/`.
- `mort-calib/validation/model_comparison.csv`, `validation.json`, `temporal/temporal_validation.json`, `temporal_era/temporal_year_term.csv`.
- `d7-all-recruitment.csv`; `fresh_fvsbc/ingrowth.py`.

---

## Appendix A. Quick mapping from evidence to FVS code

| Evidence / design element | FVS code touch point |
| --- | --- |
| Mortality hazard | `MORTS` (replace body), `MORCON` (load bundle), `BCPLOT.F77` (`MORT%` structure) |
| Species effects | `PRGPRM.F77`, `blkspp`, `ISP()` |
| BEC/site effects | `BEC%` in `BCPLOT.F77`, `becset.f`, `HABTYP` |
| BA/BAL/QMD | `BA`, `WK1`, `PCT`, `IND1`, `ISCT` in `ARRAYS.F77` |
| Growth term | `DG` after `DGDRIV`/`GRINCR` |
| Stochastic thinning | `WK2`/`PROB` in `ARRAYS.F77` |
| Ingress | `ESTAB`, `ESINIT`, `REGNBK`, `NATURAL`/`PLANT` keyword processing |
| Seed rain | tree list `DBH`, `ISP`, crown width from `CWCALC`; stand area from `PLOT.F77` |
| Diagnostics | SQLite output layer; new `MORTDIAG`/`INGRDIAG` tables |
| Domain guard | `BEC%`, `SITE`, climate bundle; wrapper `fresh_fvsbc` |
| External prototype | ES1/ES2, `AddTrees` (Robinson 2008) |

## Appendix B. One-page decision summary

- **Keep:** FVS keyword interface, `MORTS`/`ESTAB` entry points, existing multipliers as overrides, FVS tree-list semantics, the project's bundle/provenance contract.
- **Replace:** the ICH/IDF mortality table and BA-cap logic with `BCMORT`; the flat BEC × species ingress table with `BCINGR`.
- **Add:** growth, crown ratio, SI, climate (guarded), BEC/site random effects, stochastic mode, seed-rain index, hurdle/ZINB ingress, diagnostics, domain guard.
- **Do not:** fit per-BEC models; add a free year multiplier; use stochasticity to hide bias; claim a calibrated domain without independent validation; treat published model parameters as BC parameters.
- **First three deliverables:** (1) `bc-mort-hcloglog` v1 with BEC random intercept; (2) `bc-ingr-hurdle` v1 with stand-level seed rain; (3) a joint residual atlas on PSP intervals. These three alone would replace the weakest parts of FVS-BC without a code fork.
