"""BCINGR v2 screen: prior stand rates and year on the IDFdk hurdle.

Adds the previous interval's stand rates and the start year to the D9.28
prototype, then tests the 100 Mile House TSA.  This is a diagnostic screen, not
a fitted ZINB and not an FVS change.
"""

from __future__ import annotations

import bcingr_prototype as b
import numpy as np
import pandas as pd

PRIOR = ("net_ba_rate", "gross_ba_rate", "ba_mortality", "tph_mortality", "years")


def prepare() -> pd.DataFrame:
    """Load the hurdle table and merge prior-interval stand rates."""
    table, intervals = b._prepare()
    intervals = intervals.sort_values(["SITE_IDENTIFIER", "PLOT", "year0"])
    grouped = intervals.groupby(["SITE_IDENTIFIER", "PLOT"], sort=False)
    for column in PRIOR:
        intervals["prior_" + column] = grouped[column].shift(1)
    columns = ["interval_id", *["prior_" + column for column in PRIOR]]
    table = table.merge(intervals[columns], on="interval_id", how="left")
    for column in columns[1:]:
        table[column + "_missing"] = table[column].isna().astype(float)
        table[column] = table[column].fillna(table[column].median())
    return table


def design(table: pd.DataFrame, extra: bool) -> np.ndarray:
    """Build the base hurdle design, optionally with year and prior rates."""
    base = b._design(table)
    if not extra:
        return base
    columns = ["year0", *["prior_" + column for column in PRIOR]]
    return np.column_stack(
        [
            base,
            *[table[column].to_numpy() for column in columns],
            *[table[column + "_missing"].to_numpy() for column in columns if column != "year0"],
        ]
    )


def _run(table: pd.DataFrame, extra: bool) -> dict[str, float | str]:
    """Fit the hurdle and return train/test metrics."""
    train = table[~table["TSA_DESC"].astype(str).eq("100 Mile House TSA")]
    test = table[table["TSA_DESC"].astype(str).eq("100 Mile House TSA")]
    xtr = design(train, extra)
    xte = design(test, extra)
    mean = xtr[:, 1:].mean(axis=0)
    scale = xtr[:, 1:].std(axis=0)
    scale[scale == 0] = 1
    xtr[:, 1:] = (xtr[:, 1:] - mean) / scale
    xte[:, 1:] = (xte[:, 1:] - mean) / scale
    ytr = train["new_total"].to_numpy()
    yte = test["new_total"].to_numpy()
    years_train = train["years"].to_numpy()
    years_test = test["years"].to_numpy()
    beta_presence = b._logit_fit(xtr, (ytr > 0).astype(float))
    positive = ytr > 0
    beta_count = b._loglinear_fit(xtr[positive], ytr[positive] / years_train[positive])
    residual = np.log(ytr[positive] / years_train[positive] + 0.05) - xtr[positive] @ beta_count
    smear = float(np.mean(np.exp(residual)))

    def predict(x: np.ndarray, years: np.ndarray) -> np.ndarray:
        presence = 1.0 / (1.0 + np.exp(-(x @ beta_presence)))
        rate = np.exp(np.clip(x @ beta_count, -20, 20)) * smear
        return presence * rate * years

    train_metric = b._metrics(ytr, predict(xtr, years_train), years_train)
    test_metric = b._metrics(yte, predict(xte, years_test), years_test)
    print(f"extra={extra}  train {train_metric}  test {test_metric}")
    return {
        "model": "extra" if extra else "base",
        "train_corr": train_metric["corr"],
        "train_rmse": train_metric["rmse"],
        "test_corr": test_metric["corr"],
        "test_rmse": test_metric["rmse"],
        "test_obs_mean_tph": test_metric["obs_mean_tph"],
        "test_pred_mean_tph": test_metric["pred_mean_tph"],
        "test_obs_zero": test_metric["obs_zero"],
        "test_pred_zero": test_metric["pred_zero"],
    }


def main() -> None:
    """Run the base and extended screens and write the summary."""
    table = prepare()
    rows = [_run(table, False), _run(table, True)]
    pd.DataFrame(rows).to_csv("notes/reference/calibration/d9-bcingr-v2-summary.csv", index=False)


if __name__ == "__main__":
    main()
