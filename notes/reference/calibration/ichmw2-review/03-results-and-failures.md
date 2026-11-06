# Results, failures, and uncertainty

## Performance (99 sites / 569 intervals)

| Metric | Bias | MAE |
| --- | ---: | ---: |
| BA | -0.23% | 2.84 m2/ha |
| TPH | -3.44% | 216 TPH |
| QMD | +2.33% | 1.23 cm |
| Matched top height | -0.61% | 0.86 m |
| Merchantable volume | -7.54% | 46.1 m3/ha |

91/99 sites pass BA +/-10% and TPH +/-15%.

## Temporal checks

| Period | n | BA | TPH | QMD | Top height | Volume |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| >=2000 | 28 | +2.0% | -1.95% | +4.6% | -1.8% | -2.8% |
| >=2005 | 12 | +2.0% | -13.1% | +6.0% | -1.6% | +0.4% |

## Failures

The eight failing sites are well-sampled and split across Arrow and Cascadia. The main failure
directions are TPH underprediction and a smaller number of BA overpredictions. The failing-site table
is in the runtime evidence; site identifiers are intentionally not committed.

The site-cluster bootstrap intervals for BA and TPH include zero, so the pooled bias is not
precisely estimated. The temporal 2005 test has only 12 intervals and should be treated as weak
evidence.

## Uncertainty and limits

- No third TSA.
- Five-interval evidence limit is not enforced by the bundle.
- Only one temporal split is available.
- PSP volume only; non-PSP volume standards differ.
- The candidate is not a certificate.
