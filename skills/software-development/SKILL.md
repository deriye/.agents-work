---
name: software-development
description: >-
  Orchestrates the gated software-development lifecycle: AGENTS.md, intent
  spec (isdd), terminology, domain model, plan, design (huashu-design),
  implement (ask: agent codes, or tutorials via generate-tutorials), log,
  README (best practices), architecture/mechanisms. Use when writing or
  changing code (source, config, styles, assets, build, scripts), features,
  bug fixes, refactors, or polish. Before this skill is used, the user
  needs to confirm. Explore with graphify to save tokens. Load before
  isdd, domain-model, or huashu-design. Bug fixes are not exempt. Never
  edit terminology or use git unless the developer asked. Details in
  reference.md.
---

# Software Development

This skill is the orchestrator for software development tasks. Code-bearing
work flows through the same gated pipeline so that intent, terminology,
domain model, plan, design, and logs stay in sync.

**Before this skill is used, the user needs to confirm.** Load it when the
request may touch code, then stop and ask. Do not run the pipeline or write
code until they confirm.

## User controls every step (confirm or skip)

**Steps do not run automatically. Before each step (0–12), stop, tell the
user what the step will do and which artifact it produces, and ask them to
confirm it, skip it, or modify it.** Only run the step after they confirm.
The user chooses which steps run.

- **Ask per step, in order.** State the step, its purpose, and its output,
  then wait. Do not batch several steps into one "shall I proceed?" — each
  step gets its own confirm/skip choice.
- **User skip always wins.** If the user skips a step, skip it — even when
  that contradicts the mandatory-gate rules below ("gates block code",
  "bug fixes are not exempt", "selective compliance is non-compliance").
  Those rules describe the *default* pipeline; an explicit user skip
  overrides them. Note the skip (one line) so the log records what was
  skipped.
- **Blanket choices are allowed.** If the user says "run everything" or
  "skip all docs, just implement," honor it without re-asking each step; if
  they later change their mind, resume per-step asking.
- **Confirm-before-use still applies.** The initial "may I use this skill"
  confirmation is separate from and precedes the per-step asks.

## Load this skill FIRST

This skill is the orchestrator. It must be loaded **before** any other
development-related skill (`isdd`, `domain-model`, `huashu-design`); those
are delegates this skill calls at the right step. Loading a delegate
directly skips the gates this pipeline exists to enforce. **If the task
involves writing or changing code in any way, load this skill before doing
anything else**, then **wait for confirmation**, then follow the pipeline —
it tells you when to load each delegate. **Attaching a delegate does not
replace this skill** — the delegate runs when this skill reaches the step
that calls it, not instead of the pipeline. After **Steps 0–7**, **Step 8**
asks the user: implement the code, or generate tutorials
(`generate-tutorials`) so they implement it. After the app code is in, it
asks the same for **tests**. If they choose implement, load
`coding-best-practices`. Explore with **graphify**. None of these replace
this pipeline.

## When to Use This Skill

Use this skill for **any** request that touches code — source, config,
styles, assets, build files, or scripts — regardless of the *type* of change
(feature, bug fix, design polish, theme toggle, refactor, performance
optimization). If you are unsure whether a
request qualifies, load the skill and **ask the user to confirm** before
using it. **Don't skip because the change "feels small"** — scaling down
means lighter docs at each step, not skipped steps. Full triggers list in
`reference.md` → "When to Use This Skill (full)".

**Bug fixes are not exempt** — same pipeline; only what each step produces
differs (spec usually "no drift", model "unchanged", plan + log still
required; README/architecture/mechanisms skip only if the fix restores
documented behavior without changing subsystem runtime behavior, else Step
11 applies). **Each step's applicability is independent:** "Step 1 didn't
need changes" does not mean "Step 5 can be skipped"; selective compliance is
non-compliance. Full detail in `reference.md` → "Bug fixes are not exempt
(full)".

