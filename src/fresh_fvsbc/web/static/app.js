/* fresh-fvsbc web shell: a reader over the artefacts a run already wrote.
 *
 * No framework and no build step, deliberately — the same choice the ws4 and fhops front ends make. Every
 * value on screen came from the run's own files; this script computes layout and nothing else.
 */

const state = {
  skins: [],
  runs: [],
  calibrations: [],
  calibration: null,
  calibrationQuery: "",
  calibrationReview: "all",
  oracle: null,
  skin: null,
  run: null,
  workspace: "runs",
  panel: null,
  table: null,
  compareA: null,
  compareB: null,
  compareTable: null,
  compareMetric: "BA",
  compareSaved: "",
  summaryColumn: null,
  tableQuery: "",
  tableColumn: "",
  tableHidden: [],
  tableColumnsOpen: false,
  tableOffset: 0,
  tableLimit: 200,
  standYear: null,
  pollTimer: null,
  ready: false,
  detailsTrigger: null,
  assistantTrigger: null,
  assistant: {
    mode: "local",
    model: null,
    session: null,
    history: [],
    controller: null,
    busy: false,
    enabled: false,
    available: false,
    savedChat: "",
  },
};

const WORKSPACES = [
  { id: "runs", title: "Runs", panels: [] },
  { id: "stand", title: "Stand", panels: ["visuals"] },
  { id: "results", title: "Results", panels: ["summary", "tables", "trees", "compare"] },
  { id: "evidence", title: "Evidence", panels: ["provenance", "keywords"] },
  { id: "calibration", title: "Calibration", panels: [] },
];

const el = (tag, props = {}, ...children) => {
  const node = document.createElement(tag);
  Object.assign(node, props);
  for (const child of children.flat()) {
    if (child === null || child === undefined) continue;
    node.append(child.nodeType ? child : document.createTextNode(String(child)));
  }
  return node;
};

const api = async (path) => {
  const response = await fetch(path, { headers: { accept: "application/json" } });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
      /* a non-JSON error body keeps the status text */
    }
    throw new Error(`${response.status}: ${detail}`);
  }
  return response.status === 204 ? null : response.json();
};

const fmt = (value) => {
  if (value === null || value === undefined) return "";
  if (typeof value === "number") {
    if (Number.isInteger(value)) return value.toLocaleString();
    return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }
  return String(value);
};

const isNumeric = (rows, column) =>
  rows.some((row) => typeof row[column] === "number");

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function stickyColumnFor(columns, rows) {
  if (columns.length <= 5) return null;
  for (const column of columns) {
    const values = rows
      .slice(0, 20)
      .map((row) => row[column])
      .filter((value) => value !== null && value !== undefined);
    if (!values.length) continue;
    if (values.every((value) => typeof value === "string" && UUID_PATTERN.test(value))) {
      continue;
    }
    return column;
  }
  return columns[0] ?? null;
}

function badge(text, kind) {
  return el("span", { className: `badge ${kind ?? ""}`.trim() }, text);
}

function workspace_definition(id) {
  return WORKSPACES.find((workspace) => workspace.id === id) ?? WORKSPACES[0];
}

function available_workspaces() {
  const panels = new Set(state.skin?.panels ?? []);
  return WORKSPACES.filter(
    (workspace) => workspace.id === "runs" || workspace.id === "calibration" || workspace.panels.some((panel) => panels.has(panel)),
  );
}

function workspace_panels(workspace = workspace_definition(state.workspace)) {
  const panels = new Set(state.skin?.panels ?? []);
  return workspace.panels.filter((panel) => panels.has(panel));
}

function wireTabs(container) {
  const tabs = [...container.querySelectorAll('[role="tab"]')];
  tabs.forEach((tab, index) => {
    tab.addEventListener("keydown", (event) => {
      let next = null;
      if (event.key === "ArrowRight" || event.key === "ArrowDown") next = (index + 1) % tabs.length;
      if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = (index - 1 + tabs.length) % tabs.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = tabs.length - 1;
      if (next === null) return;
      event.preventDefault();
      tabs[next].focus();
      tabs[next].click();
    });
  });
}

/* ---------------------------------------------------------------- shell */

function renderShell() {
  const skinSelect = document.getElementById("skin-select");
  skinSelect.replaceChildren(
    ...state.skins.map((skin) => el("option", { value: skin.id }, skin.title)),
  );
  skinSelect.value = state.skin?.id ?? state.skins[0]?.id;
  skinSelect.onchange = () => selectSkin(skinSelect.value);

  const runSelect = document.getElementById("run-select");
  runSelect.replaceChildren(
    el("option", { value: "" }, state.runs.length ? "choose a run" : "no runs found"),
    ...state.runs.map((run) => el("option", { value: run.id }, run.id)),
  );
  runSelect.value = state.run?.id ?? "";
  runSelect.onchange = () => selectRun(runSelect.value);

  const workspaces = available_workspaces();
  if (!workspaces.some((workspace) => workspace.id === state.workspace)) {
    state.workspace = workspaces[0]?.id ?? "runs";
  }
  const workspaceNav = document.getElementById("workspace-nav");
  workspaceNav.replaceChildren(
    ...workspaces.map((workspace) =>
      el(
        "button",
        {
          className: workspace.id === state.workspace ? "active" : "",
          onclick: () => selectWorkspace(workspace.id),
          role: "tab",
          "aria-selected": String(workspace.id === state.workspace),
          tabindex: workspace.id === state.workspace ? "0" : "-1",
        },
        workspace.title,
      ),
    ),
  );
  wireTabs(workspaceNav);

  const panels = workspace_panels();
  if (!panels.includes(state.panel)) state.panel = panels[0] ?? null;
  const panelNav = document.getElementById("panel-nav");
  panelNav.replaceChildren(
    ...panels.map((panel) =>
      el(
        "button",
        {
          className: panel === state.panel ? "active" : "",
          onclick: () => selectPanel(panel),
          role: "tab",
          "aria-selected": String(panel === state.panel),
          tabindex: panel === state.panel ? "0" : "-1",
        },
        panel[0].toUpperCase() + panel.slice(1),
      ),
    ),
  );
  wireTabs(panelNav);
  panelNav.hidden = state.workspace === "runs" || state.workspace === "stand" || panels.length === 0;

  const badgeEl = document.getElementById("run-state");
  badgeEl.className = "badge";
  badgeEl.textContent = state.run ? state.run.state : "";
  const detailsButton = document.getElementById("details-button");
  if (detailsButton) detailsButton.disabled = !state.run;

  const oracleEl = document.getElementById("oracle-badge");
  oracleEl.textContent = state.oracle
    ? `${state.oracle.standalone} of ${state.oracle.exposed} tables verified against a standalone FVSbc`
    : "";

  const note = document.getElementById("footer-note");
  note.textContent = state.skin
    ? `${state.skin.title}${state.skin.read_only ? " · read-only" : ""} · every value is read from the run's own files`
    : "";
}

function selectSkin(id) {
  state.skin = state.skins.find((skin) => skin.id === id) ?? state.skins[0];
  if (!state.skin.panels.includes(state.panel)) {
    state.panel = workspace_panels()[0] ?? null;
  }
  renderShell();
  renderPanel();
}

function selectRun(id) {
  state.run = state.runs.find((run) => run.id === id) ?? null;
  state.table = null;
  state.tableQuery = "";
  state.tableColumn = "";
  state.tableOffset = 0;
  state.summaryColumn = null;
  if (state.run) {
    const workspaces = available_workspaces();
    if (state.workspace === "runs" && workspaces.some((workspace) => workspace.id === "stand")) {
      state.workspace = "stand";
    }
  }
  renderShell();
  renderPanel();
  updateUrl();
}

function selectWorkspace(id) {
  state.workspace = id;
  state.panel = workspace_panels()[0] ?? null;
  renderShell();
  renderPanel();
  updateUrl();
}

function selectPanel(panel) {
  state.panel = panel;
  renderShell();
  renderPanel();
  updateUrl();
}

/* ---------------------------------------------------------------- panels */

async function renderPanel() {
  const body = document.getElementById("panel-body");
  if (typeof body._dispose === "function") {
    body._dispose();
    body._dispose = null;
  }
  body.replaceChildren();

  if (state.workspace === "runs") {
    await renderRuns(body);
    return;
  }
  if (state.workspace === "calibration") {
    await renderCalibration(body);
    return;
  }
  if (!state.run) {
    body.append(el("p", { className: "muted" }, "Choose a run, or start a new one."));
    return;
  }
  if (state.run.state !== "complete") {
    body.append(
      el(
        "div",
        { className: "notice" },
        `The run ${state.run.id} is still running. Results and the stand view become available when summary.csv is written.`,
      ),
    );
    body.append(runActions());
    return;
  }
  if (state.workspace === "stand") {
    await renderVisuals(body);
    return;
  }

  const renderers = {
    tables: renderTables,
    summary: renderSummary,
    trees: renderTrees,
    visuals: renderVisuals,
    keywords: renderKeywords,
    provenance: renderProvenance,
    compare: renderCompare,
  };
  const renderer = renderers[state.panel];
  if (!renderer) {
    body.append(el("p", { className: "muted" }, `No renderer for ${state.panel}.`));
    return;
  }
  body.append(runHeader());
  try {
    await renderer(body);
  } catch (error) {
    body.append(el("p", { className: "no-oracle" }, String(error)));
  }
}

async function renderRuns(body) {
  const heading = el("div", { className: "section-head" },
    el("div", {},
      el("h2", {}, "Runs"),
      el("p", { className: "muted" }, "Open a run to inspect its stand, results, and evidence. Start a new one from a tree list."),
    ),
  );
  body.append(heading);
  if (!state.runs.length) {
    body.append(el("div", { className: "empty-state" },
      el("strong", {}, "No runs yet"),
      el("p", { className: "muted" }, "The service searches its runs root one level deep. Start a run with a population path."),
    ));
    return;
  }
  const grid = el("div", { className: "run-grid" });
  for (const run of state.runs) {
    const complete = run.state === "complete";
    const latest = run.latest;
    const metricLine = latest
      ? `${fmt(latest.year)} yr · BA ${fmt(latest.ba)} m²/ha · TPH ${fmt(latest.tph)}`
      : complete
        ? "No metric summary table"
        : "Waiting for summary";
    grid.append(
      el("article", { className: "run-card", title: run.path },
        el("div", { className: "run-card-head" },
          el("strong", {}, run.id),
          badge(run.state, complete ? "ok" : ""),
        ),
        el("p", { className: "run-card-metric" }, metricLine),
        el("div", { className: "run-card-meta" },
          el("span", {}, `${run.tables} tables`),
          el("span", {}, complete ? "ready" : "in progress"),
        ),
        el("div", { className: "run-card-actions" },
          el("button", { className: "primary", type: "button", disabled: !complete,
            onclick: () => { state.run = run; selectWorkspace("stand"); } }, "Open"),
          el("button", { type: "button", disabled: !complete,
            onclick: () => { state.run = run; selectWorkspace("results"); selectPanel("summary"); } }, "Summary"),
          el("button", { type: "button", disabled: !complete,
            onclick: () => { state.run = run; selectWorkspace("evidence"); } }, "Evidence"),
        ),
      ),
    );
  }
  body.append(grid);
}

function runHeader() {
  const run = state.run;
  const latest = run.latest;
  return el("div", { className: "run-header" },
    el("div", {},
      el("h2", {}, run.id),
      el("p", { className: "muted", title: run.path },
        latest
          ? `${fmt(latest.year)} yr · BA ${fmt(latest.ba)} m²/ha · TPH ${fmt(latest.tph)} `
            + `· top height ${fmt(latest.top_height)} m`
          : `${run.tables} tables · ${run.state}`,
      ),
    ),
    runActions(),
  );
}

function runActions() {
  if (!state.run) return el("span");
  return el("div", { className: "run-actions" },
    el("button", { type: "button", onclick: () => selectWorkspace("stand") }, "Stand"),
    el("button", { type: "button", onclick: () => selectWorkspace("results") }, "Results"),
    el("button", { type: "button", onclick: () => selectWorkspace("evidence") }, "Evidence"),
  );
}

async function refreshRuns() {
  try {
    state.runs = await api("api/runs");
    if (state.run) {
      state.run = state.runs.find((run) => run.id === state.run.id) ?? state.run;
    }
    renderShell();
    if (state.workspace === "runs") await renderPanel();
    if (state.runs.some((run) => run.state === "running")) startPolling();
  } catch (error) {
    body_error(error);
  }
}

function startPolling() {
  if (state.pollTimer) return;
  state.pollTimer = window.setTimeout(async () => {
    state.pollTimer = null;
    await refreshRuns();
    if (state.runs.some((run) => run.state === "running") && !state.pollTimer) startPolling();
  }, 2500);
}

function populateBundleSelect() {
  const select = document.getElementById("new-bundle");
  if (!select) return;
  const current = select.value;
  select.replaceChildren(
    el("option", { value: "" }, "No calibration"),
    ...state.calibrations.map((bundle) =>
      el("option", { value: bundle.bundle_id },
        `${bundle.bundle_id} ${bundle.review?.signed_off ? "· signed" : "· unsigned"}`,
      ),
    ),
  );
  if (state.calibrations.some((bundle) => bundle.bundle_id === current)) select.value = current;
  updateBundleNote();
}

