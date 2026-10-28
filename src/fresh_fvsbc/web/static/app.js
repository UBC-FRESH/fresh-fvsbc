/* fresh-fvsbc web shell: a reader over the artefacts a run already wrote.
 *
 * No framework and no build step, deliberately — the same choice the ws4 and fhops front ends make. Every
 * value on screen came from the run's own files; this script computes layout and nothing else.
 */

const state = {
  skins: [],
  runs: [],
  oracle: null,
  skin: null,
  run: null,
  panel: null,
  table: null,
  compareA: null,
  compareB: null,
  compareTable: null,
  summaryColumn: null,
};

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
    return value.toLocaleString(undefined, { maximumFractionDigits: 4 });
  }
  return String(value);
};

const isNumeric = (rows, column) =>
  rows.some((row) => typeof row[column] === "number");

function badge(text, kind) {
  return el("span", { className: `badge ${kind ?? ""}`.trim() }, text);
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

  const nav = document.getElementById("panel-nav");
  nav.replaceChildren(
    ...(state.skin?.panels ?? []).map((panel) =>
      el(
        "button",
        {
          className: panel === state.panel ? "active" : "",
          onclick: () => selectPanel(panel),
        },
        panel[0].toUpperCase() + panel.slice(1),
      ),
    ),
  );

  const badgeEl = document.getElementById("run-state");
  badgeEl.className = "badge";
  badgeEl.textContent = state.run ? state.run.state : "";

  const oracleEl = document.getElementById("oracle-badge");
  // The standalone comparison is the broader of the two and the one to lead with: it covers every
  // table either build writes, not only the four the official dump carries.
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
  if (!state.skin.panels.includes(state.panel)) state.panel = state.skin.panels[0];
  renderShell();
  renderPanel();
}

function selectRun(id) {
  state.run = state.runs.find((run) => run.id === id) ?? null;
  state.table = null;
  state.summaryColumn = null;
  renderShell();
  renderPanel();
}

function selectPanel(panel) {
  state.panel = panel;
  renderShell();
  renderPanel();
}

/* ---------------------------------------------------------------- panels */

