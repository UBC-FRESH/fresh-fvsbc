/* fresh-fvsbc stand visuals: a 2D schematic map and a 3D stand viewer.
 *
 * Both views read one payload built from the run's own per-tree tables. The layout is schematic:
 * FVS writes no x/y coordinates, so the backend places trees in a cell per plot, in TreeIndex
 * order. Nothing here invents a value; the 3D ground is flat because the tables carry no terrain.
 */

const COLORS = {
  background: "#0e1214",
  grid: "#1d2a24",
  cell: "#2c363f",
  cellFill: "rgba(111, 211, 168, 0.045)",
  ink: "#dfe6ec",
  muted: "#8d9aa5",
  accent: "#6fd3a8",
  cut: "#f08a24",
  trunk: "#6b543c",
};

/* The common BC species first, then a stable hue for anything else. Keys are FVS codes. */
const SPECIES = {
  FD: "#4f9a56",
  CW: "#2fbfb0",
  HW: "#7fbf4f",
  BA: "#4f7f9a",
  DR: "#b08a3e",
  AT: "#c07a4a",
  PL: "#8a6fbf",
  PY: "#bf6f8a",
  SX: "#6f9abf",
  BL: "#9abf6f",
  EP: "#5f9f8a",
  AC: "#bfa35f",
  MB: "#7f8fbf",
  PA: "#bf8f5f",
  SS: "#5fbfa8",
  LT: "#8fbf5f",
  LW: "#8f6fbf",
  PW: "#bf5f5f",
  HM: "#5f8fbf",
  YC: "#bfbf5f",
  TW: "#5fbf6f",
  BG: "#7f5f9f",
  GB: "#4fbf8f",
  WB: "#bf6f5f",
  RA: "#6fbf5f",
  AL: "#7f7fbf",
  CA: "#bf9f7f",
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

function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (value === null || value === undefined) continue;
    if (key === "class") node.className = value;
    else if (key === "text") node.textContent = value;
    else if (key === "selected") node.selected = Boolean(value);
    else if (key.startsWith("on") && typeof value === "function") {
      node.addEventListener(key.slice(2).toLowerCase(), value);
    } else node.setAttribute(key, String(value));
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined) continue;
    node.append(child.nodeType ? child : document.createTextNode(String(child)));
  }
  return node;
}

function speciesColor(code) {
  const key = String(code || "??").toUpperCase();
  if (SPECIES[key]) return SPECIES[key];
  let hash = 0;
  for (let index = 0; index < key.length; index += 1) {
    hash = (hash * 31 + key.charCodeAt(index)) >>> 0;
  }
  return `hsl(${hash % 360}, 48%, 58%)`;
}

function treeRadius(dbhCm) {
  const dbh = Number(dbhCm);
  if (!Number.isFinite(dbh) || dbh <= 0) return 2.2;
  return Math.max(1.6, Math.min(10, 1.4 + Math.sqrt(dbh) * 0.85));
}

function describe(tree) {
  const species = tree.species_plants
    ? `${tree.species} (${tree.species_plants})`
    : tree.species;
  return [
    `${species} · tree ${tree.tree_id}`,
    `plot ${tree.plot} · ${tree.status}`,
    tree.dbh_cm === null ? null : `DBH ${fmt(tree.dbh_cm)} cm`,
    tree.height_m === null ? null : `height ${fmt(tree.height_m)} m`,
    tree.tph === null ? null : `${fmt(tree.tph)} TPH`,
    tree.crown_ratio === null ? null : `crown ${fmt(tree.crown_ratio)}%`,
  ].filter(Boolean);
}

/* ------------------------------------------------------------------ 2D map */

