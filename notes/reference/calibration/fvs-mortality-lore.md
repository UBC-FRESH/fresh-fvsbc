# FVS/Prognosis mortality and regeneration/ingrowth logic: an evidence review for FVS-BC calibration to BC PSP data

**Prepared for:** FVS-BC calibration project (work package 2)
**Date:** 2026-11-07
**Status:** scratch literature review. No tracked project files were modified.

**Scope.** The FVS/Prognosis family, including Northern Idaho/Inland Empire (NI/IE), other FVS variants, and PrognosisBC/FVS-BC. Mortality (background, density-dependent, species/size effects, calibration, validation against remeasurement data, mixedwoods, young stands, dry/high-elevation stands, disturbance) and regeneration/ingress (RegEst, ESTAB/NATURAL/PLANT, natural regeneration, seed source/dispersal, establishment, small-tree ingress).

**Evidence key**

| Tag | Meaning |
|---|---|
| **[PR]** | Peer-reviewed journal article (or peer-reviewed monograph) |
| **[CONF]** | Conference proceedings paper or extended abstract; editorially reviewed, not necessarily peer-reviewed |
| **[AGY]** | Agency, university, or government report (grey literature) |
| **[THESIS]** | Graduate thesis |
| **[CODE]** | Direct inspection of FVS-BC source code in the local tree (`.../fvs-src/canada/bc`) |

**Verification convention.** Each entry states whether I read the full text, only the abstract/metadata, or only a secondary citation. Citations marked "secondary" were not independently retrieved; they should be checked before use in a formal bibliography. No citation below is invented.

---

## 0. Bottom line

1. **Mortality is a genuine weak spot, but not because the equations are uniformly wrong.** The base FVS/Prognosis mortality model is explicitly a *background/normal* mortality model. It is fitted to a restricted range of stand conditions, excludes most disturbance agents by design, and in several variants is capped by a mechanical "approach to maximum basal area" term. The documented failures are therefore of three kinds: (i) extrapolation outside the fitting range (notably low basal area in BC), (ii) missing disturbance/chronic mortality, and (iii) conventional, non-local density-dependent thresholds and species/size pooling.

2. **The strongest BC-specific evidence is about range extrapolation and data scarcity, not about a bad equation per se.** PrognosisBC documentation states that low-basal-area projections were "clearly invalidated by excessive mortality" because those stands were below the range of the mortality fitting data. The SBS/SBPS calibration report states there were insufficient PSPs to fit large-tree height or mortality models at all, so IDF/ICH mortality models were "borrowed". That is a structural calibration limitation, not a small residual bias.

3. **Regeneration/ingress is weaker than mortality.** FVS has only one full-featured regeneration establishment model (the NI/Inland Empire RegEst lineage); most variants use the "partial" model, which has *no equations* for natural regeneration and requires the user to supply `NATURAL`/plant inputs. FVS-BC contains the full RegEst code but has automatic regeneration deactivated, so operationally it behaves like a no-ingress model. BC deliberately deactivated automatic regeneration because the NI model did not reproduce BC ISIS survey composition/density. BC's replacement, Most Similar Neighbour (MSN) imputation, is a donor-based statistical fill, not a mechanistic establishment/dispersal model, and it performed poorly when extrapolated to mountain-pine-beetle stands.

4. **"Ingress is basically useless" is directionally right for FVS-BC but too strong as a general statement.** The full RegEst model is calibrated and used in the NI/IE, Montana, and southeast Alaska variants; it can work where it was fitted. In BC, however, automatic ingress is switched off at the source level (`LINGRW=.FALSE.`, `STOADJ=0.0` in `ESINIT`), so ingress is an *input assumption*, not a model prediction. For PSP calibration, that means ingress must be treated as an external driver or imputed from observed seedling/sapling counts, not as a submodel to be "validated".

5. **Most BC "validation" evidence tests growth, not mortality or ingress.** The best-known BC evaluation (Marshall et al. 2008) found acceptable 11-year dbh and stems-per-ha predictions in IDF stands, but it did **not** activate the recruitment function. Short, growth-focused validations cannot establish that mortality or ingress are adequate.

6. **The practical implication for FVS-BC calibration:** calibrate/refit mortality separately against PSP transition data (species × size × BA stratum × BEC), explicitly test low-BA and young stands, and do not rely on the standard FVS self-calibration, which adjusts only small-tree height and large-tree diameter growth. Treat ingress as observed input or an external recruitment model, and validate on holdout PSPs with long remeasurement intervals.

---

## 1. How the two submodels actually work

### 1.1 Mortality

FVS uses one of three base mortality frameworks depending on variant (Dixon 2002; Crookston and Dixon 2005):

- **Prognosis-type** (NI/IE and many western variants): an individual-tree logistic equation for annual mortality as a function of species, DBH, DBH increment, potential increment, stand basal area, and relative diameter (Wykoff 1986; Hamilton 1986), combined with a stand-level "approach to maximum basal area" term. The applied rate is a weighted average of the individual-tree rate and the stand-density rate, with the weight increasing as BA approaches BAmax (Dixon 2002, §7.3).
- **SDI-based** (e.g., Blue Mountains): stand-level mortality is partitioned into background and density-related components using two SDI thresholds, by default 55% and 85% of SDImax; mortality is then dispersed to individual trees (Dixon 2002; Vandendriesche 2010).
- **TWIGS/SDI-based** (most eastern variants): SDI determines the number of mortality trees; TWIGS-type equations disperse mortality to tree records.

Two design facts matter for calibration:

- The base model is explicitly for **background or normal mortality**. Insects, pathogens, and fire are handled by extensions; logging damage, animal damage, and wind must be supplied by keywords (Dixon 2002, §7.3).
- The "approach to BAmax" term is an **accounting constraint**, not an empirical mortality process. When BA reaches BAmax, the term removes all stand growth in excess of the maximum (Dixon 2002, eq. 7.3.1.2; ESSA 2011, §3.11). This makes long-run behaviour sensitive to BAmax/SDImax assumptions and can force convergence to a carrying capacity rather than to observed endemic dynamics.

The official FVS calibration guide reinforces a third point: the built-in self-calibration (`READCORD`, `READCORR`) calibrates **small-tree height** and **large-tree diameter** growth only. Mortality and regeneration are treated as manual keyword adjustments (`SDIMAX`, `BAMAX`, `NATURAL`, `TreeSzCp`) (Smith-Mateja 2025). In other words, the standard FVS calibration workflow does not calibrate mortality directly.

### 1.2 Regeneration and ingress

FVS has two establishment-model forms (Dixon 2002, §5.4):

- **Full establishment model (RegEst, Version 2.0 lineage):** predicts probability of stocking, seedling density, species composition, and seedling heights after disturbance, and automatically adds ingrowth. It is calibrated for western Montana, central/northern Idaho, and coastal Alaska (Dixon 2002; Ferguson and Crookston 1991; Ferguson and Carlson 1993).
- **Partial establishment model:** handles stump/root sprouting only. "Other than stump and root sprouting, the partial establishment model does not have equations for predicting natural regeneration. Whenever natural regeneration is desired, the user must schedule it using the `NATURAL` keyword record" (Dixon 2002, §5.4.5).

The regeneration period is fixed at 20 years in FVS; regeneration after that is called **ingrowth** (Dixon 2002, §5.4.1). In variants with the partial model, even ingrowth must be scheduled by the user via Event Monitor logic; it is not an automatic process.

BC's implementation is a special case. PrognosisBC inherited the NI RegEst code, but the variant description states that the NI model "does not reliably reproduce the mixture of species and density observed in the surveys. Consequently, automatic regeneration has been deactivated in the BC variant" (ESSA 2011, §2.2). The source code confirms this: `ESINIT` sets `LINGRW=.FALSE.`, `LAUTAL=.FALSE.`, and `STOADJ=0.0`, i.e. automatic ingrowth off, automatic tallies off, and probability of stocking zero (FVS-BC `esinit.f`, lines 29–32). The alternative is MSN imputation from a BC regeneration database, or manual planting/`NATURAL` input.

---

## 2. Annotated bibliography

### A. Foundational model documentation and design

**A1. Stage, A.R. 1973.** *Prognosis model for stand development.* USDA Forest Service Research Paper INT-137. Ogden, UT: Intermountain Forest and Range Experiment Station. 32 pp. [AGY]
- **Variant/region:** Original Prognosis; Northern Rocky Mountains.
- **What it is:** The founding description of the individual-tree, distance-independent stand projection model that became FVS. Establishes the growth/mortality/regeneration architecture.
- **Mortality/ingress relevance:** Mortality is treated as a competition/stand-development process; regeneration is not a fully mechanistic component. Later critiques of "mortality is only background" and "ingress is user-supplied" trace back to this design.
- **Classification:** Design limitation (architecture).
- **Verification:** Citation standard and confirmed in multiple retrieved documents; original report not read in full.

**A2. Wykoff, W.R., Crookston, N.L., and Stage, A.R. 1982.** *User's guide to the Stand Prognosis Model.* USDA Forest Service General Technical Report INT-133. Ogden, UT: Intermountain Forest and Range Experiment Station. 112 pp. DOI: 10.2737/INT-GTR-133. [AGY]
- **Variant/region:** Prognosis, Northern Rockies.
- **What it is:** User documentation for the model, including the mortality and regeneration keywords.
- **Mortality/ingress relevance:** Documents the original parameterization and the user-controlled nature of regeneration.
- **Classification:** Design limitation (documentation).
- **Verification:** DOI and metadata verified via OpenAlex; full text not read.

**A2b. Wykoff, W.R. 1986.** *Supplement to the user's guide for the Stand Prognosis Model—Version 5.0.* USDA Forest Service General Technical Report INT-208. Ogden, UT: Intermountain Research Station. 36 pp. [AGY]
- **Variant/region:** Prognosis, Northern Rockies.
- **What it is:** Documents the individual-tree mortality equation and other model changes.
- **Mortality/ingress relevance:** Source of the mortality equation form used in the Prognosis-type model.
- **Classification:** Design documentation.
- **Verification:** Citation from the ESSA (2011) reference list; full text not read.

