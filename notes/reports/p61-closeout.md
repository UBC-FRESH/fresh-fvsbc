# Phase close-out report: P61 The reference table

Phase: P61 The reference table
Parent issue: #260
Pull request: #262
Evidence head: `67decb9`
Date: 2026-10-27
Status: merged. No code.

## Recommendation

**No release.** This phase changed notes. The next release is whatever fixes the writer, or whatever
adopts a new pin.

## 1. The question

`FVS_InvReference` is written by a standalone `FVSbc` on every run and by no run of this package. Is the
package implicated, and can the cause be found from outside the binary?

## 2. Ruled out, with evidence

| Candidate | Evidence |
| --- | --- |
| The source | `dbsreference.f` and `dbscase.f` are byte-identical between the pin and upstream |
| The build | the compiled `dbsreference_` is **5,097 bytes in both binaries** — the same routine |
| The driver | this package's run now reads the stand through the **same `DSNin` route** the standalone uses, and still writes nothing |
| The inputs | same keyword file structure, same input database, same stand |
| The handle | `DBSSTATS` writes `FVS_Stats_Species_Metric` from `CALL STATS`, the statement **immediately before** `CALL DBSREFERENCE`, so the database is open |
| The case row | the same call to `DBSCASE(1)` has already run, and `FVS_Cases` holds its row |

## 3. What is left

The routine has two silent exits:

1. `fsql3_tableexists` reports the table as already present, so the `CREATE` is skipped and the inserts
   fail; or
2. the `CREATE` returns an error and the routine returns before inserting.

Both are swallowed: `iInvRef = 0; RETURN`, with no message. **Nothing distinguishes them from outside.**

## 4. What would settle it

A build of the pinned fork with one write inside `DBSREFERENCE` — the value of `iRet` after each call.
That is a change in the fork, and ADR 0001's open policy means it needs its own approval. It is named
here so the next person does not repeat this phase.

## 5. What the phase is worth

Three of the five candidates were the ones this project had been assuming, and all three are now
disproved with evidence rather than argument:

- it is **not** source drift between the pin and upstream, which was the leading explanation;
- it is **not** how the package drives FVS, which was the second;
- it is **not** the output database being closed or the case row missing.

That is the difference between "we do not know" and "we know where it is not", and it is the second
that stops the next investigation repeating this one.

## 6. A capability found on the way

This package's driver **can read a stand through `DSNin`**: the phase ran a full projection from an
input database, and FVS read the stand and its trees. That is a capability the package does not offer
yet — a run whose stand comes from a database rather than a tree list — and it is recorded here because
it was found by accident and will be lost otherwise.
