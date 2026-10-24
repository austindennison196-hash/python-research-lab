import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import {
  ancestors,
  binaryEntropy,
  catalan,
  constrain,
  oscillator,
} from "../web/model.mjs";
const data = JSON.parse(
  await readFile(new URL("../dist/site/data.json", import.meta.url)),
);

test("Python-engine browser dataset preserves exact examples and independent Catalan counts", () => {
  assert.deepEqual(data.examples, {
    0: "x",
    10: "(x)",
    1100: "((x)x)",
    111000: "(((x)x)x)",
    110100: "((x)(x)x)",
  });
  assert.deepEqual(data.models.zero_split.exploration.stages[3], [
    "110100",
    "111000",
  ]);
  assert.deepEqual(
    data.models.zero_split.exploration.stages.map((s) => s.length),
    [1, 1, 1, 2, 5, 14, 42],
  );
  assert.deepEqual(
    data.models.dyck_insertion.exploration.stages.map((s) => s.length),
    [1, 1, 2, 5, 14, 42, 132],
  );
  for (const [word, notation] of Object.entries(data.examples))
    assert.equal(data.models.zero_split.states[word].notation, notation);
  assert.deepEqual(
    Array.from({ length: 7 }, (_, n) => catalan(n)),
    [1, 1, 2, 5, 14, 42, 132],
  );
});
test("depth constraint filters reachable paths, including extinction and surviving stars", () => {
  const model = data.models.zero_split;
  assert.deepEqual(constrain(model, 0).stages, [
    ["0"],
    ["10"],
    [],
    [],
    [],
    [],
    [],
  ]);
  const stars = constrain(model, 1);
  assert.ok(stars.stages.every((s) => s.length === 1));
  assert.deepEqual(stars.stages[3], ["110100"]);
  for (const e of stars.transitions) {
    assert.ok(stars.stages[e.generation - 1].includes(e.parent));
    assert.ok(stars.stages[e.generation].includes(e.child));
  }
  const lineage = ancestors(model.exploration, 3, "111000");
  assert.deepEqual([...lineage].sort(), ["0:0", "1:10", "2:1100", "3:111000"]);
});
test("entropy has correct limits, symmetry and nontrivial reference value", () => {
  assert.equal(binaryEntropy(0), 0);
  assert.equal(binaryEntropy(1), 0);
  assert.equal(binaryEntropy(0.5), 1);
  assert.ok(Math.abs(binaryEntropy(0.25) - 0.8112781244591328) < 1e-14);
  assert.ok(Math.abs(binaryEntropy(0.1) - binaryEntropy(0.9)) < 1e-14);
  assert.throws(() => binaryEntropy(-0.1), RangeError);
  assert.throws(() => binaryEntropy(NaN), RangeError);
});
test("oscillator conserves energy and returns the known quarter-period state", () => {
  const omega = 2,
    amplitude = 3;
  const q = oscillator(Math.PI / (2 * omega), amplitude, omega);
  assert.ok(Math.abs(q.x) < 1e-14);
  assert.ok(Math.abs(q.v + 6) < 1e-14);
  for (let t = 0; t < 10; t += 0.03)
    assert.ok(Math.abs(oscillator(t, amplitude, omega).energy - 18) < 1e-12);
  assert.throws(() => oscillator(1, 1, 0), RangeError);
});
