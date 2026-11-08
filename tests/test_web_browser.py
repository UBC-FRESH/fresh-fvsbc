"""A real-browser smoke test for the cockpit.

The test is skipped unless Playwright and its Chromium build are installed. CI installs
them in the dedicated browser job; the Python quality jobs stay browser-free.
"""

from __future__ import annotations

import json
import shutil
import socket
import sqlite3
import threading
import time
import urllib.request
from collections.abc import Iterator
from pathlib import Path

import pytest

from fresh_fvsbc.web import app as webapp

playwright_module = pytest.importorskip("playwright.sync_api")

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "smoke-run"
BUNDLE = ROOT / "notes/reference/calibration/d7-cwh-4cm-bundle.json"


def _make_run(root: Path) -> None:
    """Write one complete run with a small, deterministic tree list."""
    run = root / RUN_ID
    run.mkdir(parents=True)
    (run / "run.key").write_text("STDIDENT\nbrowser smoke\n", encoding="utf-8")
    (run / "summary.csv").write_text(
        "year,age,tpa,baa\n0,60,3,3.0\n10,70,2,2.4\n", encoding="utf-8"
    )
    (run / "provenance.json").write_text(
        json.dumps(
            {
                "fresh_fvsbc_version": "0.21.4",
                "pyfvs_commit": "e95172b",
                "fvs_source_commit": "ef5fa847",
                "variant": "bc",
                "calibration_id": "cwh-growth-4cm-pilot-2026-11-04",
                "calibration_version": "0.1.3",
                "bec": "CWHvm1",
                "qmd": 12.3,
                "ba": 35.0,
                "tsa": "Arrowsmith TSA",
            }
        ),
        encoding="utf-8",
    )
    (run / "variants.json").write_text(json.dumps({"BC": "OK"}), encoding="utf-8")
    connection = sqlite3.connect(run / "FVSOut.db")
    try:
        connection.execute("create table FVS_Cases (CaseID text, StandID text, Variant text)")
        connection.execute(
            "create table FVS_TreeList_Metric ("
            "Year integer, PtIndex integer, TreeIndex integer, TreeId text, "
            "SpeciesFVS text, SpeciesPLANTS text, DBH real, Ht real, TPH real, "
            "PctCr real, CrWidth real, TreeAge real)"
        )
        rows = [
            (0, 1, 1, "0:1", "FD", "FD", 12.0, 14.0, 300.0, 55.0, 3.2, 60.0),
            (0, 1, 2, "0:2", "HW", "HW", 8.0, 10.0, 200.0, 48.0, 2.4, 55.0),
            (0, 2, 1, "0:3", "FD", "FD", 20.0, 19.0, 150.0, 35.0, 4.1, 70.0),
            (10, 1, 1, "10:1", "FD", "FD", 18.0, 18.0, 250.0, 50.0, 4.0, 70.0),
            (10, 1, 2, "10:2", "HW", "HW", 13.0, 14.0, 180.0, 44.0, 3.1, 65.0),
            (10, 2, 1, "10:3", "FD", "FD", 25.0, 22.0, 120.0, 30.0, 4.8, 80.0),
        ]
        connection.executemany(
            "insert into FVS_TreeList_Metric values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows
        )
        connection.execute(
            "create table FVS_Summary_Metric ("
            "Year integer, Age integer, Tph real, BA real, QMD real, TopHt real, "
            "CCF real, TCuM real, MCuM real)"
        )
        connection.executemany(
            "insert into FVS_Summary_Metric values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (0, 60, 300.0, 3.0, 5.0, 7.0, 10.0, 20.0, 18.0),
                (10, 70, 210.0, 18.0, 33.7, 33.0, 72.0, 207.0, 200.0),
            ],
        )
        connection.execute("insert into FVS_Cases values ('c1', 'S1', 'BC')")
        connection.commit()
    finally:
        connection.close()


