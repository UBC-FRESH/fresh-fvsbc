"""Estimate and apply deployment calibration offsets from scored target rows.

The helper consumes a frozen model card and a scored CSV with ``site``,
``group``, ``eta``, ``exposure``, and ``dead``. The default nested policy also
needs ``unit`` and ``bec_zone``. It chooses base, TSA partial, or BEC partial by
nested site cross-validation, records the selected mode and offsets, and can
apply them to the scored rows. The fixed one-sided/symmetric rule remains
available with ``--mode fixed``.

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
from sweep_support_policy import _bec_offsets, _choose_mode, _predict, _tsa_offsets

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
    parser.add_argument(
        "--mode",
        choices=("nested", "fixed"),
        default="nested",
        help="Nested support-aware policy (default) or the fixed rule.",
    )
    args = parser.parse_args()

    card = json.loads(args.card.read_text())
    policy = json.loads(args.policy.read_text())
    model_id = str(card["model_id"])
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
    selected_mode = "fixed"
    if args.mode == "nested":
        if "unit" not in frame.columns or "bec_zone" not in frame.columns:
            raise SystemExit("nested mode needs unit and bec_zone columns")
        selected_mode = _choose_mode(frame, np.random.default_rng(42))
        offsets = {}
        applied_groups: list[str] = []
        if selected_mode == "tsa_partial_symmetric":
            tsa = _tsa_offsets(frame)
            offsets = {"group": tsa}
            applied_groups = sorted(name for name, value in tsa.items() if value)
        elif selected_mode == "bec_partial_symmetric":
            unit, zone = _bec_offsets(frame)
            offsets = {
                "unit": {f"{key[0]}|{key[1]}": value for key, value in unit.items()},
                "zone": {f"{key[0]}|{key[1]}": value for key, value in zone.items()},
            }
            applied_groups = sorted({key.split("|")[1] for key in offsets["unit"]})
        payload = {
            "calibration_id": f"{model_id}-deployment",
            "model_id": model_id,
            "mode": "nested",
            "rule": selected_mode,
            "calibration_sites": len(sites),
            "site_count": len(sites),
            "minimums": policy["minimums"],
            "offsets": offsets,
            "applied_groups": applied_groups,
            "card": str(args.card),
            "card_sha256": _digest(args.card),
            "scored": str(args.scored),
            "scored_sha256": _digest(args.scored),
            "claim": "Deployment calibration offsets only. Not a bundle or certificate.",
        }
    else:
        rule = _rule_for(policy, model_id, args.rule)
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
            "mode": "fixed",
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
        if args.mode == "nested":
            applied["calibrated_prediction"] = _predict(applied, frame, selected_mode)
        else:
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
    if args.mode == "nested":
        print(f"wrote {args.output} with nested mode {selected_mode}")
    else:
        print(f"wrote {args.output} with {len(offsets)} groups")


if __name__ == "__main__":
    main()
