"""A real-browser smoke test for the cockpit.

The test is skipped unless Playwright and its Chromium build are installed. CI installs
them in the dedicated browser job; the Python quality jobs stay browser-free.
"""

from __future__ import annotations

import json
import re
import shutil
import socket
import sqlite3
import threading
import time
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import Any

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
            expect(page.get_by_role("link", name="CSV", exact=True)).to_be_visible()
            expect(page.get_by_role("link", name="Package", exact=True)).to_have_attribute(
                "href", re.compile(r"/export\?")
            )

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


def test_direct_links_restore_table_and_compare_state(cockpit: str) -> None:
    """A shared URL reopens the same filtered table and comparison."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(
                f"{cockpit}/?workspace=results&panel=tables&run={RUN_ID}"
                "&table=FVS_Summary_Metric&q=10&column=Year",
                wait_until="networkidle",
            )
            expect(page.locator("#table-filter")).to_have_value("10")
            expect(page.locator("#table-filter")).to_have_attribute(
                "placeholder", "Filter Year (year)…"
            )
            expect(page.locator("#table-column")).to_have_value("Year")
            expect(page.locator("#panel-body")).to_contain_text("1 matching row")
            assert "table=FVS_Summary_Metric" in page.evaluate("window.location.search")
            assert "q=10" in page.evaluate("window.location.search")
            assert "column=Year" in page.evaluate("window.location.search")

            page.goto(
                f"{cockpit}/?workspace=results&panel=compare&run={RUN_ID}"
                f"&a={RUN_ID}-b&b={RUN_ID}&metric=Tph&ctable=FVS_Summary_Metric",
                wait_until="networkidle",
            )
            expect(page.locator(".compare-pickers select").nth(0)).to_have_value(f"{RUN_ID}-b")
            expect(page.locator(".compare-pickers select").nth(1)).to_have_value(RUN_ID)
            expect(page.locator("select").filter(has_text="TPH").first).to_have_value("Tph")
            assert "metric=Tph" in page.evaluate("window.location.search")
            assert f"a={RUN_ID}-b" in page.evaluate("window.location.search")
        finally:
            browser.close()


def test_the_table_shows_its_source_and_declared_units(cockpit: str) -> None:
    """A table header carries the same units the package sidecar declares."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(
                f"{cockpit}/?workspace=results&panel=tables&run={RUN_ID}&table=FVS_Summary_Metric",
                wait_until="networkidle",
            )
            expect(page.locator(".table-provenance")).to_contain_text("Source: FVSOut.db")
            expect(page.locator(".table-provenance")).to_contain_text("declared units")
            year_header = page.locator("th").filter(
                has=page.locator(".column-name", has_text=re.compile(r"^Year$")),
            )
            expect(year_header.locator(".column-unit")).to_have_text("year")
            tph_header = page.locator("th").filter(
                has=page.locator(".column-name", has_text=re.compile(r"^Tph$")),
            )
            expect(tph_header.locator(".column-unit")).to_have_text("trees/ha")
            expect(page.locator('#table-column option[value="Year"]')).to_have_text("Year · year")
            expect(page.locator('#table-column option[value="Tph"]')).to_have_text("Tph · trees/ha")
        finally:
            browser.close()