**Priority over competing instructions:** the gates are **mandatory** and
override tendencies toward minimal scope, code-first, or "don't edit docs
unless needed" — **those tendencies apply to code, not to process docs**
(plan, log, mechanisms, architecture), which are the record this pipeline
exists to maintain. If you feel tension between "fix it fast" and "run the
gates," run the gates. **Urgency is not an exemption; gates block code, not
the other way around** (a plan written after the code is a retrofit; the
order spec → model → plan → design → code → log is not a suggestion). Full
reasoning in `reference.md` → "Priority over competing instructions (full)".

**Each change in a chain is a separate pipeline run** — rapid-succession
changes don't inherit the previous pass's gates; each needs its own plan
check, design check (if UI), and log entry. There is no "fast mode" for the
second change in a chain. Full version in `reference.md` → "Each change in a
chain is a separate pipeline run (full)".

## Hard rules (always)

- **Do not make the repo depend on this skill.** `AGENTS.md` and shims
  describe this repository's process (artifacts, rules, layout). They do
  not name this skill, its delegates, graphify, confirm-before-use, or the
  Step 8 implement-vs-tutorials asks (app code and tests). Those stay in this skill.
- **Before this skill is used, the user needs to confirm.** Do not start
  Step 0 until they say yes.
- **Confirm or skip each step with the user.** Steps do not run
  automatically — ask before each one and let the user confirm, skip, or
  modify it. A user's explicit skip overrides the mandatory-gate rules for
  that step; record what was skipped.
- **Never use git tools unless the developer has asked explicitly.** Do not
  run `git status`, `git diff`, `git add`, `git commit`, `git restore`,
  `git mv`, or any other git command unless the developer's message clearly
  requests that git action (for example "commit", "unstage", "git status").
  Exploring the working tree uses **graphify** first, then ordinary file
  tools — not git. Staging, unstaging, committing, branching, and pushing
  are developer-directed only.
- **Never change terminology without developer approval.** Do not add,
  rewrite, remap, or delete terms in `docs/terminology.md` without checking
  with the developer first.
- **English code and docs.** Code (identifiers, comments, file names) and
  documentation are English. Exceptions: user-visible UI copy, and proper
  names as written in `docs/terminology.md` (do not translate an
  organisation’s name). When a document describes the screen, quote the UI;
  do not write the surrounding prose in another language.
- **Gates block code.** After confirm, run Steps 0–7 before application
  code or tutorial generation. At Step 8, ask implement vs tutorials for
  **application code**, then again for **tests**. Do not run Steps 9–12
  until implementation is done (app code and tests: you finished coding, or
  they said they are done **and** the tutorial check passed).

## Behavioral Guidelines

These guidelines reduce common LLM coding mistakes. They operate **within**
the pipeline — they shape how you work at each gate, not whether you run the
gates. "Think before coding" *is* the spec/drift gates; "goal-driven
execution" *is* the plan + test plan; "simplicity" and "surgical changes"
govern the code in Step 8. They bias toward caution over speed; for genuinely
trivial tasks, use judgment — but judgment never means skipping a gate, only
producing lighter docs at that gate. Full detail (with bullets) in
`reference.md` → "Behavioral Guidelines (full)".

1. **Think before coding** — don't assume or hide confusion; state
   assumptions, present multiple interpretations rather than picking silently,
   name what's unclear and ask. (What Steps 2 and 7 enforce structurally.)
2. **Simplicity first** — minimum code that solves the problem; nothing
   speculative. If 200 lines could be 50, rewrite. Applies to Step 8 code
   within the plan's approach; if the plan is overcomplicated, fix it first.
3. **Surgical changes** — touch only what you must; clean up only your own
   mess. Don't "improve" adjacent code or refactor what isn't broken; match
   existing style; mention unrelated dead code, don't delete it; remove only
   the orphans your changes created. Every changed line must trace to the
   user's request and the plan's scope (Step 5).
4. **Goal-driven execution** — define success criteria; loop until verified
   ("Add validation" → tests for invalid inputs then pass; "Fix the bug" → a
   reproducing test then pass; "Refactor X" → tests pass before and after).
   The plan (Step 5) states `Step → verify: check`; criteria are recorded in
   the plan's test section and checked in the log (Step 9).

These are working if: fewer unnecessary changes in diffs, fewer rewrites from
overcomplication, and clarifying questions come before implementation rather
than after mistakes.