function bundleDomainSummary(bundle) {
  const domain = bundle.domain || {};
  const parts = [];
  if (domain.becs?.length) parts.push(`BEC ${domain.becs.join(", ")}`);
  if (domain.tsas?.length) parts.push(`TSA ${domain.tsas.join(", ")}`);
  if (domain.regions?.length) parts.push(`region ${domain.regions.join(", ")}`);
  if (domain.species_groups?.length) parts.push(`species ${domain.species_groups.join(", ")}`);
  if (domain.management?.length) parts.push(domain.management.join(" / "));
  if (domain.dbh_classes?.length) {
    parts.push(
      `DBH ${domain.dbh_classes.map(([low, high]) => `${low}–${high} cm`).join(", ")}`,
    );
  }
  if (domain.qmd_min) parts.push(`QMD ≥ ${domain.qmd_min} cm`);
  if (domain.ba_min) parts.push(`BA ≥ ${domain.ba_min} m²/ha`);
  return parts.length ? parts.join(" · ") : "unrestricted";
}

function updateBundleNote() {
  const select = document.getElementById("new-bundle");
  const note = document.getElementById("new-bundle-note");
  const preview = document.getElementById("new-bundle-preview");
  if (!select || !note || !preview) return;
  const bundle = state.calibrations.find((entry) => entry.bundle_id === select.value);
  preview.replaceChildren();
  if (!bundle) {
    note.textContent = "A bundle renders its parameters and ingrowth block into the run.";
    return;
  }
  note.textContent = bundle.claim;
  preview.append(
    el("div", { className: "preview-row" },
      el("strong", {}, "Domain"),
      el("span", {}, bundleDomainSummary(bundle)),
    ),
    el("div", { className: "preview-row" },
      el("strong", {}, "Review"),
      el("span", {}, bundle.review?.signed_off ? "signed" : "unsigned pilot"),
    ),
    el("div", { className: "preview-row" },
      el("strong", {}, "Parameters"),
      el("span", {}, `${bundle.parameters?.length ?? 0} keywords · ${bundle.ingrowth ? `${bundle.ingrowth.rates} ingrowth rates` : "no ingrowth"}`),
    ),
  );
  const lower = bundle.domain?.dbh_classes?.[0]?.[0];
  const minDbh = Number(document.getElementById("new-min-dbh")?.value);
  if (Number.isFinite(lower) && Number.isFinite(minDbh) && minDbh > 0 && minDbh < lower) {
    preview.append(
      el("p", { className: "preview-warning" },
        `Minimum DBH ${minDbh} cm is below this bundle's ${lower} cm domain; the run may be refused.`,
      ),
    );
  }
  for (const warning of bundle.warnings || []) {
    preview.append(el("p", { className: "preview-warning" }, warning));
  }
}

function openNewRun(bundleId = null) {
  const dialog = document.getElementById("new-run-dialog");
  const error = document.getElementById("new-run-error");
  if (error) error.hidden = true;
  populateBundleSelect();
  const bundle = document.getElementById("new-bundle");
  if (bundle) {
    bundle.onchange = updateBundleNote;
    if (typeof bundleId === "string" && state.calibrations.some((entry) => entry.bundle_id === bundleId)) {
      bundle.value = bundleId;
    }
  }
  const minDbh = document.getElementById("new-min-dbh");
  if (minDbh) minDbh.oninput = updateBundleNote;
  updateBundleNote();
  if (dialog?.showModal) dialog.showModal();
  else dialog?.setAttribute("open", "");
  document.getElementById("new-population")?.focus();
}

function closeNewRun() {
  const dialog = document.getElementById("new-run-dialog");
  if (dialog?.close) dialog.close();
  else dialog?.removeAttribute("open");
}

