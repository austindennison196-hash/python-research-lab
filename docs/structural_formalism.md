# A candidate formalization of the structural examples

## The user's observations and notation

The supplied examples are preserved literally:

| Generation | Binary | Structural notation |
| --- | --- | --- |
| 0 | `0` | `x` |
| 1 | `10` | `(x)` |
| 2 | `1100` | `((x)x)` |
| 3 | `111000` | `(((x)x)x)` |
| 3 | `110100` | `((x)(x)x)` |

These examples alone do not determine a unique transformation rule, a
probability distribution, a physical interpretation, or an encoding at every
future generation. In particular, replacing `0` with `10` gives `110`, not
`1100`. The number of zeros is unchanged by that literal replacement.
Replacing `0` with `100` adds one zero and one one, but would map the seed to
`100`, not `10`. A seed convention is therefore necessary for the candidate
below. This is a modeling choice, not a correction to the user's notation.

## DEFINITION: zero splitting (candidate rule)

Generation zero is the exceptional potential state `0`. Its only successor is
`10`. After this first step, select any existing `0` and replace it with `100`.
Deduplicate equal words within a generation, while retaining all edited
positions in the transition history. This is implemented as `zero_split`.

Selecting the two zeros of `1100` produces `111000` and `110100` respectively.
Thus this rule fits every supplied example without establishing that it is
the user's uniquely intended rule.

## DEFINITION: candidate notation grammar and tree encoding

The seed is `x`. A nonseed node has the recursive grammar

```text
node := '(' node* 'x)'
```

A node has an ordered list of children; every node has exactly one final `x`.
The `x` marker is a syntactic marker for potential in this encoding, not an
extra tree vertex. Encode a node by `1`, then encode its children in order,
then write `0`. This maps each nonempty rooted ordered tree to a primitive
Dyck word (a balanced word with no earlier return to zero balance). Encode
its notation as `(`, followed by child notations, followed by `x)`.

The binary seed `0` is not a balanced word or a nonempty tree. It is handled
separately and never counted as a standard Dyck word.

## THEOREM: language and counts for this candidate

At positive generation n the zero-splitting words are exactly the primitive
Dyck words with n pairs. Consequently there are C_(n-1) distinct states,
where C_k = binomial(2k,k)/(k+1), and each corresponding tree has n nodes.

Proof. At n=1, the only word is `10`, the encoding of the singleton root.
Replacing a node's closing `0` with `100` appends a new leaf as its last child;
it preserves one root, order, balanced prefixes, and primitiveness. Thus all
generated words encode rooted ordered trees. Conversely, any ordered tree
with at least two nodes has a deepest parent of leaves. Its last child is a
leaf. Delete that leaf to obtain a tree one node smaller; appending it again
is exactly one permitted zero split. Induction therefore reaches every
ordered tree of n nodes. Removing the first `1` and last `0` of a primitive
word is a bijection to ordinary Dyck words of n-1 pairs. The established
Catalan count for ordinary Dyck words follows, for example, by subtracting
bad paths via the reflection bijection:
C_k = binomial(2k,k) - binomial(2k,k+1). This proves the stated count. ∎

This theorem applies to the explicit candidate definition. It does not
prove a claim about physical emergence or the original informal hypothesis.

## DEFINITION: separate comparison systems

- `dyck_words(n)` enumerates all standard Dyck words with n pairs, including
  words such as `1010`. Its count is C_n. The empty word is its n=0 object.
- `ordered_trees(n)` enumerates trees with n **nodes**, counted by C_(n-1).
  Counting n **edges** instead gives C_n; index conventions matter.
- `dyck_insertion` first maps the exceptional seed to `10`, then inserts `10`
  at every binary word boundary. It generates the full Dyck language because
  each nonempty Dyck word has a removable adjacent `10` peak. It already
  permits the additional state `1010` at generation 2.
- `zero_occupancy` replaces a zero by `10` even at the seed. It gives
  `0 → 10 → 110 → 1110`, so does not reproduce the supplied second step.
- A custom `Rule` may restrict edits to, for example, the leftmost zero.
  Such restrictions represent stabilization constraints. They are explicit
  models; whether they are useful physical models remains unestablished.

## Metrics and computational evidence

`metrics` measures counts, prefix balances, height, leaf count, bigram
variety, and marginal symbol entropy. All balanced binary words have the
same marginal entropy of one bit, regardless of tree shape. This statistic
cannot establish structural or algorithmic complexity. `discover_invariants`
reports only empirically constant metrics over its sample, tagged
COMPUTATIONAL RESULT; it does not automatically infer a theorem.

Tests compare generation results with independent exhaustive binary-word
checks and standard Catalan counts at finite sizes. These tests can reveal
implementation errors but are not replacements for the proof above.

## Open questions and physical limitations

Is a distinction a new vertex, an occupied space, or an operation on an
existing space? Does the new zero count as a replacement or an additional
site? Are sibling order and histories distinguishable? Are all zero sites
eligible, and how are probabilities assigned? What is stabilization: a
forbidden edit, a weighted preference, a conserved quantity, or dynamics?
These choices lead to different state spaces.

A connection to physics requires a measurable interpretation of states,
units, dynamics, a correspondence to established measurements, falsifiable
predictions, and independent evidence. None is supplied by counting trees.
