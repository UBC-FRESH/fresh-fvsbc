# ADR 0011: the BEC is a validated input

Status: proposed; accepted when the W1.1 pull request merges
Date: 2026-11-02
Issues: #289, #290

## Context

`fresh-fvsbc` is a wrapper for the BC variant, and the BEC is the input that
decides which maximum basal area, mortality, and growth behaviour the variant
uses. Two records disagreed about where that input comes from.

`docs/reference/keywords.rst` said a caller does not supply a BEC at all, and
that `SITECODE` supplies the habitat data. `canada/bc/initre.f` says otherwise:
option 14 concatenates the first two `STDINFO` fields and calls `HABTYP`;
option 138, `SETSITE`, does the same when it is given a habitat type.
`canada/bc/habtyp.f` searches that concatenation for a region, a zone, a
subzone, a slash, and a site series, and on any failure it calls its error path
and leaves the BEC at `ICHmw2/01`.

The consequence is not theoretical. The Knife Creek pilot wrote
`STDINFO 712,CHS131`, which does not resolve. FVS ran `ICHmw2/01` with a
maximum basal area of 89 m2/ha, not the IDFdk3 default of 53. The same 1993
tree list grew to 77.4 m2/ha under the legacy string and 49.6 m2/ha under
`CAR IDFdk3/01`. The corrected 200-year yields were roughly 353 to 589 m3/ha,
against 750 to 1,232 m3/ha on the old curves.

The package's own README, usage page, and smoke-run note used the legacy string.
A caller who copied them was not running the stand they thought they were
running, and nothing in the run said so.

## Decision

**The BEC is a required, validated input.** A BC run carries a `STDINFO` whose
first two fields the package parses as a `BecCode`: a region (`CAR`, `KAM`, or
`NEL`), a zone (`ESSF`, `ICH`, `IDF`, `MS`, `PP`, `SBS`, or `SBPS`), a
two-letter subzone with an optional variant, and a `/series`. The package
refuses a code that would not resolve, including the legacy `712,CHS131`, and
it refuses a run that carries no `STDINFO` at all. The refusal names the
accepted grammar, the supported zones, and the silent default FVS would use.

The package does not make the variant resolve a zone it does not represent.
`CWH`, `CDF`, `BWBS`, `CMA`, and `MH` are refused by name; the upstream
extension is a separate workstream (W2).

## Consequences

- A caller cannot silently run `ICHmw2/01` by accident. The input is checked
  before the child process writes a file.
- The correct form is now the one the README and usage page show:
  `STDINFO=CAR,IDFdk3/01,...`.
- Runs that relied on the old default will fail until they name their BEC. That
  is the intended break: the old run was not the run the caller described.
- A code split across the two fields is accepted, because FVS concatenates
  them; a code with no series is not.
- The provenance record carries the validated BEC, so a reader does not have to
  read the keyword file to see which code a number came from.
- The five unsupported zones have a clear refusal instead of a plausible but
  wrong result.

## Alternatives considered

- **Leave the default and document it.** Rejected: the default is not an error
  in FVS, so a caller who does not read the page gets a plausible wrong number.
  The Knife Creek pilot is the evidence that this happens.
- **Warn and continue.** Rejected for an invalid code: a warning is easy to
  ignore, and the run that follows is still `ICHmw2/01`. A warning is the right
  treatment for a future, weaker case, not for a known-wrong input.
- **Validate only in the CLI.** Rejected: the API is the other public surface,
  and a caller who uses `run_case` would keep the silent default.
- **Make `HABTYP` stricter upstream.** Out of scope here, and it would change
  FVS rather than the wrapper. The wrapper can refuse the input without a
  source change.