function createMap(canvas, tooltip, onSelect = null) {
  const context = canvas.getContext("2d");
  const state = {
    payload: null,
    scale: 1,
    ox: 0,
    oy: 0,
    dragging: null,
    start: null,
    hover: null,
    selected: null,
    hits: [],
    frame: 0,
    width: 0,
    height: 0,
  };

  const schedule = () => {
    if (state.frame) return;
    state.frame = requestAnimationFrame(() => {
      state.frame = 0;
      draw();
    });
  };

  const size = () => {
    const rect = canvas.getBoundingClientRect();
    const ratio = Math.min(2, window.devicePixelRatio || 1);
    canvas.width = Math.max(1, Math.round(rect.width * ratio));
    canvas.height = Math.max(1, Math.round(rect.height * ratio));
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    state.width = rect.width;
    state.height = rect.height;
    return [rect.width, rect.height];
  };

  const worldToScreen = (x, y) => [x * state.scale + state.ox, state.oy - y * state.scale];
  const screenToWorld = (x, y) => [
    (x - state.ox) / state.scale,
    (state.oy - y) / state.scale,
  ];

  const fit = () => {
    if (!state.payload) return;
    const [width, height] = size();
    if (!width || !height) return;
    const [left, bottom, right, top] = state.payload.bounds;
    const spanX = Math.max(1, right - left);
    const spanY = Math.max(1, top - bottom);
    state.scale = Math.min(width / spanX, height / spanY) * 0.88;
    const centerX = (left + right) / 2;
    const centerY = (bottom + top) / 2;
    state.ox = width / 2 - centerX * state.scale;
    state.oy = height / 2 + centerY * state.scale;
    schedule();
  };

  const drawGrid = (width, height) => {
    const [left, top] = screenToWorld(0, 0);
    const [right, bottom] = screenToWorld(width, height);
    const step = state.scale > 4 ? 10 : state.scale > 1.5 ? 25 : 50;
    context.lineWidth = 1;
    context.strokeStyle = COLORS.grid;
    context.beginPath();
    for (let x = Math.floor(left / step) * step; x <= right; x += step) {
      const [screenX] = worldToScreen(x, 0);
      context.moveTo(screenX, 0);
      context.lineTo(screenX, height);
    }
    for (let y = Math.floor(bottom / step) * step; y <= top; y += step) {
      const [, screenY] = worldToScreen(0, y);
      context.moveTo(0, screenY);
      context.lineTo(width, screenY);
    }
    context.stroke();
  };

  const drawCells = () => {
    const cell = Number(state.payload.layout.cell_m) || 36;
    context.lineWidth = 1;
    context.strokeStyle = COLORS.cell;
    context.fillStyle = COLORS.cellFill;
    for (const plot of state.payload.plots) {
      const [left, top] = worldToScreen(plot.x - cell / 2, plot.y + cell / 2);
      const sizePx = cell * state.scale;
      context.fillRect(left, top, sizePx, sizePx);
      context.strokeRect(left, top, sizePx, sizePx);
      if (sizePx > 48) {
        context.fillStyle = COLORS.muted;
        context.font = "11px ui-sans-serif, system-ui, sans-serif";
        context.fillText(`plot ${plot.id}`, left + 6, top + 15);
        context.fillStyle = COLORS.cellFill;
      }
    }
  };

  const drawTree = (tree) => {
    const [x, y] = worldToScreen(tree.x, tree.y);
    const radius = treeRadius(tree.dbh_cm);
    context.beginPath();
    context.arc(x, y, radius, 0, Math.PI * 2);
    if (tree.status === "cut") {
      context.fillStyle = "rgba(240, 138, 36, 0.22)";
      context.fill();
      context.lineWidth = 1.4;
      context.strokeStyle = COLORS.cut;
      context.stroke();
      context.beginPath();
      context.moveTo(x - radius * 0.55, y - radius * 0.55);
      context.lineTo(x + radius * 0.55, y + radius * 0.55);
      context.moveTo(x + radius * 0.55, y - radius * 0.55);
      context.lineTo(x - radius * 0.55, y + radius * 0.55);
      context.stroke();
    } else {
      context.fillStyle = speciesColor(tree.species);
      context.globalAlpha = 0.88;
      context.fill();
      context.globalAlpha = 1;
      context.lineWidth = 0.7;
      context.strokeStyle = "rgba(14, 18, 20, 0.55)";
      context.stroke();
    }
    state.hits.push({ tree, x, y, radius });
  };

  const draw = () => {
    const width = state.width;
    const height = state.height;
    if (!width || !height) return;
    context.clearRect(0, 0, width, height);
    context.fillStyle = COLORS.background;
    context.fillRect(0, 0, width, height);
    if (!state.payload) return;
    drawGrid(width, height);
    drawCells();
    state.hits = [];
    for (const tree of state.payload.cut_trees) drawTree(tree);
    for (const tree of state.payload.trees) drawTree(tree);
    if (state.selected) {
      const [x, y] = worldToScreen(state.selected.x, state.selected.y);
      context.beginPath();
      context.arc(x, y, treeRadius(state.selected.dbh_cm) + 5, 0, Math.PI * 2);
      context.lineWidth = 2.2;
      context.strokeStyle = COLORS.accent;
      context.stroke();
    }
    if (state.hover) {
      const [x, y] = worldToScreen(state.hover.tree.x, state.hover.tree.y);
      context.beginPath();
      context.arc(x, y, treeRadius(state.hover.tree.dbh_cm) + 3.5, 0, Math.PI * 2);
      context.lineWidth = 1.6;
      context.strokeStyle = COLORS.ink;
      context.stroke();
    }
  };

  const nearest = (px, py) => {
    let best = null;
    let bestDistance = Infinity;
    for (let index = state.hits.length - 1; index >= 0; index -= 1) {
      const hit = state.hits[index];
      const distance = Math.hypot(px - hit.x, py - hit.y);
      if (distance <= hit.radius + 4 && distance < bestDistance) {
        best = hit;
        bestDistance = distance;
      }
    }
    return best;
  };

  const showTooltip = (hit, event) => {
    const rect = canvas.getBoundingClientRect();
    tooltip.replaceChildren(
      ...describe(hit.tree).map((line, index) =>
        el("div", { class: index === 0 ? "strong" : "" }, line),
      ),
    );
    tooltip.hidden = false;
    tooltip.style.left = `${event.clientX - rect.left + 12}px`;
    tooltip.style.top = `${event.clientY - rect.top + 12}px`;
  };

  const hideTooltip = () => {
    tooltip.hidden = true;
    if (state.hover) {
      state.hover = null;
      schedule();
    }
  };

  const onPointerMove = (event) => {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    if (state.dragging) {
      state.ox += x - state.dragging.x;
      state.oy += y - state.dragging.y;
      state.dragging = { x, y };
      if (state.start && Math.hypot(x - state.start.x, y - state.start.y) > 4) {
        state.start.moved = true;
      }
      hideTooltip();
      schedule();
      return;
    }
    const hit = nearest(x, y);
    if (hit) {
      state.hover = hit;
      canvas.style.cursor = "pointer";
      showTooltip(hit, event);
      schedule();
    } else {
      canvas.style.cursor = "grab";
      hideTooltip();
    }
  };

  const onPointerDown = (event) => {
    if (event.button !== 0) return;
    const rect = canvas.getBoundingClientRect();
    const point = { x: event.clientX - rect.left, y: event.clientY - rect.top };
    state.dragging = point;
    state.start = { ...point, moved: false };
    canvas.setPointerCapture(event.pointerId);
    canvas.style.cursor = "grabbing";
    hideTooltip();
  };

  const onPointerUp = (event) => {
    const wasClick = state.start && !state.start.moved;
    state.dragging = null;
    state.start = null;
    if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
    canvas.style.cursor = "grab";
    if (wasClick && onSelect) {
      const rect = canvas.getBoundingClientRect();
      const hit = nearest(event.clientX - rect.left, event.clientY - rect.top);
      if (hit) onSelect(hit.tree);
    }
  };

  const onWheel = (event) => {
    event.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const px = event.clientX - rect.left;
    const py = event.clientY - rect.top;
    const [worldX, worldY] = screenToWorld(px, py);
    const next = state.scale * Math.exp(-event.deltaY * 0.0012);
    state.scale = Math.max(0.02, Math.min(500, next));
    state.ox = px - worldX * state.scale;
    state.oy = py + worldY * state.scale;
    hideTooltip();
    schedule();
  };

  const resize = () => {
    size();
    schedule();
  };

  const observer = new ResizeObserver(resize);
  observer.observe(canvas.parentElement);
  canvas.addEventListener("pointerdown", onPointerDown);
  canvas.addEventListener("pointermove", onPointerMove);
  canvas.addEventListener("pointerup", onPointerUp);
  canvas.addEventListener("pointercancel", onPointerUp);
  canvas.addEventListener("pointerleave", hideTooltip);
  canvas.addEventListener("wheel", onWheel, { passive: false });
  canvas.style.cursor = "grab";

  return {
    setData(payload) {
      state.payload = payload;
      state.hover = null;
      state.selected = null;
      hideTooltip();
      fit();
    },
    setSelected(tree) {
      state.selected = tree;
      schedule();
    },
    fit,
    resize,
    destroy() {
      observer.disconnect();
      canvas.removeEventListener("pointerdown", onPointerDown);
      canvas.removeEventListener("pointermove", onPointerMove);
      canvas.removeEventListener("pointerup", onPointerUp);
      canvas.removeEventListener("pointercancel", onPointerUp);
      canvas.removeEventListener("pointerleave", hideTooltip);
      canvas.removeEventListener("wheel", onWheel);
      if (state.frame) cancelAnimationFrame(state.frame);
    },
  };
}

