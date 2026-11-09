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
  compareColumns: [],
  compareColumnsOpen: false,
  compareSort: "recent",
  compareKeyColumns: [],
  compareKeysOpen: false,
  compareSaved: "",
  summaryColumn: null,
  tableQuery: "",
  tableColumn: "",
  tableHidden: [],
  tableOrder: [],
  tableLayoutTable: null,
  tableLayoutWarning: false,
  tableLayoutMessage: "",
  tableExportVisible: false,
  tableColumnsOpen: false,
  tableFiltersOpen: false,
  tableSavedFilter: "",
  tableExportPresetsOpen: false,
  tableExportPreset: "",
  tableFilterSort: "recent",
  tablePresetSort: "recent",
  tableSetupOpen: false,
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
    savedSearch: "",
    savedSort: "recent",
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

function createImportPreview(id, title, onConfirm, onCancel) {
  let pending = null;
  const summary = el("p", { className: "table-filters-status" });
  const list = el("ul", { className: "table-setup-list" });
  const node = el(
    "div",
    { id, className: "table-setup-preview", hidden: true },
    el("strong", {}, title),
    summary,
    list,
    el("div", { className: "table-filters-portability" },
      el("button", {
        id: `${id}-confirm`,
        type: "button",
        onclick: async () => {
          if (pending) await onConfirm(pending);
        },
      }, "Import"),
      el("button", {
        id: `${id}-cancel`,
        type: "button",
        onclick: () => {
          pending = null;
          node.hidden = true;
          if (onCancel) onCancel();
        },
      }, "Cancel"),
    ),
  );
  return {
    node,
    show(data, summaryText, lines) {
      pending = data;
      summary.textContent = summaryText;
      list.replaceChildren(...lines.map((line) => el("li", {}, line)));
      node.hidden = false;
    },
    hide() {
      pending = null;
      node.hidden = true;
    },
  };
}

function attachSelectSearch(input, select) {
  if (!input || !select) return;
  const options = [...select.options].slice(1).map((option) => ({
    value: option.value,
    text: option.textContent || option.value,
    title: option.title,
  }));
  const placeholder = select.options[0]?.textContent || "Choose…";
  input.addEventListener("input", () => {
    const term = input.value.trim().toLowerCase();
    const matches = term
      ? options.filter((option) => option.text.toLowerCase().includes(term))
      : options;
    const previous = select.value;
    select.replaceChildren(
      el("option", { value: "" }, matches.length ? placeholder : "No matches"),
      ...matches.map((option) => {
        const node = el("option", { value: option.value }, option.text);
        if (option.title) node.title = option.title;
        return node;
      }),
    );
    const kept = matches.some((option) => option.value === previous)
      ? previous
      : (matches[0]?.value ?? "");
    select.value = kept;
    select.dispatchEvent(new Event("change", { bubbles: true }));
  });
}

function sortPresetCollection(items, mode) {
  if (mode === "name") {
    return [...items].sort((left, right) => left.name.localeCompare(right.name));
  }
  if (mode === "name-desc") {
    return [...items].sort((left, right) => right.name.localeCompare(left.name));
  }
  return items;
}

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function uniqueCopyName(name, names) {
  const base = `${name} copy`.slice(0, 80);
  if (!names.has(base)) return base;
  for (let index = 2; index < 100; index += 1) {
    const candidate = `${name} copy ${index}`.slice(0, 80);
    if (!names.has(candidate)) return candidate;
  }
  return `${name} copy ${Date.now()}`.slice(0, 80);
}

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

const TABLE_LAYOUTS_KEY = "fresh-fvsbc.table-layouts";

function normaliseColumnOrder(order, columns) {
  const known = new Set(columns);
  const seen = new Set();
  const result = [];
  if (Array.isArray(order)) {
    for (const column of order) {
      if (!known.has(column) || seen.has(column)) continue;
      seen.add(column);
      result.push(column);
    }
  }
  for (const column of columns) {
    if (!seen.has(column)) result.push(column);
  }
  return result;
}

function readTableLayout(table, columns) {
  let raw = null;
  try {
    const stored = JSON.parse(window.localStorage.getItem(TABLE_LAYOUTS_KEY) || "null");
    raw = stored?.tables?.[table] ?? null;
  } catch (_error) {
    return { order: [...columns], hidden: [], exportVisible: false, ok: false };
  }
  if (!raw || typeof raw !== "object") {
    return { order: [...columns], hidden: [], exportVisible: false, ok: true };
  }
  const order = normaliseColumnOrder(raw.order, columns);
  const known = new Set(columns);
  const hidden = Array.isArray(raw.hidden)
    ? raw.hidden.filter((column) => known.has(column))
    : [];
  const unique = [...new Set(hidden)];
  if (unique.length >= order.length && order.length) unique.shift();
  return { order, hidden: unique, exportVisible: raw.exportVisible === true, ok: true };
}

function writeTableLayout(table, order, hidden, exportVisible = false) {
  try {
    let stored = null;
    try {
      stored = JSON.parse(window.localStorage.getItem(TABLE_LAYOUTS_KEY) || "null");
    } catch (_error) {
      stored = null;
    }
    const tables = stored?.tables && typeof stored.tables === "object" ? stored.tables : {};
    tables[table] = {
      order: [...order],
      hidden: [...hidden],
      exportVisible: exportVisible === true,
    };
    window.localStorage.setItem(TABLE_LAYOUTS_KEY, JSON.stringify({ version: 1, tables }));
    return true;
  } catch (_error) {
    return false;
  }
}

function clearTableLayout(table) {
  try {
    let stored = null;
    try {
      stored = JSON.parse(window.localStorage.getItem(TABLE_LAYOUTS_KEY) || "null");
    } catch (_error) {
      stored = null;
    }
    if (!stored?.tables || typeof stored.tables !== "object") return true;
    delete stored.tables[table];
    window.localStorage.setItem(TABLE_LAYOUTS_KEY, JSON.stringify({
      version: 1,
      tables: stored.tables,
    }));
    return true;
  } catch (_error) {
    return false;
  }
}

function persistTableLayout() {
  state.tableLayoutMessage = "";
  state.tableLayoutWarning = !writeTableLayout(
    state.table,
    state.tableOrder,
    state.tableHidden,
    state.tableExportVisible,
  );
}

function readLayoutEnvelope() {
  try {
    const stored = JSON.parse(window.localStorage.getItem(TABLE_LAYOUTS_KEY) || "null");
    const tables = stored?.tables && typeof stored.tables === "object"
      && !Array.isArray(stored.tables)
      ? stored.tables
      : {};
    return { tables, ok: true };
  } catch (_error) {
    return { tables: {}, ok: false };
  }
}

function writeLayoutEnvelope(tables) {
  try {
    window.localStorage.setItem(TABLE_LAYOUTS_KEY, JSON.stringify({
      version: 1,
      tables,
    }));
    return true;
  } catch (_error) {
    return false;
  }
}

function tableLayoutsExportText() {
  return `${JSON.stringify({
    version: 1,
    exported_at: new Date().toISOString(),
    tables: readLayoutEnvelope().tables,
  }, null, 2)}\n`;
}

function previewTableLayouts(text) {
  let parsed = null;
  try {
    parsed = JSON.parse(text);
  } catch (_error) {
    throw new Error("That file is not valid JSON.");
  }
  const raw = parsed?.tables ?? parsed;
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    throw new Error("Expected a tables object in that layout file.");
  }
  const imported = {};
  for (const [table, value] of Object.entries(raw)) {
    if (!table || table.length > 100) continue;
    if (["__proto__", "constructor", "prototype"].includes(table)) continue;
    if (!value || typeof value !== "object" || Array.isArray(value)) continue;
    if (!("order" in value) && !("hidden" in value) && !("exportVisible" in value)) continue;
    const clean = (items) => Array.isArray(items)
      ? [...new Set(items
        .filter((item) => typeof item === "string" && item.trim())
        .map((item) => item.trim().slice(0, 100)))].slice(0, 100)
      : [];
    imported[table] = {
      order: clean(value.order),
      hidden: clean(value.hidden),
      exportVisible: value.exportVisible === true,
    };
  }
  const count = Object.keys(imported).length;
  if (!count) throw new Error("No table layouts found in that file.");
  return {
    count,
    tables: imported,
    merged: { ...readLayoutEnvelope().tables, ...imported },
  };
}

function commitTableLayouts(preview) {
  if (!writeLayoutEnvelope(preview.merged)) {
    throw new Error("Browser storage is unavailable; could not import layouts.");
  }
  return preview.count;
}

function importTableLayouts(text) {
  return commitTableLayouts(previewTableLayouts(text));
}

const TABLE_FILTERS_KEY = "fresh-fvsbc.table-filters";

function readTableFilters(table) {
  let raw = null;
  try {
    const stored = JSON.parse(window.localStorage.getItem(TABLE_FILTERS_KEY) || "null");
    raw = stored?.tables?.[table] ?? null;
  } catch (_error) {
    return { filters: [], ok: false };
  }
  if (!Array.isArray(raw)) return { filters: [], ok: true };
  const filters = [];
  const seen = new Set();
  for (const candidate of raw) {
    if (!candidate || typeof candidate !== "object") continue;
    const name = typeof candidate.name === "string" ? candidate.name.trim().slice(0, 80) : "";
    if (!name || seen.has(name)) continue;
    seen.add(name);
    filters.push({
      id: typeof candidate.id === "string" ? candidate.id : `filter-${filters.length}`,
      name,
      query: typeof candidate.query === "string" ? candidate.query.slice(0, 200) : "",
      column: typeof candidate.column === "string" ? candidate.column.slice(0, 100) : "",
      created_at: typeof candidate.created_at === "string" ? candidate.created_at : "",
    });
    if (filters.length === 20) break;
  }
  return { filters, ok: true };
}

function writeTableFilters(table, filters) {
  try {
    let stored = null;
    try {
      stored = JSON.parse(window.localStorage.getItem(TABLE_FILTERS_KEY) || "null");
    } catch (_error) {
      stored = null;
    }
    const tables = stored?.tables && typeof stored.tables === "object" ? stored.tables : {};
    tables[table] = filters.slice(0, 20);
    window.localStorage.setItem(TABLE_FILTERS_KEY, JSON.stringify({ version: 1, tables }));
    return true;
  } catch (_error) {
    return false;
  }
}

function setTableFilterStatus(text, kind = "") {
  const node = document.getElementById("table-filter-status");
  if (!node) return;
  node.textContent = text;
  node.className = `table-filters-status ${kind}`.trim();
}

const TABLE_RECENTS_KEY = "fresh-fvsbc.table-filter-recents";
const TABLE_RECENTS_LIMIT = 8;

function readTableRecents(table) {
  let raw = null;
  try {
    const stored = JSON.parse(window.localStorage.getItem(TABLE_RECENTS_KEY) || "null");
    raw = stored?.tables?.[table] ?? null;
  } catch (_error) {
    return { recents: [], ok: false };
  }
  if (!Array.isArray(raw)) return { recents: [], ok: true };
  const recents = [];
  for (const candidate of raw) {
    if (!candidate || typeof candidate !== "object") continue;
    const query = typeof candidate.query === "string" ? candidate.query.slice(0, 200) : "";
    const column = typeof candidate.column === "string" ? candidate.column.slice(0, 100) : "";
    if (!query && !column) continue;
    if (recents.some((entry) => entry.query === query && entry.column === column)) continue;
    recents.push({
      query,
      column,
      used_at: typeof candidate.used_at === "string" ? candidate.used_at : "",
    });
    if (recents.length === TABLE_RECENTS_LIMIT) break;
  }
  return { recents, ok: true };
}