## Folder Layout

Pipeline artifacts (terminology, domain model, feature specs/plans, logs,
architecture, mechanisms) live under an **artifacts directory** that
defaults to `docs/` (see `reference.md` → "Folder Layout (full)"). Root:
`AGENTS.md`, `README.md`, gitignored `tmp/` for scratch — never under the
artifacts directory. Architecture = decision; mechanisms = runtime process.

### Artifacts directory (user-configurable, overrides `docs/`)

The user may choose a different directory to store pipeline artifacts in the
repo; that choice **overrides the default `docs/`**.

- **Ask once, early.** At the start of a run (after confirm-before-use,
  around Step 0), ask where pipeline artifacts should live, offering `docs/`
  as the default. If they name a directory (e.g. `documentation/`,
  `.project/`, `spec/`), use it as the artifacts root for **every** step;
  if they accept the default or don't care, use `docs/`.
- **Applies to all artifact paths.** Everywhere this skill or `reference.md`
  writes `docs/…` for a pipeline artifact — `docs/terminology.md`,
  `docs/features/<feature>/`, `docs/domain-model/`, `docs/logs/`,
  `docs/architecture/`, `docs/mechanisms/` — read it as
  `<artifacts-dir>/…`, where `<artifacts-dir>` is the chosen directory
  (default `docs/`). `AGENTS.md`, `README.md`, and `tmp/` stay at the repo
  root regardless.
- **Record the choice.** When it is not the default, record the chosen
  artifacts directory in `AGENTS.md` (Step 0) so the location is part of the
  repo contract and every later run and agent uses the same directory.
  Reuse an existing repo's already-chosen directory instead of re-asking.
- **Delegates follow it too.** Tell `isdd`, `domain-model`, and any
  artifact-writing delegate to use `<artifacts-dir>` instead of `docs/`
  when their paths would otherwise be under `docs/`.

## Confirm before use

**Before this skill is used, the user needs to confirm.** Wait. Do not
explore, edit, or write docs until they say yes. If they decline, stop.

Once they say yes, walk the pipeline in order but **confirm or skip each
step with the user** (see "User controls every step" above). The default
sequence is Steps 0–7, then Step 8 (ask implement vs tutorials for app code,
then for tests), then Steps 9–12 after implementation. The user may skip any
of these; an explicit skip wins over the gate rules and is recorded. Detail:
`reference.md` → "Step 8: Implement or tutorials".

## Repos are not dependent on this skill

This skill is how the **agent** runs the pipeline. The **repo** contract is
`AGENTS.md` (artifacts, rules, layout). Do not write this skill, its
delegates, graphify, confirm-before-use, or the Step 8 asks into repository
files. If `AGENTS.md` names them, rewrite those lines to files and rules only.

Committed docs describe the **product**. README is how to clone and run it.
Do not document gitignored paths. Do not add spec, plan, log, terminology,
or domain-model entries for a developer learning path. After the user is
done implementing, Steps 9–12 record what shipped, not sittings. Detail:
`reference.md` → "Committed docs are the product".

## Explore with graphify

Use **graphify** to explore so you query a scoped subgraph instead of
reading the tree (saves tokens). Prefer `graphify query "…"`,
`graphify path A B`, and `graphify explain "X"` over glob/grep/read of many
files. If `graphify-out/graph.json` is missing or stale, run `graphify .` or
`graphify update .`, then query. After **code** changes, run `graphify update .`
(AST only; no LLM key). Do not use `graphify . --update` for that — that
re-extracts docs/papers/images and needs an API key. If the CLI is missing,
**ask once** to install it as a machine-level tool
(`uv tool install graphifyy`). Install only after they say yes, then run
`graphify .`. If they decline, fall back to file tools and do not ask
again this session. Do not add graphify to the repo. Full commands:
`reference.md` → "Explore with graphify".

## Pipeline Overview

Before each step below, confirm or skip it with the user; an explicit skip
overrides the gate and is recorded.

Artifact paths below use `<artifacts-dir>/` — the user-chosen artifacts
directory, defaulting to `docs/` (see "Artifacts directory" above).

