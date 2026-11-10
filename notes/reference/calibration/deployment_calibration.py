"""Estimate and apply deployment calibration offsets from scored target rows.

The helper consumes a frozen model card and a scored CSV with ``site``,
``group``, ``eta``, ``exposure``, and ``dead``. It estimates the policy-defined
group intercepts on a fixed number of sites, records the offsets, and can apply
them to the scored rows.

The helper does not re-score raw inventory. The frozen card does not yet store
preprocessing medians, so the scored table is the upstream contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED = ("site", "group", "eta", "exposure", "dead")
GROUPS = ("FD", "PL", "SE", "HW", "OTHER")


def _digest(path: Path) -> str:
    """Return a SHA-256 digest without loading the file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _rule_for(policy: dict[str, object], model_id: str, override: str | None) -> str:
    """Return the calibration rule for a model id.

    Parameters
    ----------
    policy : dict
        The frozen calibration policy.
    model_id : str
        The candidate model id.
    override : str or None
        An explicit rule for optional candidates.

    Returns
    -------
    str
        ``one_sided`` or ``symmetric``.

    Raises
    ------
    SystemExit
        If no rule is available and no override is given.
    """
    if override:
        return override
    for entry in policy.get("supported", {}).values():
        if entry.get("model_id") == model_id:
            return str(entry["rule"])
    for entry in policy.get("one_sided", {}).values():
        if entry.get("model_id") == model_id:
            return "one_sided"
    raise SystemExit(f"no policy rule for {model_id}; pass --rule one_sided or --rule symmetric")


def _delta(eta: np.ndarray, dead: np.ndarray, exposure: np.ndarray) -> float:
    """Return the maximum-likelihood group intercept at fixed coefficients."""
    offset = np.log(exposure) + eta
    value = 0.0
    for _ in range(60):
        mu = np.exp(np.clip(value + offset, -20, 20))
        weight = np.clip(mu, 1e-8, None)
        z = value + offset + (dead - mu) / weight
        value = float(np.sum(weight * (z - offset)) / np.sum(weight))
    return value


def _offsets(
    calibration: pd.DataFrame,
    *,
    rule: str,
    minimum_trees: int,
    trigger: float,
) -> dict[str, dict[str, float | int | bool]]:
    """Estimate one offset per supported group.

    Parameters
    ----------
    calibration : pandas.DataFrame
        The calibration-site rows.
    rule : str
        ``one_sided`` or ``symmetric``.
    minimum_trees : int
        Minimum target trees for a group.
    trigger : float
        Prediction-observed gap that activates an offset.

    Returns
    -------
    dict
        Group name to count, base mean, observed mean, applied flag, and offset.
    """
    result: dict[str, dict[str, float | int | bool]] = {}
    for group in GROUPS:
        part = calibration[calibration["group"] == group]
        if part.empty:
            continue
        eta = part["eta"].to_numpy(dtype=float)
        exposure = part["exposure"].to_numpy(dtype=float)
        dead = part["dead"].to_numpy(dtype=float)
        base = 1.0 - np.exp(-exposure * np.exp(np.clip(eta, -20, 20)))
        base_mean = float(base.mean())
        observed_mean = float(dead.mean())
        gap = base_mean - observed_mean
        supported = len(part) >= minimum_trees
        trigger_hit = abs(gap) > trigger if rule == "symmetric" else gap > trigger
        applied = bool(supported and trigger_hit)
        result[group] = {
            "n": len(part),
            "base_mean": base_mean,
            "observed_mean": observed_mean,
            "applied": applied,
            "offset": _delta(eta, dead, exposure) if applied else 0.0,
        }
    return result


def main() -> None:
    """Estimate offsets and optionally write calibrated predictions."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--card", type=Path, required=True)
    parser.add_argument("--scored", type=Path, required=True)
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path("notes/reference/calibration/calibration-policy.json"),
    )
    parser.add_argument("--sites", type=int, default=20)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--apply", type=Path, default=None)
    parser.add_argument("--rule", choices=("one_sided", "symmetric"), default=None)
    args = parser.parse_args()

    card = json.loads(args.card.read_text())
    policy = json.loads(args.policy.read_text())
    model_id = str(card["model_id"])
    rule = _rule_for(policy, model_id, args.rule)
    frame = pd.read_csv(args.scored)
    missing = [column for column in REQUIRED if column not in frame.columns]
    if missing:
        raise SystemExit(f"scored table is missing columns: {', '.join(missing)}")
    for column in ("eta", "exposure", "dead"):
        if not np.isfinite(frame[column].to_numpy(dtype=float)).all():
            raise SystemExit(f"scored table contains non-finite {column}")
    if (frame["exposure"] <= 0).any():
        raise SystemExit("scored table contains non-positive exposure")
    sites = sorted(frame["site"].astype(str).unique())
    if len(sites) < args.sites:
        raise SystemExit(f"need at least {args.sites} sites, found {len(sites)}")
    selected = set(sites[: args.sites])
    calibration = frame[frame["site"].astype(str).isin(selected)]
    offsets = _offsets(
        calibration,
        rule=rule,
        minimum_trees=int(policy["minimums"]["group_trees"]),
        trigger=float(policy["minimums"]["trigger_points"]),
    )
    payload = {
        "calibration_id": f"{model_id}-deployment",
        "model_id": model_id,
        "rule": rule,
        "calibration_sites": args.sites,
        "site_count": len(sites),
        "minimums": policy["minimums"],
        "groups": offsets,
        "applied_groups": sorted(name for name, entry in offsets.items() if entry["applied"]),
        "card": str(args.card),
        "card_sha256": _digest(args.card),
        "scored": str(args.scored),
        "scored_sha256": _digest(args.scored),
        "claim": "Deployment calibration offsets only. Not a bundle or certificate.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if args.apply is not None:
        applied = frame.copy()
        applied["base_prediction"] = 1.0 - np.exp(
            -applied["exposure"].to_numpy(dtype=float)
            * np.exp(np.clip(applied["eta"].to_numpy(dtype=float), -20, 20))
        )
        deltas = (
            applied["group"]
            .map({name: entry["offset"] for name, entry in offsets.items()})
            .fillna(0.0)
        )
        applied["calibrated_prediction"] = 1.0 - np.exp(
            -applied["exposure"].to_numpy(dtype=float)
            * np.exp(
                np.clip(
                    applied["eta"].to_numpy(dtype=float) + deltas.to_numpy(dtype=float),
                    -20,
                    20,
                )
            )
        )
        args.apply.parent.mkdir(parents=True, exist_ok=True)
        applied.to_csv(args.apply, index=False)
    print(f"wrote {args.output} with {len(offsets)} groups")


if __name__ == "__main__":
    main()
