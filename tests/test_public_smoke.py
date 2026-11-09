"""Tests for the public-demo smoke tool and its Cloudflare Access token handling."""

from __future__ import annotations

import email.message
import io
import json
import urllib.error
import urllib.request
from typing import ClassVar

import pytest

import public_smoke


def test_access_headers_are_empty_without_a_token() -> None:
    """No service-token values means no Access headers."""
    assert public_smoke.access_headers({}) == {}


def test_access_headers_require_a_complete_token_pair() -> None:
    """Half a service token is a configuration error, not an anonymous request."""
    with pytest.raises(ValueError, match="set both"):
        public_smoke.access_headers({"CF_ACCESS_CLIENT_ID": "client"})


def test_access_headers_use_the_cloudflare_names() -> None:
    """Both values become the documented Access header names."""
    assert public_smoke.access_headers(
        {
            "CF_ACCESS_CLIENT_ID": " client ",
            "CF_ACCESS_CLIENT_SECRET": " secret ",
        }
    ) == {
        "CF-Access-Client-Id": "client",
        "CF-Access-Client-Secret": "secret",
    }


def test_check_public_accepts_a_healthy_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    """The happy path reports shell, asset, runs, and agent as OK."""
    responses: dict[str, tuple[int, dict[str, str], bytes]] = {
        "https://example.test/": (200, {}, b"<title>fresh-fvsbc</title>"),
        "https://example.test/app.js": (200, {}, b"function renderTables() {}"),
        "https://example.test/api/runs": (
            200,
            {},
            json.dumps([{"id": "run-a"}, {"id": "run-b"}]).encode(),
        ),
        "https://example.test/api/agent": (
            200,
            {},
            json.dumps({"enabled": True, "available": True}).encode(),
        ),
    }

    def fake_fetch(
        url: str,
        headers: dict[str, str],
        timeout: float,
    ) -> tuple[int, dict[str, str], bytes]:
        return responses[url]

    monkeypatch.setattr(public_smoke, "_fetch", fake_fetch)
    results = public_smoke.check_public("https://example.test/", {})
    assert all(result["ok"] for result in results)
    assert [result["path"] for result in results] == [
        "/",
        "/app.js",
        "/api/runs",
        "/api/agent",
    ]
    assert "run-a" in results[2]["detail"]


def test_check_public_names_an_access_redirect(monkeypatch: pytest.MonkeyPatch) -> None:
    """An Access redirect explains how to supply a service token."""
    location = "https://example.cloudflareaccess.com/cdn-cgi/access/login"

    def fake_fetch(
        url: str,
        headers: dict[str, str],
        timeout: float,
    ) -> tuple[int, dict[str, str], bytes]:
        return 302, {"Location": location}, b""

    monkeypatch.setattr(public_smoke, "_fetch", fake_fetch)
    results = public_smoke.check_public("https://example.test", {})
    assert all(not result["ok"] for result in results)
    assert all("service token" in str(result["detail"]) for result in results)


def test_main_reports_a_partial_token(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A half-configured token exits before any network request."""
    monkeypatch.setenv("CF_ACCESS_CLIENT_ID", "client")
    monkeypatch.delenv("CF_ACCESS_CLIENT_SECRET", raising=False)
    assert public_smoke.main(["--url", "https://example.test"]) == 2
    assert "set both" in capsys.readouterr().err


def test_fetch_reads_success_and_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """The fetch helper returns normal responses and HTTP error bodies."""

    class Response:
        status = 200
        headers: ClassVar[dict[str, str]] = {"Content-Type": "text/plain"}

        def __enter__(self) -> Response:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self, size: int) -> bytes:
            return b"ok"

    class Opener:
        def __init__(self, error: Exception | None = None) -> None:
            self.error = error

        def open(self, request: object, timeout: float) -> Response:
            if self.error:
                raise self.error
            return Response()

    monkeypatch.setattr(
        urllib.request,
        "build_opener",
        lambda handler: Opener(),
    )
    assert public_smoke._fetch("https://example.test", {}, 1)[0:1] == (200,)
    headers = email.message.Message()
    headers["Content-Type"] = "text/plain"
    error = urllib.error.HTTPError(
        "https://example.test",
        404,
        "Not Found",
        headers,
        io.BytesIO(b"missing"),
    )
    monkeypatch.setattr(
        urllib.request,
        "build_opener",
        lambda handler: Opener(error),
    )
    status, _headers, body = public_smoke._fetch("https://example.test", {}, 1)
    assert status == 404
    assert body == b"missing"


def test_redirect_detail_falls_back_to_the_location() -> None:
    """A non-Access redirect still reports where it went."""
    assert "example.test" in public_smoke._redirect_detail(
        302, {"Location": "https://example.test/login"}
    )


def test_main_reports_success_and_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Main prints a concise result and returns the documented codes."""
    monkeypatch.delenv("CF_ACCESS_CLIENT_ID", raising=False)
    monkeypatch.delenv("CF_ACCESS_CLIENT_SECRET", raising=False)
    monkeypatch.setattr(
        public_smoke,
        "check_public",
        lambda *args, **kwargs: [
            {"path": "/", "ok": True, "status": 200, "detail": "ok"},
        ],
    )
    assert public_smoke.main(["--url", "https://example.test"]) == 0
    output = capsys.readouterr()
    assert "Public smoke passed." in output.out

    monkeypatch.setenv("CF_ACCESS_CLIENT_ID", "client")
    monkeypatch.setenv("CF_ACCESS_CLIENT_SECRET", "secret")
    monkeypatch.setattr(
        public_smoke,
        "check_public",
        lambda *args, **kwargs: [
            {"path": "/", "ok": False, "status": 302, "detail": "login"},
        ],
    )
    assert public_smoke.main(["--url", "https://example.test"]) == 1
    output = capsys.readouterr()
    assert "Using Cloudflare Access service-token headers." in output.out
    assert "Public smoke failed." in output.err
