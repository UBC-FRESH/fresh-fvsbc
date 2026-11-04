#!/usr/bin/env python3
"""Run a fixed candidate set through the FVS-BC calibration probe.

The probe answers one question before a bundle is written: does a candidate
parameter set move an eligible sample in the direction the residual requires,
and does it still do so on a held-out site group?  It is deliberately not an
optimizer.  The candidate list is an input file, the split is explicit, and the
output records the rows so a fit can be reproduced.

Command-line usage::

    python scripts/run_calibration_probe.py \
      --data-dir runtime/calibration --psp-dir "$FAIB_PSP_DIR" \
      --out-dir runtime/probe --domain SBPS --per-bec 5 \
      --candidates notes/reference/calibration/d7-sbps-candidates.json \
      --test-sites 4030915,4026046,4026848
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from fresh_fvsbc.backtest import (
    keywords_for,
    psp_tree_records,
    select_intervals,
    summary_for_year,
)
from fresh_fvsbc.bundle import CalibrationBundle, load_bundle
from fresh_fvsbc.calibration_probe import (
    eligible_intervals,
    ingrowth_keyword,
    insert_parameters,
    interval_checksum,
    parameter_keywords,
    summarise_probe,
)
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.run import run_case
from run_baseline_backtest import _read_trees

__all__ = ["EXIT_BAD_INPUT", "EXIT_OK", "main"]

EXIT_OK: int = 0
EXIT_BAD_INPUT: int = 2


def _parser() -> argparse.ArgumentParser:
    """Return the command's parser."""
    parser = argparse.ArgumentParser(
        prog="run_calibration_probe",
        description="Run a fixed candidate set through the FVS-BC calibration probe.",
    )
    parser.add_argument("--data-dir", required=True, type=Path, metavar="DIR")
    parser.add_argument("--psp-dir", required=True, type=Path, metavar="DIR")
    parser.add_argument("--out-dir", required=True, type=Path, metavar="DIR")
    parser.add_argument("--domain", required=True, help="BEC prefix, such as SBPS or CWH")
    parser.add_argument("--per-bec", type=int, default=5, metavar="N")
    parser.add_argument("--min-ba0", type=float, default=15.0, metavar="M2HA")
    parser.add_argument("--max-mortality-fraction", type=float, default=0.4, metavar="FRACTION")
    parser.add_argument("--min-qmd", type=float, default=6.0, metavar="CM")
    parser.add_argument(
        "--min-dbh",
        type=float,
        default=0.0,
        metavar="CM",
        help="common lower DBH limit for tree list and observations; 4.0 for cross-program work",
    )
    parser.add_argument(
        "--test-sites",
        default="",
        metavar="IDS",
        help="Comma-separated SITE_IDENTIFIER values to hold out; empty means no site split",
    )
    parser.add_argument(
        "--test-year-from",
        type=int,
        default=None,
        metavar="YEAR",
        help="hold out intervals whose year0 is at or after this year",
    )
    parser.add_argument("--candidates", required=True, type=Path, metavar="FILE")
    parser.add_argument(
        "--ingrowth", type=Path, metavar="FILE", help="optional BEC/species rate JSON"
    )
    parser.add_argument("--ingrowth-scale", type=float, default=1.0, metavar="MULT")
    parser.add_argument(
        "--bundle", type=Path, metavar="FILE", help="calibration bundle with an ingrowth model"
    )
    parser.add_argument("--cycles", type=int, default=1, metavar="N")
    parser.add_argument("--cycle-years", type=float, default=None, metavar="YEARS")
    parser.add_argument("--tree-age", type=float, default=60.0, metavar="YEARS")
    return parser


def _candidates(path: Path) -> list[dict[str, object]]:
    """Read the candidate list and refuse an entry without a label."""
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list) or not records:
        raise ValueError("the candidate file must hold a non-empty JSON list")
    for record in records:
        if "label" not in record:
            raise ValueError("every candidate needs a label")
    return records


