# BEC substitution: when the variant keeps the label and changes the model

Status: **recorded in provenance and in the support reasons.** No model changed.

## What happens

`becset.f` has a site-series table for the non-V3 zones (PP, MS, ESSF). A site series it does not
list is not refused: the routine rewrites the run's BEC to the default habitat, most often
`MSdk/01`, and says so once in the report:

```
THE BEC VARIANT PPxh2/01 HAS NO EXACT LARGE-TREE RECALIBRATION MAPPING IN
THE KAM REGION; SWITCHING TO BEC VARIANT MSdk/01 USING DEFAULT HABITAT TYPE= 660
```

The `STDINFO` echo still shows the requested label, which is why the existing "resolved BEC" check
did not see it. The run is not the zone the caller asked for.

## How far it reaches

| Requested | Engine BEC | Mapped? |
| --- | --- | --- |
| `PPxh2/01` | `MSdk/01` | no |
| `PPxh/01` | `MSdk/01` | no |
| `MSdm1/01` | `MSdk/01` | no (only `MSdm1/04` is listed) |
| `ESSFdk2/01` | `MSdk/01` | no |
| `ICHmw2/01`, `CWHvm1/01`, `SBSmw/01`, `BWBSmw/01`, `MHmm1/01`, `CDFmm/01` | unchanged | yes — the V3 zones return before the table |

The V3 zones are guarded at the top of `becset.f`, so the substitution only affects PP, MS, and ESSF,
which are the zones the support matrix already calls "via defaults".

## What changed

- `Provenance.bec_substitution` is `(requested, engine)` when the report carries the switch, and
  `None` otherwise. The record writes it as `{"requested": ..., "engine": ...}`.
- The support reasons for PP, MS, and ESSF now name the restriction: only the mapped site series
  run; an unmapped one is modelled as `MSdk/01`.
- Nothing is refused: the W2 zone prototype deliberately gives these zones a default habitat, and
  the tests that assert that behaviour still pass.

## What is still open

- The mapped-series list is small (11 labels). A PP or MS calibration cannot start until the zone's
  own site series map to the PP/MS habitat; until then those runs are MSdk runs wearing a PP label.
- `SDICAL` and the BAMAX table are keyed to the *engine* BEC, so the PP BAMAX values never apply to a
  substituted run. A PP cap fix is prepared but unshipped for that reason.
- A user who wants strict zone fidelity can read `bec_substitution` from the provenance record and
  refuse a non-null value.

## Reproduce

Run one `PPxh2` interval with `run_case` and read `result.provenance.bec_substitution`; the report
line above appears in `run.out`. The W2.3 subzone tests cover the fallback itself.