async function submitNewRun(event) {
  event.preventDefault();
  const error = document.getElementById("new-run-error");
  const population = document.getElementById("new-population").value.trim();
  const species = document.getElementById("new-species").value.trim();
  const treeAge = Number(document.getElementById("new-tree-age").value);
  const id = document.getElementById("new-run-id").value.trim();
  const keywords = document.getElementById("new-keywords").value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  const bundle = document.getElementById("new-bundle").value;
  const minDbh = document.getElementById("new-min-dbh").value.trim();
  const tsa = document.getElementById("new-tsa").value.trim();
  const cyclesRaw = document.getElementById("new-cycles").value.trim();
  const cycleYearsRaw = document.getElementById("new-cycle-years").value.trim();
  const cycles = cyclesRaw ? Number(cyclesRaw) : 1;
  const cycleYears = cycleYearsRaw ? Number(cycleYearsRaw) : null;
  if (!population || !species || !Number.isFinite(treeAge)) {
    error.textContent = "Population, species, and tree age are required.";
    error.hidden = false;
    return;
  }
  if (!Number.isInteger(cycles) || cycles < 1) {
    error.textContent = "Cycles must be a whole number of at least one.";
    error.hidden = false;
    return;
  }
  if (cycleYears !== null && (!Number.isFinite(cycleYears) || cycleYears <= 0)) {
    error.textContent = "Cycle length must be a positive number of years.";
    error.hidden = false;
    return;
  }
  const payload = { population, species, tree_age: treeAge, keywords };
  if (id) payload.id = id;
  if (bundle) payload.bundle = bundle;
  if (minDbh) payload.min_dbh = Number(minDbh);
  if (tsa) payload.tsa = tsa;
  if (cycles !== 1) payload.cycles = cycles;
  if (cycleYears !== null) payload.cycle_years = cycleYears;
  try {
    const response = await fetch("api/runs", {
      method: "POST",
      headers: { "content-type": "application/json", accept: "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.detail ?? response.statusText);
    closeNewRun();
    document.getElementById("new-run-form").reset();
    state.runs = await api("api/runs");
    const created = state.runs.find((run) => run.id === body.id);
    state.run = created ?? null;
    state.workspace = "runs";
    renderShell();
    await renderPanel();
    startPolling();
  } catch (errorValue) {
    error.textContent = String(errorValue);
    error.hidden = false;
  }
}

function body_error(error) {
  document.getElementById("panel-body")?.replaceChildren(
    el("p", { className: "no-oracle" }, String(error)),
  );
}

async function renderCalibration(body) {
  body.append(
    el("div", { className: "section-head" },
      el("div", {},
        el("h2", {}, "Calibration"),
        el("p", { className: "muted" },
          "Bundle metadata, domain boundaries, parameters, and review warnings. "
            + "A bundle is not a certificate until its review is signed.",
        ),
      ),
      el("button", { type: "button", onclick: loadCalibrations }, "Refresh"),
    ),
  );
  if (!state.calibrations.length) {
    body.append(el("div", { className: "empty-state" },
      el("strong", {}, "No calibration bundles found"),
      el("p", { className: "muted" },
        "Start the service with --bundles pointing at a directory of bundle JSON files.",
      ),
    ));
    return;
  }

  const filterInput = el("input", {
    id: "calibration-filter",
    type: "search",
    value: state.calibrationQuery,
    placeholder: "Filter bundle id, BEC, TSA, or claim…",
    "aria-label": "Filter calibration bundles",
  });
  const reviewSelect = el("select", {
    "aria-label": "Filter calibration review state",
    onchange: (event) => {
      state.calibrationReview = event.target.value;
      renderPanel();
    },
  },
    el("option", { value: "all", selected: state.calibrationReview === "all" }, "All reviews"),
    el("option", { value: "signed", selected: state.calibrationReview === "signed" }, "Signed"),
    el("option", { value: "unsigned", selected: state.calibrationReview === "unsigned" }, "Unsigned"),
  );
  body.append(
    el("form", {
      className: "table-toolbar calibration-toolbar",
      onsubmit: (event) => {
        event.preventDefault();
        state.calibrationQuery = filterInput.value.trim();
        renderPanel();
      },
    },
      filterInput,
      reviewSelect,
      el("button", { className: "primary", type: "submit" }, "Apply"),
      state.calibrationQuery || state.calibrationReview !== "all"
        ? el("button", {
            type: "button",
            onclick: () => {
              state.calibrationQuery = "";
              state.calibrationReview = "all";
              renderPanel();
            },
          }, "Clear")
        : null,
    ),
  );

  const query = state.calibrationQuery.toLowerCase();
  const filtered = state.calibrations.filter((bundle) => {
    const signed = Boolean(bundle.review?.signed_off);
    if (state.calibrationReview === "signed" && !signed) return false;
    if (state.calibrationReview === "unsigned" && signed) return false;
    if (!query) return true;
    const haystack = [
      bundle.bundle_id,
      bundle.claim,
      bundle.version,
      bundleDomainSummary(bundle),
      bundle.ingrowth?.model_id,
    ].filter(Boolean).join(" ").toLowerCase();
    return haystack.includes(query);
  });
  body.append(el("p", { className: "muted calibration-count" },
    `${filtered.length} of ${state.calibrations.length} bundles`
      + (query ? ` matching “${state.calibrationQuery}”` : ""),
  ));
  if (!filtered.length) {
    body.append(el("div", { className: "empty-state" },
      el("strong", {}, "No matching bundles"),
      el("p", { className: "muted" }, "Clear the filter or choose a different review state."),
    ));
  }

  const grid = el("div", { className: "run-grid" });
  for (const bundle of filtered) {
    const signed = Boolean(bundle.review?.signed_off);
    const warning = bundle.warnings?.[0];
    grid.append(
      el("article", { className: "run-card calibration-card", title: bundle.path },
        el("div", { className: "run-card-head" },
          el("strong", {}, bundle.bundle_id),
          badge(signed ? "signed" : "unsigned", signed ? "ok" : "warn"),
        ),
        el("p", { className: "calibration-domain" }, bundleDomainSummary(bundle)),
        el("div", { className: "run-card-meta" },
          el("span", {}, `v${bundle.version}`),
          el("span", {}, `${bundle.parameters.length} parameters`),
          el("span", {}, bundle.ingrowth ? `${bundle.ingrowth.rates} ingrowth rates` : "no ingrowth"),
        ),
        el("p", { className: "claim" }, bundle.claim),
        warning
          ? el("p", { className: "calibration-warning", title: bundle.warnings.join(" ") },
              `Warning: ${warning}${bundle.warnings.length > 1 ? ` (+${bundle.warnings.length - 1} more)` : ""}`,
            )
          : null,
        el("div", { className: "run-card-actions" },
          el("button", { type: "button", onclick: () => { state.calibration = bundle; renderPanel(); } }, "Details"),
          el("button", { class: "primary", type: "button", onclick: () => openNewRun(bundle.bundle_id) }, "Use in new run"),
        ),
      ),
    );
  }
  body.append(grid);

  const bundle = state.calibration;
  if (!bundle) return;
  const detail = el("section", { className: "calibration-detail" },
    el("div", { className: "section-head" },
      el("div", {},
        el("h2", {}, bundle.bundle_id),
        el("p", { className: "muted" }, `version ${bundle.version}`),
      ),
      el("div", { className: "run-card-actions" },
        el("button", { type: "button", class: "primary", onclick: () => openNewRun(bundle.bundle_id) }, "Use in new run"),
        el("button", { type: "button", class: "ghost", onclick: () => { state.calibration = null; renderPanel(); } }, "Close"),
      ),
    ),
    el("p", { className: "claim" }, bundle.claim),
  );
  if (bundle.warnings?.length) {
    detail.append(el("div", { className: "notice" }, ...bundle.warnings.map((warning) => el("p", {}, warning))));
  }
  const facts = [
    ["Signed", bundle.review?.signed_off ? "yes" : "no"],
    ["Reviewer", bundle.review?.reviewer ?? "—"],
    ["Date", bundle.review?.date ?? "—"],
    ["Domain", bundleDomainSummary(bundle)],
    ["Pins", Object.entries(bundle.pins || {}).map(([key, value]) => `${key}=${value}`).join(" · ")],
    ["Training split", bundle.training?.split ?? "—"],
    ["Ingrowth", bundle.ingrowth ? `${bundle.ingrowth.model_id} (${bundle.ingrowth.rates} rates)` : "none"],
  ];
  detail.append(el("div", { className: "grid" },
    ...facts.map(([label, value]) => el("div", { className: "card" }, el("h3", {}, label), el("p", {}, String(value)))),
  ));
  const header = el("tr", {}, el("th", {}, "Keyword"), el("th", {}, "Fields"), el("th", {}, "Units"), el("th", {}, "Bounds"));
  const rows = bundle.parameters.map((parameter) =>
    el("tr", {},
      el("td", {}, parameter.keyword),
      el("td", {}, parameter.fields.join(", ")),
      el("td", {}, parameter.units),
      el("td", {}, parameter.bounds ? parameter.bounds.join(" – ") : "—"),
    ),
  );
  detail.append(el("h3", {}, "Parameters"));
  detail.append(el("div", { className: "scroll" }, el("table", {}, el("thead", {}, header), el("tbody", {}, ...rows))));
  body.append(detail);
}

async function loadCalibrations() {
  try {
    state.calibrations = await api("api/calibrations");
    renderPanel();
  } catch (error) {
    body_error(error);
  }
}

function oracleNotice(tables) {
  const unverified = tables.filter((table) => !table.oracle).length;
  if (!unverified) return null;
  return el(
    "div",
    { className: "notice" },
    `${unverified} of these ${tables.length} tables are not checked against a reference. ` +
      "Their numbers are FVS's own output read back, not agreement with an independent build.",
  );
}

async function renderTables(body) {
  const tables = await api(`api/runs/${state.run.id}/tables`);
  body.append(el("h2", {}, "Tables"));
  body.append(
    el(
      "p",
      { className: "muted" },
      `${tables.length} exposed tables written by this run.`,
    ),
  );
  const notice = oracleNotice(tables);
  if (notice) body.append(notice);

  const list = el("div", { className: "table-list" });
  for (const table of tables) {
    list.append(
      el(
        "button",
        {
          className: table.name === state.table ? "active" : "",
          title: `${table.rows} rows${table.oracle ? " · checked against a reference" : ""}`,
          onclick: () => {
            state.table = table.name;
            state.tableQuery = "";
            state.tableColumn = "";
            state.tableHidden = [];
            state.tableColumnsOpen = false;
            state.tableOffset = 0;
            updateUrl();
            renderPanel();
          },
        },
        `${table.name} · ${fmt(table.rows)}`,
        table.oracle ? " ✓" : "",
      ),
    );
  }
  body.append(list);

  if (!state.table || !tables.some((table) => table.name === state.table)) {
    const preferred = ["FVS_Summary_Metric", "FVS_TreeList_Metric", "FVS_CutList_Metric"];
    state.table = preferred.find((name) => tables.some((table) => table.name === name))
      ?? tables[0]?.name
      ?? null;
    state.tableHidden = [];
    state.tableColumnsOpen = false;
    updateUrl();
  }
  if (!state.table) return;

  const tableInfo = tables.find((table) => table.name === state.table);
  const tableColumns = tableInfo?.columns ?? [];
  if (state.tableColumn && !tableColumns.includes(state.tableColumn)) {
    state.tableColumn = "";
    updateUrl();
  }
  const tablePath = `api/runs/${encodeURIComponent(state.run.id)}/tables/${encodeURIComponent(state.table)}`;
  const params = new URLSearchParams({
    limit: String(state.tableLimit),
    offset: String(state.tableOffset),
  });
  if (state.tableQuery) params.set("q", state.tableQuery);
  if (state.tableColumn) params.set("column", state.tableColumn);
  const payload = await api(`${tablePath}?${params.toString()}`);
  const knownHidden = state.tableHidden.filter((column) => payload.columns.includes(column));
  if (knownHidden.length !== state.tableHidden.length) state.tableHidden = knownHidden;
  let hidden = new Set(knownHidden);
  if (hidden.size >= payload.columns.length) {
    hidden = new Set();
    state.tableHidden = [];
  }
  const visibleColumns = payload.columns.filter((column) => !hidden.has(column));
  if (state.tableColumn && !visibleColumns.includes(state.tableColumn)) {
    state.tableColumn = "";
    updateUrl();
  }
  const csvParams = new URLSearchParams();
  if (state.tableQuery) csvParams.set("q", state.tableQuery);
  if (state.tableColumn) csvParams.set("column", state.tableColumn);
  const csvHref = `${tablePath}/csv${csvParams.toString() ? `?${csvParams}` : ""}`;
  const packageHref = `${tablePath}/export${csvParams.toString() ? `?${csvParams}` : ""}`;
  const selectedUnit = state.tableColumn ? payload.units?.[state.tableColumn] : undefined;
  const filterInput = el("input", {
    id: "table-filter",
    type: "search",
    value: state.tableQuery,
    placeholder: state.tableColumn
      ? `Filter ${state.tableColumn}${selectedUnit ? ` (${selectedUnit})` : ""}…`
      : "Filter any column…",
    "aria-label": "Filter table rows",
  });
  const columnSelect = el("select", {
    id: "table-column",
    "aria-label": "Filter column",
    onchange: (event) => {
      state.tableColumn = event.target.value;
      state.tableOffset = 0;
      updateUrl();
      renderPanel();
    },
  },
    el("option", { value: "", selected: state.tableColumn === "" }, "Any column"),
    ...visibleColumns.map((column) => {
      const unit = payload.units?.[column];
      const option = el(
        "option",
        { value: column, selected: column === state.tableColumn },
        unit ? `${column} · ${unit}` : column,
      );
      option.title = unit
        ? `${column} (${unit})`
        : `${column} — unit not declared`;
      return option;
    }),
  );
  const filterForm = el("form", {
    className: "table-toolbar",
    onsubmit: (event) => {
      event.preventDefault();
      state.tableQuery = filterInput.value.trim();
      state.tableOffset = 0;
      updateUrl();
      renderPanel();
    },
  },
    filterInput,
    columnSelect,
    el("button", { className: "primary", type: "submit" }, "Apply"),
    state.tableQuery
      ? el("button", {
          type: "button",
          className: "table-clear",
          onclick: () => {
            state.tableQuery = "";
            state.tableOffset = 0;
            updateUrl();
            renderPanel();
          },
        }, "Clear")
      : null,
    el("div", { className: "table-export-actions" },
      el("a", {
        className: "button-like",
        href: csvHref,
        download: `${state.run.id}-${state.table}.csv`,
        title: "CSV data only; use Package for units and provenance.",
      }, "CSV"),
      el("a", {
        className: "button-like",
        href: packageHref,
        download: `${state.run.id}-${state.table}.zip`,
        title: "CSV plus metadata.json and README.txt",
      }, "Package"),
    ),
  );
  body.append(filterForm);
  const columnsDetails = el(
    "details",
    { id: "table-columns", className: "table-columns", open: state.tableColumnsOpen },
    el("summary", {},
      `Columns · ${visibleColumns.length} of ${payload.columns.length} shown`,
    ),
    el("div", { className: "table-columns-body" },
      el("div", { className: "table-columns-grid" },
        ...payload.columns.map((column) => {
          const unit = payload.units?.[column];
          return el("label", { className: "table-column-toggle" },
            el("input", {
              type: "checkbox",
              value: column,
              checked: !hidden.has(column),
              onchange: (event) => {
                if (!event.target.checked && visibleColumns.length <= 1) {
                  event.target.checked = true;
                  return;
                }
                const next = new Set(state.tableHidden);
                if (event.target.checked) next.delete(column);
                else next.add(column);
                state.tableHidden = [...next];
                if (!event.target.checked && state.tableColumn === column) {
                  state.tableColumn = "";
                }
                state.tableColumnsOpen = true;
                updateUrl();
                renderPanel();
              },
            }),
            el("span", { className: "table-column-toggle-name" }, column),
            unit ? el("small", {}, unit) : null,
          );
        }),
      ),
      el("p", { className: "table-columns-note" },
        "Hidden columns stay in CSV and package exports.",
      ),
      el("button", {
        type: "button",
        onclick: () => {
          state.tableHidden = [];
          state.tableColumnsOpen = true;
          updateUrl();
          renderPanel();
        },
      }, "Show all columns"),
    ),
  );
  columnsDetails.addEventListener("toggle", () => {
    state.tableColumnsOpen = columnsDetails.open;
  });
  body.append(columnsDetails);
  body.append(
    el(
      "h3",
      {},
      `${payload.name} — ${fmt(payload.total)} ${state.tableQuery ? "matching " : ""}`
        + `${payload.total === 1 ? "row" : "rows"}, showing ${payload.rows.length}`
        + (state.tableQuery ? ` · filter “${state.tableQuery}”` : "")
        + (state.tableColumn
          ? ` · column ${state.tableColumn}${selectedUnit ? ` (${selectedUnit})` : ""}`
          : ""),
    ),
  );
  body.append(
    el(
      "p",
      { className: payload.oracle ? "oracle-tick" : "no-oracle" },
      payload.oracle
        ? "Checked against FVS's own database dump."
        : "No independent check: the reader proves the table exists and its columns match the schema.",
    ),
  );
  if (visibleColumns.length > 5) {
    body.append(el("p", { className: "scroll-hint" },
      "Scroll horizontally to see every column.",
    ));
  }
  if (!payload.rows.length) {
    body.append(el("div", { className: "empty-state" },
      el("strong", {}, state.tableQuery ? "No matching rows" : "No rows"),
      el("p", { className: "muted" }, state.tableQuery
        ? "Clear the filter or search for a different value."
        : "This table exists but has no rows."),
    ));
    return;
  }

  const units = payload.units ?? {};
  const declaredUnits = Object.keys(units).length;
  const stickyColumn = stickyColumnFor(visibleColumns, payload.rows);
  body.append(
    el("p", { className: "table-provenance" },
      `Source: ${payload.source ?? "FVSOut.db"} · `,
      declaredUnits
        ? `${declaredUnits} of ${payload.columns.length} columns have declared units; blank means this reader does not declare one.`
        : "This table has no declared units; blank does not mean dimensionless.",
      stickyColumn ? ` ${stickyColumn} stays pinned on wide screens.` : "",
    ),
  );
  const header = el(
    "tr",
    {},
    ...visibleColumns.map((column) => {
      const unit = units[column];
      const numeric = isNumeric(payload.rows, column);
      const sticky = column === stickyColumn;
      return el(
        "th",
        {
          className: `${numeric ? "num " : ""}${sticky ? "sticky-key" : ""}`.trim(),
          title: unit ? `${column} — ${unit}` : `${column} — unit not declared`,
        },
        el("span", { className: "column-name" }, column),
        unit ? el("span", { className: "column-unit" }, unit) : null,
      );
    }),
  );
  const numericColumns = new Set(
    visibleColumns.filter((column) => isNumeric(payload.rows, column)),
  );
  const rowAt = (index) => {
    const row = payload.rows[index];
    const node = el(
      "tr",
      { className: "data-row" },
      ...visibleColumns.map((column) => {
        const sticky = column === stickyColumn;
        const value = fmt(row[column]);
        const cell = el(
          "td",
          {
            className: `${numericColumns.has(column) ? "num " : ""}${sticky ? "sticky-key" : ""}`.trim(),
          },
          sticky ? el("span", { className: "sticky-value" }, value) : value,
        );
        if (sticky) cell.title = String(row[column] ?? "");
        return cell;
      }),
    );
    node.dataset.rowIndex = String(index);
    node.setAttribute("aria-rowindex", String(index + 2));
    return node;
  };
  const rowCount = payload.rows.length;
  const tbody = el("tbody");
  const table = el("table", {}, el("thead", {}, header), tbody);
  table.setAttribute("aria-rowcount", String(rowCount + 1));
  table.setAttribute("aria-colcount", String(visibleColumns.length));
  const scroll = el("div", { className: "scroll table-scroll" }, table);
  body.append(scroll);

  const VIRTUALIZE_AFTER = 120;
  if (rowCount <= VIRTUALIZE_AFTER) {
    tbody.append(...payload.rows.map((_, index) => rowAt(index)));
  } else {
    const headerHeight = header.getBoundingClientRect().height || 34;
    const probe = rowAt(0);
    tbody.append(probe);
    const rowHeight = probe.getBoundingClientRect().height || 29;
    probe.remove();
    let paintedStart = -1;
    let paintedEnd = -1;
    let frame = 0;
    const spacer = (height) => {
      const cell = el("td", { colSpan: visibleColumns.length });
      cell.style.height = `${height}px`;
      const row = el("tr", { className: "virtual-spacer" }, cell);
      row.style.height = `${height}px`;
      row.setAttribute("aria-hidden", "true");
      return row;
    };
    const paint = () => {
      const viewport = Math.max(rowHeight, scroll.clientHeight - headerHeight);
      const overscan = 6;
      const start = Math.max(
        0,
        Math.min(
          rowCount,
          Math.floor((scroll.scrollTop - headerHeight) / rowHeight) - overscan,
        ),
      );
      const end = Math.min(
        rowCount,
        start + Math.ceil(viewport / rowHeight) + overscan * 2,
      );
      if (start === paintedStart && end === paintedEnd) return;
      paintedStart = start;
      paintedEnd = end;
      const visible = [];
      if (start > 0) visible.push(spacer(start * rowHeight));
      for (let index = start; index < end; index += 1) visible.push(rowAt(index));
      if (end < rowCount) visible.push(spacer((rowCount - end) * rowHeight));
      tbody.replaceChildren(...visible);
    };
    const schedule = () => {
      if (frame) return;
      frame = window.requestAnimationFrame(() => {
        frame = 0;
        paint();
      });
    };
    scroll.addEventListener("scroll", schedule, { passive: true });
    const observer = new ResizeObserver(() => {
      if (!scroll.isConnected) {
        observer.disconnect();
        return;
      }
      paint();
    });
    observer.observe(scroll);
    paint();
    window.requestAnimationFrame(paint);
  }
  const firstRow = payload.offset + 1;
  const lastRow = payload.offset + payload.rows.length;
  const page = Math.floor(payload.offset / payload.limit) + 1;
  const pages = Math.max(1, Math.ceil(payload.total / payload.limit));
  const pageInput = el("input", {
    type: "number",
    min: "1",
    max: String(pages),
    value: String(page),
    "aria-label": "Page number",
    onchange: (event) => {
      const requested = Number(event.target.value);
      const target = Number.isFinite(requested)
        ? Math.max(1, Math.min(pages, Math.floor(requested)))
        : page;
      state.tableOffset = (target - 1) * payload.limit;
      updateUrl();
      renderPanel();
    },
  });
  const sizeSelect = el("select", {
    "aria-label": "Rows per page",
    onchange: (event) => {
      state.tableLimit = Number(event.target.value);
      state.tableOffset = 0;
      updateUrl();
      renderPanel();
    },
  },
    ...[5, 10, 25, 50, 100, 200, 500, 1000].map((size) =>
      el("option", { value: String(size), selected: size === payload.limit }, String(size)),
    ),
  );
  body.append(
    el("div", { className: "table-pager" },
      el("span", { className: "muted table-page-summary" },
        `Page ${fmt(page)} of ${fmt(pages)} · Rows ${fmt(firstRow)}–${fmt(lastRow)} of ${fmt(payload.total)}`,
      ),
      el("label", { className: "muted table-pager-field" }, "Rows ", sizeSelect),
      el("label", { className: "muted table-pager-field" }, "Go to ", pageInput),
      el("button", {
        type: "button",
        disabled: payload.offset <= 0,
        onclick: () => {
          state.tableOffset = Math.max(0, payload.offset - payload.limit);
          updateUrl();
          renderPanel();
        },
      }, "Previous"),
      el("button", {
        type: "button",
        disabled: payload.offset + payload.rows.length >= payload.total,
        onclick: () => {
          state.tableOffset = payload.offset + payload.limit;
          updateUrl();
          renderPanel();
        },
      }, "Next"),
    ),
  );
}

const SUMMARY_METRICS = {
  Year: { label: "Year", unit: "" },
  Age: { label: "Age", unit: "years" },
  Tph: { label: "TPH", unit: "trees/ha" },
  BA: { label: "BA", unit: "m²/ha" },
  QMD: { label: "QMD", unit: "cm" },
  TopHt: { label: "Top height", unit: "m" },
  CCF: { label: "CCF", unit: "%" },
  MCuM: { label: "Merch. volume", unit: "m³/ha" },
  TCuM: { label: "Total volume", unit: "m³/ha" },
};

const NATIVE_SUMMARY = {
  year: { label: "Year", unit: "" },
  age: { label: "Age", unit: "years" },
  tpa: { label: "TPA", unit: "trees/ac" },
  baa: { label: "BA", unit: "ft²/ac" },
  top_ht: { label: "Top height", unit: "ft" },
  ccf: { label: "CCF", unit: "%" },
  tcuft: { label: "Total volume", unit: "ft³/ac" },
  mcuft: { label: "Merch. volume", unit: "ft³/ac" },
};

async function loadSummaryRows(runId) {
  try {
    return {
      rows: await api(`api/runs/${encodeURIComponent(runId)}/metric-summary`),
      metric: true,
    };
  } catch (error) {
    return {
      rows: await api(`api/runs/${encodeURIComponent(runId)}/summary`),
      metric: false,
    };
  }
}

async function renderSummary(body) {
  const { rows, metric } = await loadSummaryRows(state.run.id);
  body.append(el("h2", {}, "Summary"));
  if (!rows.length) {
    body.append(el("p", { className: "muted" }, "This run wrote no summary rows."));
    return;
  }
  const schema = metric ? SUMMARY_METRICS : NATIVE_SUMMARY;
  const latest = rows[rows.length - 1];
  const kpiKeys = metric
    ? ["Year", "BA", "Tph", "QMD", "TopHt"]
    : ["year", "baa", "tpa", "top_ht"];
  const kpis = kpiKeys
    .filter((key) => schema[key] && latest[key] !== undefined && latest[key] !== null)
    .map((key) => [schema[key], latest[key]]);
  if (kpis.length) {
    body.append(
      el("div", { className: "kpi-grid" },
        ...kpis.map(([definition, value]) =>
          el("article", { className: "kpi-card" },
            el("span", { className: "kpi-label" },
              definition.label,
              definition.unit ? el("em", {}, ` ${definition.unit}`) : null,
            ),
            el("strong", {}, fmt(value)),
            el("small", {}, `at year ${fmt(latest.Year ?? latest.year ?? "?")}`),
          ),
        ),
      ),
    );
  }
  body.append(
    el("p", { className: "muted summary-source" },
      metric
        ? "Metric summary from FVS_Summary_Metric: BA m²/ha, TPH trees/ha, QMD cm, top height m, volume m³/ha."
        : "No FVS_Summary_Metric table in this run. These are summary.csv values in FVS native units "
          + "(ft²/ac, trees/ac, ft), not metric values.",
    ),
  );

  const columns = Object.keys(schema).filter((key) => rows.some((row) => row[key] !== undefined));
  const numeric = columns.filter((column) => isNumeric(rows, column) && schema[column]);
  const preferred = metric ? "BA" : "baa";
  if (!state.summaryColumn || !numeric.includes(state.summaryColumn)) {
    state.summaryColumn = numeric.includes(preferred) ? preferred : numeric[0];
  }

  const select = el(
    "select",
    {
      onchange: (event) => {
        state.summaryColumn = event.target.value;
        renderPanel();
      },
    },
    ...numeric.map((column) =>
      el("option", { value: column, selected: column === state.summaryColumn },
        schema[column].label,
      ),
    ),
  );
  body.append(el("label", { className: "muted" }, "Series ", select));

  const x = rows.map((_, index) => index);
  const y = rows.map((row) => Number(row[state.summaryColumn] ?? 0));
  const definition = schema[state.summaryColumn] ?? { label: state.summaryColumn, unit: "" };
  body.append(
    chart(
      x,
      y,
      rows.map((row) => row.Year ?? row.year ?? ""),
      definition.label,
      definition.unit,
    ),
  );

  body.append(el("h3", {}, "Rows"));
  const header = el(
    "tr",
    {},
    ...columns.map((column) =>
      el("th", {}, schema[column].label,
        schema[column].unit ? el("span", { className: "column-unit" }, schema[column].unit) : null,
      ),
    ),
  );
  const tableRows = rows.map((row) =>
    el("tr", {}, ...columns.map((column) => el("td", {}, fmt(row[column])))),
  );
  body.append(
    el(
      "div",
      { className: "scroll" },
      el("table", {}, el("thead", {}, header), el("tbody", {}, ...tableRows)),
    ),
  );
}

function chart(xs, ys, labels, name, unit = "") {
  const width = 720;
  const height = 260;
  const pad = { left: 64, right: 20, top: 20, bottom: 30 };
  const maxY = Math.max(...ys, 1);
  const minY = Math.min(...ys, 0);
  const spanY = maxY - minY || 1;
  const stepX = (width - pad.left - pad.right) / Math.max(xs.length - 1, 1);
  const px = (index) => pad.left + index * stepX;
  const py = (value) => height - pad.bottom - ((value - minY) / spanY) * (height - pad.top - pad.bottom);

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "chart");
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", `${name}${unit ? ` in ${unit}` : ""} over time`);

  for (let tick = 0; tick <= 3; tick += 1) {
    const value = minY + (spanY * tick) / 3;
    const y = py(value);
    const grid = document.createElementNS("http://www.w3.org/2000/svg", "line");
    grid.setAttribute("class", "chart-grid");
    grid.setAttribute("x1", pad.left);
    grid.setAttribute("y1", y);
    grid.setAttribute("x2", width - pad.right);
    grid.setAttribute("y2", y);
    svg.append(grid);
    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", pad.left - 8);
    label.setAttribute("y", y + 4);
    label.setAttribute("text-anchor", "end");
    label.textContent = fmt(value);
    svg.append(label);
  }

  const path = ys.map((value, index) => `${index ? "L" : "M"}${px(index)},${py(value)}`).join(" ");
  const line = document.createElementNS("http://www.w3.org/2000/svg", "path");
  line.setAttribute("class", "line");
  line.setAttribute("d", path);
  svg.append(line);

  const last = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  last.setAttribute("class", "chart-point");
  last.setAttribute("cx", px(ys.length - 1));
  last.setAttribute("cy", py(ys[ys.length - 1]));
  last.setAttribute("r", 3.5);
  svg.append(last);

  const axis = document.createElementNS("http://www.w3.org/2000/svg", "line");
  axis.setAttribute("class", "axis");
  axis.setAttribute("x1", pad.left);
  axis.setAttribute("y1", height - pad.bottom);
  axis.setAttribute("x2", width - pad.right);
  axis.setAttribute("y2", height - pad.bottom);
  svg.append(axis);

  for (let i = 0; i < labels.length; i += Math.max(1, Math.ceil(labels.length / 8))) {
    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", px(i));
    text.setAttribute("y", height - 8);
    text.setAttribute("text-anchor", "middle");
    text.textContent = String(labels[i]);
    svg.append(text);
  }

  const caption = document.createElementNS("http://www.w3.org/2000/svg", "text");
  caption.setAttribute("class", "chart-caption");
  caption.setAttribute("x", pad.left);
  caption.setAttribute("y", 14);
  caption.textContent = `${name}${unit ? ` (${unit})` : ""} · latest ${fmt(ys[ys.length - 1])}`;
  svg.append(caption);

  return svg;
}

async function renderTrees(body) {
  body.append(el("h2", {}, "Trees"));
  const tables = await api(`api/runs/${state.run.id}/tables`);
  const names = tables.map((table) => table.name);
  const wanted = ["FVS_TreeList_Metric", "FVS_CutList_Metric"].filter((name) =>
    names.includes(name),
  );
  if (!wanted.length) {
    body.append(el("p", { className: "muted" }, "This run wrote no per-tree tables."));
    return;
  }
  body.append(
    el(
      "div",
      { className: "notice" },
      "FVS spells one column differently in the two tables: CCum in the tree list, CCuM in the cut list.",
    ),
  );
  for (const name of wanted) {
    const payload = await api(
      `api/runs/${state.run.id}/tables/${encodeURIComponent(name)}?limit=200`,
    );
    body.append(el("h3", {}, `${name} — ${fmt(payload.total)} rows`));
    const columns = payload.columns.filter((column) =>
      ["Year", "TreeId", "SpeciesFVS", "SpeciesPLANTS", "DBH", "Ht", "TPH", "CCum", "CCuM"].includes(
        column,
      ),
    );
    const header = el("tr", {}, ...columns.map((column) => el("th", {}, column)));
    const rows = payload.rows.map((row) =>
      el("tr", {}, ...columns.map((column) => el("td", {}, fmt(row[column])))),
    );
    body.append(
      el(
        "div",
        { className: "scroll" },
        el("table", {}, el("thead", {}, header), el("tbody", {}, ...rows)),
      ),
    );
  }
}

async function renderVisuals(body) {
  // three.js is fetched only when this panel opens, and only when the 3D view is chosen.
  const module = await import("./visuals.js");
  await module.mountVisuals(body, state.run.id, {
    year: state.standYear,
    onYear: (year) => {
      state.standYear = year;
      updateUrl();
    },
  });
}

async function renderKeywords(body) {
  body.append(el("h2", {}, "Keyword set"));
  const response = await fetch(`api/runs/${state.run.id}/keywords`);
  const text = await response.text();
  body.append(el("p", { className: "muted" }, `run.key — ${text.split("\n").length} lines.`));
  body.append(el("pre", {}, text));
}

function copyValue(text, button) {
  const original = button.textContent;
  if (navigator.clipboard?.writeText) {
    navigator.clipboard.writeText(String(text)).then(() => {
      button.textContent = "Copied";
      window.setTimeout(() => { button.textContent = original; }, 1400);
    }).catch(() => {
      button.textContent = "Copy failed";
    });
  } else {
    button.textContent = "Copy unavailable";
  }
}

function hashRow(label, value) {
  const text = String(value ?? "—");
  const button = el("button", { type: "button", className: "ghost hash-copy" }, "Copy");
  button.addEventListener("click", () => copyValue(text, button));
  return el("div", { className: "hash-row" },
    el("span", { className: "hash-label" }, label),
    el("code", { title: text }, text),
    button,
  );
}

async function renderProvenance(body) {
  body.append(el("h2", {}, "Provenance"));
  let payload;
  try {
    payload = await api(`api/runs/${encodeURIComponent(state.run.id)}/provenance`);
  } catch (error) {
    body.append(el("p", { className: "no-oracle" }, String(error)));
    return;
  }
  const record = payload.provenance ?? null;
  if (!record) {
    body.append(el("div", { className: "empty-state" },
      el("strong", {}, "No provenance record"),
      el("p", { className: "muted" }, "This run did not write provenance.json."),
    ));
    return;
  }
  const pins = [
    ["Model version", record.fresh_fvsbc_version],
    ["PyFVS commit", record.pyfvs_commit],
    ["FVS source commit", record.fvs_source_commit],
    ["Variant", record.variant],
    ["Run date", record.run_datetime],
    ["Random seed", record.random_seed],
    ["Case id", record.case_id],
  ].filter(([, value]) => value !== undefined && value !== null && value !== "");
  body.append(
    el("div", { className: "pin-grid" },
      ...pins.map(([label, value]) =>
        el("article", { className: "pin-card" },
          el("span", { className: "muted" }, label),
          el("strong", { title: String(value ?? "") }, fmt(value)),
        ),
      ),
    ),
  );

  body.append(el("h3", {}, "Hashes"));
  body.append(
    el("div", { className: "hash-list" },
      hashRow("Keyword set", record.keyword_set_hash),
      hashRow("Tree list", record.treelist_hash),
    ),
  );

  body.append(el("h3", {}, "Calibration"));
  const calibrationId = record.calibration_id;
  if (!calibrationId) {
    body.append(el("p", { className: "muted" }, "No calibration bundle is recorded for this run."));
  } else {
    const bundle = state.calibrations.find((entry) => entry.bundle_id === calibrationId);
    const signed = Boolean(bundle?.review?.signed_off);
    body.append(
      el("div", { className: "calibration-callout" },
        el("div", { className: "calibration-callout-head" },
          el("strong", {}, calibrationId),
          badge(signed ? "signed" : "unsigned", signed ? "ok" : "warn"),
        ),
        el("p", { className: "muted" },
          `Version ${record.calibration_version || "—"} · `,
          bundle ? "bundle found in the configured roots" : "bundle is not in the configured roots",
        ),
        bundle?.claim ? el("p", { className: "claim" }, bundle.claim) : null,
        bundle?.warnings?.length
          ? el("div", { className: "notice" }, ...bundle.warnings.map((warning) => el("p", {}, warning)))
          : null,
      ),
    );
  }

  body.append(el("h3", {}, "Variants"));
  const variants = Array.isArray(payload.variants)
    ? payload.variants
    : Object.keys(payload.variants || {});
  body.append(
    el("div", { className: "badge-row" },
      ...(variants.length
        ? variants.map((variant) => badge(String(variant), "ok"))
        : [el("span", { className: "muted" }, "No variant list recorded.")]),
    ),
  );

  body.append(
    el("p", { className: "muted" },
      "A result without these pins cannot be reproduced.",
    ),
  );
  body.append(
    el("details", { className: "raw-record" },
      el("summary", {}, "Raw provenance JSON"),
      el("pre", {}, JSON.stringify(payload, null, 2)),
    ),
  );
}

function compareRowsByYear(rows) {
  const map = new Map();
  for (const row of rows) {
    const year = Number(row.Year ?? row.year ?? 0);
    if (Number.isFinite(year)) map.set(year, row);
  }
  return map;
}

function dualChart(years, seriesA, seriesB, name, unit) {
  const width = 720;
  const height = 280;
  const pad = { left: 64, right: 20, top: 34, bottom: 30 };
  const values = [...seriesA, ...seriesB].filter((value) => Number.isFinite(value));
  const maxY = Math.max(...values, 1);
  const minY = Math.min(...values, 0);
  const spanY = maxY - minY || 1;
  const stepX = (width - pad.left - pad.right) / Math.max(years.length - 1, 1);
  const px = (index) => pad.left + index * stepX;
  const py = (value) => height - pad.bottom - ((value - minY) / spanY) * (height - pad.top - pad.bottom);
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "chart");
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", `${name}${unit ? ` in ${unit}` : ""} for runs A and B`);

  for (let tick = 0; tick <= 3; tick += 1) {
    const value = minY + (spanY * tick) / 3;
    const y = py(value);
    const grid = document.createElementNS("http://www.w3.org/2000/svg", "line");
    grid.setAttribute("class", "chart-grid");
    grid.setAttribute("x1", pad.left);
    grid.setAttribute("y1", y);
    grid.setAttribute("x2", width - pad.right);
    grid.setAttribute("y2", y);
    svg.append(grid);
    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", pad.left - 8);
    label.setAttribute("y", y + 4);
    label.setAttribute("text-anchor", "end");
    label.textContent = fmt(value);
    svg.append(label);
  }

  const draw = (valuesForSeries, className) => {
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("class", `line ${className}`);
    path.setAttribute("d", valuesForSeries.map((value, index) =>
      `${index ? "L" : "M"}${px(index)},${py(Number(value) || 0)}`,
    ).join(" "));
    svg.append(path);
  };
  draw(seriesA, "series-a");
  draw(seriesB, "series-b");

  const axis = document.createElementNS("http://www.w3.org/2000/svg", "line");
  axis.setAttribute("class", "axis");
  axis.setAttribute("x1", pad.left);
  axis.setAttribute("y1", height - pad.bottom);
  axis.setAttribute("x2", width - pad.right);
  axis.setAttribute("y2", height - pad.bottom);
  svg.append(axis);

  for (let i = 0; i < years.length; i += Math.max(1, Math.ceil(years.length / 8))) {
    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", px(i));
    text.setAttribute("y", height - 8);
    text.setAttribute("text-anchor", "middle");
    text.textContent = String(years[i]);
    svg.append(text);
  }

  const caption = document.createElementNS("http://www.w3.org/2000/svg", "text");
  caption.setAttribute("class", "chart-caption");
  caption.setAttribute("x", pad.left);
  caption.setAttribute("y", 14);
  caption.textContent = `${name}${unit ? ` (${unit})` : ""}`;
  svg.append(caption);

  const legend = document.createElementNS("http://www.w3.org/2000/svg", "text");
  legend.setAttribute("class", "chart-legend");
  legend.setAttribute("x", width - pad.right);
  legend.setAttribute("y", 14);
  legend.setAttribute("text-anchor", "end");
  legend.textContent = "A ──   B ──";
  svg.append(legend);
  return svg;
}

const COMPARE_STORAGE_KEY = "fresh-fvsbc.comparisons";
const COMPARE_EXPORT_VERSION = 1;

function normaliseComparison(item) {
  if (!item || typeof item !== "object") return null;
  const name = typeof item.name === "string" ? item.name.trim().slice(0, 80) : "";
  const a = typeof item.a === "string" ? item.a.trim().slice(0, 200) : "";
  const b = typeof item.b === "string" ? item.b.trim().slice(0, 200) : "";
  const metric = typeof item.metric === "string" ? item.metric.trim().slice(0, 50) : "";
  const ctable = typeof item.ctable === "string" ? item.ctable.trim().slice(0, 100) : "";
  if (!name || !a || !b || !metric) return null;
  return { name, a, b, metric, ctable };
}

function readSavedComparisons() {
  let stored = null;
  try {
    stored = JSON.parse(window.localStorage.getItem(COMPARE_STORAGE_KEY) || "[]");
  } catch (_error) {
    stored = [];
  }
  if (!Array.isArray(stored)) return [];
  const seen = new Set();
  const items = [];
  for (const raw of stored) {
    const item = normaliseComparison(raw);
    if (!item || seen.has(item.name)) continue;
    seen.add(item.name);
    items.push(item);
    if (items.length === 20) break;
  }
  return items;
}

function writeSavedComparisons(items) {
  try {
    window.localStorage.setItem(COMPARE_STORAGE_KEY, JSON.stringify(items.slice(0, 20)));
  } catch (_error) {
    /* localStorage can be unavailable */
  }
}

function saveCurrentComparison(name) {
  const clean = String(name || "").trim();
  if (!clean) return false;
  const items = readSavedComparisons().filter((item) => item.name !== clean);
  items.unshift({
    name: clean.slice(0, 80),
    a: state.compareA,
    b: state.compareB,
    metric: state.compareMetric,
    ctable: state.compareTable ?? "",
  });
  writeSavedComparisons(items);
  state.compareSaved = clean.slice(0, 80);
  return true;
}

function comparisonExportText() {
  return `${JSON.stringify({
    version: COMPARE_EXPORT_VERSION,
    exported_at: new Date().toISOString(),
    comparisons: readSavedComparisons(),
  }, null, 2)}\n`;
}

function importComparisons(text) {
  let parsed = null;
  try {
    parsed = JSON.parse(text);
  } catch (_error) {
    throw new Error("That file is not valid JSON.");
  }
  const raw = Array.isArray(parsed) ? parsed : parsed?.comparisons;
  if (!Array.isArray(raw)) throw new Error("Expected a comparisons array.");
  const imported = [];
  const seen = new Set();
  for (const candidate of raw) {
    const item = normaliseComparison(candidate);
    if (!item || seen.has(item.name)) continue;
    seen.add(item.name);
    imported.push(item);
    if (imported.length === 20) break;
  }
  if (!imported.length) throw new Error("No valid comparisons found in that file.");
  const names = new Set(imported.map((item) => item.name));
  const merged = [
    ...imported,
    ...readSavedComparisons().filter((item) => !names.has(item.name)),
  ].slice(0, 20);
  writeSavedComparisons(merged);
  state.compareSaved = imported[0].name;
  return { imported: imported.length, total: merged.length };
}

async function renderCompare(body) {
  body.append(el("h2", {}, "Compare two runs"));
  const complete = state.runs.filter((run) => run.state === "complete");
  if (complete.length < 2) {
    body.append(el("p", { className: "muted" }, "Two complete runs are needed to compare."));
    return;
  }
  if (!state.compareA || !complete.some((run) => run.id === state.compareA)) {
    state.compareA = complete[0].id;
  }
  if (!state.compareB || !complete.some((run) => run.id === state.compareB)) {
    state.compareB = complete.find((run) => run.id !== state.compareA)?.id ?? complete[1].id;
  }

  const picker = (current, onchange) =>
    el(
      "select",
      { onchange },
      ...complete.map((run) =>
        el("option", { value: run.id, selected: run.id === current }, run.id),
      ),
    );

  body.append(
    el(
      "div",
      { className: "compare-pickers" },
      el("label", {}, "A ", picker(state.compareA, (event) => {
        state.compareA = event.target.value;
        updateUrl();
        renderPanel();
      })),
      el("label", {}, "B ", picker(state.compareB, (event) => {
        state.compareB = event.target.value;
        updateUrl();
        renderPanel();
      })),
      el("button", {
        type: "button",
        onclick: () => {
          [state.compareA, state.compareB] = [state.compareB, state.compareA];
          updateUrl();
          renderPanel();
        },
      }, "Swap"),
    ),
  );

  const saved = readSavedComparisons();
  if (!state.compareSaved && saved.length) state.compareSaved = saved[0].name;
  const savedSelect = el("select", {
    id: "compare-saved",
    "aria-label": "Saved comparisons",
    onchange: (event) => { state.compareSaved = event.target.value; },
  },
    el("option", { value: "" }, saved.length ? "Choose a saved comparison" : "No saved comparisons"),
    ...saved.map((item) =>
      el("option", { value: item.name, selected: item.name === state.compareSaved }, item.name),
    ),
  );
  const saveName = el("input", {
    id: "compare-save-name",
    type: "text",
    placeholder: "Name this comparison…",
    "aria-label": "Comparison name",
  });
  const savedStatus = el("p", {
    id: "compare-saved-status",
    className: "compare-saved-status",
    role: "status",
    "aria-live": "polite",
  }, "Saved in this browser. Export JSON to share; import merges by name.");
  const setSavedStatus = (text, kind = "") => {
    savedStatus.textContent = text;
    savedStatus.className = `compare-saved-status ${kind}`.trim();
  };
  const importFile = el("input", {
    id: "compare-import-file",
    type: "file",
    accept: ".json,application/json",
    hidden: true,
    "aria-label": "Import comparisons JSON",
  });
  importFile.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (file.size > 200_000) {
      setSavedStatus("That file is too large; choose a JSON export under 200 KB.", "error");
      event.target.value = "";
      return;
    }
    try {
      const result = importComparisons(await file.text());
      await renderPanel();
      const fresh = document.getElementById("compare-saved-status");
      if (fresh) {
        fresh.textContent = `Imported ${result.imported} comparison`
          + `${result.imported === 1 ? "" : "s"} (${result.total} saved).`;
      }
    } catch (error) {
      setSavedStatus(error?.message ?? "That file could not be imported.", "error");
    } finally {
      event.target.value = "";
    }
  });
  body.append(
    el("div", { className: "compare-saved" },
      el("div", { className: "compare-saved-row" },
        savedSelect,
        el("button", {
          type: "button",
          disabled: !saved.length,
          onclick: () => {
            const item = saved.find((entry) => entry.name === state.compareSaved);
            if (!item) return;
            state.compareA = item.a;
            state.compareB = item.b;
            state.compareMetric = item.metric;
            state.compareTable = item.ctable || null;
            updateUrl();
            renderPanel();
          },
        }, "Load"),
        el("button", {
          type: "button",
          disabled: !saved.length,
          onclick: () => {
            const items = readSavedComparisons().filter((item) => item.name !== state.compareSaved);
            writeSavedComparisons(items);
            state.compareSaved = items[0]?.name ?? "";
            renderPanel();
          },
        }, "Delete"),
        el("button", {
          type: "button",
          disabled: !saved.length,
          onclick: () => {
            const url = URL.createObjectURL(
              new Blob([comparisonExportText()], { type: "application/json" }),
            );
            const link = el("a", {
              href: url,
              download: "fresh-fvsbc-comparisons.json",
            });
            document.body.append(link);
            link.click();
            link.remove();
            window.setTimeout(() => URL.revokeObjectURL(url), 1000);
          },
        }, "Export JSON"),
        el("button", {
          type: "button",
          onclick: () => importFile.click(),
        }, "Import JSON"),
      ),
      el("div", { className: "compare-saved-row" },
        saveName,
        el("button", {
          type: "button",
          onclick: () => {
            if (saveCurrentComparison(saveName.value)) renderPanel();
          },
        }, "Save"),
      ),
      savedStatus,
      importFile,
    ),
  );

  const [summaryA, summaryB] = await Promise.all([
    loadSummaryRows(state.compareA),
    loadSummaryRows(state.compareB),
  ]);
  if (summaryA.metric && summaryB.metric) {
    const byYearA = compareRowsByYear(summaryA.rows);
    const byYearB = compareRowsByYear(summaryB.rows);
    const years = [...byYearA.keys()].filter((year) => byYearB.has(year)).sort((a, b) => a - b);
    if (!years.length) {
      body.append(el("p", { className: "muted" }, "The two runs share no summary years."));
    } else {
      const latestA = byYearA.get(years[years.length - 1]) ?? {};
      const latestB = byYearB.get(years[years.length - 1]) ?? {};
      const metrics = ["BA", "Tph", "QMD", "TopHt", "MCuM"];
      body.append(el("h3", {}, "Summary comparison"));
      body.append(el("div", { className: "kpi-grid compare-kpis" },
        ...metrics.map((key) => {
          const definition = SUMMARY_METRICS[key];
          const aValue = Number(latestA[key] ?? 0);
          const bValue = Number(latestB[key] ?? 0);
          const delta = bValue - aValue;
          return el("article", { className: "kpi-card" },
            el("span", { className: "kpi-label" },
              definition.label,
              definition.unit ? el("em", {}, ` ${definition.unit}`) : null,
            ),
            el("strong", {}, fmt(bValue)),
            el("small", {},
              `A ${fmt(aValue)} · Δ ${delta >= 0 ? "+" : ""}${fmt(delta)}`,
            ),
          );
        }),
      ));
      if (!state.compareMetric || !SUMMARY_METRICS[state.compareMetric]) {
        state.compareMetric = "BA";
        updateUrl();
      }
      const metricSelect = el("select", {
        onchange: (event) => {
          state.compareMetric = event.target.value;
          updateUrl();
          renderPanel();
        },
      }, ...metrics.map((key) =>
        el("option", { value: key, selected: key === state.compareMetric },
          SUMMARY_METRICS[key].label,
        ),
      ));
      body.append(el("label", { className: "muted" }, "Series ", metricSelect));
      const definition = SUMMARY_METRICS[state.compareMetric];
      body.append(dualChart(
        years,
        years.map((year) => Number(byYearA.get(year)?.[state.compareMetric] ?? 0)),
        years.map((year) => Number(byYearB.get(year)?.[state.compareMetric] ?? 0)),
        definition.label,
        definition.unit,
      ));
      body.append(el("h3", {}, "Year-by-year"));
      const header = el("tr", {},
        el("th", {}, "Year"),
        el("th", { className: "num" }, `A ${definition.label}`),
        el("th", { className: "num" }, `B ${definition.label}`),
        el("th", { className: "num" }, "Δ (B - A)"),
      );
      body.append(el("div", { className: "scroll" },
        el("table", {}, el("thead", {}, header), el("tbody", {},
          ...years.map((year) => {
            const aValue = Number(byYearA.get(year)?.[state.compareMetric] ?? 0);
            const bValue = Number(byYearB.get(year)?.[state.compareMetric] ?? 0);
            return el("tr", {},
              el("td", {}, fmt(year)),
              el("td", { className: "num" }, fmt(aValue)),
              el("td", { className: "num" }, fmt(bValue)),
              el("td", { className: "num" }, `${bValue - aValue >= 0 ? "+" : ""}${fmt(bValue - aValue)}`),
            );
          }),
        )),
      ));
    }
  } else {
    body.append(el("div", { className: "notice" },
      "Summary comparison needs FVS_Summary_Metric in both runs; "
        + "the row-level table comparison below is still available.",
    ));
  }

  const tablesA = await api(`api/runs/${state.compareA}/tables`);
  const tablesB = await api(`api/runs/${state.compareB}/tables`);
  const shared = tablesA
    .map((table) => table.name)
    .filter((name) => tablesB.some((table) => table.name === name));
  if (!shared.length) {
    body.append(el("p", { className: "muted" }, "The two runs share no exposed table."));
    return;
  }
  if (!state.compareTable || !shared.includes(state.compareTable)) {
    state.compareTable = ["FVS_Summary_Metric", "FVS_TreeList_Metric", "FVS_CutList_Metric"]
      .find((name) => shared.includes(name)) ?? shared[0];
    updateUrl();
  }

  body.append(el("h3", {}, "Row-level table diff"));
  body.append(el("label", { className: "muted" }, "Table ",
    el("select", {
      onchange: (event) => {
        state.compareTable = event.target.value;
        updateUrl();
        renderPanel();
      },
    }, ...shared.map((name) =>
      el("option", { value: name, selected: name === state.compareTable }, name),
    )),
  ));

  const [a, b] = await Promise.all([
    api(`api/runs/${state.compareA}/tables/${encodeURIComponent(state.compareTable)}?limit=5000`),
    api(`api/runs/${state.compareB}/tables/${encodeURIComponent(state.compareTable)}?limit=5000`),
  ]);
  // The database carries a different CaseID per run. Use the table's real identity instead:
  // Year for the summary, and plot + tree index for the per-tree tables.
  const keyCandidates = state.compareTable === "FVS_Summary_Metric"
    ? ["Year"]
    : state.compareTable.includes("TreeList") || state.compareTable.includes("CutList")
      ? ["Year", "PtIndex", "TreeIndex"]
      : ["Year", "TreeId", "TreeIndex"];
  const keyColumns = keyCandidates.filter((column) => a.columns.includes(column));
  const key = keyColumns.length ? keyColumns : ["Year"];
  const valueColumns = a.columns.filter(
    (column) => !keyColumns.includes(column) && isNumeric(a.rows, column),
  );
  const indexB = new Map(b.rows.map((row) => [key.map((c) => row[c]).join("|"), row]));
  const diffs = [];
  for (const row of a.rows) {
    const rowKey = key.map((c) => row[c]).join("|");
    const other = indexB.get(rowKey);
    if (!other) continue;
    let score = 0;
    const cells = {};
    for (const column of valueColumns) {
      const delta = Number(other[column] ?? 0) - Number(row[column] ?? 0);
      cells[column] = delta;
      score += Math.abs(delta);
    }
    diffs.push({ key: rowKey, cells, score });
  }
  diffs.sort((left, right) => right.score - left.score);
  const capped = diffs.slice(0, 200);
  body.append(el("p", { className: "muted" },
    `${diffs.length} rows matched on ${key.join(", ") || "row order"}; `
      + `showing the ${capped.length} with the largest absolute difference. B minus A.`,
  ));
  if (!capped.length) {
    body.append(el("p", { className: "muted" }, "No rows matched between the two runs."));
    return;
  }
  const header = el("tr", {},
    el("th", {}, key.join(" / ")),
    ...valueColumns.map((column) => el("th", { className: "num" }, column)),
  );
  if (valueColumns.length > 4) {
    body.append(el("p", { className: "scroll-hint" },
      "Scroll horizontally to see every diff column.",
    ));
  }
  const rows = capped.map((entry) =>
    el("tr", {},
      el("td", {}, entry.key),
      ...valueColumns.map((column) =>
        el("td", { className: "num" }, fmt(entry.cells[column])),
      ),
    ),
  );
  body.append(el("div", { className: "scroll" },
    el("table", {}, el("thead", {}, header), el("tbody", {}, ...rows)),
  ));
}