def test_a_large_page_only_renders_a_virtual_window(cockpit: str) -> None:
    """A 500-row page keeps the DOM small and still reveals the final row on scroll."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        rows = [{"TreeIndex": index, "DBH": index / 10} for index in range(500)]

        def table_page(route: Any) -> None:  # noqa: ANN401
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "name": "FVS_TreeList_Metric",
                        "columns": ["TreeIndex", "DBH"],
                        "rows": rows,
                        "total": len(rows),
                        "offset": 0,
                        "limit": 1000,
                        "query": "",
                        "column": "",
                        "oracle": True,
                        "source": "FVSOut.db",
                        "units": {"DBH": "cm"},
                    }
                ),
            )

        page.route(
            re.compile(r".*/api/runs/smoke-run/tables/FVS_TreeList_Metric\?.*"),
            table_page,
        )
        try:
            page.goto(
                f"{cockpit}/?workspace=results&panel=tables&run={RUN_ID}"
                "&table=FVS_TreeList_Metric&limit=1000",
                wait_until="networkidle",
            )
            expect(page.locator("tr.data-row").first).to_be_visible()
            assert 20 <= page.locator("tr.data-row").count() < 500
            page.locator(".table-scroll").evaluate(
                "(node) => { node.scrollTop = node.scrollHeight; }"
            )
            expect(page.locator("tr.data-row").last).to_contain_text("499")
        finally:
            browser.close()


def test_the_table_key_column_stays_pinned_when_scrolling_sideways(cockpit: str) -> None:
    """The first useful key column stays at the left while the rest scrolls."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 900})
        try:
            page.goto(
                f"{cockpit}/?workspace=results&panel=tables&run={RUN_ID}&table=FVS_TreeList_Metric",
                wait_until="networkidle",
            )
            sticky = page.locator("th.sticky-key")
            expect(sticky).to_have_count(1)
            expect(sticky).to_contain_text("Year")
            assert sticky.evaluate("(node) => getComputedStyle(node).position") == "sticky"
            scroll = page.locator(".table-scroll")
            assert scroll.evaluate("(node) => node.scrollWidth > node.clientWidth")
            before = sticky.bounding_box()
            scroll.evaluate("(node) => { node.scrollLeft = 160; }")
            page.wait_for_timeout(100)
            after = sticky.bounding_box()
            assert before is not None
            assert after is not None
            assert abs(before["x"] - after["x"]) < 1
            expect(page.locator("td.sticky-key").first).to_be_visible()
        finally:
            browser.close()


def test_a_large_table_can_page_and_change_its_page_size(cockpit: str) -> None:
    """The table pager exposes page size, page number, and the filtered row range."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(
                f"{cockpit}/?workspace=results&panel=tables&run={RUN_ID}"
                "&table=FVS_TreeList_Metric&limit=5",
                wait_until="networkidle",
            )
            expect(page.locator("#panel-body")).to_contain_text("Page 1 of 2")
            expect(page.locator("#panel-body")).to_contain_text("Rows 1")
            page.get_by_role("button", name="Next").click()
            expect(page.locator("#panel-body")).to_contain_text("Page 2 of 2")
            expect(page.locator("#panel-body")).to_contain_text("Rows 6")
            assert "limit=5" in page.evaluate("window.location.search")
            assert "offset=5" in page.evaluate("window.location.search")
        finally:
            browser.close()


def test_a_named_comparison_survives_reload(cockpit: str) -> None:
    """A saved comparison reloads its A/B runs and metric from localStorage."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(
                f"{cockpit}/?workspace=results&panel=compare&run={RUN_ID}"
                f"&a={RUN_ID}&b={RUN_ID}-b&metric=Tph",
                wait_until="networkidle",
            )
            page.locator("#compare-save-name").fill("smoke comparison")
            page.get_by_role("button", name="Save", exact=True).click()
            expect(page.locator("#compare-saved")).to_contain_text("smoke comparison")
            page.reload(wait_until="networkidle")
            expect(page.locator("#compare-saved")).to_contain_text("smoke comparison")
            page.get_by_role("button", name="Load").click()
            expect(page.locator(".compare-pickers select").nth(0)).to_have_value(RUN_ID)
            expect(page.locator(".compare-pickers select").nth(1)).to_have_value(f"{RUN_ID}-b")
            assert "metric=Tph" in page.evaluate("window.location.search")
        finally:
            browser.close()


