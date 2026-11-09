"""Run one MPB segment as a FreshForge-native diagnostic.

The script reads one case from an external JSON file, builds the FVS case from
the PSP interval, writes an ``INITMORT`` outbreak block, runs the installed BC
variant, and reports the final PL size distribution. It writes aggregate JSON
only; the generated FVS case stays in a temporary directory.

The case file carries the interval key and severity multiplier. It stays
outside the repository so the tracked workflow contains no site-level key::

    {
      "interval_id": "<site|visit|year0|year1>",
      "multiplier": 0.08
    }
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

import pandas as pd
from pyfvs import fvs

from fresh_fvsbc.backtest import keywords_for, psp_tree_records
from fresh_fvsbc.keywords import Keyword, KeywordSet
from fresh_fvsbc.run import with_tree_handoff
from fresh_fvsbc.treelist import write_tree_file

TREE_COLUMNS = [
    "SITE_IDENTIFIER",
    "CLSTR_ID",
    "VISIT_NUMBER",
    "PLOT",
    "TREE_NO",
    "SPECIES",
    "DBH",
    "HEIGHT",
    "CR_CL",
    "LV_D",
    "PHF_TREE",
]


def _path(variable: str) -> Path:
    """Return a required data path from the environment.

    Parameters
    ----------
    variable : str
        The environment variable that names the file.

    Returns
    -------
    pathlib.Path
        The resolved path.

    Raises
    ------
    RuntimeError
        If the variable is missing or the file does not exist.
    """
    value = os.environ.get(variable)
    if not value:
        raise RuntimeError(f"set {variable} to the input file path")
    path = Path(value)
    if not path.exists():
        raise RuntimeError(f"{variable} does not name an existing path: {path}")
    return path


def _vector(survival: pd.DataFrame, interval: str) -> tuple[list[float], float]:
    """Return observed dead PL per acre per year and the observed dead fraction.

    Parameters
    ----------
    survival : pandas.DataFrame
        The tree-survival rows.
    interval : str
        The interval key.

    Returns
    -------
    tuple of (list of float, float)
        Ten one-inch-class values for the ``INITMORT`` records and the
        observed PL dead fraction.
    """
    frame = survival[(survival["interval_id"] == interval) & (survival["group"] == "PL")]
    frame = frame[frame["known"] == 1].copy()
    years = float(frame["years"].iloc[0])
    classes = []
    for dbh in frame["dbh"]:
        inches = int(dbh / 2.54)
        classes.append(max(1, min(10, inches // 2 + inches % 2)))
    frame["class"] = classes
    values = []
    for index in range(1, 11):
        part = frame[frame["class"] == index]
        values.append(
            float(part.loc[part["dead"] == 1, "phf"].sum() / years / 2.471) if len(part) else 0.0
        )
    observed = float(frame["dead"].mean()) if len(frame) else 0.0
    return values, observed


def _keywords(interval: dict[str, object]) -> list[Keyword]:
    """Return one interval's keywords, split into ten-year cycles.

    Parameters
    ----------
    interval : dict
        One interval row.

    Returns
    -------
    list of Keyword
        The keywords with ``TIMEINT`` and ``NUMCYCLE`` rewritten so no cycle
        exceeds ten years.
    """
    years = int(float(interval["years"]))
    keywords = list(keywords_for(interval))
    if years <= 10:
        return keywords
    result: list[Keyword] = []
    for keyword in keywords:
        if keyword.name == "TIMEINT":
            result.append(Keyword("TIMEINT", ("1", "10")))
            result.append(Keyword("TIMEINT", ("2", str(years - 10))))
        elif keyword.name == "NUMCYCLE":
            result.append(Keyword("NUMCYCLE", ("2",)))
        else:
            result.append(keyword)
    return result


def main() -> None:
    """Run one interval and write aggregate segment JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--multiplier", type=float, default=None)
    args = parser.parse_args()

    case = json.loads(args.case.read_text())
    interval_id = str(case["interval_id"])
    multiplier = args.multiplier if args.multiplier is not None else float(case["multiplier"])
    psp4 = _path("FRESH_FVSBC_PSP4_GROWTH")
    tree_data = _path("FRESH_FVSBC_TREE_DETAIL")
    survival = pd.read_csv(
        psp4 / "tree_survival.csv",
        usecols=["interval_id", "group", "dbh", "dead", "known", "phf", "years"],
    )
    intervals = pd.read_csv(psp4 / "intervals.csv").set_index("interval_id")
    interval = intervals.loc[interval_id].to_dict()
    interval["interval_id"] = interval_id
    trees = pd.read_csv(tree_data, usecols=TREE_COLUMNS)
    records, skipped = psp_tree_records(trees, interval)
    observed_vector, observed_fraction = _vector(survival, interval_id)
    values = [value * multiplier for value in observed_vector]
    block = Keyword(
        "MPB",
        nested=(
            Keyword("MPBSTART", ("1",)),
            Keyword(
                "INITMORT",
                tuple(f"{value:.4f}" for value in values[:7]),
                supplemental=(" ".join(f"{value:.4f}" for value in values[7:]),),
            ),
            Keyword("MAXYEARS", ("10",)),
        ),
    )
    keywords = _keywords(interval)
    keywords = [keyword for keyword in keywords if keyword.name != "DATABASE"]
    process = next(index for index, keyword in enumerate(keywords) if keyword.name == "PROCESS")
    keywords.insert(process, block)
    text = KeywordSet(with_tree_handoff(keywords)).render()
    with tempfile.TemporaryDirectory(prefix="ff-mpb-") as directory:
        workspace = Path(directory)
        key = workspace / "run.key"
        key.write_text(text)
        (workspace / "run.tre").write_text(write_tree_file(records))
        previous = Path.cwd()
        os.chdir(workspace)
        try:
            sim = fvs.FVS("bc", workspace=str(workspace), cleanup=True)
            sim.init_projection(str(key))
            for _ in range(sim.globals.ncyc):
                sim.grow()
            sim.end_projection()
            final = sim.trees
        finally:
            os.chdir(previous)
        final_year = int(final["year"].max())
        initial_year = int(float(interval["year0"]))
        initial = final[(final["year"] == initial_year) & (final["spp_seq"] == 7)]
        ending = final[(final["year"] == final_year) & (final["spp_seq"] == 7)]
        initial_tpa = float(initial["live_tpa"].sum())
        final_tpa = float(ending["live_tpa"].sum())
        bins = [0, 5, 10, 12.5, 15, 17.5, 20, 25, 30, 40, 999]
        sizes = (
            ending.groupby(pd.cut(ending["live_dbh"], bins), observed=False)["live_tpa"]
            .sum()
            .to_dict()
        )
        result = {
            "multiplier": multiplier,
            "initial_pl_tpa": initial_tpa,
            "final_pl_tpa": final_tpa,
            "dead_fraction": (initial_tpa - final_tpa) / initial_tpa if initial_tpa else None,
            "observed_dead_fraction": observed_fraction,
            "final_year": final_year,
            "max_live_dbh": float(ending["live_dbh"].max()) if len(ending) else 0.0,
            "live_pl_above_15_tpa": float(ending.loc[ending["live_dbh"] > 15, "live_tpa"].sum()),
            "live_pl_by_dbh": {str(key): float(value) for key, value in sizes.items()},
            "skipped_trees": skipped,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
