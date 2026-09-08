# software-development — Reference

Detailed templates and long-form reference for the `software-development`
skill. The lean `SKILL.md` auto-loads on every code-touching request; this
file is read only when a step needs a template or the full failure-mode
list. References are one level deep from `SKILL.md`.

---

## Folder Layout (full)

### Artifacts directory (user-configurable, overrides `docs/`)

Pipeline artifacts live under an **artifacts directory** that defaults to
`docs/`. The user may override it with any repo-relative directory (e.g.
`documentation/`, `.project/`, `spec/`); that choice replaces `docs/` as the
root for **every** artifact path in this skill and this reference.

- **Where it is chosen:** Step 0 asks once (default `docs/`) and, when the
  choice is non-default, records it in `AGENTS.md` so every later run and
  every agent uses the same directory. If `AGENTS.md` already records one,
  reuse it — do not re-ask.
- **What it covers:** everything written as `docs/…` below —
  `docs/terminology.md`, `docs/features/`, `docs/domain-model/`,
  `docs/logs/`, `docs/architecture/`, `docs/mechanisms/`, and the per-folder
  `index.md` files. Read every `docs/…` path in this file as
  `<artifacts-dir>/…`.
- **What never moves:** `AGENTS.md`, `README.md`, and the gitignored `tmp/`
  stay at the repository root regardless of the artifacts directory.
- **Delegates:** `isdd`, `domain-model`, and any artifact-writing delegate
  must write under `<artifacts-dir>` instead of `docs/`.

The rest of this file uses `docs/` as the concrete default; substitute the
chosen artifacts directory wherever it appears.

All pipeline artifacts live under the artifacts directory (default `docs/`):

```
docs/
  terminology.md          ← single source of truth for vocabulary (Step 3)
  domain-model/
    concepts/
      index.md            ← index + spec→concept map
      <concept>.md        ← abstract recurring patterns
    entities/
      index.md            ← index + entity index + relationships + spec→entity map
      <entity>.md         ← persisted relational database tables
  features/
    <feature>/
      spec.md            ← intent spec (isdd)
      plan.md            ← implementation plan
  logs/
    index.md             ← index of implementation logs
    <feature>.md         ← implementation log (written AFTER implementation)
  architecture/
    index.md             ← index of architectural decisions
    <topic>.md           ← decisions: stack, topology, boundaries, data flow
  mechanisms/
    index.md             ← index of subsystem runtime behaviors
    <mechanism>.md       ← runtime behavior: auth flow, caching, sync, error handling
```

At the repository root (not under `docs/`):

```
AGENTS.md              ← read first (Step 0), review last (Step 12)
README.md              ← project front door (Step 10)
tmp/                   ← gitignored debug/scratch artifacts (outside docs/)
```

- **AGENTS.md** is the first file read (Step 0) and the last re-read (Step 12)
  to verify pipeline compliance.
- **README.md** is the project's public front door, updated in Step 10.
- **Features** live under `docs/features/<feature>/`; **logs** under
  `docs/logs/<feature>.md` (one file per feature, flat); **concepts** and
  **entities** flat under their respective folders.
- **Terminology** lives in a single `docs/terminology.md` (Step 3) — the
  source of truth for vocabulary; concept and entity files link back to
  terms here rather than redefining them.
- Each docs subfolder uses `index.md` (not `README.md`) as its structured
  index. Only the repository root has a `README.md` (and an `AGENTS.md`).
  Index files provide **discoverability** (one file shows the full
  inventory), **traceability** (spec→concept/entity maps), and a
  **consistency check** (a missing entry signals an incomplete model).
  Without them the folder is a pile of files; with them the model and logs
  become a navigable graph.
- Design artifacts (Step 6) go where `huashu-design` specifies — this skill
  does not prescribe their location.
- **Debug/scratch artifacts** must live **outside** `docs/` in a gitignored
  `tmp/` at the repo root. Never put transient artifacts under `docs/`. If
  `tmp/` does not exist, create it and ensure it is in `.gitignore`.
  `AGENTS.md` may note `tmp/` as local scratch so agents do not dump junk
  in `docs/`. **Do not put `tmp/` (or anything gitignored) in README,
  specs, plans, logs, architecture, mechanisms, or terminology.** A clone
  never has those files.

## Committed docs are the product

`README.md`, `docs/`, and `AGENTS.md` describe the software in this
repository: what it is, how to run it, what staff experience, what was
decided. They do not describe how the developer learned to build it.

- **README** — name, purpose, prerequisites, install, run. A fresh clone
  must be able to follow Getting Started. Link to `docs/` for depth.
- **Spec / plan / log / domain model / architecture / mechanisms** —
  the product. After implementation (agent or user), record what shipped
  (files, behavior), not sitting numbers or course paths.
- **Terminology** — product vocabulary. Do not add terms whose only
  purpose is a learning path (unless the developer explicitly asks).
- **Do not** create `docs/features/` for a series of sittings.
- **Do not** link gitignored paths from committed files.

`tmp/` is for the agent and the developer. It is not the front door.

### Architecture vs. Mechanisms

- **Architecture** (`docs/architecture/`) documents **what was decided and
  why** — tech stack, system boundaries, deployment topology, data flow.
  These are foundational decisions that change rarely, only when a core
  choice shifts. Example: "We use JWT with refresh tokens, stateless backend,
  OAuth via provider X, because Y."
- **Mechanisms** (`docs/mechanisms/`) documents **how specific subsystems
  work at runtime** — the step-by-step process of authentication (token
  issue → refresh → expiry → redirect), cache invalidation, sync/conflict
  resolution, error handling. These change more often, whenever a feature
  touches that subsystem.

**Dividing line:** Architecture documents the *decision*; mechanisms document
the *process*. If a doc mixes "we chose X because Y" with "then step 3 does
Z," split it — the decision goes in architecture, the process in mechanisms.
Both get their own `index.md`; mechanisms link to the domain model and list
features that rely on them.

---

## When to Use This Skill (full)