def test_saved_comparisons_can_be_exported_and_imported(cockpit: str, tmp_path: Path) -> None:
    """A comparison file round-trips names, runs, metric, and table through the UI."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(
                f"{cockpit}/?workspace=results&panel=compare&run={RUN_ID}"
                f"&a={RUN_ID}&b={RUN_ID}-b&metric=Tph",
                wait_until="networkidle",
            )
            page.locator("#compare-save-name").fill("Export smoke")
            page.get_by_role("button", name="Save", exact=True).click()
            with page.expect_download() as download_info:
                page.get_by_role("button", name="Export JSON").click()
            exported = tmp_path / "exported.json"
            download_info.value.save_as(exported)
            payload = json.loads(exported.read_text(encoding="utf-8"))
            assert payload["version"] == 1
            assert payload["comparisons"][0]["name"] == "Export smoke"
            assert payload["comparisons"][0]["a"] == RUN_ID
            assert payload["comparisons"][0]["b"] == f"{RUN_ID}-b"
            assert payload["comparisons"][0]["metric"] == "Tph"

            imported = tmp_path / "imported.json"
            imported.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "comparisons": [
                            {
                                "name": "Imported smoke",
                                "a": f"{RUN_ID}-b",
                                "b": RUN_ID,
                                "metric": "BA",
                                "ctable": "FVS_Summary_Metric",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            page.locator("#compare-import-file").set_input_files(str(imported))
            expect(page.locator("#compare-saved")).to_have_value("Imported smoke")
            expect(page.locator("#compare-saved-status")).to_contain_text("Imported 1 comparison")
            page.get_by_role("button", name="Load").click()
            expect(page.locator(".compare-pickers select").nth(0)).to_have_value(f"{RUN_ID}-b")
            expect(page.locator(".compare-pickers select").nth(1)).to_have_value(RUN_ID)
            assert "metric=BA" in page.evaluate("window.location.search")

            malformed = tmp_path / "malformed.json"
            malformed.write_text("{}", encoding="utf-8")
            page.locator("#compare-import-file").set_input_files(str(malformed))
            expect(page.locator("#compare-saved-status")).to_contain_text(
                "Expected a comparisons array"
            )
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
                "/?workspace=calibration",
                f"/?workspace=results&panel=tables&run={RUN_ID}",
                f"/?workspace=results&panel=compare&run={RUN_ID}",
            ):
                page.goto(f"{cockpit}{path}", wait_until="networkidle")
                assert page.evaluate("document.body.scrollWidth <= document.body.clientWidth")
            expect(page.get_by_role("heading", name="Compare two runs")).to_be_visible()
            expect(page.locator(".scroll-hint").first).to_be_visible()
        finally:
            browser.close()


def test_mobile_table_controls_form_a_compact_grid(cockpit: str) -> None:
    """On a phone the filter, exports, and pager stack without losing controls."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 390, "height": 844})
        try:
            page.goto(
                f"{cockpit}/?workspace=results&panel=tables&run={RUN_ID}"
                "&table=FVS_TreeList_Metric&limit=5",
                wait_until="networkidle",
            )
            panel = page.locator("#panel-body").bounding_box()
            filter_box = page.locator("#table-filter").bounding_box()
            column_box = page.locator("#table-column").bounding_box()
            export_box = page.locator(".table-export-actions").bounding_box()
            assert panel is not None
            assert filter_box is not None
            assert column_box is not None
            assert export_box is not None
            assert (
                page.locator(".table-toolbar").evaluate("(node) => getComputedStyle(node).display")
                == "grid"
            )
            assert filter_box["width"] >= panel["width"] * 0.8
            assert column_box["y"] >= filter_box["y"] + filter_box["height"]
            assert export_box["y"] >= column_box["y"] + column_box["height"]
            assert (
                page.locator(".table-pager").evaluate("(node) => getComputedStyle(node).display")
                == "grid"
            )
            expect(page.locator(".table-page-summary")).to_be_visible()
            expect(page.locator(".table-pager select")).to_be_visible()
            next_button = page.get_by_role("button", name="Next", exact=True)
            expect(next_button).to_be_enabled()
            next_box = next_button.bounding_box()
            assert next_box is not None
            assert next_box["height"] >= 36
            assert page.evaluate("document.body.scrollWidth <= document.body.clientWidth")
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
            expect(page.locator("#calibration-filter")).to_be_visible()
            page.locator("#calibration-filter").fill("cwh-growth-4cm")
            page.get_by_role("button", name="Apply").click()
            expect(page.locator("#panel-body")).to_contain_text("1 of")
            page.get_by_role("button", name="Details", exact=True).click()
            page.locator(".calibration-detail").get_by_role("button", name="Use in new run").click()
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


