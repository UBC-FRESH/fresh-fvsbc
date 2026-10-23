# License analysis for fresh-fvsbc

Decision: `fresh-fvsbc` is MIT. This note records the check behind that decision, its sources, and what
remains uncertain.

Date: 2026-10-21
Related: ADR 0001, ADR 0002, ADR 0003

## What fresh-fvsbc depends on

`fresh-fvsbc` does not reimplement the FVS build or its bindings. It pins a fork of PyFVS, which builds FVS
from a fork of the USDA source. Three licenses therefore matter.

| Component | License | Source | Obligation on `fresh-fvsbc` |
| --- | --- | --- | --- |
| FVS, USDA Forest Service | U.S. public domain | `license.txt` at the repository root | None |
| FVS fork, `forest-modeling/ForestVegetationSimulator` | Same public-domain notice | `license.txt` at the repository root | None |
| PyFVS, `forest-modeling/PyFVS` | MIT, copyright 2021 Forest Modeling | `LICENSE` | Retain the copyright and permission notice where its code or binaries are distributed |

## How each fact was read

- The USDA notice was read at
  `https://github.com/USDAForestService/ForestVegetationSimulator/blob/main/license.txt`. It states that
  materials produced by U.S. Federal employees as part of their official duties are not entitled to
  domestic copyright protection and are therefore in the U.S. public domain, and that FVS "is released
  without any conditions upon its use".
- The same notice is present at the root of the `forest-modeling` fork. The fork adds no separate
  `LICENSE`. The GitHub license API reports `NOASSERTION` for it, which reflects an unrecognized notice
  rather than a restriction.
- The PyFVS license was read at `https://github.com/forest-modeling/PyFVS/blob/main/LICENSE`. The GitHub
  license API reports `MIT` for both `forest-modeling/PyFVS` and `UBC-FRESH/PyFVS`.

## Copyleft check

The FVS repository was searched for copyleft markers. Each query returned zero results:

| Query | Result |
| --- | --- |
| `"General Public License"` | 0 |
| `"GNU Lesser"` | 0 |
| `SPDX-License-Identifier` | 0 |

The BC variant's source list references one third-party component: `dbsqlite`, which is SQLite. SQLite
is in the public domain. The remaining directories that the BC build compiles (`base`, `fire`, `canada`,
`rd`, `metric`, `common`, `strp`, `mistoe`, `vbase`, `pg`, `clim`, `ie`, `vie`, `vws`, `vstrp`,
`volume`) hold FVS source.

## The caveat in the FVS notice

The USDA notice adds that the package "may include certain open source components that are subject to
open source licenses". The copyleft check found none in the FVS tree, and the only third-party component
in the BC build is SQLite, which is in the public domain.

Not verified: no `FVSbc` has been built, so the linked object files have not been inspected. A build can
pull in a system library that the source tree does not show. Re-check at the first build.

## Conclusion

MIT is compatible. FVS imposes no conditions, and MIT satisfies the one obligation that PyFVS carries.
MIT also matches the lab's other packages, including `ubc-fresh-dev-workflow` and PyFVS itself.