/* ------------------------------------------------------------------ 3D view */

async function createScene(container) {
  const THREE = await import("three");
  const { OrbitControls } = await import("./vendor/three/OrbitControls.js");

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
  renderer.setSize(container.clientWidth || 640, container.clientHeight || 420);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.append(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0e1214);
  const camera = new THREE.PerspectiveCamera(48, 1, 0.5, 100000);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.maxPolarAngle = Math.PI / 2 - 0.02;
  scene.add(new THREE.HemisphereLight(0xffffff, 0x24302d, 1.5));
  const sun = new THREE.DirectionalLight(0xfff2d8, 2.0);
  sun.position.set(160, 320, 180);
  scene.add(sun);

  let payload = null;
  let group = null;
  let disposed = false;

  const clearGroup = () => {
    if (!group) return;
    scene.remove(group);
    group.traverse((object) => {
      if (object.geometry) object.geometry.dispose();
      if (object.material) object.material.dispose();
    });
    group = null;
  };

  const fit = () => {
    if (!payload) return;
    const [left, bottom, right, top] = payload.bounds;
    const centerX = (left + right) / 2;
    const centerZ = (bottom + top) / 2;
    const span = Math.max(30, right - left, top - bottom);
    camera.position.set(centerX + span * 0.65, span * 0.7, centerZ + span * 0.8);
    controls.target.set(centerX, 0, centerZ);
    controls.minDistance = Math.max(2, span * 0.05);
    controls.maxDistance = span * 12;
    controls.update();
  };

  const addInstances = (geometry, material, records, place) => {
    if (!records.length) return;
    const mesh = new THREE.InstancedMesh(geometry, material, records.length);
    mesh.instanceMatrix.setUsage(THREE.StaticDrawUsage);
    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();
    const scale = new THREE.Vector3();
    const quaternion = new THREE.Quaternion();
    records.forEach((tree, index) => {
      const shape = place(tree);
      position.set(tree.x, shape.base + shape.height / 2, tree.y);
      scale.set(shape.radius * 2, shape.height, shape.radius * 2);
      matrix.compose(position, quaternion, scale);
      mesh.setMatrixAt(index, matrix);
      if (shape.color) mesh.setColorAt(index, new THREE.Color(shape.color));
    });
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    group.add(mesh);
  };

  const build = (next) => {
    payload = next;
    clearGroup();
    group = new THREE.Group();
    scene.add(group);
    const [left, bottom, right, top] = payload.bounds;
    const width = Math.max(1, right - left);
    const depth = Math.max(1, top - bottom);
    const centerX = (left + right) / 2;
    const centerZ = (bottom + top) / 2;
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(width, depth),
      new THREE.MeshStandardMaterial({ color: 0x16211b, roughness: 0.98 }),
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.set(centerX, 0, centerZ);
    group.add(ground);
    const gridSize = Math.max(width, depth) * 1.08;
    const divisions = Math.max(4, Math.min(60, Math.round(gridSize / 10)));
    const grid = new THREE.GridHelper(gridSize, divisions, 0x2c363f, 0x1d2a24);
    grid.position.set(centerX, 0.02, centerZ);
    group.add(grid);

    const trunkGeometry = new THREE.CylinderGeometry(0.5, 0.7, 1, 6);
    const crownGeometry = new THREE.ConeGeometry(0.5, 1, 7);
    const liveTrunkMaterial = new THREE.MeshStandardMaterial({
      color: COLORS.trunk,
      roughness: 0.92,
    });
    const crownMaterial = new THREE.MeshStandardMaterial({ roughness: 0.9, vertexColors: false });
    const cutMaterial = new THREE.MeshStandardMaterial({ color: COLORS.cut, roughness: 0.9 });

    addInstances(trunkGeometry, liveTrunkMaterial, payload.trees, (tree) => {
      const height = Math.max(1.5, Number(tree.height_m) || 18);
      const dbh = Math.max(0.05, (Number(tree.dbh_cm) || 25) / 100);
      const crown = Math.max(0.1, Math.min(0.95, (Number(tree.crown_ratio) || 60) / 100));
      const trunk = Math.max(0.6, height * (1 - crown));
      return { base: 0, height: trunk, radius: Math.max(0.12, dbh * 0.2) };
    });
    addInstances(crownGeometry, crownMaterial, payload.trees, (tree) => {
      const height = Math.max(1.5, Number(tree.height_m) || 18);
      const dbh = Math.max(0.05, (Number(tree.dbh_cm) || 25) / 100);
      const crown = Math.max(0.1, Math.min(0.95, (Number(tree.crown_ratio) || 60) / 100));
      const trunk = Math.max(0.6, height * (1 - crown));
      return {
        base: trunk,
        height: height - trunk,
        radius: Math.max(0.7, dbh * 9),
        color: speciesColor(tree.species),
      };
    });
    addInstances(trunkGeometry, cutMaterial, payload.cut_trees, (tree) => {
      const dbh = Math.max(0.05, (Number(tree.dbh_cm) || 25) / 100);
      return { base: 0, height: 1.2, radius: Math.max(0.15, dbh * 0.2) };
    });
    fit();
  };

  const resize = () => {
    const width = container.clientWidth || 640;
    const height = container.clientHeight || 420;
    renderer.setSize(width, height);
    camera.aspect = width / Math.max(1, height);
    camera.updateProjectionMatrix();
  };

  const observer = new ResizeObserver(resize);
  observer.observe(container);
  resize();

  const animate = () => {
    if (disposed) return;
    requestAnimationFrame(animate);
    if (container.hidden) return;
    controls.update();
    renderer.render(scene, camera);
  };
  animate();

  return {
    setData(payload) {
      build(payload);
    },
    fit,
    resize,
    destroy() {
      disposed = true;
      observer.disconnect();
      controls.dispose();
      clearGroup();
      renderer.dispose();
      renderer.domElement.remove();
    },
  };
}