```
 C. Confirm             → user must confirm before this skill is used
                          then confirm/skip each step below, in order
 0. AGENTS.md           → create/read AGENTS.md at repo root (read first);
                          ask/record the artifacts dir (default docs/)
 1. Intent Spec          → isdd skill                (<artifacts-dir>/features/<feature>/spec.md)
 2. Intent Drift         → confirm with user before updating spec
 3. Terminology          → <artifacts-dir>/terminology.md   (source of truth for vocabulary)
 4. Domain Model         → domain-model skill        (<artifacts-dir>/domain-model/)
 5. Implementation Plan                             (<artifacts-dir>/features/<feature>/plan.md)
 6. Design               → huashu-design skill       (UI/UX/front-end only)
 7. Plan Drift           → update plan before implementing
 8. Implement            → ask app: agent or tutorials; then ask tests the same way
 9. Log                  → create/update AFTER implementation (<artifacts-dir>/logs/<feature>.md)
10. Repo README          → update README.md AFTER implementation if user-facing
11. Architecture &       → update AFTER implementation if foundational decision or
    Mechanisms             subsystem runtime behavior changed
12. AGENTS.md Review     → re-read AGENTS.md, verify pipeline compliance
```

Every step has a gate — **a hard stop that blocks the next step.** By default
"mandatory" means you stop and do it before moving on, not "recommended."
Treating this skill as background reference rather than blocking gates is a
failure. Steps 9–12 wait until Step 8 is done.

**But the user decides which steps run.** Before each step, ask them to
confirm, skip, or modify it (see "User controls every step"). A step the
user skips is skipped — an explicit skip overrides these gate rules — and the
skip is recorded (one line, surfaced in the Step 9 log). Absent an explicit
skip, the default is to run the step.

### If your context was compressed

If the conversation was compressed, re-read this skill. Before writing code,
check which step you are at (spec match? plan cover this change?). If not,
run earlier steps first. Templates and failure modes: `reference.md`.

---

## Step 0: AGENTS.md (read first)

Before any work begins, ensure an `AGENTS.md` exists at the repository root —
the entry point for any AI agent, read **first** before any code or docs are
touched.

- Does not exist (or empty/boilerplate) → create it from the template in
  `reference.md` → "Step 0: AGENTS.md template" (process only: artifacts,
  rules, layout — **no skill names**).
