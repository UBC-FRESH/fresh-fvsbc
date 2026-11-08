# D9.46 BC MPB extension builds

Status: **the BC variant now links the real LPMPB extension; projection calibration is next**
Date: 2026-11-08
Code: `patches/mpblkdbc.f`
Build: external PyFVS source tree, variant `bc`

## 1. What was wrong

The shipped BC source list includes `fvs/base/exmpb.f`, a stub that:

- leaves `MPBINT`, `MPBOPS`, and `MPBOUT` empty;
- returns `L=.FALSE.` from `MPBGO`;
- makes the `MPB` keyword fail with `ERRGRO`.

The full extension is present in `fvs/lpmpb`, but it has no BC block data. That is why the
post-2000 PL failure could not be addressed by the BC binary.

## 2. What was built

1. Added a BC 15-species `MPBLKD` block data file: `patches/mpblkdbc.f`.
2. Replaced `../base/exmpb.f` in `FVSc_sourceList.txt` with the `../lpmpb/*.f` sources.
3. Kept exactly one `mpblkd*.f` block data file, the BC one.
4. Added `../wsbwe/txnote.f` for the `TXNOTE` symbol used by `MPBIN`.
5. Built the `bc` variant with meson/ninja.

The BC species mapping is:

- PW=1, LW=2, FD=3, BG=3, HW=3, CW=3, PL=7, SE=1, BL=3, PY=10, EP/AT/AC/OC/OH=3;
- `IDXWP,IDXWL,IDXDF,IDXLP,IDXPP = 1,2,3,7,10`.

## 3. Build result

- Meson setup: pass.
- Ninja compile/link: pass.
- `fvsbc.cpython-312-x86_64-linux-gnu.so` loads as a Python extension.
- `TXNOTE` is resolved; MPB entry points are linked.

The extension's F2PY `revise` signature differs from the installed PyFVS Python wrapper, so
`version_info` is not usable with that wrapper. The library itself loads and is ready for a
projection test. This is a build milestone, not a calibration result.

## 4. Next

- Run a BC projection with a real `MPB` keyword case.
- Validate against the D9.45 post-2000 PL intervals.
- Sweep the MPB outbreak options only where the PSP record supports them.
- Keep the provincial background model and local calibration for non-PL species.
- Do not integrate or issue a bundle until the PL/MPB test is complete.

## 5. Limits

- The BC species-to-MPB surrogate map is a first implementation; it needs a reviewer.
- The MPB model expects outbreak/beetle options that are not yet wired to PSP stands.
- No projection has been run with the new extension.
- The patch is against an external FVS source pin, not a tracked FVS source tree.

## 6. Claim boundary

This is a build and integration prototype. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
