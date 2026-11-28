# Fire-response validation from the full PSP extent

Status: **validation set materialized; the in-interval fire sample is too small to fit a term.**
No engine or bundle change ships.

## 1. What was fetched

OpenMaps WFS, full PSP bounding box (EPSG:3005 565608,387544,1840073,1671680):

| Layer | Features |
| --- | ---: |
| BC Wildfire Fire Perimeters – Historical | 24,751 |
| Fire Burn Severity – Historical | 935,082 province-wide; 93,573 returned for the 305 fires that contain PSP sites |

The fire perimeters were paginated at the server's 10,000-feature cap. The burn-severity endpoint
returns a 500 when `bbox` and `CQL_FILTER` are combined, so the severity query used
`CQL_FILTER=FIRE_NUMBER IN (...)` in batches without a bbox.

## 2. Join result

- 4,957 calibration site points.
- **1,161 site–fire pairs** at 1,030 sites, across **305 fires**.
- Burn severity overlaps **96 site–fire pairs at 95 sites** (30 fires):
  high 13, medium 38, low 20, unburned 25.
- Adding the South Coast cutblocks gives **100 observations at 99 sites** (96 fire, 4 harvest).
- The harness reports **6 events inside calibration intervals**: 4 fire, 2 harvest, at 6 sites.

## 3. The in-interval fire events

Only four fire events fall between a site's two visits. One is unburned, and one shows no BA loss:

| BEC | Severity | Interval | BA0 → BA1 | TPH0 → TPH1 | Dead BA / TPH |
| --- | ---: | --- | ---: | ---: | ---: |
| BWBSmw | 0.66 | 22 yr, fire in 2022 | 55.4 → 14.9 | 1,767 → 250 | 19.1 / 617 |
| ICHdw1 | 0.66 | 15 yr, fire in 2021 | 33.2 → 24.5 | 1,910 → 481 | 9.7 / 234 |
| ESSFmv3 | 0.66 | 23 yr, fire in 2021 | 31.8 → 52.8 | 7,128 → 5,678 | 0.2 / 25 |
| IDFxw | 0.00 | 20 yr, fire in 2017 | 12.1 → 16.2 | 2,271 → 2,242 | 0.1 / 100 |

The ESSF interval has the fire year at the second visit, so its “post-fire” measurement is not a
post-fire stand. The IDF polygon is unburned by rating. That leaves **two** usable severity-rated
fire intervals, both medium severity.

## 4. Why no term is fitted

A fire-response curve needs more than two events, and those two are in different zones (BWBS,
ICH) with different fuel and stand structures. Fitting a severity multiplier on two intervals and
testing it on the same two would not be held-out evidence. The validation set is now ready; the
block is the number of in-interval fires, not the public data access.

No engine or bundle parameter changes. The existing disturbance wiring tests remain the only
fire-response check.

## Reproduce

- Fetch/join scripts: `~/workspace/bwbs-work/build_disturbance_observations.py` and the
  burn-severity batch query.
- Observations (contains PSP ids, kept outside the repo):
  `~/workspace/bwbs-work/disturbance-data/disturbance-observations-bc.csv`.
- Harness: `scripts/validate_disturbance.py --observations ... --intervals ...`.