/* ---------------------------------------------------------------- URL state */

function readUrlState() {
  const params = new URLSearchParams(window.location.search);
  return {
    workspace: params.get("workspace"),
    run: params.get("run"),
    panel: params.get("panel"),
    year: params.get("year"),
    table: params.get("table"),
    q: params.get("q"),
    column: params.get("column"),
    offset: params.get("offset"),
    limit: params.get("limit"),
    a: params.get("a"),
    b: params.get("b"),
    metric: params.get("metric"),
    ctable: params.get("ctable"),
  };
}

function updateUrl() {
  if (!state.ready) return;
  const params = new URLSearchParams();
  if (state.workspace) params.set("workspace", state.workspace);
  if (state.run) params.set("run", state.run.id);
  if (state.panel) params.set("panel", state.panel);
  if (state.workspace === "stand" && state.standYear !== null) {
    params.set("year", String(state.standYear));
  }
  if (state.workspace === "results" && state.panel === "tables" && state.table) {
    params.set("table", state.table);
    if (state.tableQuery) params.set("q", state.tableQuery);
    if (state.tableColumn) params.set("column", state.tableColumn);
    if (state.tableLimit !== 200) params.set("limit", String(state.tableLimit));
    if (state.tableOffset > 0) params.set("offset", String(state.tableOffset));
  }
  if (state.workspace === "results" && state.panel === "compare") {
    if (state.compareA) params.set("a", state.compareA);
    if (state.compareB) params.set("b", state.compareB);
    if (state.compareMetric) params.set("metric", state.compareMetric);
    if (state.compareTable) params.set("ctable", state.compareTable);
  }
  const query = params.toString();
  window.history.replaceState(null, "", `${window.location.pathname}${query ? `?${query}` : ""}`);
}