**A3. Dixon, G.E. (comp.) 2002.** *Essential FVS: A user's guide to the Forest Vegetation Simulator.* USDA Forest Service, Forest Management Service Center, Internal Report. 208 pp. (last revised February 2007). URL: https://www.fs.usda.gov/sites/default/files/forest-management/essential-fvs.pdf. [AGY]
- **Variant/region:** All FVS variants.
- **What it is:** The canonical user guide; describes mortality model types, the 20-year regeneration period, full vs partial establishment, and keyword behaviour.
- **Mortality/ingress finding:** Base mortality is "intended to reflect background or normal mortality rates"; disturbance mortality requires extensions or keywords. The partial establishment model has no natural-regeneration equations. Only the full model automatically simulates ingrowth.
- **Key quotes:** "The Forest Vegetation Simulator base model mortality predictions are intended to reflect background or normal mortality rates." "Other than stump and root sprouting, the partial establishment model does not have equations for predicting natural regeneration." "Regeneration that occurs after the regeneration period is called ingrowth."
- **Classification:** Design limitation (explicit in official documentation).
- **Verification:** Full text read (downloaded PDF).

**A4. Smith-Mateja, E.E. (comp.) 2025.** *A guide to using the model calibration option in the Forest Vegetation Simulator (FVS).* USDA Forest Service, revised February 2025. URL: https://www.fs.usda.gov/sites/default/files/guidelines-for-calibrating-forest-vegetation-simulator.pdf. [AGY]
- **Variant/region:** All variants; examples use Inland Empire.
- **What it is:** Official calibration workflow.
- **Mortality/ingress finding:** The calibration option computes small-tree height and large-tree diameter growth scale factors. Mortality is not calibrated by this mechanism; the guide only suggests "adjustments to better parameterize mortality, regrowth and senescence (SDIMAX, BAMAX, NATURAL and TreeSzCp keywords)".
- **Classification:** Design limitation (calibration architecture).
- **Verification:** Full text read.

**A5. Ferguson, D.E., and Crookston, N.L. 1991.** *User's guide to Version 2 of the Regeneration Establishment Model: Part of the Prognosis Model.* USDA Forest Service General Technical Report INT-279. Ogden, UT: Intermountain Forest and Range Experiment Station. 34 pp. DOI: 10.2737/INT-GTR-279. [AGY]
- **Variant/region:** NI/Inland Empire RegEst.
- **What it is:** Documentation of the full establishment model (stocking probability, density, species, height; `ESTAB`/`NATURAL`/`PLANT` keywords).
- **Mortality/ingress finding:** Defines what the full model can and cannot do; establishment is statistical and plot-based, not mechanistic seed dispersal.
- **Classification:** Design limitation (scope of model).
- **Verification:** DOI verified; full text not read.

**A6. Ferguson, D.E., and Carlson, C.E. 1993.** *Predicting regeneration establishment with the Prognosis model.* USDA Forest Service Research Paper INT-467. Ogden, UT: Intermountain Research Station. 54 pp. DOI: 10.5962/bhl.title.68938. [AGY]
- **Variant/region:** Northern Rocky Mountains.
- **What it is:** Describes the regeneration establishment prediction system.
- **Mortality/ingress relevance:** The empirical basis of RegEst; establishment requires intensive regeneration plot data (Robinson 2008 notes >12,000 plots in 500 stands for the original Ferguson model).
- **Classification:** Design limitation (data-hungry empirical model).
- **Verification:** Metadata verified; series number (INT-467) taken from the 2017 FVS e-Conference reference list; full text not read.

**A7. Ferguson, D.E., Stage, A.R., and Boyd, R.J. 1986.** Predicting regeneration in the grand fir–cedar–hemlock ecosystem of the northern Rocky Mountains. *Forest Science Monograph* 26: 41 pp. (also *Forest Science* 32(Suppl. 1): a0001). DOI: 10.1093/forestscience/32.s1.a0001. [PR]
- **Variant/region:** Northern Rocky Mountains.
- **What it is:** Peer-reviewed monograph describing regeneration prediction in the habitat types that underpinned RegEst.
- **Mortality/ingress finding:** Establishment is strongly tied to habitat type, overstory, and site preparation; the model is region- and habitat-specific.
- **Classification:** Design limitation (regional specificity).
- **Verification:** Metadata verified; full text not read.

**A8. Crookston, N.L., and Dixon, G.E. 2005.** The Forest Vegetation Simulator: a review of its structure, content, and applications. *Computers and Electronics in Agriculture* 49(1): 60–80. DOI: 10.1016/j.compag.2005.02.003. [PR]
- **Variant/region:** All FVS.
- **What it is:** Peer-reviewed overview of FVS architecture, including mortality and regeneration components.
- **Mortality/ingress relevance:** Confirms the three mortality frameworks and the extension-based treatment of disturbance; useful for citing the design boundaries without relying only on agency docs.
- **Classification:** Design description, not a critique.
- **Verification:** Metadata verified; abstract/sections read via secondary sources; full text not retrieved.

**A9. Crookston, N.L., Rehfeldt, G.E., Dixon, G.E., and Weiskittel, A.R. 2010.** Addressing climate change in the Forest Vegetation Simulator to assess impacts on landscape forest dynamics. *Forest Ecology and Management* 260(7): 1198–1211. DOI: 10.1016/j.foreco.2010.07.013. [PR]
- **Variant/region:** Climate-FVS, western US.
- **What it is:** Adds climate-sensitive mortality, growth, and regeneration functions to FVS.
- **Mortality/ingress finding:** The authors found it necessary to *replace/augment* the base mortality and regeneration functions with climate-linked ones; projections were "most sensitive to mortality". This is indirect evidence that the base functions are not climate-responsive.
- **Classification:** Design limitation (base model lacks climate effects).
- **Verification:** Metadata verified; abstract read; full text not retrieved.

---

### B. Mortality: peer-reviewed evaluations and critiques

**B1. Hamilton, D.A., Jr. 1986.** A logistic model of mortality in thinned and unthinned mixed conifer stands of northern Idaho. *Forest Science* 32(4): 989–1000. DOI: 10.1093/forestscience/32.4.989. [PR]
- **Variant/region:** Northern Idaho; the empirical foundation of the Prognosis/NI mortality model.
- **What was tested:** Development (not validation) of the individual-tree logistic mortality equation from thinned and unthinned mixed-conifer plots, remeasured over multiple periods.
- **Mortality finding:** Mortality is modelled as a function of species, size, increment, and competition. The data are from a particular set of stands and BA range; this is the origin of the range-extrapolation problem documented later in BC.
- **Classification:** Foundational; not a critique. Its limitations become critiques when applied outside the fitting domain.
- **Verification:** Metadata and abstract verified; full text not read.

**B2. Canavan, S.J., and Ramm, C.W. 2000.** Accuracy and precision of 10-year predictions for Forest Vegetation Simulator—Lake States. *Northern Journal of Applied Forestry* 17(2): 62–70. DOI: 10.1093/njaf/17.2.62. [PR]
- **Variant/region:** FVS-Lake States (LS-TWIGS); 44 stands, 10 ecological land type phases, Michigan.
- **What was tested:** 10-year dbh growth, basal area growth, and mortality for seven upland hardwood species; sensitivity to cycle length and input detail.
- **Mortality finding:** "Basal area and mortality errors were less consistent. Mean errors for trees per acre ranged from −24 for red maple to +14 for white oak." Diameter growth was consistently overpredicted.
- **Classification:** Validation (mixed); mortality errors are real but not uniformly biased.
- **Verification:** Abstract read; full text not retrieved.

**B3. Lacerte, V., Larocque, G.R., Woods, M., Parton, W.J., and Penner, M. 2004.** Testing the Lake States variant of FVS (Forest Vegetation Simulator) for the main forest types of northern Ontario. *The Forestry Chronicle* 80(4): 495–506. DOI: 10.5558/tfc80495-4. [PR]
- **Variant/region:** FVS-Lake States; northern Ontario; 537 remeasured plots; black spruce, white spruce, jack pine, trembling aspen; range of site index, density, and age.
- **What was tested:** Biological consistency, mean percent difference for stand density, BA, top height, QMD, and individual-tree dbh over multiple projection lengths.
- **Mortality finding:** **"The decrease in stand basal area at young ages was inconsistent with the normal development pattern of the forest stands under study and was attributed to deficiencies in the prediction of mortality."** LS-FVS underpredicted stand density, BA, and top height, and overpredicted QMD.
- **Classification:** Validation failure (mortality in young stands); design limitation (boreal species).
- **Verification:** Abstract read (AGRIS); full text blocked by publisher (403). This is one of the clearest peer-reviewed statements that FVS mortality fails in young stands.

**B4. Radtke, P.J., Herring, N.D., Loftis, D.L., and Keyser, C.E. 2012.** Evaluating Forest Vegetation Simulator predictions for southern Appalachian upland hardwoods with a modified mortality model. *Southern Journal of Applied Forestry* 36(2): 61–70. DOI: 10.5849/sjaf.10-017. [PR]
- **Variant/region:** FVS-Southern (FVS-Sn); 1,780 permanent FIA plots; mixed-species upland hardwoods, Southern Appalachians.
- **What was tested:** 5-year projections of BA and trees per acre; refitting the background mortality equation; relaxing the SDI thresholds that activate density-dependent mortality.
- **Mortality finding:** Baseline predictions were within ±15% on >88% of plots, with average bias of 3.5% (BA) and 4.1% (TPA). **"In plots with high initial stand densities, notable gains in accuracy were achieved by relaxing thresholds that activated a density-dependent mortality algorithm in FVS-Sn."** Refitting background mortality cut overestimation bias by 56% (BA) and 80% (TPA).
- **Classification:** Partial validation; critique of the density-dependent mortality thresholds and background coefficients.
- **Verification:** Full text read (USDA PDF).