- Exists but doesn't mention the pipeline → merge the **process** section
  (don't overwrite existing content; flag conflicts to the user).
- Exists and names this skill or its delegates → rewrite those lines to
  files and rules. Do not re-inject skill names.
- Already documents the process without skills → verify artifacts and
  rules; keep it free of this skill.

**Artifacts directory:** as part of Step 0, settle where pipeline artifacts
live. If `AGENTS.md` already records an artifacts directory, reuse it. If
not, ask the user (default `docs/`); if they choose a non-default directory,
record it in `AGENTS.md` and use it for every artifact path this run. Only
`docs/` (or the chosen directory) moves — `AGENTS.md`, `README.md`, and
`tmp/` stay at the repo root.

The AGENTS.md must state it is read first; summarize Steps 0–12 as **files
and actions**; list the key rules that belong to the repo (gates block
code, each change a separate run, bug fixes not exempt, tests required,
terminology wins, never change terminology without developer approval,
English code and docs, never use git unless asked); describe the artifacts
directory (default `docs/`, or the chosen override) and its layout; state
Step 12 re-reads it. It must **not** name this skill, delegates, graphify,
confirm-before-use, or the Step 8 ask.

### Per-agent instruction files

`AGENTS.md` is canonical. Per-agent files (`CLAUDE.md`,
`.cursor/rules/pipeline.mdc` with `alwaysApply: true`, opencode config) are
**thin shims** that point at `AGENTS.md` — never duplicates, never this
skill's name. Table and shim template in `reference.md` → "Per-agent
instruction files". **Rules:** one `AGENTS.md` at repo root; read at Step 0
and Step 12; keep it a process contract, not a copy of this skill.

---

## Step 1: Intent Spec (delegate to `isdd`)

Load the `isdd` skill and follow its workflow to ensure an intent spec exists
at `docs/features/<feature>/spec.md`. No spec for the request → create one
(via isdd); spec matches → proceed to Step 2; spec exists but the request
differs → go to Step 2 (Intent Drift).

The spec describes **what** the user experiences, never **how** it is built.
When writing it, use canonical terms from `docs/terminology.md` (Step 3); if
the spec needs a term not yet defined there, flag it so Step 3 can add it.

---

## Step 2: Intent Drift Check

Compare the user's current request against the existing spec at
`docs/features/<feature>/spec.md`.

- **Matches** → proceed to Step 3.
- **Differs** → **STOP. Do not implement.** Present the drift to the user
  (quote the relevant spec section, describe the difference) and ask how to
  proceed: (1) update the spec to match the new request, (2) keep the spec
  and adjust the request, (3) cancel. Only after the user confirms do you
  update the spec via `isdd`. **Never silently rewrite the spec.**

**Critical:** If the spec is updated, the terminology (Step 3), domain model
(Step 4), plan (Step 5), and any design (Step 6) must all be re-derived from
the new spec **before** any code is changed — don't implement against a stale
spec/model/plan. See Step 7 for the same rule mid-implementation. After the
spec is settled, continue to Step 3.

---

## Step 3: Terminology

`docs/terminology.md` is the **single source of truth** (ubiquitous language).
When docs or code conflict with it, **terminology wins**. **Never** add,
rewrite, remap, or delete terms there without developer approval — ask first
if a term is missing or ambiguous. Using existing canonical terms does not
need approval.

After Step 2: defined term → use it (no synonym); missing → ask, then add
only after approval; legacy term → rewrite to canonical (or existing
mapping). Terminology = dictionary; domain model = structure. No vocabulary
impact → note "terminology unchanged" in the plan. Full template in
`reference.md` → "Step 3: Terminology".

---

## Step 4: Domain Model (delegate to `domain-model`)

**Extract concepts and entities as soon as changes are planned** — after the
spec exists, before or during implementation planning; the model informs the
plan. Load the `domain-model` skill and run its workflow against the spec: it
classifies candidates (concept, entity, field, relationship, neither),
creates/updates concept and entity files, updates both `index.md` files
(including spec→concept and spec→entity maps), adds a `## Domain Model`
section to the spec, and links each concept/entity back to its canonical term
in `docs/terminology.md`.

- **Uncertain items** → resolve with the user before Step 5; don't plan
  against an ambiguous model.
- **When the spec changes later** → re-run Step 3 and this step, and update
  all affected docs (terminology, concepts, entities, both index files, the
  spec's `## Domain Model`) before implementation; the plan must derive from
  the current model, not a stale one.
- **No domain impact** → note "domain model unchanged" in the plan and
  proceed to Step 5.

### Do not manually patch delegate output

**Do not hand-edit domain-model files yourself** — re-run the
`domain-model` skill (it enforces classification, index, cross-reference,
and mechanism→model rules that manual patching bypasses). Same for all
delegates: Step 1 (`isdd`) — don't hand-edit `spec.md`; Step 4
(`domain-model`) — don't hand-edit concepts/entities; Step 6
(`huashu-design`) — don't hand-edit design artifacts. Re-run the delegate.

---

## Step 5: Implementation Plan

**Always** create an implementation plan before writing any code, however
small. Store it at `docs/features/<feature>/plan.md`.

The plan covers: (1) **Scope** — what files/modules change and why;
(2) **Terminology** — new/changed terms from Step 3; (3) **Domain model** —
concepts/entities this change touches; (4) **Approach** — technical strategy
(libraries, patterns, data flow); implementation details live here, NOT in
the spec; (5) **Steps** — ordered, concrete, checkable; (6) **Risk / Rollback**
— what could break and how to revert; (7) **Test plan** — what to verify after
implementation. The test plan **must include e2e tests when possible**: if the
change has a user-visible flow (open the app, click, type, see a result),
name those journeys. If e2e does not apply (no UI, no runnable flow), say
why in the plan. Do not defer “add tests later.”

Read the current spec, terminology, **and** domain model before writing the
plan. The plan must trace back to the spec's `## Desired Behavior`, `##
Success Criteria`, and `## Domain Model`, and use canonical terms from
`docs/terminology.md`.

---

## Step 6: Design (delegate to `huashu-design`, UI/UX only)

Evaluate whether the feature involves **front-end UI or UX work** — new
screens, pages, dialogs, or components; changes to layout, flow,
interaction, or visual behavior; anything the user will see or click.

- **If YES** → load `huashu-design` and produce the required design artifacts
  **before** implementation, aligned with the spec and plan. The only valid
  skip reason is the user explicitly saying "skip design" / "no design
  needed." "Extends existing UI" is not a skip reason — if the user will see
  or click anything new or changed, design runs; if in doubt, ask. If the
  user already provided designs, honor that and note it in the plan.
  Otherwise deliver designs and get the user's pick/confirmation before
  Step 7.
- **If NO** (backend/logic/config only) → skip this step. Proceed to Step 7.

---

## Step 7: Plan Drift Check

Before implementing, re-read `docs/features/<feature>/plan.md` and compare it
against: the (possibly updated) intent spec; the terminology from Step 3;
the domain model from Step 4; the user's latest request and any design
decisions from Step 6; and the current state of the codebase.

- **If the plan is still accurate** → proceed to Step 8.
- **If the plan has drifted** → **update the plan before implementing.** Do
  not implement changes that diverge from a written plan without first
  rewriting the plan to match. Update `plan.md` in place; note what changed
  and why (one line is fine). If the drift originated from a spec change,
  confirm Step 3 and Step 4 were re-run and all docs (terminology, concepts,
  entities, spec `## Domain Model`) are up to date — **all docs must match
  the current spec before code is written.** Then proceed to Step 8.

This applies mid-implementation too: if the approach needs to change, **stop,
update the plan (and re-run terminology and the domain model if the spec
drifted), then continue.**

---

## Step 8: Implement

**Stop and ask (application code).** Do not write application code and do
not generate tutorials until the user chooses:

1. **You implement** — write the application code (conventions below). Then
   the **tests ask**.
2. **Tutorials** — load `generate-tutorials`, write implement-a-real-app
   sittings under gitignored `tmp/`, then **wait**. Do not inspect or patch
   while they work. When they say they are done, **check** (below). Then the
   **tests ask**. Do not run Steps 9–12 yet.

If the plan is already satisfied by the tree, they may say they are already
done — skip writing app code; still check against the plan, then the tests
ask.

### After tutorials: check

When they say they are done (app sittings or test sittings):

1. Compare the tree to the sittings and to the plan for this pass. Load
   `coding-best-practices` for every stack in the change (including Testing).
2. Run lint / typecheck / tests if those commands exist.
3. **Match** → continue (tests ask after app sittings; Step 9 after test
   sittings). The log records what shipped, not sittings.
4. **Mismatch** → **STOP.** List what is missing or wrong. Do not patch
   unless they ask. Do not write the log. Wait until they fix it (or ask
   you to) and say to check again.

Do not treat “I’m done” as proof the sittings were followed.

### Tests ask (after application code is in)

**Stop and ask.** Do not write tests and do not generate test tutorials
until the user chooses:

1. **You implement** — write the tests (conventions below).
2. **Tutorials** — load `generate-tutorials` for implement-a-real-app
   sittings that add the tests in the plan (including e2e when possible).
   Then **wait** and **check** as above.

The test plan from Step 5 is the scope. **Add e2e when possible** (a
user-visible flow). If e2e does not apply, say why and still add
unit/component tests for changed behavior.

Load `coding-best-practices` for every stack under test. If a stack file
has no Testing section, research official docs, add Testing to that file,
then follow it. If the repo has no runner, adding the recorded tools is
part of this step — do not skip with “no test framework.”

Tests from this ask must pass before Step 9. Then `graphify update .` if
present, then Steps 9–12.

When you implement application code, conventions:

- Load `coding-best-practices` for **every** language/stack this change writes. A React file does not skip SQL. If a stack is recorded there, follow it. If it is not, research the internet for the best practices, add them to coding-best-practices, then implement. Match names already in this repo; do not create empty folders.
- Explore with **graphify** before reading many files.
- Mimic the codebase's existing style, libraries, and patterns.
- Follow the **Behavioral Guidelines**. Every changed line must trace to
  the user's request and the plan's scope.
- **Use canonical terms from `docs/terminology.md`.** Identifiers, comments,
  and documentation are English. User-visible UI copy may use another
  language. Missing term → Step 3 first.
- Run lint / typecheck / existing tests if those commands exist (do not
  add new tests until the tests ask).
- **Never use git tools unless the developer has asked explicitly.**

Full sequence: `reference.md` → "Step 8: Implement or tutorials".

---

## Step 9: Log (AFTER implementation)

Every implementation produces or updates a **log** entry, written **after**
the code is done (logs are the implementation record; terminology, domain model,
and plan are the pre-implementation record). Store logs at
`docs/logs/<feature>.md` (flat — one file per feature); create it if it doesn't
exist, and maintain `docs/logs/index.md`.

Use the log format in `reference.md` → "Step 9: Log format" (plan
implementation status table, summary of changes, deviations from plan, files
touched, tests, recommended follow-ups) and the `docs/logs/index.md` format
there. **Record any steps the user chose to skip** (which step, and that the
user requested the skip) so the pipeline record is honest about what ran. **Rules:** one log file per feature, updated on each pass (no
`<feature>-v2.md`); omit empty sections; note deviations under `## Deviations
from plan` and ensure `plan.md` was updated in Step 7; update the
`docs/logs/index.md` row. **Never write the log before the code exists** —
that belongs in `plan.md`.

---

## Step 10: Repo README (AFTER implementation)

**Mandatory after implementation** when the change affects what a README
reader needs to know. Update `README.md` for changes to what the project is
or does, how to run/use/develop it, where docs live, **or** when README
product vocabulary conflicts with `docs/terminology.md`. Skip only with a
one-line note in the log ("No README changes needed") for internal
refactors, behavior-neutral bug fixes, or docs-only work that does **not**
leave the README using wrong product terms.

**Must follow README best practices** (name + one-line description; Getting
Started a clone can run; usage; configuration; links to `docs/`;
Development; Contributing; license; scannable; current; no boilerplate).
Do not point README at gitignored files or a developer learning path.
Full checklist: `reference.md` → "Step 10: Repo README format". One root
README; summary entry point only; update in place.

---

## Step 11: Architecture & Mechanisms (AFTER implementation)

Update architecture when stack/boundaries/topology/data flow/integrations
change; update mechanisms when subsystem runtime behavior changes. Else note
"No architecture/mechanism changes needed" in the log. Architecture =
decision; mechanisms = process. Formats in `reference.md` → "Step 11".

---

## Step 12: AGENTS.md Review (LAST step)

Re-read root `AGENTS.md` every time before declaring done. Verify: every
pipeline step ran; todos map to steps/docs; docs match implementation;
canonical terminology; no retroactive-only plan/spec; AGENTS.md current.
Fix gaps before done. Note AGENTS.md edits in the log.

---

## Failure Modes to Avoid (summary)

Full list in `reference.md` → "Failure Modes to Avoid." Never: use this
skill without confirmation; **run steps automatically without confirming or
skipping each one with the user**; write this skill into `AGENTS.md`; skip
Steps 0–7 before code or tutorials *on your own initiative*; skip either
Step 8 ask (app or tests); run Steps 9–12 before tests are done; skip e2e
when the change has a user-visible flow; put a developer learning path in
README or `docs/`; document gitignored paths; silent spec rewrite; skip
terminology/domain model/design (UI)/log *without the user asking*; dump the
tree instead of graphify (or skip asking to install the CLI); edit
terminology or use git without an explicit ask; stale README when Step 10
applies; hand-patch delegate output; skip AGENTS.md review *unasked*.

**Not a failure:** skipping a step because the **user** asked to. An explicit
user skip overrides the gate — honor it and record it in the log.

## Additional resources

- Templates, Step 0 AGENTS.md, Step 9–11 formats: [reference.md](reference.md)
- Step 8 implement or tutorials, graphify, committed docs: [reference.md](reference.md)
