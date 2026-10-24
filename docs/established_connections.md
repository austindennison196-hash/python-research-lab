# Connections to established mathematics

This document concerns the explicit candidate definitions implemented in the
laboratory. The original interpretation of `0` as potential and `1` as
distinction is preserved as research motivation. An encoding into an existing
mathematical object establishes properties of the chosen definition, not a
physical interpretation or the uniqueness of that definition.

## Formal languages, grammars, and automata

**DEFINITION.** The standard one-type Dyck language D consists of binary words
with equal numbers of `1` and `0` and nonnegative prefix balance, taking `1`
as an opening parenthesis. A context-free grammar is

```text
S → 1 S 0 S | ε
```

A counter or pushdown automaton recognizes D: increase stack depth for `1`,
decrease it for `0`, reject an attempted decrease below zero, and accept
only at depth zero. The balanced-prefix test used by `is_dyck` implements
this recognition criterion. For one bracket type it needs only a depth
counter rather than distinct stack symbols.

**THEOREM (standard).** D is not regular. If it were regular, its intersection
with the regular language `1*0*` would be regular. That intersection is
`{1^n 0^n : n ≥ 0}`, a standard nonregular language (by the pumping lemma).
This is a statement about the unbounded language; every finite subset used
in a bounded experiment is itself regular.

**DEFINITION (candidate).** Nonseed structural notation uses
`N → ( L x )`, `L → N L | ε`. Its `x` is a terminal marker, and child order
is retained. Erasing these markers and replacing parentheses by `1` and `0`
yields a primitive Dyck word. The seed `x ↔ 0` remains an explicit exception:
erasing the `x` of the seed would give the empty word, not the literal `0`.
The candidate nonseed grammar is not an independently derived meaning of
the user's notation; it extends the supplied examples consistently.

## Combinatorics and trees: the index matters

**THEOREM (standard).** Dyck words of n pairs are counted by
C_n = binomial(2n,n)/(n+1). They are in bijection with rooted ordered trees of
n edges, hence n+1 vertices, by interpreting the word as a contour walk from
an implicit root. The empty Dyck word corresponds to the one-vertex tree.

The laboratory's explicit-node encoding instead writes `1` on entering the
root and `0` on leaving it. It maps an n-node tree to a **primitive** word of
n pairs. Removing its exterior symbols gives an ordinary Dyck word of n−1
pairs. Thus `ordered_trees(n)` counts C_(n−1), while `dyck_words(n)` counts
C_n. They differ in their arguments' meanings, even though both use Catalan
numbers. `1010` is a full Dyck word but is not primitive and is not one
explicit-root tree under this encoding.

The proof in [structural_formalism.md](structural_formalism.md) shows that
candidate zero splitting reaches every ordered tree at its corresponding
node count. It proves an equivalence for that rule, not for every possible
rule compatible with the first few examples. Classical full binary trees,
triangulations, and many other objects also have Catalan counts; identical
counts alone do not identify objects or provide an encoding between them.

Catalan growth C_n ~ 4^n / (sqrt(π) n^(3/2)) explains why enumeration quickly
becomes expensive. The engine bounds retained states and transitions rather
than relying on available RAM. Those caps do not sandbox arbitrary custom
Python callbacks or limit the byte length of a user-defined state.

## Information and complexity measures

**DEFINITION.** Marginal symbol entropy is
H = −p(0) log₂ p(0) − p(1) log₂ p(1), using empirical symbol frequencies.
All nonempty balanced binary words have H = 1 bit per symbol. This measure
ignores ordering: `111000` and `110100` therefore have the same marginal
entropy despite different tree heights and leaf counts.

Bigram counts, tree height, and leaf count describe other features; none is
a complete measure of structural complexity. `log₂ |S_n|` is the Shannon
entropy of a **uniform** distribution on a finite stage S_n, not the entropy
of an unspecified growth process. Uniformly choosing an edit can induce a
nonuniform distribution on deduplicated states because histories can merge.
A random process requires an explicit probability rule, including how edit
multiplicities are treated.

Algorithmic (Kolmogorov) complexity concerns shortest descriptions relative
to a specified universal machine. It is uncomputable in general and is not
calculated by these metrics. Finite empirical constancy is reported as a
COMPUTATIONAL RESULT and never automatically upgraded to a theorem.

## Discrete dynamics, graph constraints, and stabilization

A state-transition graph has structures as vertices and permitted rewrites
as directed edges. All built-in rules increase word length; their unbounded
state graphs are acyclic. In a finite exploration, vertices are additionally
indexed by generation. A general custom rule can contain cycles even though
its generation-indexed unfolding is layered.

**THEOREM (elementary).** With the same seed, deleting allowed edges cannot
increase the reachable set at a fixed number of steps. Every constrained
path is also an unconstrained path. This elementary inclusion supports
studying stabilization as an explicit restriction on transformations.
It does not imply physical stability, equilibrium, or an attractor.

A state-space constraint, a transition probability, an energy function, and
a physical time evolution are different additional structures. A bounded
height constraint, for example, defines a smaller combinatorial state space;
its physical interpretation would need independent motivation and tests.
Evidence of new global statistics in a recursive process is a computational
observation until a claim, assumptions, and a proof or an empirical test are
specified.

## Established references

These references support the standard connections above. None validates
speculative claims about the origin of physical law.

- Richard P. Stanley, *Catalan Numbers*, Cambridge University Press, 2015:
  Catalan families, Dyck paths, and tree correspondences.
- Philippe Flajolet and Robert Sedgewick, *Analytic Combinatorics*, Cambridge
  University Press, 2009: recursive combinatorial specifications and growth.
- Michael Sipser, *Introduction to the Theory of Computation*, third edition:
  regular languages, pumping lemmas, context-free languages, and pushdown
  automata.
- Thomas M. Cover and Joy A. Thomas, *Elements of Information Theory*, second
  edition, Wiley, 2006: entropy and probability models.
- Ming Li and Paul Vitányi, *An Introduction to Kolmogorov Complexity and Its
  Applications*, fourth edition, Springer, 2019: algorithmic complexity and
  its limitations.