/* ------------------------------------------------------------------ panel */

function updateLegend(legend, payload) {
  const items = payload.species.slice(0, 12).map((entry) =>
    el(
      "span",
      { class: "stand-legend-item" },
      el("i", { class: "swatch", style: `background:${speciesColor(entry.code)}` }),
      `${entry.code} ${fmt(entry.count)}`,
    ),
  );
  if (payload.species.length > 12) {
    const rest = payload.species.slice(12).reduce((sum, entry) => sum + entry.count, 0);
    items.push(el("span", { class: "stand-legend-item muted" }, `+${fmt(rest)} more`));
  }
  if (payload.counts.cut) {
    items.push(
      el(
        "span",
        { class: "stand-legend-item" },
        el("i", { class: "swatch swatch-cut" }),
        `cut ${fmt(payload.counts.cut)}`,
      ),
    );
  }
  legend.replaceChildren(...items);
}

function updateStats(stats, payload) {
  const summary = payload.summary || {};
  const bits = [
    `${fmt(payload.counts.trees)} live trees`,
    `${fmt(payload.counts.plots)} plot${payload.counts.plots === 1 ? "" : "s"}`,
    payload.counts.cut ? `${fmt(payload.counts.cut)} cut` : null,
    summary.baa === undefined || summary.baa === null ? null : `baa ${fmt(summary.baa)}`,
    summary.tpa === undefined || summary.tpa === null ? null : `tpa ${fmt(summary.tpa)}`,
  ].filter(Boolean);
  stats.textContent = bits.join(" · ");
}