async function renderPanel() {
  const body = document.getElementById("panel-body");
  body.replaceChildren();
  if (!state.run) {
    body.append(el("p", { className: "muted" }, "Choose a run."));
    return;
  }
  if (state.run.state !== "complete") {
    body.append(
      el("p", { className: "muted" }, `The run ${state.run.id} is still running.`),
    );
    return;
  }
  const renderers = {
    tables: renderTables,
    summary: renderSummary,
    trees: renderTrees,
    keywords: renderKeywords,
    provenance: renderProvenance,
    compare: renderCompare,
  };
  const renderer = renderers[state.panel];
  if (!renderer) {
    body.append(el("p", { className: "muted" }, `No renderer for ${state.panel}.`));
    return;
  }
  try {
    await renderer(body);
  } catch (error) {
    body.append(el("p", { className: "no-oracle" }, String(error)));
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
          onclick: () => {
            state.table = table.name;
            renderPanel();
          },
        },
        table.name,
        table.oracle ? " ✓" : "",
      ),
    );
  }
  body.append(list);

  if (!state.table && tables.length) state.table = tables[0].name;
  if (!state.table) return;

  const payload = await api(
    `api/runs/${state.run.id}/tables/${encodeURIComponent(state.table)}?limit=200`,
  );
  body.append(
    el(
      "h3",
      {},
      `${payload.name} — ${fmt(payload.total)} rows, showing ${payload.rows.length}`,
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

  const header = el(
    "tr",
    {},
    ...payload.columns.map((column) =>
      el("th", { className: isNumeric(payload.rows, column) ? "num" : "" }, column),
    ),
  );
  const rows = payload.rows.map((row) =>
    el(
      "tr",
      {},
      ...payload.columns.map((column) =>
        el(
          "td",
          { className: typeof row[column] === "number" ? "num" : "" },
          fmt(row[column]),
        ),
      ),
    ),
  );
  body.append(
    el(
      "div",
      { className: "scroll" },
      el("table", {}, el("thead", {}, header), el("tbody", {}, ...rows)),
    ),
  );
}

async function renderSummary(body) {
  const rows = await api(`api/runs/${state.run.id}/summary`);
  body.append(el("h2", {}, "Summary"));
  if (!rows.length) {
    body.append(el("p", { className: "muted" }, "This run wrote no summary rows."));
    return;
  }
  const columns = Object.keys(rows[0]);
  const numeric = columns.filter((column) => isNumeric(rows, column));
  if (!state.summaryColumn || !numeric.includes(state.summaryColumn)) {
    state.summaryColumn = numeric.includes("baa") ? "baa" : numeric[0];
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
      el("option", { value: column, selected: column === state.summaryColumn }, column),
    ),
  );
  body.append(el("label", { className: "muted" }, "Series ", select));

  const x = rows.map((_, index) => index);
  const y = rows.map((row) => Number(row[state.summaryColumn] ?? 0));
  body.append(chart(x, y, rows.map((row) => row.year ?? ""), state.summaryColumn));

  body.append(el("h3", {}, "Rows"));
  const header = el("tr", {}, ...columns.map((column) => el("th", {}, column)));
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

function chart(xs, ys, labels, name) {
  const width = 720;
  const height = 240;
  const pad = { left: 56, right: 12, top: 12, bottom: 28 };
  const maxY = Math.max(...ys, 1);
  const minY = Math.min(...ys, 0);
  const spanY = maxY - minY || 1;
  const stepX = (width - pad.left - pad.right) / Math.max(xs.length - 1, 1);
  const px = (index) => pad.left + index * stepX;
  const py = (value) => height - pad.bottom - ((value - minY) / spanY) * (height - pad.top - pad.bottom);

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "chart");
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

  const path = ys.map((value, index) => `${index ? "L" : "M"}${px(index)},${py(value)}`).join(" ");
  const line = document.createElementNS("http://www.w3.org/2000/svg", "path");
  line.setAttribute("class", "line");
  line.setAttribute("d", path);
  svg.append(line);

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

  const top = document.createElementNS("http://www.w3.org/2000/svg", "text");
  top.setAttribute("x", 6);
  top.setAttribute("y", pad.top + 10);
  top.textContent = `${name} ${maxY.toFixed(1)}`;
  svg.append(top);

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

async function renderKeywords(body) {
  body.append(el("h2", {}, "Keyword set"));
  const response = await fetch(`api/runs/${state.run.id}/keywords`);
  const text = await response.text();
  body.append(el("p", { className: "muted" }, `run.key — ${text.split("\n").length} lines.`));
  body.append(el("pre", {}, text));
}

async function renderProvenance(body) {
  body.append(el("h2", {}, "Provenance"));
  const payload = await api(`api/runs/${state.run.id}/provenance`);
  const grid = el("div", { className: "grid" });
  for (const [key, value] of Object.entries(payload)) {
    grid.append(
      el(
        "div",
        { className: "card" },
        el("h3", {}, key),
        el("pre", {}, value === null ? "not written by this run" : JSON.stringify(value, null, 2)),
      ),
    );
  }
  body.append(grid);
  body.append(
    el(
      "p",
      { className: "muted" },
      "A result without these pins cannot be reproduced.",
    ),
  );
}

async function renderCompare(body) {
  body.append(el("h2", {}, "Compare two runs"));
  const complete = state.runs.filter((run) => run.state === "complete");
  if (complete.length < 2) {
    body.append(el("p", { className: "muted" }, "Two complete runs are needed to compare."));
    return;
  }
  if (!state.compareA) state.compareA = complete[0].id;
  if (!state.compareB) state.compareB = complete[1].id;

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
      { className: "controls" },
      el(
        "label",
        {},
        "A ",
        picker(state.compareA, (event) => {
          state.compareA = event.target.value;
          renderPanel();
        }),
      ),
      el(
        "label",
        {},
        "B ",
        picker(state.compareB, (event) => {
          state.compareB = event.target.value;
          renderPanel();
        }),
      ),
    ),
  );

  const tablesA = await api(`api/runs/${state.compareA}/tables`);
  const tablesB = await api(`api/runs/${state.compareB}/tables`);
  const shared = tablesA
    .map((table) => table.name)
    .filter((name) => tablesB.some((table) => table.name === name));
  if (!shared.length) {
    body.append(el("p", { className: "muted" }, "The two runs share no exposed table."));
    return;
  }
  if (!state.compareTable || !shared.includes(state.compareTable)) state.compareTable = shared[0];

  body.append(
    el(
      "label",
      { className: "muted" },
      "Table ",
      el(
        "select",
        {
          onchange: (event) => {
            state.compareTable = event.target.value;
            renderPanel();
          },
        },
        ...shared.map((name) =>
          el("option", { value: name, selected: name === state.compareTable }, name),
        ),
      ),
    ),
  );

  const [a, b] = await Promise.all([
    api(`api/runs/${state.compareA}/tables/${encodeURIComponent(state.compareTable)}?limit=5000`),
    api(`api/runs/${state.compareB}/tables/${encodeURIComponent(state.compareTable)}?limit=5000`),
  ]);

  const keyColumns = ["CaseID", "StandID", "Year", "TreeId", "TreeIndex"];
  const key = keyColumns.filter((column) => a.columns.includes(column));
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

  body.append(
    el(
      "p",
      { className: "muted" },
      `${diffs.length} rows matched on ${key.join(", ") || "row order"}; ` +
        `showing the ${capped.length} with the largest absolute difference. B minus A.`,
    ),
  );
  if (!capped.length) {
    body.append(el("p", { className: "muted" }, "No rows matched between the two runs."));
    return;
  }
  const header = el(
    "tr",
    {},
    el("th", {}, key.join(" / ")),
    ...valueColumns.map((column) => el("th", { className: "num" }, column)),
  );
  const rows = capped.map((entry) =>
    el(
      "tr",
      {},
      el("td", {}, entry.key),
      ...valueColumns.map((column) => el("td", { className: "num" }, fmt(entry.delta ?? entry.cells[column]))),
    ),
  );
  body.append(
    el(
      "div",
      { className: "scroll" },
      el("table", {}, el("thead", {}, header), el("tbody", {}, ...rows)),
    ),
  );
}

/* ---------------------------------------------------------------- boot */

async function boot() {
  try {
    const [skins, runs, oracle] = await Promise.all([
      api("api/skins"),
      api("api/runs"),
      api("api/oracle"),
    ]);
    state.skins = skins;
    state.runs = runs;
    state.oracle = oracle;
    state.skin = skins[0];
    state.panel = state.skin.panels[0];
    const firstComplete = runs.find((run) => run.state === "complete") ?? runs[0] ?? null;
    state.run = firstComplete;
    renderShell();
    await renderPanel();
  } catch (error) {
    document.getElementById("panel-body").replaceChildren(
      el("p", { className: "no-oracle" }, `Could not start: ${error}`),
    );
  }
}

boot();