**B5. Russell, M.B., Weiskittel, A.R., and Kershaw, J.A., Jr. 2013.** Benchmarking and calibration of Forest Vegetation Simulator individual tree attribute predictions across the northeastern United States. *Northern Journal of Applied Forestry* 30(2): 75–84. DOI: 10.5849/njaf.12-034. [PR]
- **Variant/region:** FVS-Northeast; FIA permanent plots; 20 most abundant species.
- **What was tested:** Total height, 5-year dbh increment, 5-year height increment; spatial trends; calibration with tree size, site, and climate.
- **Mortality finding:** Not a mortality test directly, but the paper documents poor submodel performance (dbh increment within 15% of observed only 8.4–17.3% of the time) and shows that calibration improves growth but **"5-year basal area growth continued to be underpredicted across all ecoregions and forest types"** even after calibration. The authors do not isolate mortality, but the stand-level BA bias is consistent with missing mortality/recruitment.
- **Classification:** Validation (growth); indirect evidence of stand-level process gaps.
- **Verification:** Abstract read; full text not retrieved.

**B6. Herbert, C., Fried, J.S., and Butsic, V. 2023.** Validation of Forest Vegetation Simulator model finds overprediction of carbon growth in California. *Forests* 14(3): 604. DOI: 10.3390/f14030604. [PR]
- **Variant/region:** California FVS variants; thousands of remeasured inventory plots.
- **What was tested:** 10-year carbon sequestration in live trees, using bootstrapped equivalence tests; sensitivity to forest type, variant, site class, age, ownership.
- **Mortality finding:** Out-of-the-box FVS **"overpredicts carbon sequestration in live trees that remain alive ten years later by 27%, on average."** Largest overpredictions in North Coast, lowest site class, unknown or 50–100-year ages, reserved areas/national forests. The "trees that remain alive" framing means survivor growth is overstated; mortality/recruitment bias is a plausible contributor but not isolated.
- **Classification:** Validation failure (stand-level carbon/growth); indirect mortality/ingress evidence.
- **Verification:** Abstract read via Crossref; full text not retrieved (MDPI 403).

**B7. Bagdon, B.A., Nguyen, T.H., Vorster, A., Paustian, K., and Field, J.L. 2021.** A model evaluation framework applied to the Forest Vegetation Simulator (FVS) in Colorado and Wyoming lodgepole pine forests. *Forest Ecology and Management* 480: 118619. DOI: 10.1016/j.foreco.2020.118619. [PR]
- **Variant/region:** Central Rockies FVS; Colorado/Wyoming lodgepole pine; FIA chronosequence and remeasurement data.
- **What was tested:** Default FVS versus observed stand development; sensitivity to initial species mix, site index, large-tree diameter increment, and BAmax.
- **Mortality finding:** **"The default model settings substantially over-predict basal area and total stand carbon after 50 years for both pure lodgepole pine stands and mixed lodgepole..."** The authors identify BAmax and mortality/ingrowth as sensitive parameters. A companion slide deck quotes Vandendriesche's warning that "FVS tends to concentrate substantial growth on few survivor trees".
- **Classification:** Validation failure (long-run BA/carbon); design limitation (BAmax and regeneration assumptions).
- **Verification:** Abstract snippet and companion slide deck read; full text not retrieved. The quoted sentence is from the publisher abstract snippet, not the full paper.

**B8. Dempster, W.R. 2024.** Representation of regeneration dynamics in growth and yield models: a review. *Canadian Journal of Forest Research* 54(8). DOI: 10.1139/cjfr-2024-0016. [PR]
- **Variant/region:** Review; Alberta/boreal focus, but the argument is general.
- **What was tested:** Literature review of regeneration representation in growth and yield models, motivated by Alberta reforestation assessments.
- **Mortality/ingress finding:** **"Existing growth and yield models, used to predict whether regeneration performance will meet management objectives, do not adequately represent juvenile mortality, ingress of natural regeneration, stand density, and the responses of ingress and mortality to reforestation treatments."** The review also notes that FVS regeneration models have had "somewhat limited application" and cites Bagdon et al. (2021) on establishment-routine limitations.
- **Classification:** Critique/review; strong general statement of the ingress gap.
- **Verification:** Abstract read via Crossref; full text not retrieved.

**B9. Metsaranta, J.M., Fortin, M., White, J.C., and Sattler, D. 2024.** Climate sensitive growth and yield models in Canadian forestry: challenges and opportunities. *The Forestry Chronicle* 100(1): 88–106. DOI: 10.5558/tfc2024-005. [PR]
- **Variant/region:** Canada, including FVS-BC.
- **What it is:** Technical review of climate sensitivity in provincial/territorial growth and yield models.
- **Mortality/ingress relevance:** Notes that several models used in Canada "do not adequately account for climate and other environmental variables", which limits their effectiveness; frames mortality and regeneration as key processes needing climate-sensitive treatment. Useful context, not a direct FVS mortality test.
- **Classification:** Context/review.
- **Verification:** Abstract read; full text not retrieved.

---

### C. Mortality and regeneration: conference proceedings and agency analyses

**C1. Marshall, P.L., Parysow, P., and Akindele, S. 2008.** Evaluating growth models: a case study using PrognosisBC. In: Havis, R.N., and Crookston, N.L. (comps.), *Third Forest Vegetation Simulator Conference; 2007 February 13–15; Fort Collins, CO. Proceedings RMRS-P-54.* Fort Collins, CO: USDA Forest Service, Rocky Mountain Research Station, pp. 167–185. URL: https://research.fs.usda.gov/download/treesearch/30979.pdf. [CONF]
- **Variant/region:** PrognosisBC Version 3.0; IDFdk3, Alex Fraser Research Forest, Williams Lake, BC; 30 permanent plots (6 in an uneven-aged installation, 24 in a PCT experiment); 11-year remeasurement (1993–2003).
- **What was tested:** Independent-data validation of dbh, stems per ha, and stand volume; simulation sensitivity across up to 64 BDq combinations (some infeasible).
- **Mortality/ingress finding:** **"Future stems per ha (or its corollary, mortality level) appeared to be acceptably predicted overall (fig. 5). There was a slight underestimate of future stems per ha..."** However, **"Since the recruitment (regeneration) function of PrognosisBC was not activated for this assessment, all scenarios showed a decrease in stems per ha with time."** The paper concludes, "we were pleased with the performance of the model."
- **Classification:** Partial validation/success for mortality in mature IDF; design limitation for ingress (not tested).
- **Verification:** Full text read. This is the most important counter-evidence to a blanket "mortality is broken in BC" claim.

**C2. DeRose, R.J., Shaw, J.D., Vacchiano, G., and Long, J.N. 2008.** Improving longleaf pine mortality predictions in the Southern Variant of the Forest Vegetation Simulator. In: *Third Forest Vegetation Simulator Conference Proceedings RMRS-P-54*, pp. 160–166. URL: https://hdl.handle.net/2318/72065. [CONF]
- **Variant/region:** FVS-Southern; Ft. Bragg, North Carolina; longleaf pine.
- **What was tested:** Biologically unrealistic size–density predictions at large diameters; three remedies: stand-density modifier keywords, a tree size cap, and iterative empirical mortality rates.
- **Mortality finding:** **"Inventory data from Ft. Bragg indicated the mortality submodel was responsible for the over-predictions."** Only the iterative empirical mortality approach was viable.
- **Classification:** Validation failure (species/size range); demonstrates that keyword workarounds are insufficient.
- **Verification:** Abstract read via OpenAlex; full text not retrieved.

**C3. Vandendriesche, D. 2010.** FVS out of the box—assembly required. In: Jain, T.B., Graham, R.T., and Sandquist, J. (tech. eds.), *Integrated management of carbon sequestration and biomass utilization opportunities in a changing climate: Proceedings of the 2009 National Silviculture Workshop; 2009 June 15–18; Boise, ID.* Proceedings RMRS-P-61. Fort Collins, CO: USDA Forest Service, Rocky Mountain Research Station, pp. 289–306. URL: https://www.fs.usda.gov/rm/pubs/rmrs_p061/rmrs_p061_289_306.pdf. [CONF/AGY]
- **Variant/region:** Blue Mountains (Oregon) case study; general FVS.
- **What was tested:** Default FVS versus measured inventory trends; methods to craft an "endemic" run (self-calibration, defect, SDImax/BAmax caps, regeneration response).
- **Mortality/ingress finding:** **"Mortality and regeneration aspects are difficult components to model. One subtracts trees from the ecosystem; the other adds trees to it."** **"The default mortality paradigm embedded in FVS allows stands to progress to full site occupancy (i.e. maximum stand density). However, this ceiling does not represent the generalized endemic growth pattern typified by inventory data sets used for landscape assessments."** **"Most FVS variants include only the partial establishment extension that lacks automatic natural regeneration features. Thus, tree frequencies steadily decline over time. Growth dynamics are accumulated in the survivor trees resulting in excessive stand volume."** Abstract: "over long projections, FVS tends to concentrate substantial growth on few survivor trees."
- **Classification:** Critique/design limitation; the single best plain-language statement of both problems.
- **Verification:** Full text read.

**C4. Ray, D., Keyser, C., Seymour, R., and Brissette, J. 2008.** Predicting the recruitment of established regeneration into the sapling size class following partial cutting in the Acadian forest region: using long-term observations to assess the performance of FVS-NE. In: *Third Forest Vegetation Simulator Conference Proceedings RMRS-P-54*, pp. 186–195. URL: https://research.fs.usda.gov/download/treesearch/30980.pdf. [CONF]
- **Variant/region:** FVS-Northeast; Penobscot Experimental Forest, Maine; 729 plot/5-year interval combinations; repeated partial harvests.
- **What was tested:** Sapling (≥0.5 in dbh) recruitment and subsequent survival; production vs beta parameterizations.
- **Mortality/ingress finding:** **"Among the 20 regional variants of FVS, only five support full establishment models. Users of variants lacking this functionality are required to specify measured or anticipated regeneration..."** Recruitment is "a weak link in available models". Predicted sapling recruitment averaged **47% (production) and 206% (beta) of observed**; **"Mortality rates among the newly recruited saplings were overestimated by both models, and species composition of the survivors did not closely match the observations."** Limiting input regeneration to ≤1,800 TPA largely removed bias but only modestly improved R² (0.398 vs 0.341).
- **Classification:** Validation failure (recruitment/early survival); design limitation (no full establishment model; user-supplied regeneration).
- **Verification:** Full text read.

