# Data provenance and selection audit

## Data

- 4 cm PSP reference: 17,132 intervals / 5,732 sites / 139 BEC labels.
- ICHmw2: 978 intervals / 225 sites.
- Candidate evidence: Arrow and Cascadia, DBH >=4 cm, sites with >=5 intervals: 99 sites / 569
  intervals.
- Eligibility: initial BA >=15 m2/ha, initial QMD >=6 cm, dead BA / initial BA <=0.4.
- Excluded: Okanagan and Kootenay Lake TSAs, sites with fewer than five intervals, and disturbance-
  dominated intervals.

The bundle cannot enforce the five-interval or disturbance filters; they are evidence limits.

## Selection

- Grid: baseline and `BAIMULT` 0.5, 0.75, 1.0, 1.25.
- Arrow-only selection on 66 well-sampled sites: `BAIMULT 0.75` wins with 63/66 site passes
  (BA -0.8%, TPH -3.6%).
- The selected value is frozen and tested once on 33 Cascadia sites: 29/33 site passes
  (BA +1.1%, TPH -3.1%).
- No refit on Cascadia; no test-set tuning.

The original bundle parameter was selected on all well-sampled sites; the Arrow-to-Cascadia
holdout was added afterward to provide a genuine spatial check. This is stated rather than hidden.

## Checksum

The candidate evidence checksum is `sha256:9ea62944e9939253e44950febdddfd3af8e3bfac67d38fb457467d1c1cdb86f5`.