function updateNote(note, payload) {
  const parts = [
    "Schematic layout: FVS writes no x/y, so trees sit in a cell per plot in TreeIndex order.",
    "The 3D ground is flat: the per-tree tables carry no terrain.",
  ];
  if (payload.counts.cut) parts.push("Species counts include the cut trees.");
  if (payload.truncated) {
    parts.push(
      `Only the first ${fmt(payload.counts.shown)} trees are drawn; ` +
        `${fmt(payload.counts.total)} are in this year.`,
    );
  }
  note.textContent = parts.join(" ");
}

function updateInspector(panel, tree) {
  if (!tree) {
    panel.replaceChildren(
      el("p", { class: "muted" }, "Click a tree in the 2D map to inspect it."),
    );
    return;
  }
  const rows = [
    ["Species", tree.species_plants ? `${tree.species} (${tree.species_plants})` : tree.species],
    ["Status", tree.status],
    ["Plot", tree.plot],
    ["Tree", tree.tree_id],
    ["DBH", tree.dbh_cm === null ? "—" : `${fmt(tree.dbh_cm)} cm`],
    ["Height", tree.height_m === null ? "—" : `${fmt(tree.height_m)} m`],
    ["TPH", tree.tph === null ? "—" : fmt(tree.tph)],
    ["Crown", tree.crown_ratio === null ? "—" : `${fmt(tree.crown_ratio)}%`],
    ["Age", tree.tree_age === null ? "—" : fmt(tree.tree_age)],
  ];
  panel.replaceChildren(
    el("p", { class: "inspector-kicker" }, "Selected tree"),
    el("div", { class: "inspector-grid" },
      ...rows.flatMap(([label, value]) => [
        el("span", { class: "muted" }, label),
        el("strong", {}, String(value)),
      ]),
    ),
  );
}

