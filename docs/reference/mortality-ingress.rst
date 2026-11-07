Mortality and ingress in FVS-BC
================================

This page maps the FVS-BC mortality and ingress logic and records the structural reasons it is hard
to calibrate to PSP data. The full source map is in
``notes/reference/calibration/fvs-mortality-code.md``; the literature review is in
``notes/reference/calibration/fvs-mortality-lore.md``; the cross-model design is in
``notes/reference/calibration/fvs-mortality-ingress-upgrades.md``.

The source claims below refer to the pinned FVS tree at ``ef5fa847`` and the BC variant in
``canada/bc``. Check the pinned source before quoting line numbers.

Why this matters
----------------

FVS-BC does not contain a general mortality hazard or an automatic recruitment model. It contains:

* a small BEC × BA × DBH mortality table, with a legacy Hamilton fallback and a density cap;
* a keyword-only establishment path, where the user supplies ``PLANT`` or ``NATURAL`` counts.

A calibration layer that only changes ``BAIMULT``, ``BAMAX``, or ``MORTMULT`` cannot repair a
missing recruitment process or a mortality table with no site, climate, crown, or growth terms. The
two errors are confounded: missing ingress forces a lower mortality multiplier to match BA, and a
biased mortality table forces a recruitment rate that is not biologically meaningful.

Mortality flow
--------------

.. code-block:: text

   GRINCR
     -> DGDRIV          diameter growth
     -> HTGF            height growth
     -> REGENT          small-tree growth
     -> MORTS           mortality
          -> LV2ATV?    legacy Hamilton model
          -> V3 table   PW/LW/FD/BG/HW/CW/PL/SE/PY
          -> logistic   EP/AT/AC/OH (four BEC classes)
          -> BAMAX / SDIMAX cap
          -> MORTMULT / FIXMORT

Key facts:

* ``MORTS`` is variant-specific. BC calls ``canada/bc/morts.f`` from
  ``canada/bc/grincr.f`` after diameter growth, height growth, and small-tree growth.
* The V3 table is indexed by **two BEC classes** (ICH/IDF; SBPS maps to IDF and SBS to ICH), five
  BA classes, and four DBH classes. Subzone and site series do not enter.
* The V3 table has no site index, climate, crown ratio, recent growth, or species-specific
  competition term. The legacy fallback has a site-potential and growth term, but it is not the main
  BC path.
* Mortality is applied deterministically as an expected fraction; there is no stochastic
  thinning.
* Startup does not fit mortality. ``CRATET`` initializes density and growth but never calls
  ``MORTS``.
* ``MORTMSB`` is parsed but not read by BC mortality.
* The only runtime levers are ``BAMAX``, ``SDIMAX``, ``MORTMULT``, and ``FIXMORT``. The actual
  table coefficients, ``PMSC``/``GMULT``/``REIN``/``POT``, and the logistic coefficients are not
  exposed.

Ingress flow
------------

.. code-block:: text

   ESTAB block
     -> esin.f reads PLANT / NATURAL lines
     -> estab.f creates trees
          DBH = 0.1 in
          height = supplied or random
          IESTAT = 0
     -> ESGENT / REGENT grows the new trees to the end of the cycle

Key facts:

* The BC build compiles the **STRP** establishment path, not the old ``canada/bc/estab.f``.
* Automatic natural regeneration is disabled: ``STOADJ = 0``, ``LINGRW = .FALSE.``,
  ``LAUTAL = .FALSE.``, the best-tree block is removed, and ``INGROW`` is a no-op.
* ``PLANT`` and ``NATURAL`` are the only ways to add trees in the current build.
* There is no seed source, parent-tree, dispersal, germination, species establishment probability,
  or competition response. ``NATURAL`` only carries cycle, species, stems, survival, and an optional
  shade code.
* Sprouting is on by default for EP/AT/AC/OH, but the rules are generic.
* The BC metric reader expects the ``NATURAL``/``PLANT`` stems field in **trees per hectare**.
  ``esin.f`` divides by ``HAtoACR`` internally. The wrapper previously pre-converted to trees per
  acre, delivering 2.471× too few stems; that was fixed in D9.24.

Documented weaknesses
---------------------

The literature review separates direct FVS-BC evidence from broader FVS evidence. The strongest
direct points:

* PrognosisBC's own variant description warns that low-BA projections were "clearly invalidated by
  excessive mortality" because those stands were below the range used to fit the mortality models.
* Marshall and Lee (2011) report insufficient PSPs to develop SBS/SBPS large-tree mortality or height
  models; IDF/ICH models were borrowed.