**C5. Robinson, D.C.E. 2008.** Development of external regeneration models for FVS: another wrench in the toolkit. In: *Third Forest Vegetation Simulator Conference Proceedings RMRS-P-54*, pp. 225–234. URL: https://research.fs.usda.gov/download/treesearch/30983.pdf. [CONF]
- **Variant/region:** FVS generally; examples include the Blue Mountains and PrognosisBC `AddTrees` model.
- **What was tested:** A capability for external regeneration models to be called from FVS without modifying source code.
- **Mortality/ingress finding:** **"Despite more than three decades of development, only one full-featured regeneration model has been developed for the Forest Vegetation Simulator (FVS)."** Robinson adds a footnote that some would count five such models, but he treats the NI/Inland Empire RegEst and the neighbouring Central Idaho, Kootenai/Kaniksu/Tally Lake, Eastern Montana, and Southeast Alaska variants as one model lineage. Regeneration is an "all-or-none" process that is hard to observe; the original Ferguson model required >12,000 regeneration plots in 500 stands. FVS variants without the full model have "a range" of workarounds, but no general predictive capability.
- **Classification:** Critique/design limitation.
- **Verification:** Full text read.

**C6. Weiskittel, A., Kershaw, J., Crookston, N., and Hennigar, C. 2017.** The Acadian variant of the Forest Vegetation Simulator: continued development and evaluation. In: Keyser, C.E., and Keyser, T.L. (eds.), *Proceedings of the 2017 Forest Vegetation Simulator (FVS) e-Conference.* e-Gen. Tech. Rep. SRS-224. Asheville, NC: USDA Forest Service, Southern Research Station, pp. 9–12. URL: https://research.fs.usda.gov/treesearch/download/54844.pdf. [CONF]
- **Variant/region:** FVS-Acadian (ACD) vs FVS-NE; Maine/Maritimes mixedwoods.
- **What was tested:** Development and evaluation of ACD equations; comparison of 50-year BA trajectories with NE.
- **Mortality/ingress finding:** ACD was developed because NE had "potential shortcomings in the Acadian Region, particularly for the spruce-fir forest type". ACD includes a new mortality equation (Weiskittel et al. 2012) and an ingrowth model (Li et al. 2011). The paper's key claim: **"Multi-stage approach to mortality predictions outperforms more traditional approaches including methods currently used by other FVS variants."** This is an implicit critique of the legacy mortality model in mixedwoods.
- **Classification:** Critique (mixedwood mortality); model-development response.
- **Verification:** Full text read.

**C6b. Ray, D., and Seymour, R. 2017.** Performance of FVS variants in relation to an extensive chronosequence and remeasurement dataset for eastern white pine (*Pinus strobus*, L.) in central Maine. In: Keyser, C.E., and Keyser, T.L. (eds.), *Proceedings of the 2017 Forest Vegetation Simulator (FVS) e-Conference.* e-Gen. Tech. Rep. SRS-224. Asheville, NC: USDA Forest Service, Southern Research Station, pp. 77–80. URL: https://research.fs.usda.gov/treesearch/download/54844.pdf. [CONF]
- **Variant/region:** FVS-Northeast vs FVS-Acadian (ACD); central Maine; eastern white pine chronosequence and remeasurement plots (14 control plots plus PCT, B-line, and low-density thinning plots).
- **What was tested:** Stand-level TPA, BA, and QMD predictions; uncalibrated vs calibrated NE; ACD with base mortality model and climate site index (CSI) vs traditional site index (SI).
- **Mortality/ingress finding:** Uncalibrated NE had a TPA bias of **+183.5** stems/ac (RMSE 1,160.7); calibrated NE, **+48.6** (RMSE 307.2); ACD with base mortality, **+27.2** (RMSE 172.2). **"Due to unresolved issues with the mortality function for the ACD, this aspect was handled by the base model option available in FVSOnline."** Calibration improved NE across the board; ACD with measured SI reduced bias only for QMD. The authors note that calibration requires observed growth data, which ACD could not use in the same way.
- **Classification:** Validation (mixed); explicit evidence of unresolved mortality in a new mixedwood variant.
- **Verification:** Full text read.

**C7. Affleck, D.L.R. 2024.** Impacts of precommercial thinning on observed versus FVS-projected diameter and height increments in the Inland Northwest. In: Shaw, J.D., Battaglia, M.A., and Castle, M. (comps.), *Sixth Forest Vegetation Simulator Conference; 2023 March 7–9; Fort Collins, CO. Proceedings RMRS-P-81.* Fort Collins, CO: USDA Forest Service, Rocky Mountain Research Station, pp. 61–65. DOI: 10.2737/RMRS-P-81. [CONF]
- **Variant/region:** FVS-Inland Empire (FVS-IE); Region 1 Permanent Growth Plot network, >300 stands; Douglas-fir and western larch.
- **What was tested:** PCT versus control diameter and height projection errors.
- **Mortality/ingress finding:** **"The model was calibrated to reflect gradual, mortality-driven reductions in CCF as opposed to abrupt changes from active management."** Diameter growth errors were significantly larger on PCT plots; height errors similar. This is a design limitation: the competition index is calibrated to mortality-driven self-thinning, not to abrupt density reduction.
- **Classification:** Design limitation (mortality/CCF coupling); validation failure for PCT.
- **Verification:** Full text read.

**C8. Frank, J., and Castle, M. 2024.** Using FIA data and GY models for state-wide forest projections. In: *Sixth Forest Vegetation Simulator Conference Proceedings RMRS-P-81*, pp. 66–68. DOI: 10.2737/RMRS-P-81. [CONF]
- **Variant/region:** FVS-Northeast; Maine statewide FIA.
- **What was tested:** Growing the first complete annual FIA inventory forward 15 years; comparison of FVS and FIA gross growth and mortality.
- **Mortality/ingress finding:** **"FVS growth rates appeared to exceed FIA growth rates"**, and **"Preliminary results suggest that FIA mortality estimates exceed FVS-NE mortality estimates resulting in over-estimates of net growth across Maine."** Proposed fixes: modify maximum density and mortality distribution with `BAmax`, or adjust `SDImax` directly "if base mortality functions in FVS-NE are not refit."
- **Classification:** Validation failure (under-mortality); design limitation (mortality not refit).
- **Verification:** Full text read.

**C9. Sattler, D.F., LeMay, V., and Marshall, P.L. 2009.** Estimating natural regeneration in stands following attack by mountain pine beetle using a linked-model approach. In: *Forest Growth and Timber Quality: Crown Models and Simulation Methods for Sustainable Forest Management. Proceedings of an International Conference; Portland, OR; 2007.* USDA Forest Service General Technical Report PNW-GTR-791. DOI: 10.2737/PNW-GTR-791. (Page numbers not verified.) [CONF]
- **Variant/region:** PrognosisBC + SORTIE-ND; IDF, SBPS, SBS, MS zones, central/southeastern BC; MPB-attacked stands.
- **What was tested:** Linking SORTIE-ND regeneration estimates (trees <7.5 cm dbh) into PrognosisBC at 5 and 10 years post-attack; 25-year projections; comparison with PrognosisBC-only and SORTIE-only.
- **Mortality/ingress finding:** **"The lack of an effective sub-model capable of predicting the abundance and species composition of natural regeneration for MPB-attacked stands is a major limitation of PrognosisBC."** **"Although use of the linked-model approach provided slight improvements over using PrognosisBC only or SORTIE-ND only, overall results were generally poor."** Lodgepole pine densities were largely underestimated for smaller trees. Earlier: **"efforts to calibrate the regeneration sub-model did not fare well (Boisvenue 1999, Zumrawi et al. 2005a)."**
- **Classification:** Validation failure (ingress); design limitation (no effective regeneration submodel).
- **Verification:** Full text read.

**C10. Snowdon, B. 1997.** British Columbia's Forest Vegetation Simulator application software. In: Teck, R., Moeur, M., and Adams, J. (tech. eds.), *Proceedings of the Forest Vegetation Simulator Conference; 1997 February 3–7; Fort Collins, CO.* USDA Forest Service General Technical Report INT-373. Ogden, UT: Intermountain Forest and Range Experiment Station. [CONF]
- **Variant/region:** PrognosisBC (early).
- **What it is:** Describes the BC adaptation of FVS (metric units, BEC linkage, interface).
- **Mortality/ingress relevance:** Establishes that BC is a *derived* variant, inheriting NI mortality and establishment logic; the adaptation focused on growth, units, and interface, not on new mortality/ingress process models.
- **Classification:** Design/origin.
- **Verification:** Citation confirmed in multiple BC documents; full text not retrieved.

**C11. Zumrawi, A., Stage, A., and Snowdon, B. 2002.** Stand level scaling of a single tree distance independent diameter growth model: interim calibration of Prognosis in the south-eastern interior of British Columbia. In: Crookston, N.L., and Havis, R.N. (comps.), *Proceedings of the Second Forest Vegetation Simulator (FVS) Conference; 2002 February 12–14; Fort Collins, CO.* Proceedings RMRS-P-25. Ogden, UT: USDA Forest Service, Rocky Mountain Research Station, pp. 151–157. [CONF]
- **Variant/region:** PrognosisBC; southeastern BC.
- **What was tested:** Scaling a single-tree diameter growth model to stand level; interim calibration.
- **Mortality/ingress relevance:** Documents that BC calibration effort concentrated on diameter growth; mortality was not the focus.
- **Classification:** Design/calibration emphasis.
- **Verification:** Citation confirmed; full text not retrieved.

---

### D. British Columbia: PrognosisBC/FVS-BC reports, theses, and program reviews

