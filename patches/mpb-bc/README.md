# BC MPB build patch

This patch links the real LPMPB extension into the BC variant instead of
`fvs/base/exmpb.f`.

The banked CI form is `notes/reference/calibration/d9-mpb-bc.patch.gz`; it is
applied by `.github/workflows/ci.yml` and `.github/workflows/wheels.yml`. The
files here are the readable copy.

## Apply

Use the pinned PyFVS source tree (`e95172b` in the project pins):

```sh
cp mpblkdbc.f fvs/lpmpb/mpblkdbc.f
patch -p1 < FVSbc_sourceList.patch
SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0 meson setup build-mpb -Dfvsvariants=bc
ninja -C build-mpb
```

The source-list patch:

- removes the `exmpb.f` stub;
- adds the `fvs/lpmpb` sources;
- keeps exactly one MPB block-data file, the BC one;
- adds `fvs/wsbwe/txnote.f` for the `TXNOTE` symbol used by `MPBIN`.

## Verify

```sh
nm -D build-mpb/fvsbc*.so | grep txnote_
```

The symbol should be defined. The extension should load as a Python module.

## Boundary

This is an external build patch. It is not yet wired into the `fresh-fvsbc`
wrapper, and the stock BC binary does not carry it.