* The original Northern Idaho regeneration model "was not satisfactory for use in BC" and was not
  implemented. The replacement is donor-based, not a seed-source model.
* Lacerte et al. (2004) attribute young-stand BA decline to mortality deficiencies.
* Vandendriesche (2010) shows default FVS mortality drives stands to full occupancy and biases
  volume.
* Hülsmann et al. (2017) find mortality prediction improves when individual growth and competition
  are included and models stay within an ecological zone.
* Lappi and Pukkala (2020) show ingrowth is zero-inflated and over-dispersed; fixed-effects models
  can be unbiased, while mixed models can be biased in marginal prediction.
* Bugmann et al. (2019) show mortality submodels that fit history can diverge 10–40% per century
  under current climate and 20–170% under climate change.

The full annotated bibliography, with DOIs and caveats, is in
``notes/reference/calibration/fvs-mortality-lore.md``.

What other models do better
---------------------------

The comparison report covers SILVA, BWINPro/TreeGrOSS, MOSES, PICUS, SORTIE-ND/BC, iLand, FORMIND,
TASS/TIPSY, PrognosisBC, MGM, Organon, and the FVS establishment model. The common pattern:

* **Mortality** is a discrete-time survival model with individual size, competition, growth, and
  site/climate covariates, often with species and site random effects.
* **Ingress** is a hurdle or zero-inflated count model with an explicit seed-source/parent-tree term,
  overdispersion, and a real probability of zero.
* **Validation** is by site/region and time, not by a single pooled bias.

Recommended core functions
--------------------------

``BCMORT``
   A hierarchical discrete-time survival model on the complementary log-log scale:

   .. code-block:: text

      log(-log(1 - p_dead)) =
          a_species
        + f(DBH, BAL, BA, relative DBH)
        + b_growth * recent_growth
        + b_crown * crown_ratio
        + b_site * site_index
        + b_climate * climate_moisture
        + u_BEC + u_site

   Optional two-component background + stress hazard. Optional stochastic thinning that preserves
   the expectation. Coefficients and random effects come from a versioned calibration bundle; they
   are not hard-coded.

``BCINGR``
   A hurdle/zero-inflated negative-binomial recruitment model:

   .. code-block:: text

      seed_rain = sum_over_trees(fecundity * crown_area * dispersal_weight)
      P(recruit > 0) = logit(a + b_seed * log1p(seed_rain) + b_BA * BA + ...)
      E[recruits | >0] = exp(a + b_seed * log1p(seed_rain) + b_site * SI + ...)
      recruits ~ ZINB(p_zero, mu, alpha)

   The stand-level seed-rain index is the distance-independent approximation. Establishment occurs
   at a defined size threshold, not at DBH 0.1 with a random height.

Architecture
------------

* Keep ``MORTS`` and ``ESTAB`` as entry points; replace their internals.
* Load coefficients from a versioned external bundle, not from source constants.
* Add diagnostics tables for per-tree survival probability, expected vs realized mortality, seed
  rain, and recruitment by species.
* Add a domain/envelope guard that refuses low-BA or out-of-range stands.
* Prototype ``BCINGR`` through the existing ES1/ES2 external-model interface before porting it to
  Fortran.
* Do not use per-BEC separate models, a free year multiplier, or stochasticity to hide bias.

Validation
----------

1. Fit survival on tree-level PSP transitions by BEC × species × size × competition.
2. Fit recruitment as a hurdle/ZINB on plot-level new stems, with seed rain and site covariates.
3. Validate by TSA and time; report BA, TPH, QMD, height, volume, and calibration coverage.
4. Compare against the current fixed-multiplier candidates.
5. Only then consider a joint mortality/ingress calibration and an unsigned bundle.

The unit bug
------------

The BC metric build reads ``NATURAL``/``PLANT`` stems as trees per hectare. The wrapper previously
converted TPH to TPA, so every ingrowth line delivered 2.471× too few trees. This was confirmed by a
controlled run (``NATURAL 1 FD 100 100`` produced ``TphAll = 100``) and fixed in D9.24. All
ingrowth-based calibration evidence from before D9.24 must be re-run; the ICHmw2 and CWH candidates
do not use ingrowth and are unaffected.

Full notes
----------

* ``notes/reference/calibration/fvs-mortality-lore.md``
* ``notes/reference/calibration/fvs-mortality-code.md``
* ``notes/reference/calibration/fvs-mortality-ingress-upgrades.md``
