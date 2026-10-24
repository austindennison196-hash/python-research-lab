# Explicit transformation systems

The library provides separate systems and a bounded state-space explorer. Choose a rule by name; never infer equivalence from similar first examples.

## Candidate A: `zero_split`

**DEFINITION.** Start at the special seed `0`. Its only successor is `10`. On every subsequent step replace exactly one selected `0` by `100`; every eligible position is explored. Deduplicate equal resulting words within each generation while retaining transition records.

For example:

```text
0 -> 10
10 -> 1100
1100 -> 111000   (replace the first zero)
1100 -> 110100   (replace the second zero)
```

For nonseed words this rewrite increases both the one count and the zero count by one. It is therefore consistent with balanced examples. It interprets “introducing a distinction creates an additional zero” as a **net** change: the selected zero becomes one distinction and two zeros. The seed step has a different zero-count change, which remains an explicit exception.

In the ordered-tree encoding, replacing the closing zero of a node with `100` appends a new leaf to that node. Thus every existing zero has an operational role, including zeros belonging to nonleaf nodes. This is a mathematical candidate for the proposed process, not a claim that every intended semantic meaning has been captured.

## Candidate B: `zero_occupancy`

Replace one selected `0` by `10`, including the seed. This is a literal consume-and-replace reading. It reaches `10` but then reaches `110`, not `1100`. Each nonseed step adds one one and no net zeros, so this candidate fails the supplied second transition. It remains useful as an explicitly labeled alternative and as a counterexample to the claim that the semantic sentence alone determines the balanced process.

## Candidate C: `dyck_insertion`

After the special seed step, insert `10` into any gap of a word. This generates the full standard Dyck family, including `1010` already at generation 2. It reproduces the listed examples but also produces additional states. Agreement on selected examples therefore does not establish equality of state spaces.

## Independent standard modes

`dyck_words(n)` generates standard Dyck words with n pairs. `ordered_trees(n)` generates rooted ordered trees with n nodes. Under the documented tree encoding, ordered trees correspond to **primitive** Dyck words, not to all Dyck words of the same size. Full Dyck words instead encode ordered forests, or ordered trees when one adds a virtual root and shifts size.

## Custom rules and constraints

The engine supports configurable local replacements and bounded exploration. A new rule needs a name, a precise eligible-position definition, a seed treatment, and domain checks. Apply size and state-count bounds before exponential enumeration. Stabilization can be studied as a filter on allowed successors, but choosing the filter is an additional modeling assumption.

Specify whether constraints are checked after every rewrite or only at the final generation: those experiments need not have the same reachability. Likewise, deduplicated states, edges with positions, and full histories count different objects.