function writeTableRecents(table, recents) {
  try {
    let stored = null;
    try {
      stored = JSON.parse(window.localStorage.getItem(TABLE_RECENTS_KEY) || "null");
    } catch (_error) {
      stored = null;
    }
    const tables = stored?.tables && typeof stored.tables === "object" ? stored.tables : {};
    tables[table] = recents.slice(0, TABLE_RECENTS_LIMIT);
    window.localStorage.setItem(TABLE_RECENTS_KEY, JSON.stringify({ version: 1, tables }));
    return true;
  } catch (_error) {
    return false;
  }
}

function recordTableRecent(table, query, column) {
  const q = String(query || "").trim();
  const c = String(column || "").trim();
  if (!q && !c) return false;
  const { recents } = readTableRecents(table);
  const next = [
    { query: q, column: c, used_at: new Date().toISOString() },
    ...recents.filter((entry) => entry.query !== q || entry.column !== c),
  ].slice(0, TABLE_RECENTS_LIMIT);
  return writeTableRecents(table, next);
}

function recentFilterLabel(entry) {
  if (entry.query && entry.column) return `${entry.column} = ${entry.query}`;
  if (entry.query) return `Search: ${entry.query}`;
  return `Column: ${entry.column}`;
}

function normaliseFilterEntries(raw) {
  if (!Array.isArray(raw)) return [];
  const filters = [];
  const seen = new Set();
  for (const candidate of raw) {
    if (!candidate || typeof candidate !== "object") continue;
    const name = typeof candidate.name === "string" ? candidate.name.trim().slice(0, 80) : "";
    if (!name || seen.has(name)) continue;
    seen.add(name);
    filters.push({
      id: typeof candidate.id === "string" && candidate.id
        ? candidate.id.slice(0, 200)
        : `filter-${filters.length}-${Date.now()}`,
      name,
      query: typeof candidate.query === "string" ? candidate.query.slice(0, 200) : "",
      column: typeof candidate.column === "string" ? candidate.column.slice(0, 100) : "",
      created_at: typeof candidate.created_at === "string" ? candidate.created_at : "",
    });
    if (filters.length === 20) break;
  }
  return filters;
}

function normaliseRecentEntries(raw) {
  if (!Array.isArray(raw)) return [];
  const recents = [];
  for (const candidate of raw) {
    if (!candidate || typeof candidate !== "object") continue;
    const query = typeof candidate.query === "string" ? candidate.query.slice(0, 200) : "";
    const column = typeof candidate.column === "string" ? candidate.column.slice(0, 100) : "";
    if (!query && !column) continue;
    if (recents.some((entry) => entry.query === query && entry.column === column)) continue;
    recents.push({
      query,
      column,
      used_at: typeof candidate.used_at === "string" ? candidate.used_at : "",
    });
    if (recents.length === TABLE_RECENTS_LIMIT) break;
  }
  return recents;
}

function readFilterEnvelope() {
  try {
    const stored = JSON.parse(window.localStorage.getItem(TABLE_FILTERS_KEY) || "null");
    const tables = stored?.tables && typeof stored.tables === "object"
      && !Array.isArray(stored.tables)
      ? stored.tables
      : {};
    return { tables, ok: true };
  } catch (_error) {
    return { tables: {}, ok: false };
  }
}

function writeFilterEnvelope(tables) {
  try {
    window.localStorage.setItem(TABLE_FILTERS_KEY, JSON.stringify({ version: 1, tables }));
    return true;
  } catch (_error) {
    return false;
  }
}

function readRecentEnvelope() {
  try {
    const stored = JSON.parse(window.localStorage.getItem(TABLE_RECENTS_KEY) || "null");
    const tables = stored?.tables && typeof stored.tables === "object"
      && !Array.isArray(stored.tables)
      ? stored.tables
      : {};
    return { tables, ok: true };
  } catch (_error) {
    return { tables: {}, ok: false };
  }
}

function writeRecentEnvelope(tables) {
  try {
    window.localStorage.setItem(TABLE_RECENTS_KEY, JSON.stringify({ version: 1, tables }));
    return true;
  } catch (_error) {
    return false;
  }
}

function tableFiltersExportText() {
  const filterTables = readFilterEnvelope().tables;
  const recentTables = readRecentEnvelope().tables;
  const names = new Set([...Object.keys(filterTables), ...Object.keys(recentTables)]);
  const tables = {};
  for (const table of names) {
    const filters = normaliseFilterEntries(filterTables[table]);
    const recents = normaliseRecentEntries(recentTables[table]);
    if (filters.length || recents.length) tables[table] = { filters, recents };
  }
  return `${JSON.stringify({
    version: 1,
    exported_at: new Date().toISOString(),
    tables,
  }, null, 2)}\n`;
}

function previewTableFilters(text) {
  let parsed = null;
  try {
    parsed = JSON.parse(text);
  } catch (_error) {
    throw new Error("That file is not valid JSON.");
  }
  const raw = parsed?.tables;
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    throw new Error("Expected a tables object in that filter file.");
  }
  const filterTables = { ...readFilterEnvelope().tables };
  const recentTables = { ...readRecentEnvelope().tables };
  const details = [];
  let filters = 0;
  let recents = 0;
  for (const [table, value] of Object.entries(raw)) {
    if (!table || table.length > 100) continue;
    if (["__proto__", "constructor", "prototype"].includes(table)) continue;
    if (!value || typeof value !== "object" || Array.isArray(value)) continue;
    const incomingFilters = normaliseFilterEntries(value.filters);
    const incomingRecents = normaliseRecentEntries(value.recents);
    if (!incomingFilters.length && !incomingRecents.length) continue;
    if (incomingFilters.length) {
      const existing = normaliseFilterEntries(filterTables[table]);
      const names = new Set(incomingFilters.map((entry) => entry.name));
      filterTables[table] = [
        ...incomingFilters,
        ...existing.filter((entry) => !names.has(entry.name)),
      ].slice(0, 20);
      filters += incomingFilters.length;
    }
    if (incomingRecents.length) {
      const existing = normaliseRecentEntries(recentTables[table]);
      const keys = new Set(incomingRecents.map((entry) => `${entry.column}\u0000${entry.query}`));
      recentTables[table] = [
        ...incomingRecents,
        ...existing.filter((entry) => !keys.has(`${entry.column}\u0000${entry.query}`)),
      ].slice(0, TABLE_RECENTS_LIMIT);
      recents += incomingRecents.length;
    }
    details.push({
      name: table,
      filters: incomingFilters.length,
      recents: incomingRecents.length,
    });
  }
  if (!details.length) throw new Error("No table filters found in that file.");
  return {
    tables: details.length,
    filters,
    recents,
    details,
    filterTables,
    recentTables,
  };
}

function commitTableFilters(preview) {
  if (!writeFilterEnvelope(preview.filterTables)) {
    throw new Error("Browser storage is unavailable; could not import filters.");
  }
  if (!writeRecentEnvelope(preview.recentTables)) {
    throw new Error("Browser storage is unavailable; could not import recent filters.");
  }
  return {
    tables: preview.tables,
    filters: preview.filters,
    recents: preview.recents,
  };
}

function importTableFilters(text) {
  return commitTableFilters(previewTableFilters(text));
}

function setTableLayoutStatus(text, kind = "") {
  const node = document.getElementById("table-layout-status");
  if (!node) return;
  node.textContent = text;
  node.className = `table-columns-status ${kind}`.trim();
}

const TABLE_EXPORT_PRESETS_KEY = "fresh-fvsbc.table-export-presets";

function normaliseExportPresetEntries(raw) {
  if (!Array.isArray(raw)) return [];
  const presets = [];
  const seen = new Set();
  for (const candidate of raw) {
    if (!candidate || typeof candidate !== "object") continue;
    const name = typeof candidate.name === "string" ? candidate.name.trim().slice(0, 80) : "";
    if (!name || seen.has(name)) continue;
    seen.add(name);
    presets.push({
      id: typeof candidate.id === "string" && candidate.id
        ? candidate.id.slice(0, 200)
        : `preset-${presets.length}-${Date.now()}`,
      name,
      query: typeof candidate.query === "string" ? candidate.query.slice(0, 200) : "",
      column: typeof candidate.column === "string" ? candidate.column.slice(0, 100) : "",
      order: Array.isArray(candidate.order)
        ? candidate.order.filter((item) => typeof item === "string").slice(0, 100)
        : [],
      hidden: Array.isArray(candidate.hidden)
        ? candidate.hidden.filter((item) => typeof item === "string").slice(0, 100)
        : [],
      created_at: typeof candidate.created_at === "string" ? candidate.created_at : "",
    });
    if (presets.length === 20) break;
  }
  return presets;
}

function readTableExportPresets(table) {
  let raw = null;
  try {
    const stored = JSON.parse(window.localStorage.getItem(TABLE_EXPORT_PRESETS_KEY) || "null");
    raw = stored?.tables?.[table] ?? null;
  } catch (_error) {
    return { presets: [], ok: false };
  }
  return { presets: normaliseExportPresetEntries(raw), ok: true };
}

function readExportPresetEnvelope() {
  try {
    const stored = JSON.parse(window.localStorage.getItem(TABLE_EXPORT_PRESETS_KEY) || "null");
    const tables = stored?.tables && typeof stored.tables === "object"
      && !Array.isArray(stored.tables)
      ? stored.tables
      : {};
    return { tables, ok: true };
  } catch (_error) {
    return { tables: {}, ok: false };
  }
}

function writeExportPresetEnvelope(tables) {
  try {
    window.localStorage.setItem(TABLE_EXPORT_PRESETS_KEY, JSON.stringify({
      version: 1,
      tables,
    }));
    return true;
  } catch (_error) {
    return false;
  }
}

function tableExportPresetsExportText() {
  const envelope = readExportPresetEnvelope();
  const tables = {};
  for (const table of Object.keys(envelope.tables)) {
    const presets = normaliseExportPresetEntries(envelope.tables[table]);
    if (presets.length) tables[table] = presets;
  }
  return `${JSON.stringify({
    version: 1,
    exported_at: new Date().toISOString(),
    tables,
  }, null, 2)}\n`;
}

function previewTableExportPresets(text) {
  let parsed = null;
  try {
    parsed = JSON.parse(text);
  } catch (_error) {
    throw new Error("That file is not valid JSON.");
  }
  const raw = parsed?.tables;
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    throw new Error("Expected a tables object in that preset file.");
  }
  const merged = { ...readExportPresetEnvelope().tables };
  const details = [];
  let presets = 0;
  for (const [table, value] of Object.entries(raw)) {
    if (!table || table.length > 100) continue;
    if (["__proto__", "constructor", "prototype"].includes(table)) continue;
    const incoming = normaliseExportPresetEntries(value);
    if (!incoming.length) continue;
    const existing = normaliseExportPresetEntries(merged[table]);
    const names = new Set(incoming.map((preset) => preset.name));
    merged[table] = [
      ...incoming,
      ...existing.filter((preset) => !names.has(preset.name)),
    ].slice(0, 20);
    details.push({ name: table, presets: incoming.length });
    presets += incoming.length;
  }
  if (!details.length) throw new Error("No export presets found in that file.");
  return { tables: details.length, presets, details, merged };
}

