# D8.6 MH and CMA screens: no domain bundle

Build: `fresh-fvsbc-pyfvs 0.4.1`; wrapper `0.21.4`. Public tree detail only.

## MH

MH has three labels and 31 intervals across five TSAs. A CWH-style candidate
(`BAIMULT 7.0`, `MORTMULT 0.45`) was tested unchanged on each TSA.

| Holdout | Fold | n | BA bias | BA % | TPH bias | TPH % |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Sunshine Coast | test | 12 | +1.16 | +1.5% | +63.1 | +5.5% |
| Sunshine Coast | train | 17 | +2.23 | +2.8% | -263.6 | -8.7% |
| Fraser | test | 5 | +2.69 | +3.5% | -142.6 | -5.1% |
| Fraser | train | 24 | +1.60 | +2.0% | -125.5 | -5.9% |
| North Island | test | 5 | +0.11 | +0.2% | -317.1 | -7.2% |
| North Island | train | 24 | +2.14 | +2.6% | -89.1 | -4.9% |
| Arrowsmith | test | 4 | +0.57 | +0.5% | +63.0 | +5.5% |
| Arrowsmith | train | 25 | +1.98 | +2.7% | -159.1 | -6.5% |
| GBR North | test | 3 | **+7.22** | **+8.5%** | **-811.5** | **-22.0%** |
| GBR North | train | 26 | +1.16 | +1.5% | -49.6 | -2.4% |

Four TSA folds pass; **GBR North fails both BA and TPH**. The GBR test is only three intervals,
but it is the same failure pattern as CDF: a small TSA with different growth. No MH bundle.

## CMA

CMA has one label and six intervals, all North Island, 1977-1985. That is **validation-only**; no
capacity, growth, or mortality candidate is attempted.

## Decision

**No MH or CMA bundle.** MH needs a GBR-specific growth/mortality term or more GBR data; CMA has
only six intervals. Neither is a certificate. Dashboard: `OVERALL: GREEN`, every gate, before this
commit.