/* ---------------------------------------------------------------- drawers */

const DRAWER_BACKGROUND = [".topbar", "#workspace-nav", ".shell", ".footer"];

function activeDrawer() {
  for (const id of ["assistant-drawer", "details-drawer"]) {
    const drawer = document.getElementById(id);
    if (drawer && !drawer.hidden) return drawer;
  }
  return null;
}

function syncDrawerBackground() {
  const open = Boolean(activeDrawer());
  for (const selector of DRAWER_BACKGROUND) {
    for (const element of document.querySelectorAll(selector)) {
      element.inert = open;
    }
  }
}

function drawerFocusables(drawer) {
  return [...drawer.querySelectorAll(
    'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), '
      + 'textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
  )].filter((element) => element.offsetParent !== null);
}

function trapDrawerTab(event) {
  if (event.key !== "Tab") return;
  const drawer = activeDrawer();
  if (!drawer) return;
  const focusable = drawerFocusables(drawer);
  if (!focusable.length) {
    event.preventDefault();
    return;
  }
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  const active = document.activeElement;
  if (event.shiftKey && (!drawer.contains(active) || active === first)) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && (!drawer.contains(active) || active === last)) {
    event.preventDefault();
    first.focus();
  }
}

/* ---------------------------------------------------------------- details drawer */

