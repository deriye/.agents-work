# Playground

A personal space for learning, notes, and hands-on experiments. Two pillars:

- **`knowledge/`** — theory organized by domain (`ai`, `cs`, `math`). This is the curated, structured side.
- **`tools/`** — practical scaffolds per tool (`cordis`, `graphify`, `multica`, `qt`, `uv`), each with its own tutorials and sandboxes.

---

## Layout

```
playground/
  README.md                 # this file — the map and the rules
  knowledge/
    README.md               # (optional) top-level knowledge index
    <domain>/               # ai | cs | math
      README.md             # index of the domain's topics
      <topic>/              # e.g. agent-harness, algorithms, foundations
        README.md           # what this topic is + links to its buckets
        explanations/       # concepts, background, the "why"
        tutorials/          # learning-oriented, sequential lessons
        how-tos/            # task recipes for a specific goal
        references/         # facts, APIs, cheatsheets
        projects/           # runnable projects for this topic (your own or cloned)
  tools/
    <tool>/                 # one folder per tool
      tutorials/            # hands-on guides
      explanations/         # optional background
```

Depth is flexible: a large topic (like `cs/algorithms`) may add a **sub-topic** level
(`algorithms/dijkstra/`) before the buckets. A small topic may skip buckets entirely and just hold notes.

---

## The Diátaxis buckets

Documentation is split by *purpose*, following [Diátaxis](https://diataxis.fr/). Use plural folder names,
and **only create the buckets a topic actually needs** — no empty placeholders.

| Bucket | Purpose | Answers |
|--------|---------|---------|
| `tutorials/` | Learning by doing | "Teach me, step by step." |
| `how-tos/` | Achieving a goal | "How do I accomplish X?" |
| `references/` | Looking things up | "What is the exact signature / value?" |
| `explanations/` | Understanding | "Why does this work? What are the trade-offs?" |

Beyond the four Diátaxis buckets, two code buckets keep runnable material out of the notes:

| Bucket | Purpose | Holds |
|--------|---------|-------|
| `projects/` | One coherent, self-contained thing | Scratch apps you build, or cloned repos you study. Origin-agnostic. |
| `practice/` | Loose drills and exercises | Many small single-file programs (e.g. `practice/io/`, `practice/problems/`). Not coherent projects. |

The rule of thumb: **nothing runnable floats at a topic root.** If it's one whole thing, it's a `project/`.
If it's a pile of little exercises, it's `practice/`. A topic root should show only its `README.md` and the
buckets it needs — no stray source files.

---

## Naming conventions

- **Folders: kebab-case, no spaces, no apostrophes.**
  `agent-harness/`, `stable-matching/`, `low-level-programming/`.
- **No `N. ` prefixes on folders.** Use zero-padded numeric prefixes instead: `01-clock-module/`.
- **Numbered note *files* are fine and encouraged** where reading order matters:
  `01-linear-algebra.md`, `02-calculus.md`.
- **One concept per folder** where practical (e.g. each OOP pattern, each algorithm).

---

## Every folder gets a README

Each domain, section, and topic folder has a `README.md` that acts as an **index** — even a single table is
enough. This is what makes the tree navigable and tells future-you exactly where a new note belongs.

**When adding something new:**
1. Find or create the right `<domain>/<topic>/` folder (kebab-case).
2. Drop the content in the correct bucket (`explanations/`, `tutorials/`, `how-tos/`, `references/`) or `projects/`.
3. Add a one-line entry to that folder's `README.md` index.

---

## Projects and practice

Anything runnable and self-contained — scratch apps you build and third-party repos you clone for study —
lives under its topic's `projects/` folder, e.g. `ai/agent-harness/projects/pi`,
`ai/rag/projects/page-index`, or `cs/low-level-programming/projects/basekernel`.

Loose drills and exercises — many tiny single-file programs — go under `practice/` instead, e.g.
`languages/c/practice/io/` and `languages/c/practice/problems/`. They aren't coherent projects, but grouping
them under one bucket keeps them from cluttering the topic root.

**Projects vs. practice vs. docs.** A *project* is one coherent thing (→ `projects/`). A *drill* is a small
throwaway exercise (→ `practice/`). A single-file conceptual note (e.g. `oop/adapter/README.md`) is
documentation, not code. The invariant: **no runnable source floats at a topic root.**

**Build artifacts are never committed.** Compiled output (`*.exe`, `*.o`, `*.out`, `__pycache__/`) and
generated build directories are git-ignored; only source belongs in the repo. Large clones you don't intend
to version can also be added to `.gitignore`.

Current ignore rules (`.gitignore`): `node_modules`, `.venv`, `.env`, `*.exe`, `*.out`, `*.o`, `*.obj`,
`__pycache__/`.

---

## Domains at a glance

| Domain | Focus |
|--------|-------|
| [`knowledge/ai`](./knowledge/ai/) | Agent harnesses, RAG. |
| [`knowledge/cs`](./knowledge/cs/) | Algorithms, computer engineering, data structures, low-level programming, networks, programming languages. |
| [`knowledge/math`](./knowledge/math/) | Foundations: linear algebra, calculus, statistics, probability, discrete math. |