**D1. ESSA Technologies Ltd. 2011.** *PrognosisBC Version 4.2 variant description.* DRAFT. Prepared by ESSA Technologies Ltd., Vancouver, BC, for Dr. Peter Marshall, UBC Faculty of Forestry. 58 pp. March 2011. Local copy: `.opencode/tmp/opencode/prognosisbc-v42.pdf` (text extraction: `prognosisbc-v42.txt`). [AGY]
- **Variant/region:** PrognosisBC/FVS-BC v4.2; IDF, ICH, MS, ESSF, PP (documented), with SBS/SBPS additions; BC.
- **What it is:** The official (draft) variant description: model execution sequence, mortality equations, maximum-BA constraints, regeneration submodel status, and calibration notes.
- **Mortality findings (direct quotes):**
  - "During model tests that simulated growth from bare ground plantings, it became clear that the model was not behaving appropriately for some species and site combinations. ... predictions for some species were clearly invalidated by excessive mortality at very low stand basal area. Further study showed that stand basal area lay well below the range of basal area used to fit the mortality models."
  - "Until the model includes data collected from stands with low basal area, users are cautioned to carefully review model projections when the stand basal area falls below 10 m2/ha."
  - "Depending on the species, there are two kinds of mortality model. A logistic model (Eqn 3.13) is used for hardwoods and simple tabular model (Eqn 3.14) for conifers. The tabular model was implemented after attempts to create a comprehensive logistic model failed to give reliable appropriate behaviour beyond the range of the fitting data."
  - "Predicted mortality is modified as the stand approaches the maximum basal area defined for the variant and site series. ... when the stand reaches the maximum basal area, mortality removes all stand growth in excess of the maximum."
- **Ingress findings (direct quotes):**
  - "A comparative analysis of ISIS regeneration surveys and the Regeneration model (Robinson and Kurz 1998) showed that the NI variant does not reliably reproduce the mixture of species and density observed in the surveys. Consequently, automatic regeneration has been deactivated in the BC variant."
  - "Some FVS variants have natural regeneration routines, but most variants depend on the user to specify the species and number of trees to plant."
- **Classification:** Design limitation + documented validation failure at low BA; primary BC source.
- **Verification:** Full text read.

**D2. Marshall, P.L., and Lee, T. 2011.** *Development of PrognosisBC for complex stands in the southern and central interior of BC: application of the model's growth functions to the SBS and SBPS BEC zones.* Technical Report, April 26, 2011. Funded under Forest Science Plan Project G117074. University of British Columbia, Forest Resources Management Department. 14 pp. URL: https://a100.gov.bc.ca/pub/eirs/finishDownloadDocument.do?subdocumentId=14542. [AGY]
- **Variant/region:** PrognosisBC v4.2; SBS and SBPS zones, Williams Lake and Quesnel Forest Districts, central interior BC; data from 2008–2009 plus 2001 industry data.
- **What was tested:** Calibration of juvenile height growth and 10-year radial increment; selection of "nearest neighbour" source subzones for missing components.
- **Mortality/ingress finding:** **"There were insufficient permanent sample plot data available in all the SPS [sic] and SPBS subzones to develop large tree height growth or mortality models."** Mortality models were "borrowed" from IDF/ICH subzones (e.g., SBPSdc ← IDFdk; SBPSmk ← IDFdk; SBSdw1 ← ICHmk; SBSdw2 ← IDFdk; SBSmh ← ICHmk). The report warns: **"Although the functions and substitutions presented in this document have been tested individually to the extent possible given the available data, data were quite limited for certain species, subzone variants, and functions..."** and **"Official release of PrognosisBC, Version 4.2 should be deferred until it is is appropriately tested and validated."**
- **Classification:** Design/calibration limitation (no local mortality model; borrowed parameters; insufficient PSPs).
- **Verification:** Full text read.

**D3. Zumrawi, A.-A., LeMay, V., Marshall, P., Hassani, B.T., and Robinson, D. 2005a.** *Implementing a PrognosisBC regeneration sub-model for complex stands of southeastern and central British Columbia.* Report submitted to the Forest Science Program, Project No. Y051355. Research Branch, BC Ministry of Forests; UBC; ESSA Technologies. 66 pp. URL: https://a100.gov.bc.ca/pub/eirs/finishDownloadDocument.do?subdocumentId=18524. [AGY]
- **Variant/region:** PrognosisBC; IDF, ICH, MS, SBS, SBPS; BC.
- **What was tested:** (i) PrognosisBC natural regeneration predictions against mountain pine beetle data; (ii) long-term effects of partial cutting; (iii) regeneration model software/database.
- **Mortality/ingress findings:** **"The initial calibration of the Northern Idaho regeneration model was not satisfactory for use in BC (Boisvenue 1999), and was not implemented. Instead, model users have had to specify the amount and composition of natural regeneration following simulated partial harvesting and thinning. This limited the use of PrognosisBC in making reliable long-term projections..."** The MSN imputation approach "consistently underestimated regeneration of the shade intolerant species" in MPB stands; **"regeneration was often underestimated"** even when MPB data were added. The report attributes poor performance to sparse MPB data, missing variables (snags, CWD, decay/fall), and reference-domain mismatch.
- **Classification:** Validation failure/design limitation (ingress); primary BC source.
- **Verification:** Full text read.

**D4. Zumrawi, A.-A., Marshall, P., Akindele, S.O., Ortlepp, S., and Thony, P. 2005b.** *Calibrating PrognosisBC in the Sub-Boreal Spruce and the Sub-Boreal Pine-Spruce biogeoclimatic zones: development of growth and mortality models for major tree species.* Report submitted to the BC Forest Science Program, Project No. Y051356. 30 pp. [AGY]
- **Variant/region:** PrognosisBC; SBS/SBPS, central interior BC.
- **What was tested:** Development of growth and mortality models for major species.
- **Mortality/ingress finding:** This is the companion calibration report cited by Marshall and Lee (2011). It documents the data and model development that led to the conclusion that mortality models could not be fitted for all SBS/SBPS subzones. I did not retrieve the report itself; the finding above is from Marshall and Lee's summary and should be verified against the original.
- **Classification:** Calibration/design limitation.
- **Verification:** Secondary citation only (Marshall and Lee 2011; SBS/SBPS reference list). Not independently read.

**D5. Temesgen, H., and Mitchell, S.J. 2005.** An individual-tree mortality model for complex stands of southeastern British Columbia. *Western Journal of Applied Forestry* 20(2): 101–109. DOI: 10.1093/wjaf/20.2.101. [PR]
- **Variant/region:** Southeastern BC; multi-cohort, multi-aged, mixed-species stands; 29,773 trees from BC permanent sample plots.
- **What was tested:** Development and evaluation of a generalized logistic mortality model relating mortality to tree size, competition, and relative position; 70% development / 30% evaluation.
- **Mortality finding:** Observed average annual mortality ranged from **0.3% to 2.6%**; average annual diameter increment 0.08–0.17 cm/yr. The evaluation showed the model "well behaved and robust"; average deviation between observed and predicted annual mortality was **−0.5% to 0.7%** for the eight species.
- **Classification:** Peer-reviewed BC mortality model; counter-evidence that BC data can support a defensible mortality model. Its existence makes the continued use of borrowed/coarse tabular mortality in some BC subzones a *choice/implementation* issue, not only a data limitation.
- **Verification:** Abstract read; full text not retrieved. The FVS-BC source code contains a logistic survival relationship "fitted by Temesgen Hailemarian, UBC Forestry; December 8, 2001" (`morts.f`), consistent with this work.

**D6. Temesgen, H., and LeMay, V. 2000.** *Re-fitting the mortality model of PrognosisBC for both conifers and hardwoods in the Nelson and Kamloops forest regions.* Report to the BC Ministry of Forests. 23 pp. [AGY]
- **Variant/region:** PrognosisBC; Nelson and Kamloops Forest Regions, BC.
- **What was tested:** Re-fitting the mortality model for conifers and hardwoods.
- **Mortality finding:** Existence of this report shows that the inherited NI mortality model was recognized as inadequate for BC and was refitted. The exact results are not available to me. The report is described as an "unpublished internal report" in some citing documents.
- **Classification:** Calibration response to a recognized mortality weakness.
- **Verification:** Secondary citation only (Marshall and Lee 2011; ESSA 2011; Sattler et al. 2009 reference list). No URL found. **Unverified.**

**D7. Robinson, D.C.E., and Kurz, W.A. 1998.** *Analysis of the Prognosis Regeneration Establishment Model behaviour with BC regeneration data.* Prepared by ESSA Technologies Ltd., Vancouver, BC, for the BC Ministry of Forests, Victoria, BC. 42 pp. [AGY]
- **Variant/region:** Prognosis/NI RegEst applied to BC regeneration data (ISIS surveys).
- **What was tested:** Comparison of RegEst predictions with BC ISIS regeneration survey species mixture and density.
- **Ingress finding:** The NI variant "does not reliably reproduce the mixture of species and density observed in the surveys" (quoted in ESSA 2011). This is the technical basis for deactivating automatic regeneration in PrognosisBC.
- **Classification:** Validation failure (ingress); design limitation.
- **Verification:** Secondary citation only (ESSA 2011; Zumrawi et al. 2005a reference list). **Unverified** at full-text level.

**D8. Lencar, C. 2003.** *PrognosisBC database consolidation: sampling procedures and database organization of data collected during 1998–2002 for calibrating small tree height growth and regeneration components of PrognosisBC.* Contract No. HQ03-199. Prepared for BC Ministry of Forests, Research Branch. 35 pp. URL: https://a100.gov.bc.ca/pub/eirs/finishDownloadDocument.do?subdocumentId=17782. [AGY]
- **Variant/region:** PrognosisBC; ICHmw2 (Nelson), IDF (Kamloops/Williams Lake), and other BEC zones.
- **What it is:** Documents the field sampling and database used to calibrate small-tree height growth and natural regeneration.
- **Mortality/ingress relevance:** Shows the regeneration calibration data were temporary plots concentrated in a few subzones, not a province-wide PSP network; this underpins the reference-domain limitation of MSN.
- **Classification:** Data/design limitation.
- **Verification:** Full text read.

**D9. Robinson, D.C.E. 1997.** *Prognosis Southern Interior (SI 1.0g) geographic variant description.* Report to the BC Ministry of Forests. 178 pp. [AGY]
- **Variant/region:** Prognosis Southern Interior, BC.
- **What it is:** Early BC variant description.
- **Mortality/ingress relevance:** Documents the initial BC adaptation and its reliance on NI equations; useful for tracing which components were localized vs inherited.
- **Classification:** Design/origin.
- **Verification:** Secondary citation only (Marshall and Lee 2011). **Unverified.**