Use this skill for **any** request that touches code — source, config,
styles, assets, build files, or scripts — regardless of the *type* of
change. The nature of the work (feature, bug fix, design polish, theme
toggle, refactor, performance optimization)
does not matter.

**Before this skill is used, the user needs to confirm.** Load the skill
when the request may qualify, then ask. Do not run Step 0 until they
confirm. If they decline, stop.

A few illustrative triggers (not exhaustive):

- "Add a feature that..." · "Build a function/module/service that..."
- "Fix this bug" · "Refactor X" · "Optimize X" · "Change how X works"
- "Improve the design / UI / styling" · "Add light/dark mode / theme toggle"
- Any request to create, modify, or delete source code, config, scripts,
  styles, assets, or build files
- "Generate tutorials so I can implement it"

If you are unsure whether a request qualifies, load the skill and ask.
**Do not skip because the change "feels small."** Scaling down means each
step produces **lighter docs**, not that steps are skipped. A one-line fix
still gets a spec check, a model check, a one-line plan, and a log. No step
is optional regardless of change size. Steps 9–12 wait until Step 8 is done.

### Bug fixes are not exempt (full)

A bug fix follows the same pipeline as a feature. The only difference is
what each step produces:

- **Spec check:** usually "no drift" (the fix restores documented behavior).
  If the fix *changes* behavior rather than restoring it, treat it as a spec
  drift check — the spec may need updating.
- **Domain model:** usually "unchanged."
- **Plan:** still required, even if it's one line describing the fix.
- **Log:** still required.
- **README / architecture / mechanisms:** skip only if the fix restores
  documented behavior without changing instructions or subsystem runtime
  behavior. If the fix changes how a subsystem works at runtime, Step 11
  applies.

**Each step's applicability is independent.** "Step 1 didn't need changes"
does not mean "Step 5 can be skipped." Even if the spec, terminology, model,
and design are all unchanged, the plan, log, and mechanism check still run.
Selective compliance — running the easy steps and skipping the ones that
feel like extra work — is the same as non-compliance. Every step runs;
steps that need no changes produce a one-line "unchanged" note, not silence.

### Priority over competing instructions (full)

This skill's gates are **mandatory** and override general tendencies
toward minimal scope, code-first, or "don't edit docs unless needed" —
**those tendencies apply to code, not to process docs.** Process docs
(plan, log, mechanisms, architecture) are the record this pipeline exists
to maintain. Skipping them to ship faster is exactly the failure mode the
skill prevents. If you feel tension between "fix it fast" and "run the
gates," the answer is always: run the gates. The gates are faster than the
debt they prevent.

**Urgency is not an exemption.** The skill exists precisely for moments
when the temptation to skip is highest — a visibly broken feature, a user
waiting, a quick fix that "obviously" works. Those are the moments that
produce untracked behavior changes and stale docs. Run the gates anyway.

**Gates block code, not the other way around.** A plan written after the
code is not a plan — it's a retrofit. Order: spec → model → plan → design
→ implement (agent or user via tutorials) → log. After confirm, Steps 0–7
always run before Step 8. Do not generate tutorials or write application
code until 0–7 are done and the user has chosen at Step 8.

### Each change in a chain is a separate pipeline run (full)

