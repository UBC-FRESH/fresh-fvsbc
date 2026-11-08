# D9.47 BC MPB extension runs a BC projection

Status: **MPB keyword is active; the test stand has no eligible PL host**
Date: 2026-11-08
Build: D9.46 BC MPB extension
Test case: `runtime/internal-increment-test/4009738_1_2008_2014-incr`

## 1. What ran

Using the D9.46 extension:

- the BC projection loads and completes (`ncyc=1`, `end=0`);
- an `MPB` block is parsed;
- `MPBSTART` schedules a 2008 outbreak;
- `BEETLES` reads 100.0 starting beetles per acre;
- `PRBSCALE` reads 1.0.

The activity log records:

```
MPB      MPBSTART  2008  NOT DONE
WARNING: A REQUESTED MOUNTAIN PINE BEETLE OUTBREAK CAN NOT BE SIMULATED.
```

The test stand is an ICHmw2 stand with PW/FD/AT/HW in the tree list and no lodgepole pine. The
warning is consistent with a host-eligibility failure, not a missing or stubbed MPB module.

## 2. What this establishes

- The real LPMPB extension is linked into the BC variant.
- The BC `MPB` keyword reaches the extension.
- The keyword parser reads `MPBSTART`, `BEETLES`, and `PRBSCALE`.
- The extension runs inside a BC projection and reaches its outbreak scheduler.

It does not establish a PL mortality calibration. The next test needs a post-2000 PL stand from the
PSP record.

## 3. Next

- Select a post-2000 PL interval with enough live PL and at least one valid MPB host.
- Run the BC MPB extension with outbreak options.
- Compare predicted PL mortality to the D9.45 observed 0.506.
- Sweep only options supported by the PSP record.
- Keep the provincial background model and local calibration for non-PL species.

## 4. Limits

- No PL test stand yet.
- The BC species-to-MPB surrogate map needs review.
- MPB outbreak timing/severity is not yet calibrated to the PSP record.
- No integration or bundle.

## 5. Claim boundary

This is a runtime integration test. It does not support a yield, AAC, legal, or whole-block claim,
and it is not a certificate.