export async function mountVisuals(body, runId, options = {}) {
  body.append(el("h2", {}, "Stand"));
  body.append(
    el(
      "p",
      { class: "muted" },
      "The stand as the run's own per-tree tables describe it. Every value is read from the run.",
    ),
  );

  let payload;
  try {
    const initialYear = Number(options.year);
    const query = Number.isFinite(initialYear) ? `?year=${encodeURIComponent(initialYear)}` : "";
    payload = await api(`api/runs/${encodeURIComponent(runId)}/visuals${query}`);
  } catch (error) {
    if (body.isConnected) body.append(el("p", { class: "no-oracle" }, String(error)));
    return;
  }
  if (!body.isConnected) return;

  if (typeof options.onYear === "function") options.onYear(payload.year);
  if (!payload.available) {
    body.append(el("div", { class: "notice" }, payload.reason));
    body.append(
      el(
        "p",
        { class: "muted" },
        "This run wrote no per-tree table. A DATABASE block with TREELIDB and a TREELIST " +
          "keyword are what make FVS_TreeList_Metric appear.",
      ),
    );
    return;
  }

  const yearSelect = el(
    "select",
    { "aria-label": "Stand year" },
    ...payload.years.map((year) =>
      el(
        "option",
        { value: String(year), selected: year === payload.year ? "selected" : null },
        String(year),
      ),
    ),
  );
  const speciesSelect = el(
    "select",
    { "aria-label": "Species filter" },
    el("option", { value: "" }, "All species"),
    ...payload.species.map((entry) => el("option", { value: entry.code }, entry.code)),
  );
  const statusSelect = el(
    "select",
    { "aria-label": "Status filter" },
    el("option", { value: "all" }, "Live + cut"),
    el("option", { value: "live" }, "Live only"),
    el("option", { value: "cut" }, "Cut only"),
  );
  const playButton = el("button", { type: "button", class: "play-button" }, "▶ Play years");
  const view2d = el("button", { class: "active", type: "button" }, "2D map");
  const view3d = el("button", { type: "button" }, "3D stand");
  const fit = el("button", { type: "button" }, "Fit");
  const stats = el("span", { class: "muted stand-stats" });
  const legend = el("div", { class: "stand-legend" });
  const note = el("p", { class: "muted stand-note" });
  const tooltip = el("div", { class: "stand-tooltip", hidden: "" });
  const canvas = el("canvas", { class: "stand-canvas" });
  const stage = el("div", { class: "stand-stage" }, canvas, tooltip);
  const sceneHost = el("div", { class: "stand-3d", hidden: "" });
  const inspector = el("aside", { class: "stand-inspector", "aria-label": "Tree inspector" });
  const inspectorBody = el("div");
  inspector.append(
    el("div", { class: "stand-inspector-head" },
      el("h3", {}, "Inspector"),
      el("span", { class: "muted", id: "inspector-hint" }, "click a tree"),
    ),
    inspectorBody,
  );
  updateInspector(inspectorBody, null);
  stage.append(sceneHost);

  body.append(
    el(
      "div",
      { class: "stand-toolbar" },
      el("label", {}, "Year ", yearSelect),
      el("label", {}, "Species ", speciesSelect),
      el("label", {}, "Show ", statusSelect),
      playButton,
      el("div", { class: "segmented" }, view2d, view3d),
      fit,
      stats,
    ),
  );
  body.append(el("div", { class: "stand-layout" }, stage, inspector));
  body.append(legend);
  body.append(note);

  let selected = null;
  const selectTree = (tree) => {
    selected = tree;
    map.setSelected(tree);
    updateInspector(inspectorBody, tree);
  };
  const map = createMap(canvas, tooltip, selectTree);
  let scene = null;
  let view = "2d";
  let playing = false;
  let playTimer = null;
  let loading = false;

  const visiblePayload = () => {
    const species = speciesSelect.value;
    const status = statusSelect.value;
    const keep = (tree) =>
      (!species || tree.species === species) && (status === "all" || tree.status === status);
    const trees = payload.trees.filter(keep);
    const cutTrees = status === "live" ? [] : payload.cut_trees.filter(keep);
    return {
      ...payload,
      trees,
      cut_trees: cutTrees,
      counts: {
        ...payload.counts,
        trees: trees.length,
        cut: cutTrees.length,
        shown: trees.length + cutTrees.length,
      },
    };
  };

  const update = () => {
    const visible = visiblePayload();
    map.setData(visible);
    if (scene) scene.setData(visible);
    updateLegend(legend, payload);
    updateStats(stats, visible);
    updateNote(note, visible);
    if (selected) {
      const still = [...visible.trees, ...visible.cut_trees].find(
        (tree) => tree.tree_id === selected.tree_id,
      );
      if (still) {
        selected = still;
        map.setSelected(still);
      } else {
        selected = null;
        updateInspector(inspectorBody, null);
      }
    }
  };

  const stopPlay = () => {
    playing = false;
    playButton.textContent = "▶ Play years";
    if (playTimer) window.clearTimeout(playTimer);
    playTimer = null;
  };

  const loadYear = async (year) => {
    if (loading) return;
    loading = true;
    try {
      const next = await api(
        `api/runs/${encodeURIComponent(runId)}/visuals?year=${encodeURIComponent(year)}`,
      );
      if (!body.isConnected) return;
      if (next.available) {
        payload = next;
        yearSelect.value = String(payload.year);
        selected = null;
        updateInspector(inspectorBody, null);
        if (typeof options.onYear === "function") options.onYear(payload.year);
        update();
      }
    } catch (error) {
      note.textContent = String(error);
    } finally {
      loading = false;
    }
  };

  const stepPlay = async () => {
    if (!playing) return;
    const index = payload.years.indexOf(payload.year);
    if (index < 0 || index >= payload.years.length - 1) {
      stopPlay();
      return;
    }
    await loadYear(payload.years[index + 1]);
    if (!playing) return;
    playTimer = window.setTimeout(stepPlay, 900);
  };

  playButton.onclick = () => {
    if (playing) {
      stopPlay();
    } else {
      playing = true;
      playButton.textContent = "⏸ Pause";
      if (payload.year === payload.years[payload.years.length - 1]) {
        loadYear(payload.years[0]).then(() => {
          if (playing) playTimer = window.setTimeout(stepPlay, 900);
        });
      } else {
        playTimer = window.setTimeout(stepPlay, 900);
      }
    }
  };
  yearSelect.onchange = () => {
    stopPlay();
    loadYear(Number(yearSelect.value));
  };
  speciesSelect.onchange = update;
  statusSelect.onchange = update;
  view2d.onclick = () => showView("2d");
  view3d.onclick = () => showView("3d");
  fit.onclick = () => {
    if (view === "2d") map.fit();
    else if (scene) scene.fit();
  };

  const showView = async (next) => {
    view = next;
    view2d.classList.toggle("active", view === "2d");
    view3d.classList.toggle("active", view === "3d");
    canvas.hidden = view !== "2d";
    sceneHost.hidden = view !== "3d";
    if (view === "3d" && !scene) {
      view3d.textContent = "3D stand…";
      try {
        scene = await createScene(sceneHost);
        if (!body.isConnected) {
          scene.destroy();
          scene = null;
          return;
        }
        scene.setData(visiblePayload());
        view3d.textContent = "3D stand";
      } catch (error) {
        view3d.textContent = "3D stand";
        sceneHost.replaceChildren(
          el("p", { class: "no-oracle" }, `The 3D viewer could not start: ${error}`),
        );
      }
    }
    if (view === "2d") map.fit();
    if (view === "3d" && scene) scene.fit();
  };

  body._dispose = () => {
    stopPlay();
    map.destroy();
    if (scene) scene.destroy();
  };

  update();
  requestAnimationFrame(() => {
    map.resize();
    map.fit();
  });
}