def test_the_assistant_model_selector_sends_the_chosen_model(cockpit: str) -> None:
    """The drawer lists the CLI models and records the selected model per reply."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        captured: dict[str, object] = {}

        def agent_info(route: Any) -> None:  # noqa: ANN401
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "enabled": True,
                        "available": True,
                        "model": "provider/model",
                        "models": ["provider/model", "provider/other"],
                        "workspace": "/tmp",
                        "timeout": 30.0,
                    }
                ),
            )

        def agent_chat(route: Any) -> None:  # noqa: ANN401
            captured.update(route.request.post_data_json)
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "reply": "model answer",
                        "session": "ses_test",
                        "model": captured["model"],
                        "actions": [],
                        "chips": [],
                    }
                ),
            )

        page.route("**/api/agent", agent_info)
        page.route("**/api/agent/chat", agent_chat)
        try:
            page.goto(f"{cockpit}/?workspace=stand&run={RUN_ID}", wait_until="networkidle")
            page.get_by_role("button", name="Ask the FVS assistant").click()
            select = page.locator("#assistant-model-select")
            expect(select).to_be_visible()
            expect(select.locator("option")).to_have_count(2)
            select.select_option("provider/other")
            page.locator("#assistant-input").fill("hello")
            page.locator("#assistant-input").press("Enter")
            expect(page.locator("#assistant-log")).to_contain_text("model answer")
            expect(page.locator(".assistant-meta")).to_have_text("provider/other")
            assert captured["model"] == "provider/other"
        finally:
            browser.close()


def test_an_assistant_table_chip_opens_the_filtered_row(cockpit: str) -> None:
    """A cited table/column/value becomes a filtered Tables view."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.route(
            "**/api/assistant",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "reply": "The year-10 row is the one.",
                        "citations": [],
                        "suggestions": [],
                        "chips": [
                            {
                                "label": "Year 10",
                                "action": "open_table",
                                "target": "FVS_Summary_Metric",
                                "column": "Year",
                                "query": "10",
                            }
                        ],
                    }
                ),
            ),
        )
        try:
            page.goto(f"{cockpit}/?workspace=stand&run={RUN_ID}", wait_until="networkidle")
            page.get_by_role("button", name="Ask the FVS assistant").click()
            page.locator("#assistant-input").fill("cite the year")
            page.locator("#assistant-input").press("Enter")
            page.get_by_role("button", name="Year 10", exact=True).click()
            expect(page.locator("#table-filter")).to_have_value("10")
            expect(page.locator("#table-column")).to_have_value("Year")
            expect(page.locator("#panel-body")).to_contain_text("1 matching row")
        finally:
            browser.close()