@pytest.fixture(scope="module")
def cockpit(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    """Serve one temporary run and the reviewed CWH bundle on a loopback port."""
    uvicorn = pytest.importorskip("uvicorn")

    root = tmp_path_factory.mktemp("browser-runs")
    _make_run(root)
    shutil.copytree(root / RUN_ID, root / f"{RUN_ID}-b")
    application = webapp.create_app([root], bundles=[BUNDLE])

    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    port = int(probe.getsockname()[1])
    probe.close()
    server = uvicorn.Server(
        uvicorn.Config(application, host="127.0.0.1", port=port, log_level="warning")
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            with urllib.request.urlopen(f"{base}/api/runs", timeout=0.5):
                break
        except OSError:
            time.sleep(0.05)
    else:  # pragma: no cover - only on a broken local server
        pytest.fail("the browser-smoke server did not start")
    try:
        yield base
    finally:
        server.should_exit = True
        thread.join(timeout=5)


def test_the_cockpit_runs_stand_calibration_and_url_state(cockpit: str) -> None:
    """The cockpit opens runs, draws a stand, lists bundles, and restores URL state."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        errors: list[str] = []
        page.on(
            "console",
            lambda message: errors.append(message.text) if message.type == "error" else None,
        )
        page.on("pageerror", lambda error: errors.append(str(error)))
        try:
            page.goto(f"{cockpit}/?workspace=runs&run={RUN_ID}", wait_until="networkidle")
            expect(page.get_by_role("heading", name="Runs", exact=True)).to_be_visible()
            card = page.locator("article").filter(has=page.get_by_text(RUN_ID, exact=True))
            expect(card).to_be_visible()
            card.get_by_role("button", name="Open", exact=True).click()
            expect(page.get_by_role("heading", name="Stand", exact=True)).to_be_visible()
            expect(page.locator("canvas.stand-canvas")).to_be_visible()
            expect(page.get_by_role("combobox", name="Stand year")).to_have_value("0")
            expect(page.locator(".stand-stats")).to_contain_text("TPH")

            page.get_by_role("tab", name="Results").click()
            page.get_by_role("tab", name="Summary").click()
            expect(page.locator("#panel-body")).to_contain_text(
                "Metric summary from FVS_Summary_Metric"
            )
            expect(page.locator("#panel-body")).to_contain_text("m²/ha")
            expect(page.locator("#panel-body")).to_contain_text("210")
            page.get_by_role("tab", name="Tables").click()
            expect(page.get_by_role("button", name="FVS_Summary_Metric · 2 ✓")).to_be_visible()
            expect(page.locator("#panel-body")).to_contain_text("Year")
            page.locator("#table-filter").fill("70")
            page.get_by_role("button", name="Apply").click()
            expect(page.locator("#panel-body")).to_contain_text("1 matching row")
            expect(page.locator("#panel-body")).to_contain_text("Rows 1")
            expect(page.locator("#panel-body")).to_contain_text("of 1")
            expect(page.get_by_role("link", name="Download CSV")).to_be_visible()

            page.get_by_role("tab", name="Evidence").click()
            page.get_by_role("tab", name="Provenance").click()
            expect(page.locator("#panel-body")).to_contain_text("Model version")
            expect(page.locator("#panel-body")).to_contain_text("Keyword set")
            expect(page.locator("#panel-body")).to_contain_text("unsigned")
            expect(page.locator("#panel-body")).to_contain_text("Raw provenance JSON")

            page.get_by_role("tab", name="Calibration").click()
            expect(page.get_by_role("heading", name="Calibration", exact=True)).to_be_visible()
            expect(page.get_by_text("cwh-growth-4cm-pilot-2026-11-04").first).to_be_visible()
            page.get_by_role("button", name="Details", exact=True).click()
            expect(page.locator("#panel-body")).to_contain_text("not signed off")

            page.goto(
                f"{cockpit}/?workspace=stand&run={RUN_ID}&year=10",
                wait_until="networkidle",
            )
            expect(page.get_by_role("heading", name="Stand", exact=True)).to_be_visible()
            expect(page.get_by_role("combobox", name="Stand year")).to_have_value("10")
            assert "year=10" in page.evaluate("window.location.search")
            assert errors == []
        finally:
            browser.close()


def test_the_compare_workspace_shows_two_run_deltas(cockpit: str) -> None:
    """Compare defaults to the metric summary and shows A/B deltas, not an empty Cases diff."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(
                f"{cockpit}/?workspace=results&panel=compare&run={RUN_ID}",
                wait_until="networkidle",
            )
            expect(page.get_by_role("heading", name="Compare two runs")).to_be_visible()
            expect(page.locator("#panel-body")).to_contain_text("Summary comparison")
            expect(page.locator("#panel-body")).to_contain_text("Year-by-year")
            expect(page.locator("#panel-body")).to_contain_text("Δ (B - A)")
            expect(page.locator("#panel-body")).to_contain_text("Row-level table diff")
            page.get_by_role("button", name="Swap").click()
            expect(page.locator("#panel-body")).to_contain_text("Summary comparison")
        finally:
            browser.close()


def test_the_mobile_shell_does_not_overflow(cockpit: str) -> None:
    """The runs and summary views fit a phone-width viewport."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 390, "height": 844})
        try:
            for path in (
                f"/?workspace=runs&run={RUN_ID}",
                f"/?workspace=results&panel=summary&run={RUN_ID}",
            ):
                page.goto(f"{cockpit}{path}", wait_until="networkidle")
                assert page.evaluate("document.body.scrollWidth <= document.body.clientWidth")
            expect(page.get_by_role("heading", name="Summary", exact=True)).to_be_visible()
        finally:
            browser.close()


def test_the_calibration_editor_previews_the_domain_and_cycles(cockpit: str) -> None:
    """A bundle can be carried into the run editor, where its domain and warnings are visible."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(f"{cockpit}/?workspace=calibration", wait_until="networkidle")
            page.get_by_role("button", name="Details", exact=True).click()
            page.get_by_role("button", name="Use in new run").click()
            expect(page.locator("#new-run-dialog")).to_be_visible()
            expect(page.locator("#new-bundle")).to_have_value("cwh-growth-4cm-pilot-2026-11-04")
            expect(page.locator("#new-bundle-preview")).to_contain_text("Domain")
            expect(page.locator("#new-bundle-preview")).to_contain_text("unsigned pilot")
            page.locator("#new-min-dbh").fill("2")
            expect(page.locator("#new-bundle-preview")).to_contain_text("below this bundle")
            page.locator("#new-cycles").fill("2")
            page.locator("#new-cycle-years").fill("5")
            expect(page.locator("#new-cycles")).to_have_value("2")
            expect(page.locator("#new-cycle-years")).to_have_value("5")
            page.get_by_role("button", name="Cancel").click()
            expect(page.locator("#new-run-dialog")).to_be_hidden()
        finally:
            browser.close()


def test_the_assistant_sends_on_enter_and_adds_a_newline_on_shift_enter(cockpit: str) -> None:
    """The narrow composer follows the familiar chat contract."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(f"{cockpit}/?workspace=stand&run={RUN_ID}", wait_until="networkidle")
            page.get_by_role("button", name="Ask the FVS assistant").click()
            input_box = page.locator("#assistant-input")
            expect(page.locator("#assistant-model")).to_contain_text("local summary")
            input_box.fill("Line one")
            input_box.press("Shift+Enter")
            input_box.type("Line two")
            expect(input_box).to_have_value("Line one\nLine two")
            expect(page.locator("#assistant-log")).not_to_contain_text("Line one")
            input_box.press("Enter")
            expect(page.locator("#assistant-log")).to_contain_text(RUN_ID)
            expect(input_box).to_have_value("")
            page.get_by_role("button", name="New", exact=True).click()
            expect(page.locator("#assistant-hint")).to_be_visible()
        finally:
            browser.close()


def test_the_details_drawer_restores_focus_and_escape_closes(cockpit: str) -> None:
    """The evidence drawer traps attention, reports its state, and returns focus."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(f"{cockpit}/?workspace=stand&run={RUN_ID}", wait_until="networkidle")
            trigger = page.locator("#details-button")
            expect(trigger).to_be_enabled()
            trigger.click()
            drawer = page.locator("#details-drawer")
            expect(drawer).to_be_visible()
            expect(trigger).to_have_attribute("aria-expanded", "true")
            assert page.evaluate("document.activeElement.id") == "close-details"
            assert page.evaluate("document.querySelector('.shell').inert") is True
            page.keyboard.press("Shift+Tab")
            assert (
                page.evaluate(
                    "document.querySelector('#details-drawer').contains(document.activeElement)"
                )
                is True
            )
            expect(page.get_by_text("Provenance record")).to_be_visible()
            page.keyboard.press("Escape")
            expect(drawer).to_be_hidden()
            assert page.evaluate("document.activeElement.id") == "details-button"
            assert page.evaluate("document.querySelector('.shell').inert") is False
        finally:
            browser.close()


def test_the_assistant_reads_the_open_run_and_cites_its_source(cockpit: str) -> None:
    """The assistant answers from the run and opens the cited panel."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(f"{cockpit}/?workspace=stand&run={RUN_ID}", wait_until="networkidle")
            page.get_by_role("button", name="Ask the FVS assistant").click()
            expect(page.locator("#assistant-drawer")).to_be_visible()
            page.locator("#assistant-quick button", has_text="Summary").click()
            expect(page.locator("#assistant-log")).to_contain_text(RUN_ID)
            expect(page.locator("#assistant-log")).to_contain_text("Latest TPH")
            page.locator("#assistant-log").get_by_role("button", name="Summary", exact=True).click()
            expect(page.locator("#assistant-drawer")).to_be_hidden()
            expect(page.locator("#panel-body")).to_contain_text("Summary")
            assert "workspace=results" in page.evaluate("window.location.search")
            assert "panel=summary" in page.evaluate("window.location.search")
        finally:
            browser.close()
