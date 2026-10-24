import {
  ancestors,
  binaryEntropy,
  catalan,
  constrain,
  oscillator,
} from "./model.mjs";
const $ = (id) => document.getElementById(id);
const NS = "http://www.w3.org/2000/svg";
let data,
  selected = "110100",
  playTimer = null;
const svg = (tag, attrs = {}) => {
  const el = document.createElementNS(NS, tag);
  for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value);
  return el;
};
const text = (parent, x, y, label, attrs = {}) => {
  const el = svg("text", { x, y, ...attrs });
  el.textContent = label;
  parent.append(el);
  return el;
};
const getDepth = () =>
  $("depth").value === "none" ? null : Number($("depth").value);
const getModel = () => data.models[$("rule").value];
const getExploration = () =>
  constrain(getModel(), $("rule").value === "zero_split" ? getDepth() : null);
function applyView(view) {
  if (!view || typeof view !== "object") return;
  if (Object.hasOwn(data.models, view.rule)) $("rule").value = view.rule;
  const generation = Number(view.generation);
  if (Number.isInteger(generation) && generation >= 0 && generation <= 6)
    $("generation").value = generation;
  if (["none", "0", "1", "2", "3", "4", "5"].includes(view.depth))
    $("depth").value = view.depth;
  selected = view.state || view.selected || selected;
}
function setRoute() {
  const route = location.hash.slice(1).split("?")[0] || "structures";
  for (const p of document.querySelectorAll(".panel"))
    p.hidden = p.id !== route;
  for (const link of document.querySelectorAll("[data-tab]")) {
    link.classList.toggle("active", link.dataset.tab === route);
    if (link.dataset.tab === route) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
  if (!$(route)) location.hash = "structures";
  if (data && location.hash.includes("?")) {
    stopPlay();
    applyView(
      Object.fromEntries(new URLSearchParams(location.hash.split("?")[1])),
    );
    render();
  }
}
function stopPlay() {
  clearInterval(playTimer);
  playTimer = null;
  $("play").textContent = "▶ Play generations";
}
function selectState(generation, word) {
  $("generation").value = generation;
  selected = word;
  render();
}
function drawHistory(exploration, generation) {
  const trail = ancestors(exploration, generation, selected),
    rows = [],
    positions = new Map();
  for (let g = 0; g <= generation; g++) {
    const all = exploration.stages[g],
      included = all.filter((w) => trail.has(`${g}:${w}`));
    for (const word of all)
      if (included.length < 7 && !included.includes(word)) included.push(word);
    included.sort();
    rows.push(included);
    included.forEach((word, i) =>
      positions.set(`${g}:${word}`, { x: 30 + g * 180, y: 65 + i * 44 }),
    );
  }
  const width = Math.max(420, 210 + generation * 180),
    height = Math.max(160, 105 + Math.max(...rows.map((r) => r.length)) * 44);
  const canvas = svg("svg", {
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-label":
      "State transitions from the initial seed to the selected generation",
  });
  canvas.style.minWidth = `${width}px`;
  for (const e of exploration.transitions) {
    if (e.generation > generation) continue;
    const p = positions.get(`${e.generation - 1}:${e.parent}`),
      c = positions.get(`${e.generation}:${e.child}`);
    if (!p || !c) continue;
    const path = svg("path", {
      d: `M${p.x + 110},${p.y} C${p.x + 145},${p.y} ${c.x - 35},${c.y} ${c.x},${c.y}`,
      fill: "none",
      stroke:
        trail.has(`${e.generation}:${e.child}`) &&
        trail.has(`${e.generation - 1}:${e.parent}`)
          ? "#a9d86e"
          : "#34483a",
      "stroke-width": 1.4,
    });
    canvas.append(path);
  }
  rows.forEach((words, g) => {
    text(
      canvas,
      30 + g * 180,
      22,
      `GEN ${g} · ${exploration.stages[g].length} STATE${exploration.stages[g].length === 1 ? "" : "S"}`,
      { "font-size": 10 },
    );
    words.forEach((word) => {
      const p = positions.get(`${g}:${word}`),
        isSelected = g === generation && word === selected;
      const group = svg("g", {
        role: "button",
        tabindex: "0",
        "aria-label": `Inspect ${word} at generation ${g}`,
        "aria-pressed": String(isSelected),
        "data-word": word,
        "data-generation": g,
        class: "history-state",
      });
      group.append(
        svg("rect", {
          x: p.x,
          y: p.y - 15,
          width: 110,
          height: 30,
          rx: 4,
          fill: isSelected ? "#c5ec7f" : "#203024",
          stroke: trail.has(`${g}:${word}`) ? "#a9d86e" : "#3a4b3d",
        }),
      );
      text(group, p.x + 55, p.y + 4, word, {
        "text-anchor": "middle",
        style: `fill:${isSelected ? "#1a2818" : "#d0ddce"}`,
      });
      const activate = () => {
        stopPlay();
        selectState(g, word);
      };
      group.addEventListener("click", activate);
      group.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          activate();
        }
      });
      canvas.append(group);
    });
    if (exploration.stages[g].length > words.length)
      text(
        canvas,
        30 + g * 180,
        height - 15,
        `+ ${exploration.stages[g].length - words.length} more · use state selector`,
        { "font-size": 9 },
      );
  });
  $("history").replaceChildren(canvas);
}
function drawTree(state) {
  const area = $("tree");
  area.replaceChildren();
  if (state.word === "0") {
    area.innerHTML =
      '<div class="seed-display">x<span>Initial potential</span></div>';
    $("tree-note").textContent =
      "The exceptional seed is not a standard nonempty tree.";
    return;
  }
  if (!state.tree) {
    area.innerHTML =
      '<div class="seed-display">∅<span>No tree in this encoding</span></div>';
    $("tree-note").textContent =
      "This alternative state is not a primitive Dyck word. The candidate parentheses/tree mapping is undefined for it.";
    return;
  }
  let count = 0;
  const nodes = [],
    edges = [];
  function visit(node, depth) {
    const current = { id: count++, depth, x: 0 };
    nodes.push(current);
    const kids = node.children.map((child) => visit(child, depth + 1));
    for (const k of kids) edges.push([current, k]);
    if (!kids.length)
      ((current.x = nodes.filter((n) => n.leaf).length), (current.leaf = true));
    else current.x = kids.reduce((sum, k) => sum + k.x, 0) / kids.length;
    return current;
  }
  visit(state.tree, 0);
  const maxX = Math.max(...nodes.map((n) => n.x), 1),
    maxD = Math.max(...nodes.map((n) => n.depth), 1);
  const canvas = svg("svg", {
    viewBox: "0 0 520 280",
    role: "img",
    "aria-label": `Rooted ordered tree for ${state.word}`,
  });
  const point = (n) => [45 + (n.x / maxX) * 420, 35 + (n.depth / maxD) * 195];
  for (const [a, b] of edges) {
    const [x1, y1] = point(a),
      [x2, y2] = point(b);
    canvas.append(svg("line", { x1, y1, x2, y2, class: "tree-edge" }));
  }
  for (const n of nodes) {
    const [cx, cy] = point(n);
    canvas.append(svg("circle", { cx, cy, r: 9, class: "tree-node" }));
    text(canvas, cx, cy + 29, String(n.id), { "text-anchor": "middle" });
  }
  area.append(canvas);
  $("tree-note").textContent =
    "Nodes are numbered in preorder; children retain their order. The x marker in the notation is not an extra vertex.";
}
function render() {
  if (!data) return;
  const rule = $("rule").value,
    generation = Number($("generation").value),
    model = getModel(),
    exploration = getExploration();
  $("generation-value").value = generation;
  $("depth").disabled = rule !== "zero_split";
  $("rule-description").textContent =
    model.description +
    (rule === "zero_split" && getDepth() !== null
      ? ` Stabilization constraint: maximum tree depth ${getDepth()} edges.`
      : "");
  const words = exploration.stages[generation];
  if (!words.includes(selected)) selected = words[0] || "";
  $("state").replaceChildren(
    ...words.map((word) => {
      const option = document.createElement("option");
      option.value = word;
      option.textContent = word;
      return option;
    }),
  );
  $("state").value = selected;
  $("state-count").textContent = words.length;
  $("distinction-count").textContent = selected
    ? model.states[selected].metrics.ones
    : "—";
  $("catalan-count").textContent = generation
    ? catalan(generation - 1)
    : "seed";
  $("dyck-count").textContent = catalan(generation);
  $("count-context").textContent =
    rule === "zero_split" && getDepth() === null
      ? "Candidate count applies to the unconstrained zero-split definition."
      : "C(n−1) is an unconstrained zero-split baseline, not a prediction for the selected alternative or constraint.";
  drawHistory(exploration, generation);
  renderComparison(generation);
  if (!selected) {
    $("selected-word").textContent = "No reachable states";
    $("notation").textContent = "Try a weaker depth constraint.";
    $("metrics").replaceChildren();
    $("tree").replaceChildren();
    $("tree-note").textContent = "No permitted path reaches this generation.";
    $("state").disabled = true;
    return;
  }
  $("state").disabled = false;
  const state = model.states[selected];
  $("selected-word").textContent = selected;
  $("notation").textContent =
    state.notation || "No candidate notation for this state";
  const labels = {
    length: "Binary length",
    ones: "Distinctions (1)",
    zeros: "Potential markers (0)",
    tree_nodes: "Tree nodes",
    tree_height: "Tree height (edges)",
    leaf_count: "Leaves",
    symbol_entropy_bits: "Marginal entropy (bits)",
  };
  $("metrics").replaceChildren();
  for (const [key, label] of Object.entries(labels)) {
    const dt = document.createElement("dt"),
      dd = document.createElement("dd");
    dt.textContent = label;
    const value = state.metrics[key];
    dd.textContent =
      value === null
        ? "Not defined"
        : typeof value === "number" && !Number.isInteger(value)
          ? value.toFixed(4)
          : value;
    $("metrics").append(dt, dd);
  }
  drawTree(state);
  try {
    localStorage.setItem(
      "research-lab-view",
      JSON.stringify({ rule, generation, selected, depth: $("depth").value }),
    );
  } catch {
    /* Storage is optional; private browsing remains usable. */
  }
}
function lineChart(series, { xlabel = "x", ylabel = "y", point = null } = {}) {
  const width = 800,
    height = 310,
    pad = { l: 62, r: 25, t: 25, b: 50 },
    all = series.flatMap((s) => s.points),
    xmin = Math.min(...all.map((p) => p.x)),
    xmax = Math.max(...all.map((p) => p.x)),
    ymin = Math.min(0, ...all.map((p) => p.y)),
    ymax = Math.max(...all.map((p) => p.y));
  const xy = (p) => [
    pad.l + ((p.x - xmin) / (xmax - xmin || 1)) * (width - pad.l - pad.r),
    height -
      pad.b -
      ((p.y - ymin) / (ymax - ymin || 1)) * (height - pad.b - pad.t),
  ];
  const canvas = svg("svg", {
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-label": `${ylabel} against ${xlabel}`,
  });
  for (let i = 0; i <= 4; i++) {
    const y = ymin + ((ymax - ymin) * i) / 4,
      [, screenY] = xy({ x: xmin, y });
    canvas.append(
      svg("line", {
        x1: pad.l,
        x2: width - pad.r,
        y1: screenY,
        y2: screenY,
        stroke: "#2b3c30",
      }),
    );
    text(canvas, pad.l - 10, screenY + 4, y.toFixed(2), {
      "text-anchor": "end",
      "font-size": 11,
    });
  }
  for (let i = 0; i <= 5; i++) {
    const x = xmin + ((xmax - xmin) * i) / 5,
      [screenX] = xy({ x, y: 0 });
    text(canvas, screenX, height - 25, x.toFixed(1), {
      "text-anchor": "middle",
      "font-size": 11,
    });
  }
  for (const s of series) {
    const points = s.points.map((p) => xy(p).join(",")).join(" ");
    canvas.append(
      svg("polyline", {
        points,
        fill: "none",
        stroke: s.color || "#c5ec7f",
        "stroke-width": 2.5,
      }),
    );
  }
  text(canvas, width / 2, height - 3, xlabel, {
    "text-anchor": "middle",
    "font-size": 11,
  });
  text(canvas, pad.l, 12, ylabel, { "font-size": 11 });
  if (point) {
    const [cx, cy] = xy(point);
    canvas.append(svg("circle", { cx, cy, r: 7, class: "chart-point" }));
  }
  return canvas;
}
function renderComparison(generation) {
  const rows = [];
  for (let g = 0; g <= generation; g++) {
    const tr = document.createElement("tr");
    for (const value of [
      g,
      data.models.zero_split.exploration.stages[g].length,
      data.models.zero_occupancy.exploration.stages[g].length,
      data.models.dyck_insertion.exploration.stages[g].length,
    ]) {
      const td = document.createElement("td");
      td.textContent = value;
      tr.append(td);
    }
    rows.push(tr);
  }
  $("comparison-body").replaceChildren(...rows);
}
let motion = 0,
  motionPaused = window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  lastFrame = 0;