**D10. Boisvenue, C. 1999.** *Early height growth and regeneration: applicability of Prognosis components to the southern interior of British Columbia.* M.Sc. thesis, University of British Columbia, Vancouver, BC. DOI: 10.14288/1.0099443 (cIRcle deposit dated 2009). [THESIS]
- **Variant/region:** Prognosis/NI; ICHmw2, Nelson, BC.
- **What was tested:** Whether the NI regeneration and small-tree height-growth components could be calibrated to BC; original NI equation forms vs refitted forms vs Nelson-based variables.
- **Ingress/mortality finding:** **"In all cases, the original fitted equations in Prognosis NI were outperformed by either the refitted equations or equations with Nelson-based variables."** **"Prognosis NI was not developed in BC and it uses a different ecosystem classification. Although correspondences have been made between BC site series and Idaho habitat types, the two systems are different, and so are the sites. These differences contribute to errors in model predictions."** The Nelson dataset was much smaller than the NI fitting dataset; some data categories had more predictors than observations, producing **"non-robust models."**
- **Classification:** Validation/calibration failure of transferred NI regeneration logic; direct evidence for the "borrowed model" problem.
- **Verification:** Abstract read; full text not retrieved.

**D11. Sattler, D.F. 2009.** *A hybrid model to estimate natural recruitment and growth in stands following mountain pine beetle disturbance.* M.Sc. thesis, University of British Columbia, Vancouver, BC. DOI: 10.14288/1.0066900. [THESIS]
- **Variant/region:** PrognosisBC + SORTIE-ND; IDF and SBS, central/southeastern BC; MPB-disturbed stands.
- **What was tested:** Linking SORTIE-ND regeneration estimates to PrognosisBC; development of density-dependent crown allometry for SORTIE-ND.
- **Ingress finding:** **"PrognosisBC, a spatially-implicit growth model, lacked a submodel suitable for predicting natural regeneration in unsalvaged MPB-disturbed stands."** The hybrid model "provided good estimates" only after improving crown allometry; the underlying problem is the missing recruitment model.
- **Classification:** Design limitation (ingress).
- **Verification:** Abstract read; full text not retrieved.

**D12. Lencar, C.C. 2009.** *Effects of regeneration dynamics on predicted development of interior Douglas-fir stands.* M.Sc. thesis, University of British Columbia, Vancouver, BC. DOI: 10.14288/1.0099697. [THESIS]
- **Variant/region:** PrognosisBC; IDFdk1, IDFdk2, IDFdk3, Kamloops/Williams Lake, BC; 335 plots sampled in 1999.
- **What was tested:** Small-tree height-growth equations; relationships between regeneration abundance and overstory/site; stand matrix by residual BA and site; projections of partially cut stands.
- **Ingress finding:** Regeneration abundance is strongly related to overstory and site; the calibration data were collected specifically because the inherited model was inadequate. The thesis documents the empirical foundation for BC's small-tree and regeneration components.
- **Classification:** Calibration/data description; design limitation (empirical, subzone-specific).
- **Verification:** Abstract read; full text not retrieved.

**D13. Penner, M. (Forest Analysis Ltd.) 2021.** *Growth and yield modelling systems for BC: a review.* Final report, revised March 5, 2021. Prepared for Forest Analysis and Inventory Branch, BC Ministry of Forests, Lands, Natural Resource Operations and Rural Development. URL: https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/stewardship/forest-analysis-inventory/growth-yield/modelreview_finalreport_march_2021.pdf. [AGY]
- **Variant/region:** BC growth and yield models: VDYP, TASS/TIPSY, PrognosisBC/FVS-BC, MGM, SORTIE-ND.
- **What it is:** Independent program review.
- **Mortality/ingress findings:** FVS "has been calibrated in BC for the ICH and IDF subzones. Legacy models are available for the ESSF, MS and PP. **Partial development occurred for the SBS and SBPS.**" Extensions (FFE-Carbon, Climate-FVS, root disease, dwarf mistletoe, budworm) "have had minimal testing". "PrognosisBC has not been enhanced since the release of the Windows VISTA operating system" (as of 2021; ESSA later released FVS-BC FS2022.4). "It is not designed to be initiated from bare ground but rather from tree lists. It does have an establishment extension but in the short term it could be initiated from tree lists from ground surveys..."
- **Classification:** Program/design limitation; independent confirmation of partial development and minimal extension testing.
- **Verification:** Full text read.

**D14. Bourgeois, W., Binkley, C., LeMay, V., Moss, I., and Reynolds, N. 2018.** *British Columbia Forest Inventory Review Panel technical background report.* Prepared for the Office of the Chief Forester Division, BC Ministry of Forests, Lands, Natural Resource Operations and Rural Development. December 2018. URL: https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/stewardship/forest-analysis-inventory/brp_technical_document_final.pdf. [AGY]
- **Variant/region:** BC forest inventory and growth/yield program.
- **What it is:** Expert panel review of inventory and growth/yield.
- **Mortality/ingress findings:** "PrognosisBC is a useful software platform and more areas in BC should be calibrated to it." But: "There are too many unsubstantiated assumptions and extrapolated data use..." and "Models do not sufficiently account for forest dynamics (biotic/abiotic stand disturbance factors)." The report also flags that legacy PSPs have been dropped or not remeasured, undermining calibration data.
- **Classification:** Program critique/context.
- **Verification:** Relevant sections read.

**D15. Moss, I. [2011].** *Forest, stand and tree growth and yield in British Columbia.* Background brief, BC Forest Conversation / Healthy Forests–Healthy Communities. 5 pp. URL: http://bcforestconversation.com/wp-content/uploads/Forest-stand-and-growth-and-yield-in-BC.pdf. [AGY/NGO]
- **Variant/region:** BC growth and yield program.
- **What it is:** Practitioner critique of the provincial program.
- **Mortality/ingress findings:** "There is no feedback loop to assess the veracity of forest level projections." The PSP network "is not being maintained by way of carrying out re-measurements and by way of periodically reporting the actual results relative to forecasts..." and "There is no funding currently devoted to this program." This is context for why mortality/ingress calibration data are scarce.
- **Classification:** Program critique/context.
- **Verification:** Full text read. Publication date inferred from PDF metadata (2011); verify before citing.

**D16. Bealle Statland, C.A. 2010.** GYMP: development of the PrognosisBC model for complex stands. [AGY]
- **Variant/region:** PrognosisBC; BC.
- **What it is:** Cited in the BC Forest Inventory Review Panel reference list. I could not retrieve it.
- **Mortality/ingress relevance:** Likely documents PrognosisBC development for complex stands; not independently verified.
- **Classification:** Unknown.
- **Verification:** Secondary citation only (Bourgeois et al. 2018 reference list). **Unverified.**

**D17. Hassani, B.T., LeMay, V., Marshall, P.L., and others. 2004.** Regeneration imputation models for complex stands of southeastern British Columbia. *The Forestry Chronicle* 80(2): 271–278. [PR]
- **Variant/region:** PrognosisBC; ICH, IDF, MS, BC.
- **What it is:** Development of Most Similar Neighbour (MSN) imputation for natural regeneration, the replacement for the failed RegEst calibration.
- **Ingress finding:** MSN predicts several regeneration variables at once by matching a target stand to the most similar reference plot. It requires a large, ecologically representative regeneration database; "its ability to accurately predict regeneration in under-represented ecological conditions is therefore limited" (Sattler et al. 2009, citing Moeur and Stage 1995; Hassani et al. 2004). It is a donor/imputation method, not a process model of seed source, dispersal, or establishment.
- **Classification:** Design limitation (statistical imputation; reference-domain dependence).
- **Verification:** Citation from the 2017 FVS e-Conference reference list; full text not read. Additional MSN reports by Martin et al. (2002) and Froese et al. (2003) are cited in Zumrawi et al. (2005a) but were not verified.

---

## 3. Synthesis: documented failure modes

### 3.1 Mortality

**M1. Range extrapolation: the model fails at low basal area.**
The clearest BC statement is in the PrognosisBC v4.2 description: bare-ground and low-BA simulations were "clearly invalidated by excessive mortality", because "stand basal area lay well below the range of basal area used to fit the mortality models" (ESSA 2011, §2.1). The practical threshold given is 10 m²/ha. This is not a subtle residual bias; it is a structural failure when projecting young stands, heavy partial cuts, post-disturbance regeneration, or short-suppression stands. For PSP calibration, low-BA plots are exactly where mortality has the largest relative effect on future trajectory.

**M2. The "approach to BAmax" term is a mechanical ceiling, not a mortality process.**
The model increases mortality smoothly as BA approaches a variant/site-series BAmax, and at BAmax "mortality removes all stand growth in excess of the maximum" (ESSA 2011, §3.11). This produces convergence to a prescribed carrying capacity. In unadjusted runs, the broader FVS literature describes the same behaviour: "The default mortality paradigm embedded in FVS allows stands to progress to full site occupancy (i.e. maximum stand density). However, this ceiling does not represent the generalized endemic growth pattern typified by inventory data sets used for landscape assessments" (Vandendriesche 2010). The result is too few trees and too much volume concentrated in survivors: "tree frequencies steadily decline over time. Growth dynamics are accumulated in the survivor trees resulting in excessive stand volume" (Vandendriesche 2010).

**M3. Missing disturbance mortality is a design feature, not a bug — but it is fatal if extensions are not calibrated.**
"Base model mortality predictions are intended to reflect background or normal mortality rates. Increases in mortality from insects, pathogens, and fire are accounted for in the various FVS extensions... Mortality from other causes, such as logging damage, animal damage, or wind events, needs to be simulated with FVS keywords" (Dixon 2002, §7.3). In BC, the linked extensions (FFE-Carbon, Climate-FVS, western root disease, dwarf mistletoe, and budworm) "have had minimal testing" (Penner 2021). A PSP calibration that ignores chronic disturbance will tend to under-predict mortality in exactly the stands where BC's disturbance regimes matter.