async function openDetails() {
  if (!state.run) return;
  const body = document.getElementById("details-body");
  const drawer = document.getElementById("details-drawer");
  const backdrop = document.getElementById("drawer-backdrop");
  closeAssistant();
  state.detailsTrigger = document.activeElement;
  body.replaceChildren(el("p", { className: "muted" }, "Loading provenance…"));
  drawer.hidden = false;
  backdrop.hidden = false;
  document.getElementById("details-button").setAttribute("aria-expanded", "true");
  document.body.classList.add("drawer-open");
  syncDrawerBackground();
  document.getElementById("close-details").focus();
  let payload;
  try {
    payload = await api(`api/runs/${encodeURIComponent(state.run.id)}/provenance`);
  } catch (error) {
    body.replaceChildren(el("p", { className: "no-oracle" }, String(error)));
    return;
  }
  const provenance = payload.provenance ?? {};
  const bundle = state.calibrations.find(
    (entry) => entry.bundle_id === provenance.calibration_id,
  );
  const facts = [
    ["Run", state.run.id],
    ["State", state.run.state],
    ["Path", state.run.path],
    ["Calibration", provenance.calibration_id || "none"],
    ["Calibration version", provenance.calibration_version || "—"],
    ["Bundle review", bundle ? (bundle.review?.signed_off ? "signed" : "unsigned") : "not listed"],
    ["BEC", provenance.bec ?? "—"],
    ["QMD", provenance.qmd ?? "—"],
    ["BA", provenance.ba ?? "—"],
    ["TSA", provenance.tsa ?? "—"],
  ];
  const grid = el("div", { className: "details-grid" },
    ...facts.flatMap(([label, value]) => [
      el("span", { className: "muted" }, label),
      el("strong", {}, String(value)),
    ]),
  );
  body.replaceChildren(
    el("p", { className: "details-lead" }, bundle?.claim ?? "No calibration bundle is recorded for this run."),
    grid,
  );
  if (bundle?.warnings?.length) {
    body.append(el("div", { className: "notice" }, ...bundle.warnings.map((warning) => el("p", {}, warning))));
  }
  body.append(el("h3", {}, "Provenance record"));
  body.append(el("pre", {}, JSON.stringify(payload, null, 2)));
}

function closeDetails() {
  const drawer = document.getElementById("details-drawer");
  if (!drawer || drawer.hidden) return;
  const backdrop = document.getElementById("drawer-backdrop");
  drawer.hidden = true;
  if (backdrop) backdrop.hidden = true;
  document.getElementById("details-button").setAttribute("aria-expanded", "false");
  document.body.classList.remove("drawer-open");
  syncDrawerBackground();
  state.detailsTrigger?.focus?.();
}

/* ---------------------------------------------------------------- assistant */

const ASSISTANT_WORKSPACES = new Set(["runs", "stand", "results", "evidence", "calibration"]);
const ASSISTANT_PANELS = new Set([
  "summary", "tables", "trees", "compare", "visuals", "provenance", "keywords",
]);

