"""Smoke the public FVS demo through an optional Cloudflare Access service token.

The token is read from ``CF_ACCESS_CLIENT_ID`` and ``CF_ACCESS_CLIENT_SECRET`` and is never printed
or stored. Without a token, an Access-protected host fails with an explicit redirect message rather
than a confusing HTML/login response.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from collections.abc import Mapping
from typing import Any

__all__ = ["access_headers", "check_public", "main"]

DEFAULT_URL = "https://fresh-fvsbc.01101.dev"
CLIENT_ID_ENV = "CF_ACCESS_CLIENT_ID"
CLIENT_SECRET_ENV = "CF_ACCESS_CLIENT_SECRET"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Leave Access/login redirects visible instead of following them to HTML."""

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,  # noqa: ANN401 - urllib's handler contract
        code: int,
        msg: str,
        headers: Any,  # noqa: ANN401 - urllib's handler contract
        newurl: str,
    ) -> None:
        return None


def access_headers(environ: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return Cloudflare Access service-token headers, or an empty mapping when unset.

    Parameters
    ----------
    environ : mapping of str to str, optional
        Environment values; defaults to ``os.environ``.

    Returns
    -------
    dict of str to str
        ``CF-Access-Client-Id`` and ``CF-Access-Client-Secret`` when both are set.

    Raises
    ------
    ValueError
        If only one of the two token values is set.
    """
    values = os.environ if environ is None else environ
    client = values.get(CLIENT_ID_ENV, "").strip()
    secret = values.get(CLIENT_SECRET_ENV, "").strip()
    if bool(client) != bool(secret):
        raise ValueError(
            f"set both {CLIENT_ID_ENV} and {CLIENT_SECRET_ENV}, or neither",
        )
    if not client:
        return {}
    return {"CF-Access-Client-Id": client, "CF-Access-Client-Secret": secret}


def _fetch(
    url: str,
    headers: Mapping[str, str],
    timeout: float,
) -> tuple[int, dict[str, str], bytes]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "fresh-fvsbc-public-smoke/1.0", **headers},
    )
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            return response.status, dict(response.headers.items()), response.read(2_000_000)
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers.items()), error.read(2_000_000)


def _redirect_detail(status: int, headers: Mapping[str, str]) -> str:
    if status not in (301, 302, 303, 307, 308):
        return ""
    location = headers.get("Location") or headers.get("location") or ""
    if "cloudflareaccess.com" in location:
        return (
            "Cloudflare Access login redirect. Set CF_ACCESS_CLIENT_ID and "
            "CF_ACCESS_CLIENT_SECRET from a service token."
        )
    return f"redirected to {location or 'an unknown location'}"


def check_public(
    base_url: str,
    headers: Mapping[str, str],
    *,
    timeout: float = 20.0,
) -> list[dict[str, Any]]:
    """Check the public shell, JS asset, run list, and agent status.

    Parameters
    ----------
    base_url : str
        Public origin, with or without a trailing slash.
    headers : mapping of str to str
        Extra request headers, normally :func:`access_headers`.
    timeout : float, optional
        Seconds allowed per request.

    Returns
    -------
    list of dict
        One result per endpoint with ``path``, ``ok``, ``status``, and ``detail``.
    """
    root = base_url.rstrip("/")
    results: list[dict[str, Any]] = []

    def record(path: str, ok: bool, status: int, detail: str) -> None:
        results.append({"path": path, "ok": ok, "status": status, "detail": detail})

    status, response_headers, body = _fetch(f"{root}/", headers, timeout)
    redirect = _redirect_detail(status, response_headers)
    if status == 200 and b"fresh-fvsbc" in body:
        record("/", True, status, "shell served")
    else:
        record("/", False, status, redirect or "shell marker missing")

    status, response_headers, body = _fetch(f"{root}/app.js", headers, timeout)
    redirect = _redirect_detail(status, response_headers)
    if status == 200 and b"renderTables" in body:
        record("/app.js", True, status, f"{len(body)} bytes")
    else:
        record("/app.js", False, status, redirect or "table runtime marker missing")

    status, response_headers, body = _fetch(f"{root}/api/runs", headers, timeout)
    redirect = _redirect_detail(status, response_headers)
    try:
        runs = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        runs = None
    if status == 200 and isinstance(runs, list) and runs:
        ids = ", ".join(str(run.get("id", "?")) for run in runs[:8])
        record("/api/runs", True, status, f"{len(runs)} run(s): {ids}")
    else:
        record("/api/runs", False, status, redirect or "expected a non-empty run list")

    status, response_headers, body = _fetch(f"{root}/api/agent", headers, timeout)
    redirect = _redirect_detail(status, response_headers)
    try:
        agent = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        agent = None
    if status == 200 and isinstance(agent, dict):
        record(
            "/api/agent",
            True,
            status,
            f"enabled={bool(agent.get('enabled'))} available={bool(agent.get('available'))}",
        )
    else:
        record("/api/agent", False, status, redirect or "expected an agent status object")
    return results


def main(argv: list[str] | None = None) -> int:
    """Run the public smoke checks and return a process exit code.

    Parameters
    ----------
    argv : list of str, optional
        Command-line arguments; defaults to ``sys.argv[1:]``.

    Returns
    -------
    int
        ``0`` on success, ``1`` for a failed endpoint, ``2`` for token misconfiguration.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.environ.get("FVS_PUBLIC_URL", DEFAULT_URL))
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args(argv)
    try:
        headers = access_headers()
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if headers:
        print("Using Cloudflare Access service-token headers.")
    else:
        print(
            "No service token set; an Access-protected host will fail with a redirect "
            "unless it is public.",
        )
    results = check_public(args.url, headers, timeout=args.timeout)
    failed = False
    for result in results:
        prefix = "OK  " if result["ok"] else "FAIL"
        print(f"{prefix} {result['path']:<10} {result['status']} {result['detail']}")
        failed = failed or not result["ok"]
    if failed:
        print("Public smoke failed.", file=sys.stderr)
        return 1
    print("Public smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