function updatePhysics() {
  const amplitude = Number($("amplitude").value),
    omega = Number($("omega").value);
  $("omega-value").value = omega.toFixed(1);
  $("amplitude-value").value = amplitude.toFixed(1);
  const points = Array.from({ length: 301 }, (_, i) => {
    const s = oscillator(i / 30, amplitude, omega);
    return { x: s.t, y: s.x };
  });
  $("oscillator").replaceChildren(
    lineChart([{ points }], {
      xlabel: "Time (s)",
      ylabel: "Position (m)",
      point: { x: motion, y: oscillator(motion, amplitude, omega).x },
    }),
  );
  $("energy").textContent =
    `Total energy: ${(0.5 * omega * omega * amplitude * amplitude).toFixed(4)} J · Period: ${((2 * Math.PI) / omega).toFixed(3)} s`;
  const x = oscillator(motion, amplitude, omega).x;
  $("mass").setAttribute("cx", 250 + (x / 3) * 170);
  $("spring").setAttribute("x2", 250 + (x / 3) * 170);
  $("motion-time").textContent =
    `t = ${motion.toFixed(2)} s · x = ${x.toFixed(3)} m`;
}
function frame(timestamp) {
  if (timestamp - lastFrame > 70) {
    if (!motionPaused && !$("physics").hidden && !document.hidden) {
      motion = (motion + (timestamp - lastFrame) / 1000) % 10;
      updatePhysics();
    }
    lastFrame = timestamp;
  }
  requestAnimationFrame(frame);
}
function updateInformation() {
  const p = Number($("probability").value);
  $("probability-value").value = p.toFixed(2);
  $("entropy-value").textContent = `${binaryEntropy(p).toFixed(4)} bits`;
  $("entropy-chart").replaceChildren(
    lineChart(
      [
        {
          points: Array.from({ length: 101 }, (_, i) => ({
            x: i / 100,
            y: binaryEntropy(i / 100),
          })),
        },
      ],
      {
        xlabel: "Probability of 1",
        ylabel: "Entropy (bits)",
        point: { x: p, y: binaryEntropy(p) },
      },
    ),
  );
  $("prob-zero").style.width = `${(1 - p) * 100}%`;
  $("prob-one").style.width = `${p * 100}%`;
  $("prob-label").textContent =
    `P(0) = ${(1 - p).toFixed(2)} · P(1) = ${p.toFixed(2)}`;
}
async function init() {
  setRoute();
  window.addEventListener("hashchange", setRoute);
  $("controls").addEventListener("submit", (e) => e.preventDefault());
  $("rule").addEventListener("change", () => {
    stopPlay();
    render();
  });
  $("generation").addEventListener("input", () => {
    stopPlay();
    render();
  });
  $("depth").addEventListener("change", render);
  $("state").addEventListener("change", () => {
    selected = $("state").value;
    render();
  });
  $("play").addEventListener("click", () => {
    if (playTimer) {
      stopPlay();
      return;
    }
    $("generation").value = 0;
    render();
    $("play").textContent = "Ⅱ Pause";
    playTimer = setInterval(() => {
      const g = Number($("generation").value);
      if (g === 6) {
        stopPlay();
        return;
      }
      $("generation").value = g + 1;
      render();
    }, 1100);
  });
  $("reset").addEventListener("click", () => {
    stopPlay();
    $("rule").value = "zero_split";
    $("generation").value = 3;
    $("depth").value = "none";
    selected = "110100";
    render();
  });
  $("export").addEventListener("click", () => {
    if (!data) return;
    const generation = Number($("generation").value),
      model = getModel(),
      exploration = getExploration(),
      payload = {
        schema_version: 1,
        evidence_type: "COMPUTATIONAL RESULT",
        rule: $("rule").value,
        max_tree_depth: $("rule").value === "zero_split" ? getDepth() : null,
        generation,
        states: exploration.stages[generation].map((w) => model.states[w]),
        transitions: exploration.transitions.filter(
          (e) => e.generation <= generation,
        ),
      };
    const url = URL.createObjectURL(
        new Blob([JSON.stringify(payload, null, 2)], {
          type: "application/json",
        }),
      ),
      link = document.createElement("a");
    link.href = url;
    link.download = `structural-generation-${generation}.json`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  $("share").addEventListener("click", async () => {
    if (!data) return;
    const query = new URLSearchParams({
        rule: $("rule").value,
        generation: $("generation").value,
        state: selected,
        depth: $("depth").value,
      }),
      url = `${location.href.split("#")[0]}#structures?${query}`;
    try {
      await navigator.clipboard.writeText(url);
      $("share").textContent = "Link copied ✓";
      setTimeout(() => ($("share").textContent = "Copy view link ↗"), 1800);
    } catch {
      window.prompt("Copy this view link:", url);
    }
  });
  for (const id of ["omega", "amplitude"])
    $(id).addEventListener("input", updatePhysics);
  $("probability").addEventListener("input", updateInformation);
  $("motion-toggle").addEventListener("click", () => {
    motionPaused = !motionPaused;
    $("motion-toggle").textContent = motionPaused
      ? "▶ Resume motion"
      : "Ⅱ Pause motion";
  });
  $("motion-toggle").textContent = motionPaused
    ? "▶ Resume motion"
    : "Ⅱ Pause motion";
  updatePhysics();
  updateInformation();
  requestAnimationFrame(frame);
  try {
    const response = await fetch("data.json");
    if (!response.ok)
      throw new Error(`Dataset request failed (${response.status})`);
    data = await response.json();
    if (data.schema_version !== 1)
      throw new Error("Unsupported dataset version");
    let saved = null;
    try {
      saved = JSON.parse(localStorage.getItem("research-lab-view") || "null");
    } catch {
      /* No storage permission is required. */
    }
    const params = new URLSearchParams(location.hash.split("?")[1] || ""),
      view = params.size ? Object.fromEntries(params) : saved;
    applyView(view);
    render();
    $("loading").hidden = true;
  } catch (error) {
    $("loading").hidden = true;
    $("error").hidden = false;
    $("error").textContent =
      `The structural dataset could not be loaded. Reload the page or check the site deployment. ${error.message}`;
    for (const id of [
      "rule",
      "generation",
      "depth",
      "state",
      "export",
      "play",
      "share",
    ])
      $(id).disabled = true;
  }
}
init();