function assistantEscape(value) {
  const escapes = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
  return String(value ?? "").replace(/[&<>"']/g, (character) => escapes[character]);
}

function renderAssistantMarkdown(text) {
  return String(text ?? "")
    .split(/```/)
    .map((segment, index) => {
      if (index % 2 === 1) {
        const body = segment.replace(/^[^\n]*\n/, "");
        return `<pre><code>${assistantEscape(body.trim())}</code></pre>`;
      }
      return assistantEscape(segment)
        .replace(/\`([^`\n]+)\`/g, "<code>$1</code>")
        .replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>")
        .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g,
          '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
        .replace(/\n/g, "<br>");
    })
    .join("");
}

function assistantStatus(text) {
  const node = document.getElementById("assistant-status");
  if (node) node.textContent = text;
}

function appendAssistant(role, text, options = {}) {
  const log = document.getElementById("assistant-log");
  if (!log) return null;
  document.getElementById("assistant-hint")?.remove();
  const message = el("div", { className: `assistant-message ${role}` });
  if (options.html) message.innerHTML = renderAssistantMarkdown(text);
  else message.textContent = text;
  if (options.actions?.length) {
    const row = el("div", { className: "assistant-actions" });
    for (const action of options.actions) {
      const chip = el("span", { className: "assistant-action" },
        `${action.tool}${action.summary ? `: ${action.summary}` : ""}`,
      );
      chip.title = chip.textContent;
      row.append(chip);
    }
    message.append(row);
  }
  if (options.chips?.length) {
    const row = el("div", { className: "assistant-actions" });
    for (const chip of options.chips) {
      const button = el("button", { type: "button", className: "assistant-chip" }, chip.label);
      button.addEventListener("click", () => applyAssistantAction(chip));
      row.append(button);
    }
    message.append(row);
  }
  if (options.model) {
    message.append(el("div", { className: "assistant-meta" }, options.model));
  }
  if (options.citations?.length) {
    const row = el("div", { className: "citations" });
    for (const citation of options.citations) {
      row.append(
        el("button", { type: "button", onclick: () => openCitation(citation) },
          citation.label || citation.target,
        ),
      );
    }
    message.append(row);
  }
  log.append(message);
  log.scrollTop = log.scrollHeight;
  if (options.persist !== false) {
    state.assistant.history.push({
      role,
      text: String(text ?? ""),
      citations: options.citations ?? [],
      actions: options.actions ?? [],
      chips: options.chips ?? [],
      model: options.model ?? null,
    });
    state.assistant.history = state.assistant.history.slice(-40);
    saveAssistantHistory();
  }
  return message;
}

function saveAssistantHistory() {
  try {
    window.sessionStorage.setItem("fresh-fvsbc.assistant", JSON.stringify({
      session: state.assistant.session,
      history: state.assistant.history,
    }));
  } catch (_error) {
    /* storage can be unavailable in private or embedded contexts */
  }
}

const SAVED_CHATS_KEY = "fresh-fvsbc.assistant-chats";
const SAVED_CHAT_LIMIT = 10;

function normaliseAssistantMessage(message) {
  if (!message || typeof message !== "object") return null;
  const role = ["user", "assistant", "error"].includes(message.role) ? message.role : "assistant";
  const text = typeof message.text === "string" ? message.text.slice(0, 8000) : "";
  if (!text) return null;
  const objects = (value) =>
    Array.isArray(value)
      ? value.filter((item) => item && typeof item === "object").slice(0, 20)
      : [];
  return {
    role,
    text,
    citations: objects(message.citations),
    actions: objects(message.actions),
    chips: objects(message.chips),
    model: typeof message.model === "string" ? message.model.slice(0, 200) : null,
  };
}

function normaliseSavedContext(context) {
  if (!context || typeof context !== "object") return null;
  const text = (value, length) =>
    typeof value === "string" ? value.slice(0, length) : null;
  const normalised = {
    run: text(context.run, 200),
    workspace: text(context.workspace, 50),
    panel: text(context.panel, 50),
    model: text(context.model, 200),
    mode: text(context.mode, 20),
  };
  return Object.values(normalised).some(Boolean) ? normalised : null;
}

function readSavedChats() {
  let stored = null;
  try {
    stored = JSON.parse(window.localStorage.getItem(SAVED_CHATS_KEY) || "null");
  } catch (_error) {
    stored = null;
  }
  const raw = Array.isArray(stored) ? stored : stored?.chats;
  if (!Array.isArray(raw)) return [];
  const chats = [];
  for (const candidate of raw) {
    if (!candidate || typeof candidate !== "object") continue;
    const name = typeof candidate.name === "string" ? candidate.name.trim().slice(0, 80) : "";
    const history = Array.isArray(candidate.history)
      ? candidate.history.map(normaliseAssistantMessage).filter(Boolean).slice(-40)
      : [];
    if (!name || !history.length) continue;
    chats.push({
      id: typeof candidate.id === "string" ? candidate.id : `chat-${chats.length}`,
      name,
      saved_at: typeof candidate.saved_at === "string" ? candidate.saved_at : "",
      session: typeof candidate.session === "string" ? candidate.session : null,
      context: normaliseSavedContext(candidate.context),
      history,
    });
    if (chats.length === SAVED_CHAT_LIMIT) break;
  }
  return chats;
}

function writeSavedChats(chats) {
  try {
    window.localStorage.setItem(SAVED_CHATS_KEY, JSON.stringify({
      version: 1,
      chats: chats.slice(0, SAVED_CHAT_LIMIT),
    }));
    return true;
  } catch (_error) {
    return false;
  }
}

function assistantSavedStatus(text, kind = "") {
  const node = document.getElementById("assistant-saved-status");
  if (!node) return;
  node.textContent = text;
  node.className = `assistant-saved-status ${kind}`.trim();
}

function updateAssistantSavedContext(chat) {
  const node = document.getElementById("assistant-saved-context");
  if (!node) return;
  if (!chat) {
    node.textContent = "Choose a saved chat to see its run, view, and message count.";
    return;
  }
  const context = chat.context ?? {};
  const parts = [];
  if (chat.saved_at) {
    const saved = new Date(chat.saved_at);
    if (!Number.isNaN(saved.getTime())) parts.push(`Saved ${saved.toLocaleString()}`);
  }
  if (context.run) parts.push(`Run ${context.run}`);
  const savedView = context.workspace
    ? `${context.workspace}${context.panel ? ` / ${context.panel}` : ""}`
    : "";
  if (savedView) parts.push(savedView);
  parts.push(`${chat.history.length} message${chat.history.length === 1 ? "" : "s"}`);
  if (context.model) {
    parts.push(context.model.split("/").pop());
  } else if (context.mode) {
    parts.push(context.mode === "agent" ? "agent" : "local summary");
  }
  const currentView = state.workspace
    ? `${state.workspace}${state.panel ? ` / ${state.panel}` : ""}`
    : "";
  if (context.run && state.run?.id && context.run !== state.run.id) {
    parts.push(`current run ${state.run.id}`);
  } else if (savedView && currentView && savedView !== currentView) {
    parts.push(`current view ${currentView}`);
  }
  node.textContent = parts.join(" · ");
}

function refreshAssistantSaved(selectedId = state.assistant.savedChat) {
  const select = document.getElementById("assistant-saved-select");
  if (!select) return;
  const chats = readSavedChats();
  const selected = chats.some((chat) => chat.id === selectedId) ? selectedId : "";
  select.replaceChildren(
    el("option", { value: "" }, chats.length ? "Choose a saved chat…" : "No saved chats"),
    ...chats.map((chat) => {
      const option = el("option", { value: chat.id }, chat.name);
      if (chat.saved_at) option.title = new Date(chat.saved_at).toLocaleString();
      return option;
    }),
  );
  select.value = selected;
  state.assistant.savedChat = selected;
  updateAssistantSavedContext(chats.find((chat) => chat.id === selected) ?? null);
  const load = document.getElementById("assistant-saved-load");
  const remove = document.getElementById("assistant-saved-delete");
  const rename = document.getElementById("assistant-rename");
  const exportButton = document.getElementById("assistant-saved-export");
  if (load) load.disabled = !selected;
  if (remove) remove.disabled = !selected;
  if (rename) rename.disabled = !selected;
  if (exportButton) exportButton.disabled = !chats.length;
  const count = document.getElementById("assistant-saved-count");
  if (count) count.textContent = chats.length ? `(${chats.length})` : "";
}

function pinAssistantChat() {
  if (!state.assistant.history.length) {
    assistantSavedStatus("Ask something before pinning this chat.", "error");
    return;
  }
  const input = document.getElementById("assistant-pin-name");
  const firstQuestion = state.assistant.history.find((message) => message.role === "user")?.text;
  const fallback = firstQuestion
    ? firstQuestion.trim().slice(0, 48)
    : `Chat ${new Date().toLocaleString()}`;
  const name = String(input?.value || fallback).trim().slice(0, 80);
  if (!name) {
    assistantSavedStatus("Give the chat a name first.", "error");
    return;
  }
  const chats = readSavedChats();
  const existing = chats.find((chat) => chat.name === name);
  const entry = {
    id: existing?.id ?? (
      window.crypto?.randomUUID?.()
      ?? `chat-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
    ),
    name,
    saved_at: new Date().toISOString(),
    session: state.assistant.session,
    context: {
      run: state.run?.id ?? null,
      workspace: state.workspace ?? null,
      panel: state.panel ?? null,
      model: state.assistant.model ?? null,
      mode: state.assistant.mode,
    },
    history: JSON.parse(JSON.stringify(state.assistant.history)),
  };
  const next = [
    entry,
    ...chats.filter((chat) => chat.id !== entry.id && chat.name !== name),
  ].slice(0, SAVED_CHAT_LIMIT);
  if (!writeSavedChats(next)) {
    assistantSavedStatus("Browser storage is full or unavailable; could not pin this chat.", "error");
    return;
  }
  if (input) input.value = "";
  refreshAssistantSaved(entry.id);
  assistantSavedStatus(`Pinned “${entry.name}”.`);
}

function savedChatsExportText() {
  return `${JSON.stringify({
    version: 1,
    exported_at: new Date().toISOString(),
    chats: readSavedChats(),
  }, null, 2)}\n`;
}

function renameAssistantChat() {
  const select = document.getElementById("assistant-saved-select");
  const id = select?.value || state.assistant.savedChat;
  const chats = readSavedChats();
  const chat = chats.find((entry) => entry.id === id);
  if (!chat) {
    assistantSavedStatus("Choose a saved chat to rename.", "error");
    return;
  }
  const input = document.getElementById("assistant-pin-name");
  const name = String(input?.value || "").trim().slice(0, 80);
  if (!name) {
    assistantSavedStatus("Enter the new name first.", "error");
    return;
  }
  if (name === chat.name) {
    assistantSavedStatus("That is already the chat name.", "error");
    return;
  }
  if (chats.some((entry) => entry.id !== chat.id && entry.name === name)) {
    assistantSavedStatus("Another saved chat already uses that name.", "error");
    return;
  }
  const next = chats.map((entry) => (entry.id === chat.id ? { ...entry, name } : entry));
  if (!writeSavedChats(next)) {
    assistantSavedStatus("Browser storage is unavailable; could not rename this chat.", "error");
    return;
  }
  if (input) input.value = "";
  refreshAssistantSaved(chat.id);
  assistantSavedStatus(`Renamed to “${name}”.`);
}

function exportSavedChats() {
  const chats = readSavedChats();
  if (!chats.length) {
    assistantSavedStatus("Pin a chat before exporting.", "error");
    return;
  }
  const blob = new Blob([savedChatsExportText()], {
    type: "application/json;charset=utf-8",
  });
  const href = URL.createObjectURL(blob);
  const link = el("a", {
    href,
    download: "fresh-fvsbc-assistant-chats.json",
  });
  document.body.append(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(href), 1000);
  assistantSavedStatus(`Exported ${chats.length} saved chat${chats.length === 1 ? "" : "s"}.`);
}

function renderAssistantHistory() {
  const log = document.getElementById("assistant-log");
  if (!log) return;
  log.replaceChildren();
  for (const message of state.assistant.history) {
    appendAssistant(message.role, message.text, {
      html: message.role === "assistant",
      citations: message.citations ?? [],
      actions: message.actions ?? [],
      chips: message.chips ?? [],
      model: message.model ?? null,
      persist: false,
    });
  }
}

function loadAssistantChat() {
  const select = document.getElementById("assistant-saved-select");
  const id = select?.value || state.assistant.savedChat;
  const chat = readSavedChats().find((entry) => entry.id === id);
  if (!chat) {
    assistantSavedStatus("Choose a saved chat first.", "error");
    return;
  }
  state.assistant.session = chat.session;
  state.assistant.history = JSON.parse(JSON.stringify(chat.history));
  state.assistant.savedChat = chat.id;
  renderAssistantHistory();
  saveAssistantHistory();
  refreshAssistantSaved(chat.id);
  assistantSavedStatus(`Loaded “${chat.name}”.`);
  assistantStatus("Conversation loaded · Enter sends · Shift+Enter adds a newline.");
}

function deleteAssistantChat() {
  const select = document.getElementById("assistant-saved-select");
  const id = select?.value || state.assistant.savedChat;
  const chats = readSavedChats();
  const chat = chats.find((entry) => entry.id === id);
  if (!chat) {
    assistantSavedStatus("Choose a saved chat to delete.", "error");
    return;
  }
  const next = chats.filter((entry) => entry.id !== chat.id);
  if (!writeSavedChats(next)) {
    assistantSavedStatus("Browser storage is unavailable; could not delete this chat.", "error");
    return;
  }
  state.assistant.savedChat = next[0]?.id ?? "";
  refreshAssistantSaved();
  assistantSavedStatus(`Deleted “${chat.name}”.`);
}

function restoreAssistantHistory() {
  let stored = null;
  try {
    stored = JSON.parse(window.sessionStorage.getItem("fresh-fvsbc.assistant") || "null");
  } catch (_error) {
    stored = null;
  }
  if (!stored || !Array.isArray(stored.history) || !stored.history.length) return;
  state.assistant.session = typeof stored.session === "string" ? stored.session : null;
  state.assistant.history = stored.history.slice(-40);
  renderAssistantHistory();
  assistantStatus("Conversation restored · Enter sends · Shift+Enter adds a newline.");
}

function assistantTranscript() {
  if (!state.assistant.history.length) return "";
  const run = state.run?.id ?? "no run";
  const model = state.assistant.model || (state.assistant.mode === "agent" ? "agent" : "local summary");
  const lines = [
    "# fresh-fvsbc assistant transcript",
    "",
    `- Run: ${run}`,
    `- Workspace: ${state.workspace || "—"} / ${state.panel || "—"}`,
    `- Mode: ${state.assistant.mode}`,
    `- Model: ${model}`,
    `- Session: ${state.assistant.session || "—"}`,
    `- Exported: ${new Date().toISOString()}`,
    "",
  ];
  for (const message of state.assistant.history) {
    lines.push(`## ${message.role === "user" ? "User" : message.role === "error" ? "Error" : "Assistant"}`, "");
    lines.push(message.text || "", "");
    if (message.model) lines.push(`- Model: ${message.model}`, "");
    for (const citation of message.citations || []) {
      lines.push(`- Citation: ${citation.label || citation.target} (${citation.target})`);
    }
    for (const action of message.actions || []) {
      lines.push(`- Tool: ${action.tool}${action.summary ? `: ${action.summary}` : ""}`);
    }
    for (const chip of message.chips || []) {
      lines.push(`- Follow-up: ${chip.label} [${chip.action}: ${chip.target}]`);
    }
    if ((message.citations || []).length || (message.actions || []).length || (message.chips || []).length) {
      lines.push("");
    }
  }
  return lines.join("\n").trimEnd() + "\n";
}

async function copyAssistantTranscript() {
  const text = assistantTranscript();
  if (!text) {
    assistantStatus("Nothing to copy yet.");
    return;
  }
  try {
    await navigator.clipboard.writeText(text);
    assistantStatus("Transcript copied.");
  } catch (_error) {
    assistantStatus("Clipboard unavailable; use Export instead.");
  }
}

function exportAssistantTranscript() {
  const text = assistantTranscript();
  if (!text) {
    assistantStatus("Nothing to export yet.");
    return;
  }
  const blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
  const href = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = href;
  link.download = `fresh-fvsbc-assistant-${state.run?.id || "transcript"}.md`;
  document.body.append(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(href), 1000);
  assistantStatus("Transcript downloaded.");
}

function assistantContext() {
  return {
    workspace: state.workspace,
    panel: state.panel,
    run_id: state.run?.id ?? null,
    year: state.standYear,
    table: state.table,
    compare: state.workspace === "results" && state.panel === "compare"
      ? { a: state.compareA, b: state.compareB, table: state.compareTable }
      : null,
    skin: state.skin?.id ?? null,
  };
}