**M4. Coarse species/size pooling and borrowed parameters.**
The BC variant uses a simple tabular mortality model for conifers: four DBH classes (<10, 10–25, 25–40, >40 cm) crossed with five BA classes (<20, 20–30, 30–40, 40–50, >50 m²/ha), with some species grouped or assigned another species' table (ESSA 2011, Table 3.20). The variant description says a comprehensive logistic model was attempted but "failed to give reliable appropriate behaviour beyond the range of the fitting data" (ESSA 2011, §3.11). The tabular form cannot represent continuous size effects, species mixing, or fine-scale competition; hard class boundaries can produce discontinuities. In SBS/SBPS, whole mortality models were borrowed from IDF/ICH because of insufficient PSPs (Marshall and Lee 2011). Temesgen and Mitchell (2005) show that a defensible individual-tree BC mortality model can be fitted from 29,773 PSP trees, which suggests that continued reliance on borrowed tables in some subzones is an implementation gap as much as a data gap.

**M5. Density-dependent mortality thresholds are arbitrary and hard to calibrate.**
In SDI-based variants, mortality switches on at 55% of SDImax and becomes severe at 85%. Radtke et al. (2012) found that "in plots with high initial stand densities, notable gains in accuracy were achieved by relaxing thresholds that activated a density-dependent mortality algorithm", but also that lowering thresholds increased RMSE and "exacerbated" residuals in other conditions. The thresholds are conventional defaults, not locally calibrated parameters; they are model architecture. FVS-NE's Maine evaluation concluded that "adjusting SDImax directly may ultimately prove a better solution, if base mortality functions in FVS-NE are not refit" (Frank and Castle 2024).

**M6. Young stands and early cohort dynamics are a particular failure zone.**
Lacerte et al. (2004) found "the decrease in stand basal area at young ages was inconsistent with the normal development pattern... attributed to deficiencies in the prediction of mortality" in northern Ontario boreal stands. FVS-NE's uncalibrated projection on the central Maine eastern white pine control plots had a TPA bias of +183.5 stems/ac (calibrated +48.6), i.e. far too little mortality (Ray and Seymour 2017, Table 1). Ray et al. (2008) found that "mortality rates among the newly recruited saplings were overestimated" even as recruitment itself was biased. The direction of error is not universal; the consistency is that early-life mortality/recruitment is poorly constrained.

**M7. Mixedwoods and uneven-aged stands are poorly served by legacy equations.**
The Acadian variant was developed because FVS-NE had "potential shortcomings... particularly for the spruce-fir forest type" (Weiskittel et al. 2017). The companion eastern white pine paper states: "Due to unresolved issues with the mortality function for the ACD, this aspect was handled by the base model option" (Ray and Seymour 2017, in the same proceedings). ACD's own claim is that a "multi-stage approach to mortality predictions outperforms more traditional approaches including methods currently used by other FVS variants" (Weiskittel et al. 2017). In BC, complex stands are the raison d'être of PrognosisBC, yet the mortality model remains a borrowed/coarse table in several zones.

**M8. The standard calibration workflow does not calibrate mortality.**
FVS self-calibration adjusts small-tree height and large-tree diameter growth, not mortality directly (Smith-Mateja 2025). Mortality is adjusted only indirectly via `SDIMAX`, `BAMAX`, or multipliers. A calibration project that follows the standard workflow can therefore produce a "calibrated" variant with essentially unchanged mortality. This is a process design limitation with direct consequences for PSP calibration.

**M9. Short growth-focused validations can mask mortality error.**
Marshall et al. (2008) found acceptable 11-year stems-per-ha predictions in IDF, but the evaluation did not activate recruitment and focused on dbh/volume. A model can match 10-year volume while having compensating errors in mortality and ingress; only transition-level tests (survival by species/size/BA, ingress by species/size) can detect this.

### 3.2 Regeneration and ingress

**R1. There is only one full establishment model in the FVS family.**
"Despite more than three decades of development, only one full-featured regeneration model has been developed for the Forest Vegetation Simulator (FVS)" (Robinson 2008). "Among the 20 regional variants of FVS, only five support full establishment models" (Ray et al. 2008). Everywhere else, ingress is a user assumption.

**R2. The partial model has no natural-regeneration equations.**
"Other than stump and root sprouting, the partial establishment model does not have equations for predicting natural regeneration. Whenever natural regeneration is desired, the user must schedule it using the `NATURAL` keyword record" (Dixon 2002, §5.4.5). This is the operational reality for most variants, including FVS-BC.

**R3. BC deliberately deactivated automatic regeneration.**
The NI RegEst model "does not reliably reproduce the mixture of species and density observed in the surveys. Consequently, automatic regeneration has been deactivated in the BC variant" (ESSA 2011, §2.2). The source code confirms it: `LINGRW=.FALSE.`, `LAUTAL=.FALSE.`, `STOADJ=0.0` in `ESINIT` (FVS-BC `esinit.f`, lines 29–32). This is the single strongest BC-specific fact for the "ingress is not a model output" argument.

**R4. The initial BC calibration of the NI regeneration model failed and was not implemented.**
"The initial calibration of the Northern Idaho regeneration model was not satisfactory for use in BC (Boisvenue 1999), and was not implemented" (Zumrawi et al. 2005a). Boisvenue's thesis shows why: the original NI equations were "outperformed by either the refitted equations or equations with Nelson-based variables", and the BC/Idaho ecosystem classification mismatch "contribute[s] to errors in model predictions" (Boisvenue 1999).

**R5. BC's replacement is donor-based imputation, not a process model.**
MSN matches a target stand to the most similar reference plot and copies its regeneration. It requires a large, representative regeneration database; "its ability to accurately predict regeneration in under-represented ecological conditions is therefore limited" (Sattler et al. 2009). It does not model seed source, dispersal, fecundity, mast, microsite, or establishment mechanisms. It did not extrapolate reliably to novel conditions such as the MPB epidemic: "the model... consistently underestimated regeneration of the shade intolerant species, even when data from MPB-affected stands was used" (Zumrawi et al. 2005a).

**R6. The MPB case is a documented failure of the BC ingress system.**
"The lack of an effective sub-model capable of predicting the abundance and species composition of natural regeneration for MPB-attacked stands is a major limitation of PrognosisBC" (Sattler et al. 2009). The linked SORTIE-ND approach "provided slight improvements... overall results were generally poor"; lodgepole pine densities were "largely underestimated for smaller trees." This matters because post-MPB stands are a large share of BC's calibration and projection workload.

**R7. Recruitment/early survival is a weak link even where a full establishment model exists.**
Ray et al. (2008) found sapling recruitment averaged 47% (production) and 206% (beta) of observed, with overestimated mortality among recruits and mismatched species composition. Limiting input regeneration reduced bias but only modestly improved accuracy. This is not a BC-specific result, but it shows that "full establishment model" does not mean "accurate ingress".

**R8. The 20-year regeneration period and the ingrowth concept are crude.**
FVS fixes the regeneration period at 20 years and calls subsequent regeneration "ingrowth" (Dixon 2002, §5.4.1). Regeneration is added at the end of the cycle; there is no continuous seed rain and no dispersal kernel. Overstory density and species enter only as statistical predictors, not as an explicit seed-source mechanism. The model is plot-based and statistical. This is adequate for even-aged silviculture in the regions where RegEst was fitted; it is not adequate for continuous-cover, mixedwood, or post-disturbance ingress.

**R9. Data requirements for a real establishment model are enormous.**
The original Ferguson model required "over 12,000 regeneration plots... in 500 stands" (Robinson 2008). BC's regeneration calibration data were temporary plots concentrated in a few subzones (Lencar 2003). This is why BC chose imputation rather than refitting a full establishment model — a rational response to a data constraint, but it leaves ingress without a mechanistic model.

**R10. Models used for regeneration assessment often do not represent juvenile mortality or ingress at all.**
Dempster (2024): "existing growth and yield models, used to predict whether regeneration performance will meet management objectives, do not adequately represent juvenile mortality, ingress of natural regeneration, stand density, and the responses of ingress and mortality to reforestation treatments." This is a general Canadian statement, not FVS-specific, but it closely matches the FVS-BC situation.

---

## 4. Strongest evidence, with caveats

### 4.1 "Mortality is a weak spot" — strongest evidence

1. **BC low-BA failure (direct, primary):** "predictions for some species were clearly invalidated by excessive mortality at very low stand basal area... stand basal area lay well below the range of basal area used to fit the mortality models" (ESSA 2011, §2.1). This is the strongest BC-specific mortality critique because it is a documented model failure, not an inference.
2. **No local mortality models in SBS/SBPS (direct, primary):** "There were insufficient permanent sample plot data available in all the SPS [sic] and SPBS subzones to develop large tree height growth or mortality models" (Marshall and Lee 2011). Whole models were borrowed from IDF/ICH.
3. **Default FVS mortality drives stands to full occupancy (direct, generic):** "The default mortality paradigm embedded in FVS allows stands to progress to full site occupancy... This ceiling does not represent the generalized endemic growth pattern..." (Vandendriesche 2010). The consequence is too few trees and too much volume in survivors.
4. **Young boreal stands (peer-reviewed):** "the decrease in stand basal area at young ages was inconsistent with the normal development pattern... attributed to deficiencies in the prediction of mortality" (Lacerte et al. 2004). Underpredicted stand density and BA.
5. **Under-mortality in FVS-NE (direct, recent):** "FIA mortality estimates exceed FVS-NE mortality estimates resulting in over-estimates of net growth across Maine" (Frank and Castle 2024). The proposed fix is to adjust SDImax or refit base mortality.
6. **Species/size failure in longleaf pine (conference):** "the mortality submodel was responsible for the over-predictions"; only an iterative empirical mortality rate was viable (DeRose et al. 2008).
7. **Density-dependent thresholds (peer-reviewed):** high-density plots required relaxed SDI thresholds to reduce bias, but the fix was not universally better (Radtke et al. 2012). The threshold architecture is arbitrary.
8. **Mixedwood mortality is unresolved in practice (conference):** despite ACD's new multi-stage mortality work, the eastern white pine evaluation had to fall back to the base model because of "unresolved issues with the mortality function for the ACD" (Ray and Seymour 2017).
9. **Calibration architecture (official):** FVS self-calibration does not calibrate mortality; it adjusts growth only (Smith-Mateja 2025). This is a structural reason why mortality remains weak after "calibration".