function commitTableExportPresets(preview) {
  if (!writeExportPresetEnvelope(preview.merged)) {
    throw new Error("Browser storage is unavailable; could not import presets.");
  }
  return { tables: preview.tables, presets: preview.presets };
}

function importTableExportPresets(text) {
  return commitTableExportPresets(previewTableExportPresets(text));
}

function writeTableExportPresets(table, presets) {
  try {
    let stored = null;
    try {
      stored = JSON.parse(window.localStorage.getItem(TABLE_EXPORT_PRESETS_KEY) || "null");
    } catch (_error) {
      stored = null;
    }
    const tables = stored?.tables && typeof stored.tables === "object" ? stored.tables : {};
    tables[table] = presets.slice(0, 20);
    window.localStorage.setItem(
      TABLE_EXPORT_PRESETS_KEY,
      JSON.stringify({ version: 1, tables }),
    );
    return true;
  } catch (_error) {
    return false;
  }
}

function normaliseLayoutEntry(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  if (!("order" in value) && !("hidden" in value) && !("exportVisible" in value)) return null;
  const clean = (items) => Array.isArray(items)
    ? [...new Set(items
      .filter((item) => typeof item === "string" && item.trim())
      .map((item) => item.trim().slice(0, 100)))].slice(0, 100)
    : [];
  return {
    order: clean(value.order),
    hidden: clean(value.hidden),
    exportVisible: value.exportVisible === true,
  };
}

function hasAnalysisSetup() {
  return Object.keys(readLayoutEnvelope().tables).length > 0
    || Object.keys(readFilterEnvelope().tables).length > 0
    || Object.keys(readRecentEnvelope().tables).length > 0
    || Object.keys(readExportPresetEnvelope().tables).length > 0;
}

function analysisSetupExportText() {
  const layouts = readLayoutEnvelope().tables;
  const filters = readFilterEnvelope().tables;
  const recents = readRecentEnvelope().tables;
  const presets = readExportPresetEnvelope().tables;
  const names = new Set([
    ...Object.keys(layouts),
    ...Object.keys(filters),
    ...Object.keys(recents),
    ...Object.keys(presets),
  ]);
  const tables = {};
  for (const table of names) {
    const entry = {};
    const layout = normaliseLayoutEntry(layouts[table]);
    if (layout) entry.layout = layout;
    const tableFilters = normaliseFilterEntries(filters[table]);
    if (tableFilters.length) entry.filters = tableFilters;
    const tableRecents = normaliseRecentEntries(recents[table]);
    if (tableRecents.length) entry.recents = tableRecents;
    const tablePresets = normaliseExportPresetEntries(presets[table]);
    if (tablePresets.length) entry.export_presets = tablePresets;
    if (Object.keys(entry).length) tables[table] = entry;
  }
  return `${JSON.stringify({
    version: 1,
    exported_at: new Date().toISOString(),
    tables,
  }, null, 2)}\n`;
}

function previewAnalysisSetup(text) {
  let parsed = null;
  try {
    parsed = JSON.parse(text);
  } catch (_error) {
    throw new Error("That file is not valid JSON.");
  }
  const raw = parsed?.tables;
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    throw new Error("Expected a tables object in that setup file.");
  }
  const layoutTables = { ...readLayoutEnvelope().tables };
  const filterTables = { ...readFilterEnvelope().tables };
  const recentTables = { ...readRecentEnvelope().tables };
  const presetTables = { ...readExportPresetEnvelope().tables };
  const counts = { tables: 0, layouts: 0, filters: 0, recents: 0, presets: 0 };
  const tables = [];
  for (const [table, value] of Object.entries(raw)) {
    if (!table || table.length > 100) continue;
    if (["__proto__", "constructor", "prototype"].includes(table)) continue;
    if (!value || typeof value !== "object" || Array.isArray(value)) continue;
    const layout = normaliseLayoutEntry(value.layout);
    const incomingFilters = normaliseFilterEntries(value.filters);
    const incomingRecents = normaliseRecentEntries(value.recents);
    const incomingPresets = normaliseExportPresetEntries(value.export_presets);
    if (!layout && !incomingFilters.length && !incomingRecents.length && !incomingPresets.length) {
      continue;
    }
    if (layout) {
      layoutTables[table] = layout;
      counts.layouts += 1;
    }
    if (incomingFilters.length) {
      const existing = normaliseFilterEntries(filterTables[table]);
      const names = new Set(incomingFilters.map((entry) => entry.name));
      filterTables[table] = [
        ...incomingFilters,
        ...existing.filter((entry) => !names.has(entry.name)),
      ].slice(0, 20);
      counts.filters += incomingFilters.length;
    }
    if (incomingRecents.length) {
      const existing = normaliseRecentEntries(recentTables[table]);
      const keys = new Set(incomingRecents.map((entry) => `${entry.column}\u0000${entry.query}`));
      recentTables[table] = [
        ...incomingRecents,
        ...existing.filter((entry) => !keys.has(`${entry.column}\u0000${entry.query}`)),
      ].slice(0, TABLE_RECENTS_LIMIT);
      counts.recents += incomingRecents.length;
    }
    if (incomingPresets.length) {
      const existing = normaliseExportPresetEntries(presetTables[table]);
      const names = new Set(incomingPresets.map((entry) => entry.name));
      presetTables[table] = [
        ...incomingPresets,
        ...existing.filter((entry) => !names.has(entry.name)),
      ].slice(0, 20);
      counts.presets += incomingPresets.length;
    }
    counts.tables += 1;
    tables.push({
      name: table,
      layout: Boolean(layout),
      filters: incomingFilters.length,
      recents: incomingRecents.length,
      presets: incomingPresets.length,
    });
  }
  if (!counts.tables) throw new Error("No table setup found in that file.");
  return {
    counts,
    tables,
    layoutTables,
    filterTables,
    recentTables,
    presetTables,
  };
}

function commitAnalysisSetup(preview) {
  if (!writeLayoutEnvelope(preview.layoutTables)
    || !writeFilterEnvelope(preview.filterTables)
    || !writeRecentEnvelope(preview.recentTables)
    || !writeExportPresetEnvelope(preview.presetTables)) {
    throw new Error("Browser storage is unavailable; could not import the setup.");
  }
  return preview.counts;
}

function importAnalysisSetup(text) {
  return commitAnalysisSetup(previewAnalysisSetup(text));
}

function setAnalysisSetupStatus(text, kind = "") {
  const node = document.getElementById("table-setup-status");
  if (!node) return;
  node.textContent = text;
  node.className = `table-filters-status ${kind}`.trim();
}

