# ADR 0012: a calibration bundle is data, not code

Status: proposed; accepted when the W1.3 pull request merges
Date: 2026-11-02
Issues: #289, #292

## Context

A calibration is a set of FVS keywords, a domain in which they are valid, and
the evidence behind them. If each calibration is a Python module or a branch, a
reviewer has to read code to see a number, and every new parameter set is a
release. If each is a loose keyword file, nothing records the build, the data
checksum, the domain, or the reviewer, and a number can be applied outside the
region it was fitted to.

The Knife Creek pilot makes the cost concrete. Its multipliers are regional, its
lodgepole pine multiplier sits at a bound, and its first fit was made while the
projection carried the wrong BEC. A parameter set without a domain and a claim
boundary is not a reusable object; it is a transcript of one session.

## Decision

**A calibration bundle is a versioned JSON document, and the package treats it
as data.** A bundle names:

- the build it is valid for: PyFVS commit, FVS source commit, and variant;
- its domain: region, BEC, species group, and management regime;
- its parameters: FVS keywords, raw fields, units, the bounded field, and bounds;
- its evidence: data checksum, train/validation split, objective, and convergence;
- its review: reviewer, date, and sign-off;
- its claim boundary, in one sentence.

`fresh_fvsbc.bundle` loads and validates the document, renders it into keywords,
checks the domain against a run, and records the bundle id in provenance. It
does not fit the parameters. A parameter at a bound loads with a warning; a value
outside its bounds is refused. A bundle whose pins differ from the package is
refused, because a parameter set is reproducible only against the build that
produced it.

## Consequences

- A reviewer can compare two bundles as documents, without a code review.
- A run records `calibration_id`, so a number can be traced to the bundle.
- A bundle cannot be applied outside its domain without an error.
- A bundle cannot silently carry an untested keyword, a missing checksum, or a
  parameter outside its bounds.
- The package still needs a fitter and a validation workflow; the bundle is the
  hand-off, not the calibration.
- A new build is a new bundle. An old bundle is not edited in place.

## Alternatives considered

- **A Python module per calibration.** Rejected: a number would be buried in code,
  a reviewer would need a release, and the domain and evidence would still need a
  separate document.
- **A free-form keyword file.** Rejected: it carries no build, no checksum, no
  domain, and no review record, which is exactly the gap the Knife Creek pilot
  exposed.
- **A CSV of parameters.** Rejected: it cannot express the domain, the pins, the
  evidence, or the claim boundary without a second schema.
- **No domain check in the package.** Rejected: the package is the last place a
  caller can be stopped before a plausible but out-of-domain number.