### 4.2 "Ingress is basically useless in many cases" — strongest evidence

1. **BC turned it off (direct, primary):** "the NI variant does not reliably reproduce the mixture of species and density observed in the surveys. Consequently, automatic regeneration has been deactivated in the BC variant" (ESSA 2011, §2.2). Source code confirms `LINGRW=.FALSE.` and `STOADJ=0.0`.
2. **The initial BC calibration failed (direct, primary):** "The initial calibration of the Northern Idaho regeneration model was not satisfactory for use in BC... and was not implemented" (Zumrawi et al. 2005a).
3. **Major limitation for MPB stands (direct, primary):** "The lack of an effective sub-model capable of predicting the abundance and species composition of natural regeneration for MPB-attacked stands is a major limitation of PrognosisBC"; linked-model results "generally poor" (Sattler et al. 2009).
4. **Most variants have no natural-regeneration equations (official):** the partial establishment model "does not have equations for predicting natural regeneration" (Dixon 2002, §5.4.5).
5. **Only one full model in the family (conference):** "only one full-featured regeneration model has been developed for FVS" (Robinson 2008); "only five [of 20 variants] support full establishment models" (Ray et al. 2008).
6. **Recruitment is quantitatively biased (conference):** 47% and 206% of observed recruitment; overestimated recruit mortality; mismatched species composition (Ray et al. 2008).
7. **General Canadian review (peer-reviewed):** models "do not adequately represent juvenile mortality, ingress of natural regeneration, stand density, and the responses of ingress and mortality to reforestation treatments" (Dempster 2024).
8. **Default FVS loses stems because ingress is absent (conference):** "most FVS variants include only the partial establishment extension that lacks automatic natural regeneration features. Thus, tree frequencies steadily decline over time" (Vandendriesche 2010).

### 4.3 Caveats and counter-evidence

- **Mortality is not uniformly bad.** Marshall et al. (2008) found "future stems per ha (or its corollary, mortality level) appeared to be acceptably predicted overall" in 11-year IDF validation, with a slight underestimate of future stems. Radtke et al. (2012) found baseline FVS-Sn within ±15% on >88% of 1,780 plots (average bias 3.5–4.1%). Canavan and Ramm (2000) found mortality errors "less consistent" rather than catastrophic. The correct claim is *conditional*: mortality is weak outside the calibration domain, in young/low-BA stands, in mixedwoods, and when disturbance is omitted.
- **Some "mortality" failures are really growth or survivor-bias failures.** Herbert et al. (2023) measures carbon in trees that remain alive; Bagdon et al. (2021) measure stand BA/carbon. Both conflate growth, mortality, and recruitment. They are consistent with under-mortality, but they do not prove it.
- **The BC evidence is mostly grey literature, small samples, and old.** The strongest statements come from agency reports (ESSA 2011; Marshall and Lee 2011; Zumrawi et al. 2005a), not peer-reviewed journal articles. Marshall et al. (2008) is the main independent BC validation and it is favourable for IDF mortality. Sample sizes are small (30 plots; 6 per thinning treatment). I found no modern, published, independent FVS-BC mortality/ingress validation in this search.
- **"Ingress is useless" is too strong as a general statement.** The full RegEst model is calibrated and operational in the NI/IE, Montana, and southeast Alaska variants. In BC, the right statement is: *automatic ingress is disabled, the replacement is donor-based imputation, and neither is a validated predictor for novel conditions.* Manual planting and `NATURAL` inputs work as scenario assumptions; they are not predictions.
- **Data scarcity is a confounder.** Some failures attributed to model structure are also failures of the calibration data: insufficient PSPs in SBS/SBPS, temporary plots for regeneration, legacy PSPs dropped or not remeasured (Bourgeois et al. 2018; Moss 2011). A better model cannot be fitted without better data, but the current model still fails.
- **Publication bias.** Failures are more likely to be written up than successes; the absence of a BC mortality critique for a given zone may mean "not tested" rather than "validated".

---

## 5. Implications for calibrating FVS-BC to PSP data

1. **Treat mortality as a calibration object, not a fixed submodel.** Fit or adjust mortality to PSP transition data by BEC zone/subzone × species group × DBH class × BA class. Do not assume the inherited/borrowed table is adequate. Where data permit, refit a logistic model in the spirit of Temesgen and Mitchell (2005) rather than relying on `BAMAX` alone.
2. **Stratify and test the low-BA domain explicitly.** Include young stands, heavy partial cuts, post-disturbance stands, and BA < 10 m²/ha. The BC documentation already flags this as the failure zone. If PSP data are thin there, say so and widen uncertainty; do not extrapolate silently.
3. **Separate background from density-dependent and disturbance mortality.** Use PSP remeasurements to estimate observed annual mortality by stratum; compare to FVS's background component and to the BAmax/SDImax adjustment. Where MPB, root disease, or defoliators are present, either run the extension or add explicit disturbance mortality; do not let the base model absorb it.
4. **Evaluate at the transition level, not just volume.** Test predicted survival, TPA change, BA change, QMD change, and species composition against holdout PSPs. A 10-year volume match can hide compensating mortality and ingress errors.
5. **Do not use the standard FVS self-calibration as a mortality calibration.** It adjusts small-tree height and large-tree diameter growth only, not mortality directly. If mortality is not explicitly fitted or adjusted, a "calibrated" run may have unchanged mortality.
6. **Treat ingress as an input or an external model.** FVS-BC's automatic regeneration is off. Use observed seedling/sapling counts from PSPs to initialize or ingrow; or use an external recruitment/imputation model with explicit reference-domain limits. Do not report FVS-BC ingress as a prediction.
7. **Bound the BAmax/SDImax assumptions with local data.** Vandendriesche's (2010) method — derive endemic maximum SDI/BA from the top 3% of inventory plots and set the density-mortality ceiling accordingly — is a practical stopgap. But document that it is a constraint, not an estimated mortality process.
8. **Test mixedwoods and uneven-aged stands separately.** These are the stands FVS-BC is meant to serve, and they are where the legacy mortality/ingress logic is least defensible. Use the Acadian and BC complex-stand evidence as a warning, not a template.
9. **Use long remeasurement intervals.** Short intervals (5–10 years) may not contain enough mortality/ingress signal, especially in mature stands. Where PSP remeasurement intervals are long, use them; where they are short, aggregate or use transition models.
10. **Document the evidence grade.** BC's mortality/ingress evidence is mostly grey literature and small-sample validation. A calibration report should distinguish "validated in BC", "borrowed from another variant", "mechanistically plausible but untested", and "known to fail outside the fitting range".

---

## 6. Verification notes and unverified sources

**Fully read (primary text):** Dixon 2002 (Essential FVS); Smith-Mateja 2025; ESSA 2011 (PrognosisBC v4.2); Marshall and Lee 2011; Zumrawi et al. 2005a; Lencar 2003; Marshall et al. 2008; Ray et al. 2008; Robinson 2008; Weiskittel et al. 2017; Ray and Seymour 2017; Affleck 2024; Frank and Castle 2024; Sattler et al. 2009; Vandendriesche 2010; Radtke et al. 2012; Penner 2021 (relevant sections); Bourgeois et al. 2018 (relevant sections); Moss 2011.

**Abstract/metadata only:** Hamilton 1986; Canavan and Ramm 2000; Lacerte et al. 2004; Russell et al. 2013; Herbert et al. 2023; Bagdon et al. 2021; Dempster 2024; Metsaranta et al. 2024; DeRose et al. 2008; Temesgen and Mitchell 2005; Boisvenue 1999; Sattler 2009; Lencar 2009; Crookston and Dixon 2005; Crookston et al. 2010.

**Secondary citation only (not independently retrieved; do not cite without checking):**
- Temesgen, H., and LeMay, V. 2000. Re-fitting the mortality model of PrognosisBC... (23 pp.; described as unpublished internal report).
- Robinson, D.C.E., and Kurz, W.A. 1998. Analysis of the Prognosis Regeneration Establishment Model behaviour with BC regeneration data (42 pp.).
- Robinson, D.C.E. 1997. Prognosis Southern Interior (SI 1.0g) geographic variant description (178 pp.).
- Zumrawi, A.-A., Marshall, P., Akindele, S.O., Ortlepp, S., and Thony, P. 2005. Calibrating PrognosisBC in the SBS and SBPS zones... (30 pp.; cited in Marshall and Lee 2011).
- Bealle Statland, C.A. 2010. GYMP: development of the PrognosisBC model for complex stands.
- Martin et al. 2002; Froese et al. 2003 (MSN regeneration reports cited in Zumrawi et al. 2005a; exact titles/years not verified).
- Ferguson, D.E., and Carlson, C.E. 1993 (series number INT-467 from a secondary reference list; full text not read).
- Stage 1973 (original report not read; citation standard).
- Wykoff, Crookston, and Stage 1982 (DOI verified; full text not read).
- Ferguson, Stage, and Boyd 1986 (metadata verified; full text not read).
- Snowdon 1997; Zumrawi, Stage, and Snowdon 2002 (citations confirmed in BC documents; full text not read).

**Code-level verification [CODE]:** FVS-BC `esinit.f` (lines 29–32) sets `LINGRW=.FALSE.`, `LAUTAL=.FALSE.`, `STOADJ=0.0`; `morts.f` contains a tabular mortality model and a Temesgen-fitted logistic survival relationship. These are local source checks, not publications. They corroborate, but do not replace, the documentary evidence.

**Known gaps in this review:**
- No full-text access to Temesgen and LeMay (2000), Robinson and Kurz (1998), or Robinson (1997); these are potentially the most direct BC mortality/ingress calibration reports.
- No full-text access to Lacerte et al. (2004), Herbert et al. (2023), Bagdon et al. (2021), Dempster (2024), or Temesgen and Mitchell (2005); findings are from abstracts/metadata.
- No systematic search of the BC a100 document repository beyond targeted documents; there may be additional regional calibration reports (e.g., ICHmw2, IDFdm, MS) not captured here.
- No attempt to evaluate the current FVS-BC FS2022.4 code against PSP data; this is a literature review, not a validation.

---

*End of report.*