function setExportPresetStatus(text, kind = "") {
  const node = document.getElementById("table-export-preset-status");
  if (!node) return;
  node.textContent = text;
  node.className = `table-filters-status ${kind}`.trim();
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
            state.tableOrder = [];
            state.tableLayoutTable = null;
            state.tableLayoutWarning = false;
            state.tableLayoutMessage = "";
            state.tableExportVisible = false;
            state.tableColumnsOpen = false;
            state.tableFiltersOpen = false;
            state.tableSavedFilter = "";
            state.tableExportPresetsOpen = false;
            state.tableExportPreset = "";
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
  let pendingSetup = null;
  const setupPreviewSummary = el("p", { className: "table-filters-status" });
  const setupPreviewSearch = el("input", {
    id: "table-setup-preview-search",
    type: "search",
    className: "collection-search",
    placeholder: "Search preview tables…",
    "aria-label": "Search setup preview tables",
  });
  const setupPreviewTables = el("ul", { className: "table-setup-list" });
  const renderSetupPreviewTables = () => {
    if (!pendingSetup) return;
    const term = setupPreviewSearch.value.trim().toLowerCase();
    const rows = pendingSetup.tables.filter((table) => {
      const parts = [];
      if (table.layout) parts.push("layout");
      if (table.filters) parts.push(`${table.filters} filter${table.filters === 1 ? "" : "s"}`);
      if (table.recents) parts.push(`${table.recents} recent`);
      if (table.presets) parts.push(`${table.presets} preset${table.presets === 1 ? "" : "s"}`);
      return !term || `${table.name} ${parts.join(" ")}`.toLowerCase().includes(term);
    });
    if (!rows.length) {
      setupPreviewTables.replaceChildren(el("li", {}, "No matching tables"));
      return;
    }
    setupPreviewTables.replaceChildren(...rows.map((table) => {
      const parts = [];
      if (table.layout) parts.push("layout");
      if (table.filters) parts.push(`${table.filters} filter${table.filters === 1 ? "" : "s"}`);
      if (table.recents) parts.push(`${table.recents} recent`);
      if (table.presets) parts.push(`${table.presets} preset${table.presets === 1 ? "" : "s"}`);
      return el("li", {}, `${table.name} — ${parts.join(", ")}`);
    }));
  };
  setupPreviewSearch.addEventListener("input", renderSetupPreviewTables);
  const setupPreview = el(
    "div",
    { id: "table-setup-preview", className: "table-setup-preview", hidden: true },
    el("strong", {}, "Review setup import"),
    setupPreviewSummary,
    setupPreviewSearch,
    setupPreviewTables,
    el("div", { className: "table-filters-portability" },
      el("button", {
        id: "table-setup-confirm",
        type: "button",
        onclick: async () => {
          if (!pendingSetup) return;
          try {
            const counts = commitAnalysisSetup(pendingSetup);
            pendingSetup = null;
            setupPreview.hidden = true;
            state.tableLayoutTable = null;
            state.tableSavedFilter = "";
            state.tableExportPreset = "";
            state.tableSetupOpen = true;
            await renderPanel();
            setAnalysisSetupStatus(
              `Imported setup for ${counts.tables} table${counts.tables === 1 ? "" : "s"}.`,
            );
          } catch (error) {
            setAnalysisSetupStatus(
              error?.message ?? "That setup file could not be imported.",
              "error",
            );
          }
        },
      }, "Import setup"),
      el("button", {
        id: "table-setup-cancel",
        type: "button",
        onclick: () => {
          pendingSetup = null;
          setupPreviewSearch.value = "";
          setupPreview.hidden = true;
          setAnalysisSetupStatus("Import cancelled.");
        },
      }, "Cancel"),
    ),
  );
  const setupFile = el("input", {
    id: "table-setup-import",
    type: "file",
    accept: ".json,application/json",
    hidden: true,
    "aria-label": "Import analysis setup JSON",
  });
  setupFile.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (file.size > 1_000_000) {
      pendingSetup = null;
      setupPreview.hidden = true;
      setAnalysisSetupStatus("That file is too large; choose a setup export under 1 MB.", "error");
      event.target.value = "";
      return;
    }
    try {
      const preview = previewAnalysisSetup(await file.text());
      pendingSetup = preview;
      setupPreviewSummary.textContent = [
        `${preview.counts.tables} table${preview.counts.tables === 1 ? "" : "s"}`,
        `${preview.counts.layouts} layout${preview.counts.layouts === 1 ? "" : "s"}`,
        `${preview.counts.filters} filter${preview.counts.filters === 1 ? "" : "s"}`,
        `${preview.counts.recents} recent`,
        `${preview.counts.presets} preset${preview.counts.presets === 1 ? "" : "s"}`,
      ].join(" · ");
      setupPreviewSearch.value = "";
      renderSetupPreviewTables();
      setupPreview.hidden = false;
      setAnalysisSetupStatus("Review the import summary, then import or cancel.");
    } catch (error) {
      pendingSetup = null;
      setupPreview.hidden = true;
      setAnalysisSetupStatus(error?.message ?? "That setup file could not be imported.", "error");
    } finally {
      event.target.value = "";
    }
  });
  const setupDetails = el(
    "details",
    { id: "table-setup", className: "table-filters table-setup", open: state.tableSetupOpen },
    el("summary", {}, "Analysis setup · export/import"),
    el("div", { className: "table-filters-body" },
      el("p", { className: "table-filters-status" },
        "Bundle table layouts, saved/recent filters, and export presets."),
      el("div", { className: "table-filters-portability" },
        el("button", {
          type: "button",
          disabled: !hasAnalysisSetup(),
          onclick: async () => {
            const url = URL.createObjectURL(
              new Blob([analysisSetupExportText()], { type: "application/json" }),
            );
            const link = el("a", {
              href: url,
              download: "fresh-fvsbc-analysis-setup.json",
            });
            document.body.append(link);
            link.click();
            link.remove();
            window.setTimeout(() => URL.revokeObjectURL(url), 1000);
            state.tableSetupOpen = true;
            await renderPanel();
            setAnalysisSetupStatus("Exported the analysis setup.");
          },
        }, "Export setup"),
        el("button", {
          type: "button",
          onclick: () => setupFile.click(),
        }, "Import setup"),
        setupFile,
      ),
      setupPreview,
      el("p", {
        id: "table-setup-status",
        className: "table-filters-status",
        "aria-live": "polite",
      }),
    ),
  );
  setupDetails.addEventListener("toggle", () => {
    state.tableSetupOpen = setupDetails.open;
  });
  body.append(setupDetails);

  if (!state.table || !tables.some((table) => table.name === state.table)) {
    const preferred = ["FVS_Summary_Metric", "FVS_TreeList_Metric", "FVS_CutList_Metric"];
    state.table = preferred.find((name) => tables.some((table) => table.name === name))
      ?? tables[0]?.name
      ?? null;
    state.tableHidden = [];
    state.tableOrder = [];
    state.tableLayoutTable = null;
    state.tableLayoutWarning = false;
    state.tableLayoutMessage = "";
    state.tableExportVisible = false;
    state.tableColumnsOpen = false;
    state.tableFiltersOpen = false;
    state.tableSavedFilter = "";
    state.tableExportPresetsOpen = false;
    state.tableExportPreset = "";
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
  if (state.tableLayoutTable !== state.table) {
    const layout = readTableLayout(state.table, payload.columns);
    state.tableOrder = layout.order;
    state.tableHidden = layout.hidden;
    state.tableExportVisible = layout.exportVisible;
    state.tableLayoutWarning = !layout.ok;
    state.tableLayoutTable = state.table;
  }
  state.tableOrder = normaliseColumnOrder(state.tableOrder, payload.columns);
  state.tableHidden = state.tableHidden.filter((column) => payload.columns.includes(column));
  let hidden = new Set(state.tableHidden);
  if (hidden.size >= state.tableOrder.length) {
    hidden = new Set();
    state.tableHidden = [];
  }
  const visibleColumns = state.tableOrder.filter((column) => !hidden.has(column));
  if (state.tableColumn && !visibleColumns.includes(state.tableColumn)) {
    state.tableColumn = "";
    updateUrl();
  }
  const csvParams = new URLSearchParams();
  if (state.tableQuery) csvParams.set("q", state.tableQuery);
  if (state.tableColumn) csvParams.set("column", state.tableColumn);
  if (state.tableExportVisible) csvParams.set("columns", visibleColumns.join(","));
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
      state.tableSavedFilter = "";
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
      state.tableSavedFilter = "";
      state.tableOffset = 0;
      recordTableRecent(state.table, state.tableQuery, state.tableColumn);
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
            state.tableSavedFilter = "";
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
        title: state.tableExportVisible
          ? "CSV with the visible columns in this order."
          : "CSV data only; use Package for units and provenance.",
      }, "CSV"),
      el("a", {
        className: "button-like",
        href: packageHref,
        download: `${state.run.id}-${state.table}.zip`,
        title: state.tableExportVisible
          ? "CSV, metadata, and README for the visible columns in this order."
          : "CSV plus metadata.json and README.txt",
      }, "Package"),
    ),
  );
  body.append(filterForm);
  const storedFilters = readTableFilters(state.table);
  const savedFilters = sortPresetCollection(storedFilters.filters, state.tableFilterSort);
  if (!savedFilters.some((filter) => filter.id === state.tableSavedFilter)) {
    state.tableSavedFilter = "";
  }
  const filterSelect = el("select", {
    id: "table-filter-saved",
    "aria-label": "Saved table filters",
    onchange: (event) => {
      state.tableSavedFilter = event.target.value;
      const disabled = !event.target.value;
      document.getElementById("table-filter-load").disabled = disabled;
      document.getElementById("table-filter-delete").disabled = disabled;
      document.getElementById("table-filter-rename").disabled = disabled;
      document.getElementById("table-filter-duplicate").disabled = disabled;
    },
  },
    el("option", { value: "" },
      savedFilters.length ? "Choose a saved filter…" : "No saved filters",
    ),
    ...savedFilters.map((filter) =>
      el("option", {
        value: filter.id,
        selected: filter.id === state.tableSavedFilter,
      }, filter.name),
    ),
  );
  const filterSearch = el("input", {
    id: "table-filter-search",
    type: "search",
    className: "collection-search",
    placeholder: "Search saved filters…",
    "aria-label": "Search saved filters",
  });
  attachSelectSearch(filterSearch, filterSelect);
  const filterSort = el("select", {
    id: "table-filter-sort",
    className: "collection-sort",
    "aria-label": "Sort saved filters",
    onchange: (event) => {
      state.tableFilterSort = event.target.value;
      renderPanel();
    },
  },
    ...["recent", "name", "name-desc"].map((value) =>
      el("option", { value, selected: state.tableFilterSort === value },
        value === "recent" ? "Recent first" : value === "name" ? "Name A–Z" : "Name Z–A",
      ),
    ),
  );
  const filterName = el("input", {
    id: "table-filter-name",
    type: "text",
    maxlength: "80",
    placeholder: "Name this filter…",
    "aria-label": "Saved filter name",
  });
  const storedRecents = readTableRecents(state.table);
  const recents = storedRecents.recents;
  const filtersStorageOk = storedFilters.ok && storedRecents.ok;
  const filterEnvelope = readFilterEnvelope();
  const recentEnvelope = readRecentEnvelope();
  const hasPortableHistory = Object.values(filterEnvelope.tables).some(
    (items) => Array.isArray(items) && items.length,
  ) || Object.values(recentEnvelope.tables).some(
    (items) => Array.isArray(items) && items.length,
  );
  const filterPreview = createImportPreview(
    "table-filter-preview",
    "Review filter import",
    async (preview) => {
      try {
        const result = commitTableFilters(preview);
        filterPreview.hide();
        state.tableSavedFilter = "";
        state.tableFiltersOpen = true;
        await renderPanel();
        setTableFilterStatus(
          `Imported filters for ${result.tables} table${result.tables === 1 ? "" : "s"}.`,
        );
      } catch (error) {
        setTableFilterStatus(error?.message ?? "That filter file could not be imported.", "error");
      }
    },
    () => setTableFilterStatus("Filter import cancelled."),
  );
  const filterFile = el("input", {
    id: "table-filter-import",
    type: "file",
    accept: ".json,application/json",
    hidden: true,
    "aria-label": "Import table filters JSON",
  });
  filterFile.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (file.size > 500_000) {
      setTableFilterStatus("That file is too large; choose a filter export under 500 KB.", "error");
      event.target.value = "";
      return;
    }
    try {
      const preview = previewTableFilters(await file.text());
      filterPreview.show(
        preview,
        `${preview.tables} table${preview.tables === 1 ? "" : "s"} · `
          + `${preview.filters} filter${preview.filters === 1 ? "" : "s"} · `
          + `${preview.recents} recent`,
        preview.details.map((table) =>
          `${table.name} — ${table.filters} filter${table.filters === 1 ? "" : "s"}, `
            + `${table.recents} recent`,
        ),
      );
      setTableFilterStatus("Review the filter import, then import or cancel.");
    } catch (error) {
      filterPreview.hide();
      setTableFilterStatus(error?.message ?? "That filter file could not be imported.", "error");
    } finally {
      event.target.value = "";
    }
  });
  const recentSelect = el("select", {
    id: "table-filter-recent",
    "aria-label": "Recent table filters",
    onchange: (event) => {
      const disabled = !event.target.value;
      document.getElementById("table-filter-recent-load").disabled = disabled;
      document.getElementById("table-filter-recent-pin").disabled = disabled;
      document.getElementById("table-filter-recent-remove").disabled = disabled;
    },
  },
    el("option", { value: "" },
      recents.length ? "Choose a recent filter…" : "No recent filters",
    ),
    ...recents.map((entry, index) => {
      const option = el("option", { value: String(index) }, recentFilterLabel(entry));
      if (entry.used_at) option.title = new Date(entry.used_at).toLocaleString();
      return option;
    }),
  );
  const recentSearch = el("input", {
    id: "table-filter-recent-search",
    type: "search",
    className: "collection-search",
    placeholder: "Search recent filters…",
    "aria-label": "Search recent filters",
  });
  attachSelectSearch(recentSearch, recentSelect);
  const applyFilterValues = (query, column) => {
    state.tableQuery = query;
    state.tableColumn = payload.columns.includes(column) ? column : "";
    if (state.tableColumn && state.tableHidden.includes(state.tableColumn)) {
      state.tableHidden = state.tableHidden.filter((name) => name !== state.tableColumn);
      persistTableLayout();
    }
    state.tableOffset = 0;
  };
  const loadRecentFilter = async () => {
    if (!recentSelect.value) {
      setTableFilterStatus("Choose a recent filter first.", "error");
      return;
    }
    const entry = recents[Number(recentSelect.value)];
    if (!entry) {
      setTableFilterStatus("Choose a recent filter first.", "error");
      return;
    }
    applyFilterValues(entry.query, entry.column);
    state.tableSavedFilter = "";
    recordTableRecent(state.table, entry.query, entry.column);
    state.tableFiltersOpen = true;
    updateUrl();
    await renderPanel();
    setTableFilterStatus(`Loaded recent ${recentFilterLabel(entry)}.`);
  };
  const loadSavedFilter = async () => {
    const filter = savedFilters.find((entry) => entry.id === filterSelect.value);
    if (!filter) {
      setTableFilterStatus("Choose a saved filter first.", "error");
      return;
    }
    applyFilterValues(filter.query, filter.column);
    recordTableRecent(state.table, filter.query, filter.column);
    state.tableSavedFilter = filter.id;
    state.tableFiltersOpen = true;
    updateUrl();
    await renderPanel();
    setTableFilterStatus(`Loaded “${filter.name}”.`);
  };
  const deleteSavedFilter = async () => {
    const filter = savedFilters.find((entry) => entry.id === filterSelect.value);
    if (!filter) {
      setTableFilterStatus("Choose a saved filter to delete.", "error");
      return;
    }
    const next = savedFilters.filter((entry) => entry.id !== filter.id);
    if (!writeTableFilters(state.table, next)) {
      setTableFilterStatus("Browser storage is unavailable; could not delete this filter.", "error");
      return;
    }
    state.tableSavedFilter = next[0]?.id ?? "";
    state.tableFiltersOpen = true;
    await renderPanel();
    setTableFilterStatus(`Deleted “${filter.name}”.`);
  };
  const renameSavedFilter = async () => {
    const filter = savedFilters.find((entry) => entry.id === state.tableSavedFilter);
    if (!filter) {
      setTableFilterStatus("Choose a saved filter to rename.", "error");
      return;
    }
    const name = String(filterName.value || "").trim().slice(0, 80);
    if (!name) {
      setTableFilterStatus("Enter the new name first.", "error");
      return;
    }
    if (name === filter.name) {
      setTableFilterStatus("That is already the filter name.", "error");
      return;
    }
    if (savedFilters.some((entry) => entry.id !== filter.id && entry.name === name)) {
      setTableFilterStatus("Another saved filter already uses that name.", "error");
      return;
    }
    const next = savedFilters.map((entry) =>
      entry.id === filter.id ? { ...entry, name } : entry,
    );
    if (!writeTableFilters(state.table, next)) {
      setTableFilterStatus("Browser storage is unavailable; could not rename this filter.", "error");
      return;
    }
    state.tableSavedFilter = filter.id;
    state.tableFiltersOpen = true;
    filterName.value = "";
    await renderPanel();
    setTableFilterStatus(`Renamed to “${name}”.`);
  };
  const duplicateSavedFilter = async () => {
    const filter = savedFilters.find((entry) => entry.id === state.tableSavedFilter);
    if (!filter) {
      setTableFilterStatus("Choose a saved filter to duplicate.", "error");
      return;
    }
    const name = uniqueCopyName(filter.name, new Set(savedFilters.map((entry) => entry.name)));
    const copy = {
      ...filter,
      id: window.crypto?.randomUUID?.()
        ?? `filter-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      name,
      created_at: new Date().toISOString(),
    };
    if (!writeTableFilters(state.table, [copy, ...savedFilters])) {
      setTableFilterStatus(
        "Browser storage is unavailable; could not duplicate this filter.",
        "error",
      );
      return;
    }
    state.tableSavedFilter = copy.id;
    state.tableFiltersOpen = true;
    await renderPanel();
    setTableFilterStatus(`Duplicated as “${name}”.`);
  };
  const saveNamedFilter = async (name, query, column) => {
    const clean = String(name || "").trim().slice(0, 80);
    if (!clean) {
      setTableFilterStatus("Give the filter a name first.", "error");
      return null;
    }
    const existing = savedFilters.find((filter) => filter.name === clean);
    const entry = {
      id: existing?.id ?? (
        window.crypto?.randomUUID?.()
        ?? `filter-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
      ),
      name: clean,
      query,
      column,
      created_at: new Date().toISOString(),
    };
    const next = [
      entry,
      ...savedFilters.filter((filter) => filter.id !== entry.id && filter.name !== clean),
    ].slice(0, 20);
    if (!writeTableFilters(state.table, next)) {
      setTableFilterStatus(
        "Browser storage is unavailable; could not save this filter.",
        "error",
      );
      return null;
    }
    state.tableSavedFilter = entry.id;
    state.tableFiltersOpen = true;
    await renderPanel();
    return entry;
  };
  const pinRecentFilter = async () => {
    if (!recentSelect.value) {
      setTableFilterStatus("Choose a recent filter first.", "error");
      return;
    }
    const entry = recents[Number(recentSelect.value)];
    if (!entry) {
      setTableFilterStatus("Choose a recent filter first.", "error");
      return;
    }
    const label = recentFilterLabel(entry);
    const saved = await saveNamedFilter(
      String(filterName.value || label).trim().slice(0, 80),
      entry.query,
      entry.column,
    );
    if (saved) {
      filterName.value = "";
      setTableFilterStatus(`Pinned recent ${label} as “${saved.name}”.`);
    }
  };
  const removeRecentFilter = async () => {
    if (!recentSelect.value) {
      setTableFilterStatus("Choose a recent filter to remove.", "error");
      return;
    }
    const entry = recents[Number(recentSelect.value)];
    if (!entry) return;
    const next = recents.filter(
      (item) => item.query !== entry.query || item.column !== entry.column,
    );
    if (!writeTableRecents(state.table, next)) {
      setTableFilterStatus(
        "Browser storage is unavailable; could not remove this recent filter.",
        "error",
      );
      return;
    }
    state.tableFiltersOpen = true;
    await renderPanel();
    setTableFilterStatus(`Removed recent ${recentFilterLabel(entry)}.`);
  };
  const filtersDetails = el(
    "details",
    {
      id: "table-filters",
      className: "table-filters",
      open: state.tableFiltersOpen,
    },
    el("summary", {}, `Saved filters · ${savedFilters.length}`),
    el("div", { className: "table-filters-body" },
      el("div", { className: "table-filters-row" }, filterSearch, filterSort),
      el("div", { className: "table-filters-row" },
        filterSelect,
        el("button", {
          id: "table-filter-load",
          type: "button",
          disabled: !state.tableSavedFilter,
          onclick: loadSavedFilter,
        }, "Load"),
        el("button", {
          id: "table-filter-delete",
          type: "button",
          disabled: !state.tableSavedFilter,
          onclick: deleteSavedFilter,
        }, "Delete"),
      ),
      el("div", { className: "table-filters-row" },
        el("span", { className: "table-filters-label" }, "Recent"),
        recentSearch,
      ),
      el("div", { className: "table-filters-row" },
        recentSelect,
        el("button", {
          id: "table-filter-recent-load",
          type: "button",
          disabled: true,
          onclick: loadRecentFilter,
        }, "Load recent"),
        el("button", {
          id: "table-filter-recent-pin",
          type: "button",
          disabled: true,
          onclick: pinRecentFilter,
        }, "Pin recent"),
        el("button", {
          id: "table-filter-recent-remove",
          type: "button",
          disabled: true,
          onclick: removeRecentFilter,
        }, "Remove"),
      ),
      el("div", { className: "table-filters-row" },
        filterName,
        el("button", {
          type: "button",
          onclick: async () => {
            const query = state.tableQuery.trim();
            const column = state.tableColumn;
            const fallback = column && query
              ? `${column} = “${query.slice(0, 40)}”`
              : query
                ? `Search “${query.slice(0, 40)}”`
                : column
                  ? `Column ${column}`
                  : "All rows";
            const saved = await saveNamedFilter(
              String(filterName.value || fallback).trim().slice(0, 80),
              query,
              column,
            );
            if (saved) {
              filterName.value = "";
              setTableFilterStatus(`Saved “${saved.name}”.`);
            }
          },
        }, "Save current"),
        el("button", {
          id: "table-filter-rename",
          type: "button",
          disabled: !state.tableSavedFilter,
          onclick: renameSavedFilter,
        }, "Rename"),
        el("button", {
          id: "table-filter-duplicate",
          type: "button",
          disabled: !state.tableSavedFilter,
          onclick: duplicateSavedFilter,
        }, "Duplicate"),
      ),
      filterPreview.node,
      el("p", {
        id: "table-filter-status",
        className: `table-filters-status${filtersStorageOk ? "" : " error"}`,
        "aria-live": "polite",
      }, filtersStorageOk
        ? "Saved filters and recent history stay in this browser."
        : "Browser storage is unavailable; saved filters will not persist."),
      el("div", { className: "table-filters-portability" },
        el("button", {
          type: "button",
          disabled: !hasPortableHistory,
          onclick: async () => {
            const url = URL.createObjectURL(
              new Blob([tableFiltersExportText()], { type: "application/json" }),
            );
            const link = el("a", {
              href: url,
              download: "fresh-fvsbc-table-filters.json",
            });
            document.body.append(link);
            link.click();
            link.remove();
            window.setTimeout(() => URL.revokeObjectURL(url), 1000);
            state.tableFiltersOpen = true;
            await renderPanel();
            setTableFilterStatus("Exported saved and recent table filters.");
          },
        }, "Export filters"),
        el("button", {
          type: "button",
          onclick: () => filterFile.click(),
        }, "Import filters"),
        filterFile,
      ),
    ),
  );
  filtersDetails.addEventListener("toggle", () => {
    state.tableFiltersOpen = filtersDetails.open;
  });
  body.append(filtersDetails);
  const storedPresets = readTableExportPresets(state.table);
  const exportPresets = sortPresetCollection(storedPresets.presets, state.tablePresetSort);
  if (!exportPresets.some((preset) => preset.id === state.tableExportPreset)) {
    state.tableExportPreset = "";
  }
  const presetEnvelope = readExportPresetEnvelope();
  const hasPortablePresets = Object.values(presetEnvelope.tables).some(
    (items) => Array.isArray(items) && items.length,
  );
  const presetPreview = createImportPreview(
    "table-export-preset-preview",
    "Review preset import",
    async (preview) => {
      try {
        const result = commitTableExportPresets(preview);
        presetPreview.hide();
        state.tableExportPreset = "";
        state.tableExportPresetsOpen = true;
        await renderPanel();
        setExportPresetStatus(
          `Imported ${result.presets} preset${result.presets === 1 ? "" : "s"} for `
            + `${result.tables} table${result.tables === 1 ? "" : "s"}.`,
        );
      } catch (error) {
        setExportPresetStatus(error?.message ?? "That preset file could not be imported.", "error");
      }
    },
    () => setExportPresetStatus("Preset import cancelled."),
  );
  const presetImportFile = el("input", {
    id: "table-export-preset-import",
    type: "file",
    accept: ".json,application/json",
    hidden: true,
    "aria-label": "Import export presets JSON",
  });
  presetImportFile.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (file.size > 500_000) {
      setExportPresetStatus("That file is too large; choose a preset export under 500 KB.", "error");
      event.target.value = "";
      return;
    }
    try {
      const preview = previewTableExportPresets(await file.text());
      presetPreview.show(
        preview,
        `${preview.tables} table${preview.tables === 1 ? "" : "s"} · `
          + `${preview.presets} preset${preview.presets === 1 ? "" : "s"}`,
        preview.details.map((table) =>
          `${table.name} — ${table.presets} preset${table.presets === 1 ? "" : "s"}`,
        ),
      );
      setExportPresetStatus("Review the preset import, then import or cancel.");
    } catch (error) {
      presetPreview.hide();
      setExportPresetStatus(error?.message ?? "That preset file could not be imported.", "error");
    } finally {
      event.target.value = "";
    }
  });
  const presetSelect = el("select", {
    id: "table-export-preset-select",
    "aria-label": "Export presets",
    onchange: (event) => {
      state.tableExportPreset = event.target.value;
      const disabled = !event.target.value;
      document.getElementById("table-export-preset-load").disabled = disabled;
      document.getElementById("table-export-preset-delete").disabled = disabled;
      document.getElementById("table-export-preset-duplicate").disabled = disabled;
    },
  },
    el("option", { value: "" },
      exportPresets.length ? "Choose an export preset…" : "No export presets",
    ),
    ...exportPresets.map((preset) =>
      el("option", {
        value: preset.id,
        selected: preset.id === state.tableExportPreset,
      }, preset.name),
    ),
  );
  const presetSearch = el("input", {
    id: "table-export-preset-search",
    type: "search",
    className: "collection-search",
    placeholder: "Search export presets…",
    "aria-label": "Search export presets",
  });
  attachSelectSearch(presetSearch, presetSelect);
  const presetSort = el("select", {
    id: "table-export-preset-sort",
    className: "collection-sort",
    "aria-label": "Sort export presets",
    onchange: (event) => {
      state.tablePresetSort = event.target.value;
      renderPanel();
    },
  },
    ...["recent", "name", "name-desc"].map((value) =>
      el("option", { value, selected: state.tablePresetSort === value },
        value === "recent" ? "Recent first" : value === "name" ? "Name A–Z" : "Name Z–A",
      ),
    ),
  );
  const presetName = el("input", {
    id: "table-export-preset-name",
    type: "text",
    maxlength: "80",
    placeholder: "Name this export preset…",
    "aria-label": "Export preset name",
  });
  const loadExportPreset = async () => {
    const preset = exportPresets.find((entry) => entry.id === presetSelect.value);
    if (!preset) {
      setExportPresetStatus("Choose an export preset first.", "error");
      return;
    }
    const order = normaliseColumnOrder(preset.order, payload.columns);
    const column = payload.columns.includes(preset.column) ? preset.column : "";
    let hiddenColumns = preset.hidden.filter(
      (name) => payload.columns.includes(name) && name !== column,
    );
    if (hiddenColumns.length >= order.length) hiddenColumns = [];
    state.tableQuery = preset.query;
    state.tableColumn = column;
    state.tableOrder = order;
    state.tableHidden = hiddenColumns;
    state.tableExportVisible = true;
    state.tableOffset = 0;
    state.tableSavedFilter = "";
    state.tableLayoutTable = state.table;
    state.tableLayoutWarning = !writeTableLayout(
      state.table,
      order,
      hiddenColumns,
      true,
    );
    state.tableExportPreset = preset.id;
    state.tableExportPresetsOpen = true;
    updateUrl();
    await renderPanel();
    setExportPresetStatus(`Loaded “${preset.name}”.`);
  };
  const deleteExportPreset = async () => {
    const preset = exportPresets.find((entry) => entry.id === presetSelect.value);
    if (!preset) {
      setExportPresetStatus("Choose an export preset to delete.", "error");
      return;
    }
    const next = exportPresets.filter((entry) => entry.id !== preset.id);
    if (!writeTableExportPresets(state.table, next)) {
      setExportPresetStatus(
        "Browser storage is unavailable; could not delete this preset.",
        "error",
      );
      return;
    }
    state.tableExportPreset = next[0]?.id ?? "";
    state.tableExportPresetsOpen = true;
    await renderPanel();
    setExportPresetStatus(`Deleted “${preset.name}”.`);
  };
  const duplicateExportPreset = async () => {
    const preset = exportPresets.find((entry) => entry.id === presetSelect.value);
    if (!preset) {
      setExportPresetStatus("Choose an export preset first.", "error");
      return;
    }
    const name = uniqueCopyName(
      preset.name,
      new Set(exportPresets.map((entry) => entry.name)),
    );
    const copy = {
      ...preset,
      id: window.crypto?.randomUUID?.()
        ?? `preset-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      name,
      created_at: new Date().toISOString(),
    };
    if (!writeTableExportPresets(state.table, [copy, ...exportPresets])) {
      setExportPresetStatus(
        "Browser storage is unavailable; could not duplicate this preset.",
        "error",
      );
      return;
    }
    state.tableExportPreset = copy.id;
    state.tableExportPresetsOpen = true;
    await renderPanel();
    setExportPresetStatus(`Duplicated as “${name}”.`);
  };
  const presetsDetails = el(
    "details",
    {
      id: "table-export-presets",
      className: "table-filters table-export-presets",
      open: state.tableExportPresetsOpen,
    },
    el("summary", {}, `Export presets · ${exportPresets.length}`),
    el("div", { className: "table-filters-body" },
      el("div", { className: "table-filters-row" }, presetSearch, presetSort),
      el("div", { className: "table-filters-row" },
        presetSelect,
        el("button", {
          id: "table-export-preset-load",
          type: "button",
          disabled: !state.tableExportPreset,
          onclick: loadExportPreset,
        }, "Load"),
        el("button", {
          id: "table-export-preset-duplicate",
          type: "button",
          disabled: !state.tableExportPreset,
          onclick: duplicateExportPreset,
        }, "Duplicate"),
        el("button", {
          id: "table-export-preset-delete",
          type: "button",
          disabled: !state.tableExportPreset,
          onclick: deleteExportPreset,
        }, "Delete"),
      ),
      el("div", { className: "table-filters-row" },
        presetName,
        el("button", {
          type: "button",
          onclick: async () => {
            const filterLabel = state.tableQuery
              ? state.tableColumn
                ? `${state.tableColumn} = ${state.tableQuery}`
                : state.tableQuery
              : "visible view";
            const fallback = `Export ${filterLabel}`.slice(0, 80);
            const name = String(presetName.value || fallback).trim().slice(0, 80);
            if (!name) {
              setExportPresetStatus("Give the export preset a name first.", "error");
              return;
            }
            const existing = exportPresets.find((preset) => preset.name === name);
            const entry = {
              id: existing?.id ?? (
                window.crypto?.randomUUID?.()
                ?? `preset-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
              ),
              name,
              query: state.tableQuery,
              column: state.tableColumn,
              order: [...state.tableOrder],
              hidden: [...state.tableHidden],
              created_at: new Date().toISOString(),
            };
            const next = [
              entry,
              ...exportPresets.filter(
                (preset) => preset.id !== entry.id && preset.name !== name,
              ),
            ].slice(0, 20);
            if (!writeTableExportPresets(state.table, next)) {
              setExportPresetStatus(
                "Browser storage is unavailable; could not save this preset.",
                "error",
              );
              return;
            }
            state.tableExportPreset = entry.id;
            state.tableExportPresetsOpen = true;
            presetName.value = "";
            await renderPanel();
            setExportPresetStatus(`Saved “${entry.name}”.`);
          },
        }, "Save current"),
      ),
      el("p", {
        className: `table-filters-status${storedPresets.ok ? "" : " error"}`,
      }, storedPresets.ok
        ? "Presets store this filter, column order, hidden set, and visible-column export."
        : "Browser storage is unavailable; presets will not persist."),
      presetPreview.node,
      el("p", {
        id: "table-export-preset-status",
        className: "table-filters-status",
        "aria-live": "polite",
      }),
      el("div", { className: "table-filters-portability" },
        el("button", {
          type: "button",
          disabled: !hasPortablePresets,
          onclick: async () => {
            const envelope = readExportPresetEnvelope();
            const count = Object.values(envelope.tables)
              .reduce((total, items) => total + normaliseExportPresetEntries(items).length, 0);
            if (!count) {
              setExportPresetStatus("No export presets to export.", "error");
              return;
            }
            const url = URL.createObjectURL(
              new Blob([tableExportPresetsExportText()], { type: "application/json" }),
            );
            const link = el("a", {
              href: url,
              download: "fresh-fvsbc-table-export-presets.json",
            });
            document.body.append(link);
            link.click();
            link.remove();
            window.setTimeout(() => URL.revokeObjectURL(url), 1000);
            state.tableExportPresetsOpen = true;
            await renderPanel();
            setExportPresetStatus(
              `Exported ${count} preset${count === 1 ? "" : "s"}.`,
            );
          },
        }, "Export presets"),
        el("button", {
          type: "button",
          onclick: () => presetImportFile.click(),
        }, "Import presets"),
        presetImportFile,
      ),
    ),
  );
  presetsDetails.addEventListener("toggle", () => {
    state.tableExportPresetsOpen = presetsDetails.open;
  });
  body.append(presetsDetails);
  const savedLayoutCount = Object.keys(readLayoutEnvelope().tables).length;
  const layoutPreview = createImportPreview(
    "table-layout-preview",
    "Review layout import",
    async (preview) => {
      try {
        const count = commitTableLayouts(preview);
        layoutPreview.hide();
        state.tableLayoutTable = null;
        state.tableColumnsOpen = true;
        state.tableLayoutWarning = false;
        state.tableLayoutMessage = `Imported ${count} table layout`
          + `${count === 1 ? "" : "s"}.`;
        await renderPanel();
      } catch (error) {
        setTableLayoutStatus(error?.message ?? "That layout file could not be imported.", "error");
      }
    },
    () => setTableLayoutStatus("Layout import cancelled."),
  );
  const layoutFile = el("input", {
    id: "table-layout-import",
    type: "file",
    accept: ".json,application/json",
    hidden: true,
    "aria-label": "Import table layouts JSON",
  });
  layoutFile.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (file.size > 500_000) {
      setTableLayoutStatus("That file is too large; choose a layout export under 500 KB.", "error");
      event.target.value = "";
      return;
    }
    try {
      const preview = previewTableLayouts(await file.text());
      layoutPreview.show(
        preview,
        `${preview.count} table layout${preview.count === 1 ? "" : "s"}`,
        Object.entries(preview.tables).map(([table, layout]) => {
          const hidden = layout.hidden.length ? `, ${layout.hidden.length} hidden` : "";
          return `${table} — ${layout.order.length} columns${hidden}`;
        }),
      );
      setTableLayoutStatus("Review the layout import, then import or cancel.");
    } catch (error) {
      layoutPreview.hide();
      setTableLayoutStatus(error?.message ?? "That layout file could not be imported.", "error");
    } finally {
      event.target.value = "";
    }
  });
  const columnsDetails = el(
    "details",
    { id: "table-columns", className: "table-columns", open: state.tableColumnsOpen },
    el("summary", {},
      `Columns · ${visibleColumns.length} of ${payload.columns.length} shown`,
    ),
    el("div", { className: "table-columns-body" },
      el("div", { className: "table-columns-grid" },
        ...state.tableOrder.map((column, index) => {
          const unit = payload.units?.[column];
          return el("div", { className: "table-column-row" },
            el("label", { className: "table-column-toggle" },
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
                  persistTableLayout();
                  updateUrl();
                  renderPanel();
                },
              }),
              el("span", { className: "table-column-toggle-name" }, column),
              unit ? el("small", {}, unit) : null,
            ),
            el("div", { className: "table-column-moves" },
              (() => {
                const button = el("button", {
                  type: "button",
                  disabled: index === 0,
                  onclick: () => {
                    const target = index - 1;
                    if (target < 0) return;
                    const order = [...state.tableOrder];
                    [order[index], order[target]] = [order[target], order[index]];
                    state.tableOrder = order;
                    state.tableColumnsOpen = true;
                    persistTableLayout();
                    renderPanel();
                  },
                }, "←");
                button.setAttribute("aria-label", `Move ${column} left`);
                button.title = `Move ${column} left`;
                return button;
              })(),
              (() => {
                const button = el("button", {
                  type: "button",
                  disabled: index === state.tableOrder.length - 1,
                  onclick: () => {
                    const target = index + 1;
                    if (target >= state.tableOrder.length) return;
                    const order = [...state.tableOrder];
                    [order[index], order[target]] = [order[target], order[index]];
                    state.tableOrder = order;
                    state.tableColumnsOpen = true;
                    persistTableLayout();
                    renderPanel();
                  },
                }, "→");
                button.setAttribute("aria-label", `Move ${column} right`);
                button.title = `Move ${column} right`;
                return button;
              })(),
            ),
          );
        }),
      ),
      el("label", { className: "table-columns-export" },
        el("input", {
          type: "checkbox",
          id: "table-export-visible",
          checked: state.tableExportVisible,
          onchange: (event) => {
            state.tableExportVisible = event.target.checked;
            state.tableColumnsOpen = true;
            persistTableLayout();
            updateUrl();
            renderPanel();
          },
        }),
        el("span", {}, "CSV and package exports use these visible columns, in this order"),
      ),
      el("p", {
        className: `table-columns-note${state.tableLayoutWarning ? " error" : ""}`,
      }, state.tableLayoutWarning
        ? "Browser storage is unavailable; this layout will not persist."
        : state.tableExportVisible
          ? "Exports follow this layout."
          : "Hidden columns stay in CSV and package exports."),
      el("div", { className: "table-columns-actions" },
        el("button", {
          type: "button",
          onclick: () => {
            state.tableHidden = [];
            state.tableColumnsOpen = true;
            persistTableLayout();
            updateUrl();
            renderPanel();
          },
        }, "Show all columns"),
        el("button", {
          type: "button",
          onclick: () => {
            state.tableOrder = [...payload.columns];
            state.tableHidden = [];
            state.tableExportVisible = false;
            state.tableColumnsOpen = true;
            state.tableLayoutMessage = "";
            state.tableLayoutTable = state.table;
            state.tableLayoutWarning = !clearTableLayout(state.table);
            renderPanel();
          },
        }, "Reset layout"),
      ),
      el("div", { className: "table-columns-portability" },
        el("button", {
          type: "button",
          disabled: savedLayoutCount === 0,
          onclick: async () => {
            const envelope = readLayoutEnvelope();
            const count = Object.keys(envelope.tables).length;
            if (!count) {
              setTableLayoutStatus("No saved table layouts to export.", "error");
              return;
            }
            const url = URL.createObjectURL(
              new Blob([tableLayoutsExportText()], { type: "application/json" }),
            );
            const link = el("a", {
              href: url,
              download: "fresh-fvsbc-table-layouts.json",
            });
            document.body.append(link);
            link.click();
            link.remove();
            window.setTimeout(() => URL.revokeObjectURL(url), 1000);
            state.tableLayoutMessage = `Exported ${count} table layout${count === 1 ? "" : "s"}.`;
            state.tableColumnsOpen = true;
            await renderPanel();
          },
        }, "Export layouts"),
        el("button", {
          type: "button",
          onclick: () => layoutFile.click(),
        }, "Import layouts"),
        layoutFile,
      ),
      layoutPreview.node,
      el("p", {
        id: "table-layout-status",
        className: "table-columns-status",
        "aria-live": "polite",
      }, state.tableLayoutMessage),
    ),
  );
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
  const ccolumns = Array.isArray(item.ccolumns)
    ? item.ccolumns
      .filter((column) => typeof column === "string" && column.trim())
      .map((column) => column.trim().slice(0, 100))
      .slice(0, 100)
    : [];
  const ckey = Array.isArray(item.ckey)
    ? item.ckey
      .filter((column) => typeof column === "string" && column.trim())
      .map((column) => column.trim().slice(0, 100))
      .slice(0, 20)
    : [];
  if (!name || !a || !b || !metric) return null;
  return { name, a, b, metric, ctable, ccolumns, ckey };
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
    ccolumns: [...state.compareColumns],
    ckey: [...state.compareKeyColumns],
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

  const saved = sortPresetCollection(readSavedComparisons(), state.compareSort);
  if (!state.compareSaved && saved.length) state.compareSaved = saved[0].name;
  const savedContext = el("p", {
    id: "compare-saved-context",
    className: "compare-saved-context",
  });
  const updateSavedContext = () => {
    const item = saved.find((entry) => entry.name === state.compareSaved);
    if (!item) {
      savedContext.textContent = "Choose a saved comparison to inspect its runs, metric, table, diff columns, and keys.";
      return;
    }
    const parts = [`${item.a} → ${item.b}`, `metric ${item.metric}`];
    if (item.ctable) parts.push(item.ctable);
    parts.push(item.ccolumns.length
      ? `${item.ccolumns.length} diff column${item.ccolumns.length === 1 ? "" : "s"}: ${item.ccolumns.join(", ")}`
      : "all diff columns");
    parts.push(item.ckey.length ? `keys ${item.ckey.join(", ")}` : "default keys");
    savedContext.textContent = parts.join(" · ");
  };
  updateSavedContext();
  const savedSelect = el("select", {
    id: "compare-saved",
    "aria-label": "Saved comparisons",
    onchange: (event) => {
      state.compareSaved = event.target.value;
      updateSavedContext();
    },
  },
    el("option", { value: "" }, saved.length ? "Choose a saved comparison" : "No saved comparisons"),
    ...saved.map((item) =>
      el("option", { value: item.name, selected: item.name === state.compareSaved }, item.name),
    ),
  );
  const savedSearch = el("input", {
    id: "compare-saved-search",
    type: "search",
    className: "collection-search",
    placeholder: "Search saved comparisons…",
    "aria-label": "Search saved comparisons",
  });
  attachSelectSearch(savedSearch, savedSelect);
  const savedSort = el("select", {
    id: "compare-saved-sort",
    className: "collection-sort",
    "aria-label": "Sort saved comparisons",
    onchange: (event) => {
      state.compareSort = event.target.value;
      renderPanel();
    },
  },
    ...["recent", "name", "name-desc"].map((value) =>
      el("option", { value, selected: state.compareSort === value },
        value === "recent" ? "Recent first" : value === "name" ? "Name A–Z" : "Name Z–A",
      ),
    ),
  );
  const saveName = el("input", {
    id: "compare-save-name",
    type: "text",
    placeholder: "Name to save or rename…",
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
      el("div", { className: "compare-saved-row" }, savedSearch, savedSort),
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
            state.compareColumns = [...item.ccolumns];
            state.compareKeyColumns = [...item.ckey];
            updateUrl();
            renderPanel();
          },
        }, "Load"),
        el("button", {
          type: "button",
          disabled: !saved.length || !state.compareSaved,
          onclick: async () => {
            const items = readSavedComparisons();
            const index = items.findIndex((item) => item.name === state.compareSaved);
            if (index < 0) return;
            items[index] = {
              ...items[index],
              a: state.compareA,
              b: state.compareB,
              metric: state.compareMetric,
              ctable: state.compareTable ?? "",
              ccolumns: [...state.compareColumns],
              ckey: [...state.compareKeyColumns],
            };
            writeSavedComparisons(items);
            await renderPanel();
            const fresh = document.getElementById("compare-saved-status");
            if (fresh) fresh.textContent = `Updated “${items[index].name}”.`;
          },
        }, "Update"),
        el("button", {
          type: "button",
          disabled: !saved.length || !state.compareSaved,
          onclick: async () => {
            const item = saved.find((entry) => entry.name === state.compareSaved);
            if (!item) {
              setSavedStatus("Choose a saved comparison first.", "error");
              return;
            }
            const items = readSavedComparisons();
            const name = uniqueCopyName(item.name, new Set(items.map((entry) => entry.name)));
            const copy = { ...item, name };
            writeSavedComparisons([copy, ...items]);
            state.compareSaved = name;
            await renderPanel();
            const fresh = document.getElementById("compare-saved-status");
            if (fresh) fresh.textContent = `Duplicated as “${name}”.`;
          },
        }, "Duplicate"),
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
      savedContext,
      el("div", { className: "compare-saved-row" },
        saveName,
        el("button", {
          type: "button",
          onclick: () => {
            if (saveCurrentComparison(saveName.value)) renderPanel();
          },
        }, "Save"),
        el("button", {
          type: "button",
          disabled: !saved.length || !state.compareSaved,
          onclick: async () => {
            const item = saved.find((entry) => entry.name === state.compareSaved);
            if (!item) {
              setSavedStatus("Choose a saved comparison first.", "error");
              return;
            }
            const name = String(saveName.value || "").trim().slice(0, 80);
            if (!name) {
              setSavedStatus("Enter the new name first.", "error");
              return;
            }
            if (name === item.name) {
              setSavedStatus("That is already the comparison name.", "error");
              return;
            }
            if (saved.some((entry) => entry.name === name)) {
              setSavedStatus("Another comparison already uses that name.", "error");
              return;
            }
            const items = readSavedComparisons().map((entry) =>
              entry.name === item.name ? { ...entry, name } : entry,
            );
            writeSavedComparisons(items);
            state.compareSaved = name;
            saveName.value = "";
            await renderPanel();
            const fresh = document.getElementById("compare-saved-status");
            if (fresh) fresh.textContent = `Renamed to “${name}”.`;
          },
        }, "Rename"),
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
  // The database carries a different CaseID per run. Use real identity columns instead, with
  // the table-specific defaults preserved but overridable.
  const keyOptions = ["StandID", "Year", "PtIndex", "TreeIndex", "TreeId"]
    .filter((column) => a.columns.includes(column));
  const preferredKeys = state.compareTable === "FVS_Summary_Metric"
    ? ["Year"]
    : state.compareTable.includes("TreeList") || state.compareTable.includes("CutList")
      ? ["Year", "PtIndex", "TreeIndex"]
      : ["Year", "TreeId", "TreeIndex"];
  let defaultKeys = preferredKeys.filter((column) => keyOptions.includes(column));
  if (!defaultKeys.length) defaultKeys = keyOptions.length ? [keyOptions[0]] : a.columns.slice(0, 1);
  const selectedKeys = keyOptions.filter((column) =>
    state.compareKeyColumns.includes(column),
  );
  if (selectedKeys.length !== state.compareKeyColumns.length) {
    state.compareKeyColumns = selectedKeys;
    updateUrl();
  }
  const key = selectedKeys.length ? selectedKeys : defaultKeys;
  if (keyOptions.length > 1) {
    const checkedKeys = new Set(key);
    const keysDetails = el(
      "details",
      {
        id: "compare-keys",
        className: "compare-columns compare-keys",
        open: state.compareKeysOpen,
      },
      el("summary", {}, `Key columns · ${key.join(", ")}`),
      el("div", { className: "compare-columns-body" },
        el("div", { className: "compare-columns-grid" },
          ...keyOptions.map((column) =>
            el("label", { className: "compare-column-toggle" },
              el("input", {
                type: "checkbox",
                value: column,
                checked: checkedKeys.has(column),
                onchange: (event) => {
                  if (!event.target.checked && checkedKeys.size <= 1) {
                    event.target.checked = true;
                    return;
                  }
                  if (event.target.checked) checkedKeys.add(column);
                  else checkedKeys.delete(column);
                  const chosen = keyOptions.filter((name) => checkedKeys.has(name));
                  const isDefault = chosen.length === defaultKeys.length
                    && chosen.every((name, index) => name === defaultKeys[index]);
                  state.compareKeyColumns = isDefault ? [] : chosen;
                  state.compareKeysOpen = true;
                  updateUrl();
                  renderPanel();
                },
              }),
              el("span", {}, column),
            ),
          ),
        ),
        el("div", { className: "compare-columns-actions" },
          el("button", {
            type: "button",
            onclick: () => {
              state.compareKeyColumns = [];
              state.compareKeysOpen = true;
              updateUrl();
              renderPanel();
            },
          }, "Use default keys"),
        ),
        el("p", { className: "compare-columns-note" },
          "Rows match only when these values agree; key columns are excluded from the deltas.",
        ),
      ),
    );
    keysDetails.addEventListener("toggle", () => {
      state.compareKeysOpen = keysDetails.open;
    });
    body.append(keysDetails);
  }
  const valueColumnsAll = a.columns.filter(
    (column) => !key.includes(column) && isNumeric(a.rows, column),
  );
  const knownSelection = [...new Set(
    state.compareColumns.filter((column) => valueColumnsAll.includes(column)),
  )];
  if (knownSelection.length !== state.compareColumns.length) {
    state.compareColumns = knownSelection;
    updateUrl();
  }
  const valueColumns = knownSelection.length ? knownSelection : valueColumnsAll;
  if (valueColumnsAll.length > 1) {
    const selected = new Set(valueColumns);
    const columnsDetails = el(
      "details",
      {
        id: "compare-columns",
        className: "compare-columns",
        open: state.compareColumnsOpen,
      },
      el("summary", {},
        `Diff columns · ${valueColumns.length} of ${valueColumnsAll.length} selected`,
      ),
      el("div", { className: "compare-columns-body" },
        el("div", { className: "compare-columns-grid" },
          ...valueColumnsAll.map((column) =>
            el("label", { className: "compare-column-toggle" },
              el("input", {
                type: "checkbox",
                value: column,
                checked: selected.has(column),
                onchange: (event) => {
                  if (!event.target.checked && selected.size <= 1) {
                    event.target.checked = true;
                    return;
                  }
                  if (event.target.checked) selected.add(column);
                  else selected.delete(column);
                  const chosen = valueColumnsAll.filter((name) => selected.has(name));
                  state.compareColumns = chosen.length === valueColumnsAll.length ? [] : chosen;
                  state.compareColumnsOpen = true;
                  updateUrl();
                  renderPanel();
                },
              }),
              el("span", {}, column),
            ),
          ),
        ),
        el("div", { className: "compare-columns-actions" },
          el("button", {
            type: "button",
            onclick: () => {
              state.compareColumns = [];
              state.compareColumnsOpen = true;
              updateUrl();
              renderPanel();
            },
          }, "Show all diff columns"),
        ),
        el("p", { className: "compare-columns-note" },
          "Selection changes the row-level diff and its ranking; summary metrics above are unchanged.",
        ),
      ),
    );
    columnsDetails.addEventListener("toggle", () => {
      state.compareColumnsOpen = columnsDetails.open;
    });
    body.append(columnsDetails);
  }
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
      + `showing the ${capped.length} with the largest absolute difference. B minus A. `
      + `${valueColumns.length} of ${valueColumnsAll.length} diff columns.`,
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
    ccolumns: params.get("ccolumns"),
    ckey: params.get("ckey"),
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
    if (state.compareColumns.length) params.set("ccolumns", state.compareColumns.join(","));
    if (state.compareKeyColumns.length) params.set("ckey", state.compareKeyColumns.join(","));
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
      savedChat: state.assistant.savedChat,
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
  node.title = "";
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
    parts.push(`saved model ${context.model.split("/").pop()}`);
    node.title = `Saved model: ${context.model}`;
    if (state.assistant.model && state.assistant.model !== context.model) {
      parts.push(`current model ${state.assistant.model.split("/").pop()}`);
    }
  } else if (context.mode) {
    parts.push(context.mode === "agent" ? "saved via agent" : "local summary");
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

function updateAssistantName(chats = readSavedChats()) {
  const nameNode = document.getElementById("assistant-current-name");
  const renameButton = document.getElementById("assistant-rename-open");
  const form = document.getElementById("assistant-rename-form");
  const chat = chats.find((entry) => entry.id === state.assistant.savedChat) ?? null;
  if (nameNode) nameNode.textContent = chat ? chat.name : "Unsaved chat";
  if (renameButton) renameButton.disabled = !chat;
  if (!chat && form) form.hidden = true;
}

function openAssistantRename() {
  const chat = readSavedChats().find((entry) => entry.id === state.assistant.savedChat);
  if (!chat) {
    assistantStatus("Save or load a saved chat before renaming.");
    document.getElementById("assistant-saved").open = true;
    return;
  }
  const form = document.getElementById("assistant-rename-form");
  const input = document.getElementById("assistant-rename-input");
  if (form) form.hidden = false;
  if (input) {
    input.value = chat.name;
    input.focus();
    input.select();
  }
}

function refreshAssistantSaved(selectedId = state.assistant.savedChat) {
  const select = document.getElementById("assistant-saved-select");
  if (!select) return;
  const allChats = readSavedChats();
  const selected = allChats.some((chat) => chat.id === selectedId) ? selectedId : "";
  const term = state.assistant.savedSearch.trim().toLowerCase();
  const activeChat = allChats.find((chat) => chat.id === selected) ?? null;
  const matches = sortPresetCollection(
    term
      ? allChats.filter((chat) => chat.name.toLowerCase().includes(term))
      : allChats,
    state.assistant.savedSort,
  );
  const chats = activeChat && !matches.some((chat) => chat.id === activeChat.id)
    ? [activeChat, ...matches]
    : matches;
  select.replaceChildren(
    el("option", { value: "" },
      chats.length ? (term && !matches.length ? "No matches (active chat shown)" : "Choose a saved chat…")
        : "No saved chats",
    ),
    ...chats.map((chat) => {
      const option = el("option", { value: chat.id }, chat.name);
      const title = [];
      if (chat.saved_at) title.push(new Date(chat.saved_at).toLocaleString());
      if (chat.context?.model) title.push(chat.context.model);
      if (title.length) option.title = title.join(" · ");
      return option;
    }),
  );
  select.value = selected;
  state.assistant.savedChat = selected;
  updateAssistantSavedContext(chats.find((chat) => chat.id === selected) ?? null);
  updateAssistantName(chats);
  const load = document.getElementById("assistant-saved-load");
  const remove = document.getElementById("assistant-saved-delete");
  const rename = document.getElementById("assistant-rename");
  const duplicate = document.getElementById("assistant-duplicate");
  const exportButton = document.getElementById("assistant-saved-export");
  if (load) load.disabled = !selected;
  if (remove) remove.disabled = !selected;
  if (rename) rename.disabled = !selected;
  if (duplicate) duplicate.disabled = !selected;
  if (exportButton) exportButton.disabled = !chats.length;
  const count = document.getElementById("assistant-saved-count");
  if (count) {
    count.textContent = term && allChats.length
      ? `(${chats.length} of ${allChats.length})`
      : (allChats.length ? `(${allChats.length})` : "");
  }
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
  saveAssistantHistory();
  assistantSavedStatus(`Pinned “${entry.name}”.`);
}

function savedChatsExportText() {
  return `${JSON.stringify({
    version: 1,
    exported_at: new Date().toISOString(),
    chats: readSavedChats(),
  }, null, 2)}\n`;
}

function renameAssistantChat(name) {
  const chats = readSavedChats();
  const chat = chats.find((entry) => entry.id === state.assistant.savedChat);
  if (!chat) return { error: "Choose a saved chat to rename." };
  const clean = String(name || "").trim().slice(0, 80);
  if (!clean) return { error: "Enter the new name first." };
  if (clean === chat.name) return { error: "That is already the chat name." };
  if (chats.some((entry) => entry.id !== chat.id && entry.name === clean)) {
    return { error: "Another saved chat already uses that name." };
  }
  const next = chats.map((entry) => (entry.id === chat.id ? { ...entry, name: clean } : entry));
  if (!writeSavedChats(next)) {
    return { error: "Browser storage is unavailable; could not rename this chat." };
  }
  refreshAssistantSaved(chat.id);
  saveAssistantHistory();
  return { name: clean };
}

function renameAssistantChatFromPanel() {
  const input = document.getElementById("assistant-pin-name");
  const result = renameAssistantChat(input?.value);
  if (result.error) {
    assistantSavedStatus(result.error, "error");
    return;
  }
  if (input) input.value = "";
  assistantSavedStatus(`Renamed to “${result.name}”.`);
}

function duplicateAssistantChat() {
  const chats = readSavedChats();
  const chat = chats.find((entry) => entry.id === state.assistant.savedChat);
  if (!chat) {
    assistantSavedStatus("Choose a saved chat to duplicate.", "error");
    return;
  }
  const name = uniqueCopyName(chat.name, new Set(chats.map((entry) => entry.name)));
  const copy = {
    ...chat,
    id: window.crypto?.randomUUID?.()
      ?? `chat-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    name,
    saved_at: new Date().toISOString(),
    history: JSON.parse(JSON.stringify(chat.history)),
  };
  if (!writeSavedChats([copy, ...chats])) {
    assistantSavedStatus("Browser storage is unavailable; could not duplicate this chat.", "error");
    return;
  }
  state.assistant.savedChat = copy.id;
  refreshAssistantSaved(copy.id);
  saveAssistantHistory();
  assistantSavedStatus(`Duplicated as “${name}”.`);
}

function submitAssistantRename(event) {
  event.preventDefault();
  const input = document.getElementById("assistant-rename-input");
  const result = renameAssistantChat(input?.value);
  if (result.error) {
    assistantStatus(result.error);
    return;
  }
  const form = document.getElementById("assistant-rename-form");
  if (form) form.hidden = true;
  assistantStatus(`Renamed chat to “${result.name}”.`);
}

function closeAssistantRename() {
  const form = document.getElementById("assistant-rename-form");
  if (form) form.hidden = true;
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
  state.assistant.savedChat = typeof stored.savedChat === "string" ? stored.savedChat : "";
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
  state.assistant.savedChat = "";
  state.assistant.savedSearch = "";
  const search = document.getElementById("assistant-saved-search");
  if (search) search.value = "";
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
  refreshAssistantSaved();
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
    const chats = readSavedChats();
    updateAssistantSavedContext(
      chats.find((chat) => chat.id === state.assistant.savedChat) ?? null,
    );
    assistantStatus(`Model set to ${event.target.value.split("/").pop()}.`);
  });
  document.getElementById("assistant-pin").addEventListener("click", pinAssistantChat);
  document.getElementById("assistant-saved-load").addEventListener("click", loadAssistantChat);
  document.getElementById("assistant-saved-delete").addEventListener("click", deleteAssistantChat);
  document.getElementById("assistant-rename").addEventListener("click", renameAssistantChatFromPanel);
  document.getElementById("assistant-duplicate").addEventListener("click", duplicateAssistantChat);
  document.getElementById("assistant-rename-open").addEventListener("click", openAssistantRename);
  document.getElementById("assistant-rename-form").addEventListener("submit", submitAssistantRename);
  document.getElementById("assistant-rename-cancel").addEventListener("click", closeAssistantRename);
  document.getElementById("assistant-rename-input").addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      event.preventDefault();
      closeAssistantRename();
    }
  });
  document.getElementById("assistant-saved-export").addEventListener("click", exportSavedChats);
  const savedSelect = document.getElementById("assistant-saved-select");
  savedSelect.addEventListener("change", (event) => {
    state.assistant.savedChat = event.target.value;
    const disabled = !event.target.value;
    document.getElementById("assistant-saved-load").disabled = disabled;
    document.getElementById("assistant-saved-delete").disabled = disabled;
    document.getElementById("assistant-rename").disabled = disabled;
    document.getElementById("assistant-duplicate").disabled = disabled;
    const chats = readSavedChats();
    updateAssistantSavedContext(
      chats.find((chat) => chat.id === event.target.value) ?? null,
    );
    updateAssistantName(chats);
  });
  document.getElementById("assistant-saved-search").addEventListener("input", (event) => {
    state.assistant.savedSearch = event.target.value;
    refreshAssistantSaved();
  });
  document.getElementById("assistant-saved-sort").addEventListener("change", (event) => {
    state.assistant.savedSort = event.target.value;
    refreshAssistantSaved();
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
    state.compareColumns = initial.ccolumns
      ? initial.ccolumns.split(",").filter(Boolean)
      : [];
    state.compareKeyColumns = initial.ckey
      ? initial.ckey.split(",").filter(Boolean)
      : [];
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