def test_the_assistant_conversation_survives_reload(cockpit: str) -> None:
    """The local fallback conversation and session survive a page reload."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(f"{cockpit}/?workspace=stand&run={RUN_ID}", wait_until="networkidle")
            page.get_by_role("button", name="Ask the FVS assistant").click()
            input_box = page.locator("#assistant-input")
            input_box.fill("Persistence smoke")
            input_box.press("Enter")
            expect(page.locator("#assistant-log")).to_contain_text(RUN_ID)
            with page.expect_download() as download_info:
                page.get_by_role("button", name="Export", exact=True).click()
            transcript = download_info.value.path()
            assert transcript is not None
            text = transcript.read_text(encoding="utf-8")
            assert "fresh-fvsbc assistant transcript" in text
            assert f"Run: {RUN_ID}" in text
            assert "Persistence smoke" in text
            page.reload(wait_until="networkidle")
            page.get_by_role("button", name="Ask the FVS assistant").click()
            expect(page.locator("#assistant-log")).to_contain_text("Persistence smoke")
            expect(page.locator("#assistant-status")).to_contain_text("restored")
        finally:
            browser.close()


def test_an_assistant_chat_can_be_pinned_loaded_and_deleted(cockpit: str) -> None:
    """A named transcript survives clearing, reload, load, and delete."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(f"{cockpit}/?workspace=stand&run={RUN_ID}", wait_until="networkidle")
            page.get_by_role("button", name="Ask the FVS assistant").click()
            page.locator("#assistant-input").fill("Transcript smoke")
            page.locator("#assistant-input").press("Enter")
            expect(page.locator("#assistant-log")).to_contain_text(RUN_ID)

            page.locator("#assistant-saved summary").click()
            page.locator("#assistant-pin-name").fill("Pinned smoke")
            page.get_by_role("button", name="Pin current").click()
            expect(page.locator("#assistant-saved-status")).to_contain_text("Pinned")
            expect(page.locator("#assistant-saved-select")).to_contain_text("Pinned smoke")

            page.get_by_role("button", name="New", exact=True).click()
            expect(page.locator("#assistant-log")).not_to_contain_text("Transcript smoke")
            page.get_by_role("button", name="Load", exact=True).click()
            expect(page.locator("#assistant-log")).to_contain_text("Transcript smoke")
            expect(page.locator("#assistant-saved-status")).to_contain_text("Loaded")

            page.reload(wait_until="networkidle")
            page.get_by_role("button", name="Ask the FVS assistant").click()
            page.locator("#assistant-saved summary").click()
            saved = page.locator("#assistant-saved-select")
            saved.select_option(label="Pinned smoke")
            page.get_by_role("button", name="Load", exact=True).click()
            expect(page.locator("#assistant-log")).to_contain_text("Transcript smoke")

            page.get_by_role("button", name="Delete", exact=True).click()
            expect(page.locator("#assistant-saved-status")).to_contain_text("Deleted")
            expect(saved).not_to_contain_text("Pinned smoke")
        finally:
            browser.close()


def test_a_saved_chat_can_be_renamed_and_exported(cockpit: str, tmp_path: Path) -> None:
    """Renaming keeps the transcript, and the JSON export carries it."""
    expect = playwright_module.expect
    with playwright_module.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(f"{cockpit}/?workspace=stand&run={RUN_ID}", wait_until="networkidle")
            page.get_by_role("button", name="Ask the FVS assistant").click()
            page.locator("#assistant-input").fill("Rename export smoke")
            page.locator("#assistant-input").press("Enter")
            expect(page.locator("#assistant-log")).to_contain_text(RUN_ID)

            page.locator("#assistant-saved summary").click()
            page.locator("#assistant-pin-name").fill("Original chat")
            page.get_by_role("button", name="Pin current").click()
            expect(page.locator("#assistant-saved-select option:checked")).to_have_text(
                "Original chat"
            )

            page.locator("#assistant-pin-name").fill("Renamed chat")
            page.get_by_role("button", name="Rename", exact=True).click()
            expect(page.locator("#assistant-saved-status")).to_contain_text("Renamed to")
            saved = page.locator("#assistant-saved-select")
            expect(saved).to_contain_text("Renamed chat")
            expect(saved).not_to_contain_text("Original chat")

            with page.expect_download() as download_info:
                page.locator("#assistant-saved-export").click()
            exported = tmp_path / "assistant-chats.json"
            download_info.value.save_as(exported)
            payload = json.loads(exported.read_text(encoding="utf-8"))
            assert payload["version"] == 1
            assert payload["chats"][0]["name"] == "Renamed chat"
            assert payload["chats"][0]["history"][0]["role"] == "user"
            assert "Rename export smoke" in payload["chats"][0]["history"][0]["text"]
            assert "session" in payload["chats"][0]

            page.locator("#assistant-pin-name").fill("Original chat")
            page.get_by_role("button", name="Pin current").click()
            page.locator("#assistant-pin-name").fill("Renamed chat")
            page.get_by_role("button", name="Rename", exact=True).click()
            expect(page.locator("#assistant-saved-status")).to_contain_text("already uses")

            page.reload(wait_until="networkidle")
            page.get_by_role("button", name="Ask the FVS assistant").click()
            page.locator("#assistant-saved summary").click()
            expect(page.locator("#assistant-saved-select")).to_contain_text("Renamed chat")
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
