# Structural logic: definitions and original notation

## The proposed interpretation

The originator uses `0` for potential, space, or an initially undefined state, and `1` for a distinction, occupancy, or introduced structure. The relationships `0 ← 1` and `1 → 0` express occupancy and subsequent potential. These semantic interpretations motivate the investigation; they do not by themselves define a string rewriting system.

The literal examples are retained:

| Generation | Binary | Original parentheses notation |
| --- | --- | --- |
| 0 | `0` | `x` |
| 1 | `10` | `(x)` |
| 2 | `1100` | `((x)x)` |
| 3 | `111000` | `(((x)x)x)` |
| 3 | `110100` | `((x)(x)x)` |

The arrows are `0 → 10 → 1100 → 111000` or `0 → 10 → 1100 → 110100`, and the corresponding parentheses histories are `x → (x) → ((x)x) → (((x)x)x)` or `x → (x) → ((x)x) → ((x)(x)x)`.

## Formal choices made by the implementation

**DEFINITION — binary word.** A finite string over `{0,1}`. The initial word `0` is a distinguished seed. After the first step, the candidate `zero_split` mode uses balanced words with positive prefix balance, where `1` contributes `+1` and `0` contributes `−1`.

**DEFINITION — Dyck word.** A word with equal counts of `1` and `0`, whose every prefix has at least as many `1`s as `0`s. The empty word is allowed in the standard Dyck family.

**DEFINITION — primitive Dyck word.** A nonempty Dyck word whose proper nonempty prefixes have strictly positive balance. Thus `10` and `1100` are primitive, but `1010` is not. This restriction is a candidate-model choice; it is not implicit in the original semantic statements.

**DEFINITION — rooted ordered tree.** A root with a finite ordered tuple of child trees. Encode a node as `1`, followed by the encodings of its children, followed by `0`. A tree with n nodes is therefore encoded by a primitive Dyck word of length 2n.

**DEFINITION — original-style notation extension.** Write a node as `(`, then each child representation in order, then `x)`. The distinguished seed is written `x`. This gives exactly the five original correspondences. In particular, merely deleting every `x` would not produce the binary notation; the extension uses the tree structure, not a characterwise substitution. The extension is documented as a chosen grammar, rather than claiming the five examples uniquely imply it.

Tree isomorphism here preserves the root and child order. Forgetting order or treating words as cyclic objects creates different equivalence classes and different counts. Neither change is made silently.

## Required unresolved choices

1. Does introducing a distinction consume the selected zero, preserve it, or introduce one or two zero symbols?
2. Is the seed an exception to subsequent transformations? The seed has one zero and no one, while the first nonseed has one of each.
3. Is a step exactly one local rewrite, or may it differentiate several places at once?
4. Are all existing zeros eligible, including closing positions associated with internal nodes?
5. Are sibling order, nesting, and different generation histories observable distinctions?
6. Does stabilization restrict depth, branching, balance, some metric, or probability?

These questions are inputs for research. The implementation exposes candidate rules so they can be investigated rather than concealed in a single convention.