function openPanelWorkspace(panel) {
  if (panel === "provenance" || panel === "keywords") return "evidence";
  if (panel === "visuals") return "stand";
  return "results";
}

function applyAssistantAction(chip) {
  if (!chip || typeof chip !== "object") return;
  if (chip.action === "open_workspace" && ASSISTANT_WORKSPACES.has(chip.target)) {
    selectWorkspace(chip.target);
    closeAssistant();
    return;
  }
  if (chip.action === "open_panel" && ASSISTANT_PANELS.has(chip.target)) {
    const workspace = openPanelWorkspace(chip.target);
    selectWorkspace(workspace);
    if (workspace !== "stand") selectPanel(chip.target);
    closeAssistant();
    return;
  }
  if (chip.action === "open_run" && typeof chip.target === "string") {
    selectRun(chip.target);
    selectWorkspace("stand");
    closeAssistant();
    return;
  }
  if (chip.action === "open_table" && typeof chip.target === "string") {
    state.table = chip.target;
    state.tableQuery = String(chip.query || "");
    state.tableColumn = String(chip.column || "");
    state.tableOffset = 0;
    selectWorkspace("results");
    selectPanel("tables");
    closeAssistant();
    return;
  }
  if (chip.action === "select_year" && Number.isInteger(Number(chip.target))) {
    state.standYear = Number(chip.target);
    selectWorkspace("stand");
    closeAssistant();
    return;
  }
  if (chip.action === "ask" && typeof chip.target === "string") {
    const input = document.getElementById("assistant-input");
    if (input) {
      input.value = chip.target;
      resizeAssistantInput();
      input.focus();
    }
    return;
  }
}

function openCitation(citation) {
  if (!citation) return;
  if (citation.kind === "workspace") {
    selectWorkspace(citation.target);
    closeAssistant();
    return;
  }
  if (citation.target === "provenance" || citation.target === "keywords") {
    selectWorkspace("evidence");
    selectPanel(citation.target);
  } else if (citation.target === "summary" || citation.target === "tables" || citation.target === "trees") {
    selectWorkspace("results");
    selectPanel(citation.target);
  }
  closeAssistant();
}

function resizeAssistantInput() {
  const input = document.getElementById("assistant-input");
  if (!input) return;
  input.style.height = "auto";
  input.style.height = `${Math.min(160, Math.max(42, input.scrollHeight))}px`;
}

function setAssistantBusy(busy) {
  state.assistant.busy = busy;
  const send = document.getElementById("assistant-send");
  const form = document.getElementById("assistant-form");
  if (send) send.disabled = busy;
  const stop = document.getElementById("assistant-stop");
  if (stop) stop.hidden = !busy;
  if (form) form.setAttribute("aria-busy", String(busy));
  document.querySelectorAll("#assistant-quick button").forEach((button) => {
    button.disabled = busy;
  });
}

function configureAssistant(info) {
  state.assistant.enabled = Boolean(info?.enabled);
  state.assistant.available = Boolean(info?.available);
  state.assistant.mode = state.assistant.enabled && state.assistant.available ? "agent" : "local";
  const model = document.getElementById("assistant-model");
  const select = document.getElementById("assistant-model-select");
  const guide = document.getElementById("assistant-guide");
  if (guide) guide.hidden = state.assistant.mode !== "agent";
  if (state.assistant.mode === "agent") {
    const models = Array.isArray(info.models) && info.models.length ? info.models : [info.model];
    const current = models.includes(state.assistant.model) ? state.assistant.model : info.model;
    state.assistant.model = current;
    if (select) {
      select.replaceChildren(...models.map((modelId) =>
        el("option", { value: modelId, selected: modelId === current }, modelId.split("/").pop()),
      ));
      select.value = current;
      select.hidden = false;
    }
    if (model) model.hidden = true;
    assistantStatus("Enter sends · Shift+Enter adds a newline.");
  } else {
    state.assistant.model = null;
    if (select) {
      select.hidden = true;
      select.replaceChildren();
    }
    if (model) {
      model.hidden = false;
      model.textContent = info?.enabled && !info?.available
        ? "local summary · opencode unavailable"
        : "local summary reader";
    }
    assistantStatus(info?.enabled && !info?.available
      ? "opencode is not on the service PATH; using the local summary reader."
      : "LLM agent off; using the local summary reader.");
  }
}

function newAssistantChat() {
  state.assistant.session = null;
  state.assistant.history = [];
  try {
    window.sessionStorage.removeItem("fresh-fvsbc.assistant");
  } catch (_error) {
    /* storage can be unavailable */
  }
  const log = document.getElementById("assistant-log");
  if (!log) return;
  log.replaceChildren(
    el("p", { className: "muted", id: "assistant-hint" },
      state.assistant.mode === "agent"
        ? "New conversation. Ask about the open run, a table, the stand, or the provenance."
        : "New conversation. This mode answers from the open run's summary and provenance.",
    ),
  );
  assistantStatus(state.assistant.mode === "agent"
    ? "Enter sends · Shift+Enter adds a newline."
    : "Local summary mode.");
  document.getElementById("assistant-input")?.focus();
}

function openAssistant() {
  closeDetails();
  state.assistantTrigger = document.activeElement;
  const drawer = document.getElementById("assistant-drawer");
  drawer.hidden = false;
  document.getElementById("drawer-backdrop").hidden = false;
  document.getElementById("assistant-button").setAttribute("aria-expanded", "true");
  document.body.classList.add("drawer-open");
  syncDrawerBackground();
  refreshAssistantSaved();
  const input = document.getElementById("assistant-input");
  input?.focus();
  resizeAssistantInput();
}

function closeAssistant() {
  const drawer = document.getElementById("assistant-drawer");
  if (!drawer || drawer.hidden) return;
  drawer.hidden = true;
  document.getElementById("drawer-backdrop").hidden = true;
  document.getElementById("assistant-button").setAttribute("aria-expanded", "false");
  document.body.classList.remove("drawer-open");
  syncDrawerBackground();
  state.assistantTrigger?.focus?.();
}

async function sendAssistant(message) {
  const clean = String(message || "").trim();
  if (!clean || state.assistant.busy) return;
  appendAssistant("user", clean);
  const input = document.getElementById("assistant-input");
  input.value = "";
  resizeAssistantInput();
  const thinking = appendAssistant("assistant", "working…", { persist: false });
  thinking?.classList.add("thinking");
  setAssistantBusy(true);
  assistantStatus(state.assistant.mode === "agent"
    ? "The local OpenCode agent is reading the run…"
    : "Reading the run summary…");
  state.assistant.controller = new AbortController();
  try {
    let mode = state.assistant.mode;
    const request = () => fetch(
      mode === "agent" ? "api/agent/chat" : "api/assistant",
      {
        method: "POST",
        headers: { "content-type": "application/json", accept: "application/json" },
        signal: state.assistant.controller.signal,
        body: JSON.stringify(
          mode === "agent"
            ? {
                message: clean,
                session: state.assistant.session,
                model: state.assistant.model,
                context: assistantContext(),
                run: state.run?.id ?? null,
                year: state.standYear,
              }
            : { message: clean, run: state.run?.id ?? null },
        ),
      },
    );
    let response = await request();
    if (mode === "agent" && [502, 503, 504].includes(response.status)) {
      // The first turn can hit a cold reverse-proxy or agent timeout; one delayed retry recovers it.
      await new Promise((resolve) => window.setTimeout(resolve, 2000));
      response = await request();
    }
    if (mode === "agent" && response.status === 403) {
      mode = state.assistant.mode = "local";
      configureAssistant({ enabled: false, available: false, model: null });
      response = await request();
    }
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.detail ?? `assistant failed (${response.status})`);
    state.assistant.session = payload.session || state.assistant.session;
    thinking?.remove();
    appendAssistant("assistant", payload.reply ?? "(no reply)", {
      html: true,
      actions: payload.actions ?? [],
      chips: payload.chips ?? [],
      citations: payload.citations ?? [],
      model: payload.model || state.assistant.model,
    });
    assistantStatus(state.assistant.mode === "agent"
      ? "Enter sends · Shift+Enter adds a newline."
      : "Local summary mode.");
  } catch (error) {
    thinking?.remove();
    if (error?.name === "AbortError") {
      appendAssistant("assistant", "Stopped waiting. The local agent may still finish in the background.");
      assistantStatus("Stopped waiting; the local process may still be running.");
    } else {
      appendAssistant("error", `Assistant unavailable: ${error?.message ?? error}`);
      assistantStatus("The assistant did not answer. Try again or use the open run details.");
    }
  } finally {
    state.assistant.controller = null;
    setAssistantBusy(false);
    input?.focus();
    document.getElementById("assistant-log")?.scrollTo({
      top: document.getElementById("assistant-log").scrollHeight,
    });
  }
}

/* ---------------------------------------------------------------- boot */

async function boot() {
  document.getElementById("new-run-button").addEventListener("click", openNewRun);
  document.getElementById("close-new-run").addEventListener("click", closeNewRun);
  document.getElementById("cancel-new-run").addEventListener("click", closeNewRun);
  document.getElementById("new-run-form").addEventListener("submit", submitNewRun);
  document.getElementById("details-button").addEventListener("click", openDetails);
  document.getElementById("close-details").addEventListener("click", closeDetails);
  document.getElementById("assistant-button").addEventListener("click", openAssistant);
  document.getElementById("close-assistant").addEventListener("click", closeAssistant);
  document.getElementById("assistant-new").addEventListener("click", newAssistantChat);
  document.getElementById("assistant-copy").addEventListener("click", copyAssistantTranscript);
  document.getElementById("assistant-export").addEventListener("click", exportAssistantTranscript);
  document.getElementById("assistant-stop").addEventListener("click", () => {
    state.assistant.controller?.abort();
  });
  document.getElementById("assistant-model-select").addEventListener("change", (event) => {
    state.assistant.model = event.target.value;
    assistantStatus(`Model set to ${event.target.value.split("/").pop()}.`);
  });
  document.getElementById("assistant-pin").addEventListener("click", pinAssistantChat);
  document.getElementById("assistant-saved-load").addEventListener("click", loadAssistantChat);
  document.getElementById("assistant-saved-delete").addEventListener("click", deleteAssistantChat);
  document.getElementById("assistant-rename").addEventListener("click", renameAssistantChat);
  document.getElementById("assistant-saved-export").addEventListener("click", exportSavedChats);
  const savedSelect = document.getElementById("assistant-saved-select");
  savedSelect.addEventListener("change", (event) => {
    state.assistant.savedChat = event.target.value;
    const disabled = !event.target.value;
    document.getElementById("assistant-saved-load").disabled = disabled;
    document.getElementById("assistant-saved-delete").disabled = disabled;
    document.getElementById("assistant-rename").disabled = disabled;
    updateAssistantSavedContext(
      readSavedChats().find((chat) => chat.id === event.target.value) ?? null,
    );
  });
  const pinName = document.getElementById("assistant-pin-name");
  pinName.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" || event.isComposing) return;
    event.preventDefault();
    pinAssistantChat();
  });
  refreshAssistantSaved();
  const assistantInput = document.getElementById("assistant-input");
  assistantInput.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" || event.shiftKey || event.isComposing) return;
    event.preventDefault();
    sendAssistant(assistantInput.value);
  });
  assistantInput.addEventListener("input", resizeAssistantInput);
  document.getElementById("drawer-backdrop").addEventListener("click", () => {
    closeDetails();
    closeAssistant();
  });
  document.getElementById("assistant-form").addEventListener("submit", (event) => {
    event.preventDefault();
    sendAssistant(document.getElementById("assistant-input").value);
  });
  document.querySelectorAll("#assistant-quick button").forEach((button) => {
    button.addEventListener("click", () => sendAssistant(button.dataset.prompt));
  });
  document.addEventListener("keydown", trapDrawerTab);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeDetails();
      closeAssistant();
    }
  });
  try {
    const [skins, runs, oracle, calibrations, agentInfo] = await Promise.all([
      api("api/skins"),
      api("api/runs"),
      api("api/oracle"),
      api("api/calibrations").catch(() => []),
      api("api/agent").catch(() => null),
    ]);
    state.skins = skins;
    state.runs = runs;
    state.oracle = oracle;
    state.calibrations = calibrations;
    configureAssistant(agentInfo);
    state.skin = skins[0];
    const initial = readUrlState();
    const firstComplete = runs.find((run) => run.state === "complete") ?? runs[0] ?? null;
    state.run = runs.find((run) => run.id === initial.run) ?? firstComplete;
    state.workspace = initial.workspace || "runs";
    state.standYear = initial.year && Number.isFinite(Number(initial.year)) ? Number(initial.year) : null;
    const workspaces = available_workspaces();
    if (!workspaces.some((workspace) => workspace.id === state.workspace)) state.workspace = "runs";
    state.panel = initial.panel || workspace_panels()[0] || null;
    if (!workspace_panels().includes(state.panel)) state.panel = workspace_panels()[0] || null;
    state.table = initial.table;
    state.tableQuery = initial.q || "";
    state.tableColumn = initial.column || "";
    const offset = Number(initial.offset);
    state.tableOffset = Number.isInteger(offset) && offset > 0 ? offset : 0;
    const limit = Number(initial.limit);
    state.tableLimit = [5, 10, 25, 50, 100, 200, 500, 1000].includes(limit) ? limit : 200;
    if (initial.a) state.compareA = initial.a;
    if (initial.b) state.compareB = initial.b;
    if (initial.metric) state.compareMetric = initial.metric;
    state.compareTable = initial.ctable;
    state.ready = true;
    restoreAssistantHistory();
    renderShell();
    await renderPanel();
    updateUrl();
    if (runs.some((run) => run.state === "running")) startPolling();
  } catch (error) {
    body_error(`Could not start: ${error}`);
  }
}
boot();
