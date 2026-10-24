/** Small browser models. Structural enumerations themselves come from Python. */
export function catalan(n) {
  let c = 1;
  for (let k = 0; k < n; k++) c = (c * 2 * (2 * k + 1)) / (k + 2);
  return Math.round(c);
}
export function binaryEntropy(p) {
  if (!Number.isFinite(p) || p < 0 || p > 1)
    throw new RangeError("Probability must lie in [0,1].");
  return p === 0 || p === 1
    ? 0
    : -p * Math.log2(p) - (1 - p) * Math.log2(1 - p);
}
export function oscillator(t, amplitude, omega) {
  if (![t, amplitude, omega].every(Number.isFinite) || omega <= 0)
    throw new RangeError("Use finite inputs and positive angular frequency.");
  const x = amplitude * Math.cos(omega * t),
    v = -amplitude * omega * Math.sin(omega * t);
  return { t, x, v, energy: 0.5 * (v * v + omega * omega * x * x) };
}
export function constrain(model, maxDepth = null) {
  if (maxDepth === null) return model.exploration;
  const stages = [["0"]],
    transitions = [];
  for (let g = 1; g < model.exploration.stages.length; g++) {
    const parents = new Set(stages[g - 1]);
    const edges = model.exploration.transitions.filter(
      (e) =>
        e.generation === g &&
        parents.has(e.parent) &&
        model.states[e.child].metrics.tree_height !== null &&
        model.states[e.child].metrics.tree_height <= maxDepth,
    );
    transitions.push(...edges);
    stages.push([...new Set(edges.map((e) => e.child))].sort());
  }
  return { stages, transitions, rule: "depth-constrained-zero-split" };
}
export function ancestors(exploration, generation, word) {
  const result = new Set([`${generation}:${word}`]);
  for (let g = generation; g > 0; g--)
    for (const e of exploration.transitions)
      if (e.generation === g && result.has(`${g}:${e.child}`))
        result.add(`${g - 1}:${e.parent}`);
  return result;
}