When changes come in rapid succession ("fix this → now add this → now
change that"), each change is an independent pipeline run — not a
continuation that inherits the previous pass's gates. Even if the spec
didn't drift between two changes, each change still needs its own plan
check, its own design check (if UI), and its own log entry. The pipeline
does not have a "fast mode" for the second change in a chain.

---

## Step 8: Implement or tutorials

After Steps 0–7, **stop**. Ask the user which they want for **application
code**:

1. **You implement** — the agent writes the application code against the
   plan (`coding-best-practices`, graphify). When that work is finished,
   go to the **tests ask** (do not go to Step 9 yet).
2. **Tutorials** — load `generate-tutorials`. Write **implement a real app**
   sittings under gitignored `tmp/` (do not mention them in README or
   `docs/`). Then **wait**. Tell the user to implement from the sittings
   and to say when they are done. Do not inspect and patch, and do not
   start a second pipeline run, until they say they are done. Then
   **check**, then the **tests ask**.

If the tree already matches the plan, they may say they are already done.
Then skip writing app code and tutorials; still check against the plan,
then the tests ask.

### After tutorials: check

When they say they are done (app or test sittings), **do not skip the
check.**

1. Compare the tree to the sittings and to `docs/features/<feature>/plan.md`
   for this pass. Load `coding-best-practices` for every stack in the change (including
   Testing).
2. Run lint / typecheck / tests if those commands exist.
3. **If it matches:** continue (tests ask after app sittings; Step 9 after
   test sittings). The log records what shipped (files, behavior), not
   sitting catalogues.
4. **If it does not:** **STOP.** List gaps against the sittings and the
   plan. Do not patch unless they ask. Do not write the log. Wait until
   they fix it (or ask you to) and say to check again.

“I’m done” means they finished working, not that the sittings are correct.

### Tests ask

After application code is in, **stop** again. Ask whether they want:

1. **You implement** the tests, or
2. **Tutorials** so they implement the tests (`generate-tutorials`, wait,
   check).

Scope is the Step 5 test plan. **Include e2e when possible** (user-visible
flow). If e2e does not apply, say why; still add tests for changed
behavior.

Load `coding-best-practices`. If Testing is missing from the stack file,
research official docs, add a Testing section, then follow it. If the repo
has no runner, adding the recorded tools is part of this step.

When tests pass: `graphify update .` if the CLI is present, then Steps
9–12.

Do not generate tutorials before Step 7 is complete. Do not write
application code or tests before they choose that ask.

---

## Explore with graphify

Graphify maps the repo to `graphify-out/graph.json` so the agent queries a
scoped subgraph instead of dumping files into context.

**Before reading many source files** (plan drift, implement, domain-model):

1. If `graphify-out/graph.json` exists, query it:
   - `graphify query "<question>"` — scoped subgraph (add `--budget 1500`
     to cap tokens)
   - `graphify path "A" "B"` — how two things connect
   - `graphify explain "X"` — one node and neighbors
2. If the graph is missing or stale vs the **code** you care about:
   `graphify .` (first build) or `graphify update .` (re-extract code only;
   no LLM key), then query. On Windows PowerShell use `graphify .` not
   `/graphify .`. `graphify . --update` re-extracts docs/papers/images and
   **needs an API key** — do not use it as the post-code refresh.
3. Then **read only** the files or symbols the graph returned.
4. After Step 8 is done: `graphify update .` so the graph matches the code.

Do not `cat` `graph.json` or `GRAPH_REPORT.md` in full. Do not glob the
whole `src/` tree "to be safe" when a query would do.

If the `graphify` CLI is not installed: **stop and ask once** this
session. Explain that exploration will be slower without it. Ask to
install the CLI as a **machine-level tool**, not a repo dependency:

    uv tool install graphifyy

(PyPI package `graphifyy`; CLI command `graphify`. Alternative:
`pipx install graphifyy`.) Do not `pip install` into the project. Do
not add graphify to `package.json`, lockfiles, `AGENTS.md`, or README.
Do not run `graphify install` (that registers an assistant skill and
may write repo or assistant files).

If they say yes: install, then run `graphify .` and query. If they
decline or the install fails: say so, fall back to ordinary file
tools, and do not ask again this session.

Graphify does not replace gates, confirmation, or `coding-best-practices`.

---

## Behavioral Guidelines (full)

These guidelines reduce common LLM coding mistakes. They operate **within**
the pipeline — they shape how you work at each gate, not whether you run
the gates. "Think before coding" *is* the spec/drift gates; "goal-driven
execution" *is* the plan + test plan; "simplicity" and "surgical changes"
govern the code you write in Step 8. They bias toward caution over speed;
for genuinely trivial tasks, use judgment — but judgment never means
skipping a gate, only producing lighter docs at that gate.

### 1. Think before coding

Don't assume. Don't hide confusion. Surface tradeoffs. Before implementing
(before Step 8, during Steps 1–7):

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

This is what the Intent Drift check (Step 2) and Plan Drift check (Step 7)
enforce structurally; apply the same posture throughout.

### 2. Simplicity first

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.
- Ask: "Would a senior engineer say this is overcomplicated?" If yes,
  simplify.

This applies to the code written in Step 8, within the approach chosen in
the plan (Step 5). If the plan itself is overcomplicated, fix the plan
before implementing.

### 3. Surgical changes

Touch only what you must. Clean up only your own mess. When editing existing
code (Step 8):

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request
and to the plan's scope (Step 5). A change that doesn't trace is scope creep
even if it "improves" the code.

### 4. Goal-driven execution

Define success criteria. Loop until verified. Transform tasks into
verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass."
- "Fix the bug" → "Write a test that reproduces it, then make it pass."
- "Refactor X" → "Ensure tests pass before and after."

For multi-step tasks, the plan (Step 5) should state a brief, verifiable
plan: `[Step] → verify: [check]`. Strong success criteria let you loop
independently. The plan's test section (Step 5) and the log's test section
(Step 9) are where these criteria are recorded and checked.

### Working

These guidelines are working if: fewer unnecessary changes in diffs, fewer
rewrites due to overcomplication, and clarifying questions come before
implementation rather than after mistakes.

---

## Quick Reference: Doc Flow by Phase

| Phase | Docs created/updated | When |
|-------|----------------------|------|
| AGENTS.md (read) | repo root `AGENTS.md`, plus per-agent shims (`CLAUDE.md`, `.cursor/rules`, opencode) pointing at it | **First** — before any work |
| Intent spec | `docs/features/<feature>/spec.md` | Before planning |
| Terminology | `docs/terminology.md` | After spec settled; re-run whenever spec changes, before domain model |
| Domain model | `docs/domain-model/concepts/*`, `docs/domain-model/entities/*`, both `index.md`, spec `## Domain Model` | After terminology; re-run whenever spec changes, before implementing |
| Implementation plan | `docs/features/<feature>/plan.md` | After model, before code |
| Design | (location determined by `huashu-design` skill) | Before code, UI/UX only |
| Implementation log | `docs/logs/<feature>.md`, `docs/logs/index.md` | **After** implementation |
| Repo README | repo root `README.md` (and per-package READMEs in monorepos) | **After** implementation, if user/setup-facing change |
| Architecture | `docs/architecture/<topic>.md`, `docs/architecture/index.md` | **After** implementation, if a foundational decision changed |
| Mechanisms | `docs/mechanisms/<mechanism>.md`, `docs/mechanisms/index.md` | **After** implementation, if a subsystem's runtime behavior changed |
| AGENTS.md review | repo root `AGENTS.md` (re-read) | **Last** — after all steps, verify compliance |

---

## Step 0: AGENTS.md template

```markdown
# AGENTS.md

**Read this file first before starting any work in this repository.**

## Development Pipeline

Code changes in this repository go through these gates. The record lives
in the files named below — not in an agent skill.

**Artifacts directory:** pipeline artifacts live under `<artifacts-dir>/`
(default `docs/`; state the chosen directory here if different). Paths below
are relative to it. `AGENTS.md`, `README.md`, and `tmp/` stay at the repo
root.

0. AGENTS.md (this file) — read first
1. Intent spec — `<artifacts-dir>/features/<feature>/spec.md`
2. Intent drift — confirm with the developer before updating the spec
3. Terminology — `<artifacts-dir>/terminology.md` (source of truth for vocabulary)
4. Domain model — `<artifacts-dir>/domain-model/`
5. Implementation plan — `<artifacts-dir>/features/<feature>/plan.md`
6. Design — UI/UX only; before implementation
7. Plan drift — update the plan before implementing
8. Implement
9. Log — after implementation (`<artifacts-dir>/logs/<feature>.md`)
10. Repo README — after implementation, if user-facing
11. Architecture and mechanisms — after implementation, if applicable
12. AGENTS.md review — re-read this file to verify compliance

## Key Rules

- **Gates block code.** Plans precede code; logs follow it. No exceptions.
- **Each change is a separate pipeline run.** Chains of rapid changes
  don't inherit gates.
- **Bug fixes are not exempt.** Same pipeline, lighter docs.
- **Tests required for changed behavior**, including e2e when a user-visible flow exists.
- **Terminology is the source of truth for vocabulary.** Docs and code must
  not contradict `docs/terminology.md`; when they conflict, terminology wins.
- **Never change terminology without developer approval.** Do not add,
  rewrite, remap, or delete terms in `docs/terminology.md` without checking
  with the developer first. Ask when a term is missing or ambiguous.
- **English code and docs.** Code (identifiers, comments, file names) and
  documentation are English. Exceptions: user-visible UI copy, and proper
  names as written in `docs/terminology.md` (do not translate an
  organisation’s name). When a document describes the screen, quote the UI;
  do not write the surrounding prose in another language.
- **Never use git tools unless the developer has asked explicitly.** Do not
  run git status, diff, add, commit, restore, branch, push, or any other git
  command unless the developer's message clearly requests that action.
- **Each step's applicability is independent.** "Step 1 didn't need
  changes" does not mean "Step 5 can be skipped."
- **Artifacts directory.** Pipeline artifacts live under `<artifacts-dir>/`
  (default `docs/`). Use the directory recorded above for every artifact
  path; do not scatter them elsewhere. `AGENTS.md`, `README.md`, and `tmp/`
  stay at the repo root.

## Behavioral Guidelines

These reduce common LLM coding mistakes. They operate **within** the
pipeline — they shape how you work at each gate, not whether you run the
gates. Bias toward caution over speed; for genuinely trivial tasks, use
judgment — but judgment never means skipping a gate.

1. **Think before coding.** Don't assume; don't hide confusion. State
   assumptions explicitly. If multiple interpretations exist, present them —
   don't pick silently. If a simpler approach exists, say so. If something
   is unclear, stop, name what's confusing, and ask. (This is what Steps 2
   and 7 enforce structurally.)
2. **Simplicity first.** Minimum code that solves the problem. No features
   beyond what was asked; no abstractions for single-use code; no
   unrequested "flexibility"; no error handling for impossible scenarios.
   If 200 lines could be 50, rewrite. If a senior engineer would call it
   overcomplicated, simplify. Applies to code in Step 8 and to the plan in
   Step 5.
3. **Surgical changes.** Touch only what you must; clean up only your own
   mess. Don't "improve" adjacent code, comments, or formatting. Don't
   refactor what isn't broken. Match existing style. Mention unrelated dead
   code — don't delete it. Remove only the orphans your own changes created.
   Every changed line must trace to the user's request and the plan's scope.
4. **Goal-driven execution.** Define success criteria; loop until verified.
   "Add validation" → write tests for invalid inputs, then make them pass.
   "Fix the bug" → write a test that reproduces it, then make it pass.
   "Refactor X" → ensure tests pass before and after. State a brief,
   verifiable plan (Step → verify: check). Record criteria in the plan's
   test section (Step 5) and check them in the log (Step 9).

These are working if: fewer unnecessary changes in diffs, fewer rewrites
from overcomplication, and clarifying questions come before implementation
rather than after mistakes.

## Doc Layout

Artifacts live under `<artifacts-dir>/` (default `docs/`; if this repo uses a
different directory, state it here):

\`\`\`
<artifacts-dir>/          ← default: docs/
  terminology.md          ← source of truth for vocabulary
  features/<feature>/    ← spec.md, plan.md
  domain-model/concepts/  ← concept .md files + index.md
  domain-model/entities/  ← entity .md files + index.md
  logs/                   ← <feature>.md logs + index.md
  architecture/           ← decision docs + index.md
  mechanisms/             ← runtime behavior docs + index.md
\`\`\`
tmp/                      ← gitignored debug/scratch artifacts (outside the artifacts dir)

## As the Last Step

After creating a todo list or implementing tasks, re-read this file to
verify your work complies with the pipeline above. If you skipped any
gate, go back and run it before considering the work complete.
```

### If AGENTS.md already exists

Read it first. Then check whether it documents the **process** (spec, plan,
log, `docs/` layout) — not whether it names this skill.

**If it does NOT mention the pipeline:**

- **Do not overwrite the existing content.**
- **Append or merge** the process section from the template above
  (Steps 0–12 as files, key rules, doc layout, read first / review last).
- **Do not** add this skill's name, delegates, graphify, confirm-before-use,
  or the Step 8 asks.
- If the existing AGENTS.md has a conflicting workflow, **flag the conflict
  to the user**. Do not silently replace one workflow with another.

**If it already documents the pipeline:**

- If it names this skill or its delegates, rewrite those lines to artifacts
  and rules. Do not re-inject skill names.
- Verify per-agent shims point at `AGENTS.md` and do not name this skill.
- Then proceed to Step 1.

**If AGENTS.md exists but is empty or boilerplate:**

- Replace it with the template content above.

### Per-agent instruction files (CLAUDE.md, .cursor/rules, opencode, Codex)

`AGENTS.md` is the **canonical** entry point. Per-agent files are **thin
shims** that redirect to `AGENTS.md`. They do **not** duplicate the
pipeline and do **not** name this skill.

When you create or update `AGENTS.md` (this step), also ensure the
per-agent shims exist and point at it:

| File | Agent | Purpose |
|------|-------|---------|
| `AGENTS.md` | All (Cursor, Claude Code, Codex, opencode) | Canonical process |
| `CLAUDE.md` | Claude Code | Thin pointer → `AGENTS.md` |
| `.cursor/rules/pipeline.mdc` (`alwaysApply: true`) | Cursor | Thin pointer → `AGENTS.md` |
| `.opencode/opencode.json` or `.opencode/AGENTS.md` | opencode | Thin pointer → `AGENTS.md` |
| Codex instructions (if a separate file exists; otherwise `AGENTS.md` covers it) | Codex | Thin pointer → `AGENTS.md` |

If a shim still lives at `.cursor/rules/software-development.mdc`, replace
it with `pipeline.mdc` (same body, no skill name) and remove the old file.

#### Shim template

Each shim is the same short content, adjusted for the agent's format. For a
markdown shim (`CLAUDE.md`, `.opencode/AGENTS.md`):

```markdown
<!-- Thin shim. Canonical source: AGENTS.md. Do not duplicate the pipeline
here — keep this file a pointer only, or it will go stale. -->

# Follow the development pipeline

This repository has a gated development pipeline. **Read `AGENTS.md` first**
— it is the source of truth for the steps, key rules, behavioral
guidelines, and doc layout.

Do not skip the pipeline because a change "feels small" or is a bug fix
— bug fixes are not exempt. A one-line fix still gets a spec check, a
one-line plan, and a log. Gates block code; terminology wins. Never change
`docs/terminology.md` without developer approval. Never use git tools unless
the developer has asked explicitly.
```

For a Cursor `.mdc` rule, add frontmatter:

```yaml
---
description: Follow this repository's development pipeline
alwaysApply: true
---
```

followed by the same short body (without the HTML comment).

### Rules
- One `AGENTS.md` at the repository root. Do not create per-feature
  AGENTS.md files.
- AGENTS.md is read at two points: **Step 0** (before any work) and
  **Step 12** (after all work is done, to verify compliance).
- Keep AGENTS.md a **process contract** (artifacts, rules, layout). It is
  not a copy of this skill. Do not name this skill or its delegates.
- **Per-agent files are shims, not copies.** They point at `AGENTS.md` and
  carry no steps and no skill names.
- One shim per agent format, at the path that agent reads natively.

---

## Step 3: Terminology

`docs/terminology.md` is the **single source of truth for the vocabulary**
used across this codebase — in specs, plans, logs, architecture/mechanism
docs, code identifiers, comments, and conversation. It implements the
Domain-Driven Design practice of a *ubiquitous language*: one shared,
rigorous vocabulary used identically everywhere.

**The conflict rule:** when documentation or code conflicts with
`docs/terminology.md`, **terminology wins.** Docs and code are updated to
match, not the other way around.

### What this step does

After the intent spec is settled (Step 2), check every term the spec relies
on against `docs/terminology.md`:

- If a term is already defined → use the canonical term in the spec and all
  downstream docs. Do not introduce a new synonym.
- If a term is missing → add an entry to `docs/terminology.md` using the
  template below before proceeding to Step 4.
- If the spec uses a `legacy` or `deprecated` term → rewrite the spec to use
  the canonical term, or mark the legacy term's replacement explicitly.
- If two terms in the spec mean the same thing → pick one as canonical, list
  the other as an alias, and update the spec to use the canonical term.

### Boundary with the domain model

`terminology.md` is the **dictionary** — words, their canonical name,
aliases, status, and a short definition of the *idea*. `docs/domain-model/`
is the **structure** — entities (tables/fields/relationships), concepts
(recurring patterns/behavior). Concept and entity files (Step 4) **link
back** to the terminology entry rather than redefining the term.

Terminology may include terms that have no domain-model file at all (UI
labels, status enum values, action verbs, roles). A concept/entity file
should always reference its terminology entry.

Rule of thumb: terminology answers *"what do we call this thing and what
does the word mean?"*; the domain model answers *"how is this thing
structured and how does it behave?"*

### If `docs/terminology.md` does not exist

Create it using the template below. Seed it from the current spec's
vocabulary plus any terms already used in existing docs/code that the spec
relies on. Do not try to define the entire codebase's vocabulary at once —
define what the current change touches, plus terms those docs reference.

### `docs/terminology.md` template

```markdown
# Terminology

This file is the **single source of truth** for the vocabulary used in this
codebase. Documentation, code identifiers, comments, and conversation must
use these terms consistently. When docs or code conflict with this file,
**this file wins.**

## How to read this file

- Each entry has a **canonical term** — use it.
- **Aliases** are accepted synonyms or legacy names. Do not introduce new ones.
- **Status:** `canonical` (use freely) · `deprecated` (do not use, being
  removed) · `legacy` (still in code, do not use in new docs/code).
- **Type:** `entity` · `concept` · `action` · `status` · `role` · `meta`.
- **Definition** describes the *idea*, never the storage or implementation.
- **Code** points to where the term lives (file, type, table, column).
- **See also** links related terms; **Not to be confused with** disambiguates.

## Terms

### <Canonical Term>

- **Aliases:** <synonyms, legacy names>
- **Status:** canonical
- **Type:** entity
- **Definition:** <1–2 sentences describing the idea, not the implementation>.
- **Code:** <file/type/table/column where the term lives>
- **See also:** <related terms>
- **Not to be confused with:** <disambiguation>

## Legacy term mapping

| Legacy term | Current term | Status | Notes |
|-------------|-------------|--------|-------|
| <old>       | <canonical>  | legacy | <why it changed / where it still appears> |
```

### Rules

- **Never change terminology without developer approval.** Do not add,
  rewrite, remap, or delete entries in `docs/terminology.md` unless the
  developer has explicitly approved the change. If a term is missing,
  ambiguous, or looks wrong, stop and ask — do not invent or “correct”
  vocabulary. Using existing canonical terms elsewhere does not require
  approval; editing the terminology file does.
- One `docs/terminology.md` per repository, at `docs/terminology.md`. Do not
  create per-feature terminology files. For very large codebases, split by
  subdomain under `docs/terminology/` with an `index.md` — but only when a
  single file stops being navigable (~50–80 terms).
- Define the *idea*, never the storage. "A research library rooted at a
  folder" — not "a row in the `vaults` table." Implementation lives in the
  entity doc.
- Track aliases and deprecations explicitly. The legacy mapping table is what
  makes renaming safe; without it, old terms linger invisibly.
- Link bidirectionally: terminology → code anchor and domain-model file;
  domain-model → terminology term.
- Use **Not to be confused with** to disambiguate near-synonyms (the most
  useful field in practice).
- Keep definitions to 1–2 sentences. Depth lives in concept/entity docs.
- Order entries for findability — alphabetical within a section, or grouped
  by subdomain (`## Research model`, `## Auth`, `## Billing`). Pick one and
  stick to it.
- Do not duplicate the domain model. If you find yourself writing fields and
  relationships in terminology, move that content to the entity doc and link.
- Re-run this step whenever the spec changes (Step 2): a revised spec may
  introduce, rename, or retire terms, and the domain model (Step 4) must be
  derived from the current terminology, not a stale one.
- When the change has no new vocabulary impact, note in the plan that
  terminology is unchanged and proceed to Step 4.

### Optional CI lint

Once `docs/terminology.md` is stable, an optional check can fail PRs that
introduce a `legacy` or `deprecated` term in new code or docs. Add this only
when the file is stable — premature structure is maintenance debt.

---

## Step 9: Log format (AFTER implementation)

Every implementation produces or updates a **log** entry, written **after**
the code is done. Logs are the implementation record; the terminology,
domain model, and plan are the pre-implementation record.

Store logs at `docs/logs/<feature>.md` (flat — one file per feature). If it
does not exist, create it. Also maintain `docs/logs/index.md` as an index.

### Log file format

```markdown
# Log: <Feature Name>

**Feature:** [spec.md](../features/<feature>/spec.md)
**Plan:** [plan.md](../features/<feature>/plan.md)
**Last updated:** <date>

## Plan implementation status

| Plan section | Status | Notes |
|--------------|--------|-------|
| §<section> | Implemented / Deviation / Skipped | <what happened> |
| ... | ... | ... |

**Overall:** <one-line summary>

---

## Summary of changes

### <Area>
- **`<file>`**: <what changed>

---

## Deviations from plan

| Plan | Shipped |
|------|---------|
| <planned approach> | <what was actually done> |

---

## Files touched (main)

| Area | Files |
|------|-------|
| Utils | <files> |
| Components | <files> |
| Screens | <files> |
| Tests | <files> |
| Docs | <docs files> |

---

## Tests

| Test | Covers | Status |
|------|--------|--------|
| <test name or path> | <behavior it verifies> | Added / Updated / Existing / N/A |
| ... | ... | ... |

If no tests were added or run, state why (e.g., "e2e does not apply — no
user-visible flow", "manual verification only — see notes"). Do not leave
this section silent. "No test framework" is not a skip reason; the tests
ask adds the tools from `coding-best-practices`.

---

## Recommended follow-ups

1. <next step or related feature>
```

### Rules
- One log file per feature, updated on each implementation pass (do not
  create `<feature>-v2.md`; append/update the existing file).
- Group changes under the standard sections above; omit empty sections.
- Reference the spec and plan sections each change implements, where useful.
- If the implementation deviated from the plan, note the deviation and why
  in `## Deviations from plan` and ensure `plan.md` was updated in Step 7.
- Update `docs/logs/index.md` index: add a row for the feature if new, or
  update the "Plan status" column if the feature already had a log.

### `docs/logs/index.md` format

```markdown
# Logs

Implementation and change logs for features. Each log summarizes work done
against the feature's intent spec and implementation plan.

| Log | Feature | Plan status |
|-----|---------|-------------|
| [<feature>.md](./<feature>.md) | [<Feature name>](../features/<feature>/spec.md) | <status summary> |
| ... | ... | ... |
```

---

## Step 10: Repo README format (AFTER implementation)

The repository root `README.md` is the project's front door. After
implementation, evaluate whether the change affects anything a reader of the
README would need to know. If yes, update the README. If no, skip this step
with a one-line note in the log's `## Recommended follow-ups` or a `## README`
section stating "No README changes needed."

### When to update the README

Update the repo `README.md` when the implementation changes any of:

- **What the project is** — purpose, description, tagline, or audience.
- **What the project does** — capabilities, feature list, screenshots,
  demos, or notable behavior the user can observe.
- **How to get it running** — prerequisites, install, configuration,
  environment variables, build, run, or deploy commands.
- **How to use it** — usage examples, CLI flags, API endpoints, or user
  flows.
- **How to develop on it** — dev setup, test commands, lint/format
  commands, project structure pointers, or contribution guidelines.
- **Where things live** — links to deeper docs (`docs/` folders, feature
  specs, domain model, logs) if the README references them.
- **Product vocabulary** — when the README uses terms that conflict with
  `docs/terminology.md` (even if other work was docs-only), update the
  README to canonical terms. On-disk paths and code identifiers may still
  use legacy names when those are the real names in the tree.

Do NOT update the README for:

- Internal refactors with no user-visible or setup-visible change.
- Bug fixes that don't change documented behavior or instructions.
- Changes confined to `docs/` that do **not** leave the README using wrong
  product vocabulary (those have their own indexes).
- A developer learning path, tutorial catalogue, or any path under a
  gitignored folder (including `tmp/`). Getting Started must work on a
  clone that has never seen those files.

Getting Started must list only commands and files that exist after clone
(for example `docker compose`, `npm install`, `npm run dev`).

### Best practices for writing the README

Follow standard README best practices. A good README:

1. **Starts with the project name and a one-line description** — what it is
   and why it exists, in the first sentence a reader sees.
2. **Has a Badges / shields row** (optional) — build status, version,
   license, etc. Omit if none apply.
3. **Has a clear "Getting Started" section** — prerequisites, install,
   and run steps that a fresh clone can follow verbatim.
4. **Shows usage** — a minimal example of the most common thing a user
   does with the project.
5. **Documents configuration** — env vars, config files, options, with
   defaults.
6. **Links to deeper docs** — points at `docs/`, architecture notes, ADRs,
   feature specs, rather than duplicating them inline.
7. **Has a "Development" section** — how to run tests, lint, format, and
   where the source lives (folder layout).
8. **Has a "Contributing" section** — tells a new contributor the rules of
   engagement for the project: how to propose changes, what standards to
   follow, and where to find the development workflow. It should point to
   the documentation that this pipeline maintains — feature specs at
   `docs/features/`, domain model at `docs/domain-model/`, implementation
   logs at `docs/logs/` — so contributors know features are specced before
   code is written, not ad hoc. It should also cover: testing/lint/format
   expectations before submitting, whether PRs/issues/direct commits are the
   process, and a link to `CONTRIBUTING.md` if one exists. The goal is: a
   new contributor can read this section and know exactly how to make a
   change the right way, rather than reinventing the process.
9. **States the license** — or links to LICENSE file.
10. **Uses clear headings, code blocks, and lists** — scannable, not a
    wall of prose.
11. **Stays current** — stale instructions are worse than no instructions;
    if a step no longer applies, remove it.
12. **Avoids boilerplate** — drop the framework-generated filler if it
    does not reflect the project.

### If the README does not exist

Create it using the structure above. Even a minimal README (name, purpose,
getting started, license) is better than none.

### Format

```markdown
# <Project Name>

<One-line description of what the project is and why it exists.>

<Optional: badges>

## Features

- <Capability 1>
- <Capability 2>
- <Link to docs/features/ for the full list>

## Getting Started

### Prerequisites

- <tool/runtime versions>

### Install

\`\`\`sh
<commands>
\`\`\`

### Run

\`\`\`sh
<commands>
\`\`\`

## Usage

<minimal example of the most common task>

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `<VAR>` | <default> | <what it does> |

## Development

\`\`\`sh
<test command>
<lint command>
<format command>
\`\`\`

Project layout:

\`\`\`
<short tree of key dirs>
\`\`\`

See `docs/` for feature specs, domain model, and implementation logs.

## Contributing

<short rules or link to CONTRIBUTING.md>

## License

<license name or link to LICENSE>
```

### Rules
- One repo `README.md` at the repository root. Do not create per-feature
  READMEs at the repo root.
- Keep the README a **summary and entry point** — link to `docs/` for
  depth. Do not duplicate feature specs or logs inline.
- Update in place; do not create `README_v2.md`.
- If the project is a monorepo, each package may have its own `README.md`
  in its package root — apply the same rules per package.

---

## Step 11: Architecture & Mechanisms formats (AFTER implementation)

After implementation, evaluate whether the change affects any foundational
decision or subsystem runtime behavior. If yes, update the relevant docs.
If no, skip this step with a one-line note in the log.

### When to update architecture

Update `docs/architecture/<topic>.md` when the implementation introduces or
changes:

- **Tech stack** — a new framework, library, runtime, or tool was adopted.
- **System boundaries** — what's backend vs. frontend vs. external service
  shifted.
- **Deployment topology** — where and how the app is deployed changed.
- **Data flow** — how data moves through the system at a high level
  changed.
- **External integrations** — a new third-party service was added or an
  existing one was replaced.

### When to update mechanisms

Update `docs/mechanisms/<mechanism>.md` when the implementation adds,
changes, or extends a subsystem's runtime behavior:

- **Authentication** — login/logout flow, token refresh, session expiry,
  redirect logic gained a new step.
- **Caching** — invalidation rules, cache layers, or strategies changed.
- **Sync** — conflict resolution, offline queue, or merge logic changed.
- **Error handling** — retry strategies, fallback behavior, or error
  propagation changed.
- **Any subsystem** whose runtime process a developer needs to understand
  to debug or extend it.

### When to skip

Do NOT update architecture/mechanisms for:

- Pure UI changes with no backend/mechanism change.
- Bug fixes that restore documented behavior without changing the process.
- Refactors that preserve the same runtime behavior.
- Changes fully confined to a single feature's scope with no cross-cutting
  impact.

Note "No architecture/mechanism changes needed" in the log's
`## Recommended follow-ups` or a `## Architecture & Mechanisms` section.

### Architecture doc format

```markdown
# <Topic>

<One-paragraph summary: what decision this documents.>

## Decision

<What was chosen and why. Include alternatives considered if relevant.>

## Context

<Constraints, requirements, or events that drove this decision.>

## Consequences

<Trade-offs, risks, or follow-ups introduced by this decision.>

## References

- <Links to mechanisms, specs, or external docs this decision affects>
```

### Mechanism doc format

```markdown
# <Mechanism Name>

**Id:** `mechanisms/<mechanism>`

<One-paragraph summary: what this subsystem does at runtime.>

## How it works

<Step-by-step or component-by-component explanation of the runtime flow.
This is the "how" — not the "why we chose this" (that belongs in
architecture).>

## Dependencies

- <External services, libraries, or other mechanisms it relies on>

## Model

- **Concepts:** `concepts/<c>`
- **Entities:** `entities/<e>`

## Appears in features

- <feature-name>
- <feature-name>
```

### `docs/architecture/index.md` format

```markdown
# Architecture

Foundational decisions: tech stack, system boundaries, deployment topology,
data flow. These change rarely — only when a core choice shifts.

| Topic | Decision | Last updated |
|-------|----------|--------------|
| [<topic>](./<topic>.md) | <short summary> | <date> |
| ... | ... | ... |
```

### `docs/mechanisms/index.md` format

```markdown
# Mechanisms

How specific subsystems work at runtime. These change more often — whenever
a feature touches that subsystem.

| Mechanism | Summary | Features | Model |
|-----------|---------|----------|-------|
| [<mechanism>](./<mechanism>.md) | <short summary> | <features that rely on it> | <concepts/entities> |
| ... | ... | ... | ... |
```

### Rules
- One doc per architectural topic or mechanism. Update in place; do not
  create `<topic>-v2.md`.
- Both folders use `index.md` (not `README.md`) as their index, following
  the same convention as the rest of `docs/`.
- Mechanism docs must link to the domain model (concepts/entities they
  implement) and list features that rely on them (`## Appears in features`).
- Architecture docs must link to any mechanisms, specs, or external docs
  the decision affects (`## References`).
- If a mechanism is renamed or removed, update `docs/mechanisms/index.md`
  and any domain-model files that reference it in `## Implemented by`.

---

## Failure Modes to Avoid

0. **Using this skill without confirmation.** Before this skill is used,
   the user needs to confirm. Do not start Step 0 until they say yes.
1. **Implementing or generating tutorials without a spec.** Always run
   Steps 0–7 first. Step 8 is an ask, not a skip of the gates.
2. **Silently rewriting the spec.** Always get user confirmation in Step 2.
3. **Skipping terminology.** Step 3 is mandatory; the domain model and plan
   are derived from the canonical terms. Docs and code must not contradict
   `docs/terminology.md` — when they conflict, terminology wins.
3b. **Changing terminology without developer approval.** Never add, rewrite,
   remap, or delete entries in `docs/terminology.md` without checking with
   the developer first. Do not silently “fix” or reinterpret vocabulary.
   Ask when a term is missing or ambiguous.
3c. **Using git tools without an explicit ask.** Never run git (status, diff,
   add, commit, restore, branch, push, etc.) unless the developer clearly
   requested that git action. File exploration uses graphify first, then
   ordinary file tools — not git.
3d. **Non-English code or docs.** Identifiers, comments, file names, and
   documentation are English. Do not put another language in docs or
   code except user-visible UI copy (quoted when a document describes the
   screen) and proper names as written in `docs/terminology.md`.
3e. **Skipping the Step 8 ask.** Do not write application code and do not
   generate tutorials until the user chooses. Ask again for **tests**. Do
   not run Steps 9–12 until implementation is done (app code and tests: you
   finished coding, or they said they are done and the tutorial check
   passed).
3e2. **Skipping the tutorial check.** On a tutorials path, do not treat
   “I’m done” as a pass. Compare the tree to the sittings and the plan
   before continuing. Do not write the log over a mismatch.
3f. **Dumping the tree instead of graphify.** Prefer `graphify query` /
   `path` / `explain` over reading many files. Do not cat `graph.json`.
   If the CLI is missing, ask once to install it; do not silent-install,
   add it to the repo, or skip the ask and dump the tree.
4. **Skipping the domain model.** Step 4 is mandatory; the plan is derived
   from the model.
5. **Implementing against a stale model.** If the spec changed, re-run Step
   3 (terminology) and Step 4 (domain model) and update all docs
   (terminology, concepts, entities, spec `## Domain Model`) before
   writing code.
6. **Skipping the plan.** Step 5 is mandatory, even for one-line fixes.
7. **Skipping design for UI work.** Step 6 is mandatory unless the user opts
   out.
8. **Implementing divergent work.** Step 7 forces the plan to match reality
   first.
9. **No log.** Step 9 is mandatory, every time — written after the code,
   not before.
10. **Logs created before implementation.** Logs are the record of what was
    done, not the plan of what will be done. If you find yourself writing a
    log before code, stop — that belongs in `plan.md`.
11. **Stale README.** Step 10 is mandatory whenever the change affects what
    the project is, does, or how to run it. A README that contradicts the
    code is worse than none.
12. **Stale architecture/mechanisms docs.** Step 11 is mandatory when the
    implementation changes a foundational decision or subsystem behavior.
    Docs that contradict the code mislead anyone joining or debugging the
    project.
13. **Mixing architecture and mechanisms.** Architecture documents the
    *decision*; mechanisms document the *process*. If a doc mixes "we chose
    X because Y" with "then step 3 does Z," split it.
14. **Partial compliance breeds more non-compliance.** Skipping a step once
    makes skipping the next time feel acceptable. Each request is
    independent — prior skips do not create a precedent for future skips.
    If you skipped a step last time, that was a failure; do not repeat it.
    Run all gates on every request, regardless of how the previous request
    was handled.
15. **Retroactive docs ≠ compliance.** Writing new code first and then
    updating plan/log/mechanisms after the fact satisfies the
    file-existence check but not the gate. The plan must precede code; the
    log must follow it. Tutorials at Step 8 do not skip Steps 0–7. Steps
    9–12 wait until implementation is done (app code and tests) and, on a
    tutorials path, the check has passed.
16. **Manually patching delegate output.** Hand-editing a spec, concept,
    entity, or design file bypasses the delegate skill's classification,
    index, and cross-reference rules. Always re-run the delegate skill
    instead of patching its output by hand.
17. **No tests for changed behavior.** After app code, run the tests ask.
    Add or update tests for the behavior you changed, **including e2e when
    possible**. A bug fix without a regression test is incomplete. If the
    stack file has no Testing section, research and add it in
    `coding-best-practices`; do not skip with “no test framework.” If e2e
    does not apply, say why in the plan and log.
18. **Treating the skill as background context.** This skill's steps are
    blocking gates, not reference material. "I loaded it but didn't follow
    it" is the same as not loading it. Each step must be actively run and
    completed before the next.
19. **Skipping AGENTS.md.** Step 0 (read first) and Step 12 (review last)
    are mandatory. Starting work without reading AGENTS.md means you don't
    know the repo's pipeline rules. Ending work without re-reading it means
    you haven't verified compliance. Both are failures.
20. **No AGENTS.md in the repo.** If the repo has no AGENTS.md, Step 0
    creates it — it is not optional to have one. A repo without AGENTS.md
    has no entry point for agents and no compliance checkpoint.
21. **Vocabulary drift.** Introducing a new synonym for an existing
    canonical term, or using a `legacy`/`deprecated` term in new docs/code,
    silently breaks the ubiquitous language. When in doubt, check
    `docs/terminology.md` first; if a term is missing, add it there before
    using it in the spec, plan, or code.
22. **Per-agent instruction files out of sync.** `CLAUDE.md`, `.cursorrules`,
    `.cursor/rules/*.mdc`, and opencode config must point at `AGENTS.md` and
    duplicate no pipeline content. Keep shims thin pointers.
23. **Writing this skill into the repo.** `AGENTS.md` and shims must not
    name this skill, its delegates, graphify, confirm-before-use, or the
    Step 8 asks. Those belong in this skill. Repos are not dependent on skills.
24. **Documenting a developer learning path in the repo.** README, spec,
    plan, log, terminology, and architecture describe the product. Do not
    link gitignored paths. Do not create a feature for sittings or courses.
    After the user is done, record what shipped, not course catalogues.
