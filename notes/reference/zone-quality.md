# Zone quality: one table for the eleven forested zones

Status: **measured on the released engine (`fresh-fvsbc-pyfvs 0.4.9`), base configuration where a zone
has no bundle.**

The purpose of this page is to replace a paragraph of caveats with numbers. Every row comes from
`scripts/run_calibration_probe.py` on the calibration dataset; the exact command is at the bottom.
The samples are not identical (different `--per-bec` and held-out splits), so compare magnitudes, not
decimal places.

| Zone | Path | Intervals | Fold | BA bias (m²/ha) | BA MAE | Bundle |
| --- | --- | ---: | --- | ---: | ---: | --- |
| IDF | V3 | 167 | train | −0.63 | 3.69 | none |
| ICH | V3 | 213 | train | −1.26 | 5.53 | none |
| CWH | V3 | 398 | 108 held out | −0.71 | 3.78 | `BAIMULT 8` + W21 small-tree density |
| SBS | V3 | 144 | 38 held out | −0.53 | 5.91 | `MORTMULT 1.85` + W22 BL density |
| BWBS | V3 | 94 | train | +2.31 | 6.71 | none |
| SBPS | V3 | 27 | 6 held out | +2.18 | 2.64 | `MORTMULT 2` |
| MH | V3 | 18 | 3 held out | +1.47 | 1.71 | `BAIMULT 8` |
| CDF | V3 | 30 | 16 held out | −3.12 | 3.46 | `BAIMULT 8` + `MORTMULT 0.5` FD/AC |
| MS | V3 | 134 | 19 held out | −2.83 | 3.75 | `BAIMULT 1.6` + recruitment |
| ESSF | V3 | 302 | 42 held out | −2.21 | 5.15 | `BAIMULT 2.5` + `MORTMULT 0.9` |
| PP | V3 | 25 | 5 held out | −2.53 | 2.53 | none |

## What the table says

- **Basal area is within about ±3 m²/ha everywhere except CDF**, whose −5.1 is one dense held-out
  site and 94 intervals in total.
- **The biggest residuals are in the newest zones** (ESSF, MS, PP) and in BWBS on the high side.
  None is worse than the pre-W15 baselines (−7 to −9), and all are on V3 now.
- **TPH is the larger error everywhere** (MAE 300–740). That is expected in these runs: the probes
  apply **no recruitment**, so any stand that gains stems is counted as a miss. The recruitment v1
  bundle (`recruitment-bc-v1-bundle.json`, scale 0.4) exists but is not part of these folds.
- **Small samples explain the spread**: SBPS is 27 intervals, MH 18, PP 25, CDF 30. A one-interval
  swing moves them by 0.2–0.5 m²/ha.

## What is not in the table

- **Validation tiers.** Every zone is support `C`; none has a signed A/B review. The `path` column is
  the machine-readable part (`support.ZONE_PATH`, checked against `becset.f` by
  `scripts/check_zone_paths.py`).
- **Disturbance.** These are untreated projections. Fire and harvest response is wired and
  unit-tested on BWBS, but uncalibrated.
- **Recruitment.** As above.

## Reproduce

A candidate file with no parameters is enough for the base rows:

```console
$ printf '[{"label": "base"}]' > /tmp/base.json
$ for zone in IDF ICH CWH SBS BWBS SBPS MH CDF MS ESSF PP; do
    python scripts/run_calibration_probe.py \
      --data-dir <calibration> --psp-dir <psp> \
      --out-dir probe-$zone --domain $zone --per-bec 10 \
      --candidates /tmp/base.json
  done
```

The held-out rows use the site lists in the matching `notes/reference/w*-*.md` note. The bundle rows
add the zone's bundle to the keyword set before the probe; the base rows do not.