def main(argv: Sequence[str] | None = None) -> int:
    """Run the probe and write its interval and aggregate tables.

    Parameters
    ----------
    argv : sequence of str or None, optional
        The arguments, without the program name. ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        :data:`EXIT_OK` on success, or :data:`EXIT_BAD_INPUT` for a bad input.
    """
    args = _parser().parse_args(argv)
    try:
        intervals = pd.read_csv(args.data_dir / "intervals.csv")
        visits = pd.read_csv(args.data_dir / "visits.csv")
        candidates = _candidates(args.candidates)
        ingrowth = (
            json.loads(args.ingrowth.read_text(encoding="utf-8"))["rates"]
            if args.ingrowth is not None
            else {}
        )
        bundle: CalibrationBundle | None = load_bundle(args.bundle) if args.bundle else None
        if args.cycles < 1:
            raise ValueError("cycles must be at least one")
        if args.min_dbh < 0:
            raise ValueError("min_dbh must not be negative")
    except (OSError, ValueError, json.JSONDecodeError, KeyError) as error:
        print(f"run_calibration_probe: {error}")
        return EXIT_BAD_INPUT
    domain = intervals[intervals["BEC"].astype(str).str.startswith(args.domain)].copy()
    if domain.empty:
        print(f"run_calibration_probe: no intervals for {args.domain}")
        return EXIT_BAD_INPUT
    try:
        eligible = eligible_intervals(
            domain,
            min_ba0=args.min_ba0,
            max_mortality_fraction=args.max_mortality_fraction,
            min_qmd=args.min_qmd,
        )
    except ValueError as error:
        print(f"run_calibration_probe: {error}")
        return EXIT_BAD_INPUT
    sample = select_intervals(eligible, per_bec=args.per_bec)
    trees = _read_trees(args.psp_dir, sample)
    if args.min_dbh > 0 and "DBH" in trees.columns:
        trees = trees[trees["DBH"] >= args.min_dbh].copy()
    if trees.empty:
        print("run_calibration_probe: no tree rows for the eligible sample")
        return EXIT_BAD_INPUT
    test_sites = {value.strip() for value in args.test_sites.split(",") if value.strip()}
    rows: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    for candidate in candidates:
        label = str(candidate["label"])
        parameters = parameter_keywords(
            bamax=float(str(candidate["bamax"])) if candidate.get("bamax") is not None else None,
            baimult=candidate.get("baimult"),  # type: ignore[arg-type]
            mortmult=candidate.get("mortmult"),  # type: ignore[arg-type]
            htgmul=candidate.get("htgmul"),  # type: ignore[arg-type]
            regdmul=candidate.get("regdmul"),  # type: ignore[arg-type]
            reghmul=candidate.get("reghmul"),  # type: ignore[arg-type]
        )
        for raw in sample.to_dict("records"):
            interval = {str(key): value for key, value in raw.items()}
            records, tree_skips = psp_tree_records(trees, interval, tree_age=args.tree_age)
            if not records:
                skipped.append(
                    {
                        "candidate": label,
                        "interval_id": interval["interval_id"],
                        "BEC": interval["BEC"],
                        "reason": "no tree resolved",
                    }
                )
                continue
            observed = visits[
                (visits["SITE_IDENTIFIER"] == interval["SITE_IDENTIFIER"])
                & (visits["VISIT_NUMBER"] == interval["visit1"])
                & (visits["PLOT"] == interval["PLOT"])
            ].iloc[0]
            cycle_years = (
                args.cycle_years
                if args.cycle_years is not None
                else float(interval["years"]) / args.cycles
            )
            if args.cycles > 1 and bundle is None:
                raise ValueError("more than one cycle needs a bundle ingrowth model")
            if bundle is not None:
                ingrowth_keyword_value = bundle.ingrowth_keyword(
                    bec=str(interval["BEC"]),
                    years=float(interval["years"]),
                    ba=float(interval["ba0"]),
                    qmd=float(interval["qmd"]),
                    cycles=args.cycles,
                    cycle_years=cycle_years,
                )
            else:
                ingrowth_keyword_value = ingrowth_keyword(
                    bec=str(interval["BEC"]),
                    years=float(interval["years"]),
                    rates=ingrowth,
                    scale=args.ingrowth_scale,
                )
            block = (*parameters, ingrowth_keyword_value) if ingrowth_keyword_value else parameters
            base_keywords = list(keywords_for(interval))
            if args.cycles > 1:
                base_keywords = [
                    Keyword("TIMEINT", ("", f"{cycle_years:g}"))
                    if keyword.name == "TIMEINT"
                    else Keyword("NUMCYCLE", (str(args.cycles),))
                    if keyword.name == "NUMCYCLE"
                    else keyword
                    for keyword in base_keywords
                ]
            keywords = insert_parameters(base_keywords, block)
            run_dir = (
                args.out_dir / "runs" / f"{label}-{str(interval['interval_id']).replace('|', '_')}"
            )
            result = run_case(
                records,
                keywords,
                directory=run_dir,
                calibration=bundle,
                tsa=str(interval["TSA_DESC"]),
            )
            predicted = summary_for_year(result.database, int(interval["year1"]))
            rows.append(
                {
                    "candidate": label,
                    "fold": (
                        "test"
                        if str(interval["SITE_IDENTIFIER"]) in test_sites
                        or (
                            args.test_year_from is not None
                            and int(interval["year0"]) >= args.test_year_from
                        )
                        else "train"
                    ),
                    "BEC": interval["BEC"],
                    "interval_id": interval["interval_id"],
                    "ba0": round(float(interval["ba0"]), 3),
                    "qmd": round(float(interval["qmd"]), 3),
                    "mortality_fraction": round(float(interval["mortality_fraction"]), 4),
                    "observed_ba1": round(float(observed["ba"]), 3),
                    "predicted_ba1": round(float(predicted["ba"]), 3),
                    "observed_tph1": round(float(observed["tph"]), 3),
                    "predicted_tph1": round(float(predicted["tph"]), 3),
                    "ba_error": round(float(predicted["ba"]) - float(observed["ba"]), 3),
                    "tph_error": round(float(predicted["tph"]) - float(observed["tph"]), 3),
                    "skipped_trees": tree_skips,
                }
            )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    if frame.empty:
        print("run_calibration_probe: no interval was compared")
        return EXIT_BAD_INPUT
    data_checksum = interval_checksum(sample)
    frame.to_csv(args.out_dir / "probe.csv", index=False)
    summary = summarise_probe(frame)
    summary.to_csv(args.out_dir / "probe_summary.csv", index=False)
    summarise_probe(frame, by=("candidate", "BEC")).to_csv(
        args.out_dir / "probe_by_bec.csv", index=False
    )
    pd.DataFrame(skipped).to_csv(args.out_dir / "probe_skipped.csv", index=False)
    (args.out_dir / "probe.json").write_text(
        json.dumps(
            {
                "domain": args.domain,
                "per_bec": args.per_bec,
                "min_ba0": args.min_ba0,
                "max_mortality_fraction": args.max_mortality_fraction,
                "min_qmd": args.min_qmd,
                "min_dbh": args.min_dbh,
                "test_sites": sorted(test_sites),
                "test_year_from": args.test_year_from,
                "data_checksum": data_checksum,
                "candidates": candidates,
                "ingrowth": str(args.ingrowth) if args.ingrowth is not None else "",
                "ingrowth_scale": args.ingrowth_scale,
                "bundle": str(args.bundle) if args.bundle is not None else "",
                "cycles": args.cycles,
                "cycle_years": args.cycle_years,
                "intervals": int(frame["interval_id"].nunique()),
                "rows": len(frame),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(summary.round(2).to_string(index=False))
    print(f"wrote {args.out_dir} with {len(frame)} compared rows")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
