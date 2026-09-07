---
name: generate-tutorials
description: >-
  Generate and review Diátaxis tutorials: one sitting, one path, visible
  results, and course.md structure. Two purposes: learn only (standalone) or
  implement a real app (sequential, same product). Use when writing, editing,
  or reviewing a tutorial, lesson, sitting, or course.md. Code layout follows
  coding-best-practices for every stack the sitting writes (not one primary
  stack); if a stack is not there, research and add it to that skill first.
  Do not use for how-to guides, reference, or conceptual explanation.
---

# Generate Tutorials

Write and review **learning-oriented** Diátaxis tutorials. A tutorial is a
practical activity under the guidance of a tutor.

Two purposes appear in this repository. Decide the purpose **before** writing.
It changes whether the sitting must stand alone.

| Purpose | What we are doing | Standalone? |
|---|---|---|
| **Learn only** | Study a skill. The artefact may be thrown away. | Yes. Recreate everything in this sitting. |
| **Implement a real app** | Add functionality to the product we will keep. | No. Continue the same repository and the same program. Name the previous tutorial in this series as a prerequisite. |

The purpose is not to help the reader choose among real-world variants. That is still a how-to guide. An implementation tutorial stays one path, one sitting, one finished result — it just grows the app instead of starting over.

Load this skill when authoring or reviewing a tutorial. Apply every principle
in [reference.md](reference.md). Skip none. Where a principle splits by
purpose, follow the branch that matches the sitting. Before writing copy-paste
code, load [coding-best-practices](../coding-best-practices/SKILL.md). The
author checklist is the gate before publishing.

## When to use

Use this skill when the user:

- Asks to write, generate, edit, or review a tutorial, lesson, sitting, or `course.md`
- Wants a guided one-path sitting: visible results, copy-paste steps
- Wants either a **learn only** lesson or an **implement a real app** sitting in a series
- Is working in a courses repository whose lessons live in `course.md`

## When not to use

Do not blend modes. Classify first:

- **Explanation** (why, context, alternatives, “about …”) → load `generate-explanations` instead
- **How-to** (real-world task, variants, *if this then that*) → stop. Do not stretch a tutorial to cover it. There is no how-to skill yet. An implementation tutorial is still a tutorial; it is not a how-to just because the artefact is the real app
- **Reference** (APIs, flags, schemas, error catalogues) → stop. There is no reference skill yet

If the reader must already know the right question, or must choose among
real-world variants, it is not a tutorial.

## Workflow

1. **Decide purpose.** `learn only` or `implement a real app`. State it on the first line after the title. Do not write until this is settled.
2. **Classify.** Confirm the request is a guided one-path sitting, not unsupervised work with variants. If not, follow “When not to use”.
3. **Read [reference.md](reference.md)** before writing: what a tutorial is, the teacher’s contract, required principles (5.1–5.12), and code rules (8.1–8.6). Follow the branch that matches the purpose.
4. **Load [coding-best-practices](../coding-best-practices/SKILL.md)** for **every** language/stack whose snippets this sitting contains **before** writing copy-paste code. A React file does not skip SQL. If a stack is in that skill, follow it. If it is not, research the internet for the best practices, add them to coding-best-practices, then write that stack’s snippets against the file you added. See reference.md §8.5.
5. **Write or edit** `course.md` under gitignored `tmp/` unless the developer asked to commit it. Do not update README or `docs/` to mention the sitting.
6. **Run the author checklist.** If any box fails, the document is not yet a tutorial this repository will accept — fix it before declaring done.

Do not write “In this tutorial you will learn…”. That is presumptuous. State what we will **accomplish**.

## Language

Use this voice throughout.

| Pattern | Why |
|---|---|
| **We…** | First-person plural: tutor and learner together. |
| **In this tutorial, we will…** | Name the accomplishment, not the learning outcomes. |
| **First, do x. Now, do y. Now that you have done y, do z.** | Imperative, unambiguous, sequential. |
| **We must always do x before we do y because…** (link to explanation) | Minimal reason, then move on. |
| **The output should look something like…** | Narrative of the expected. |
| **Notice that… Remember that… Let’s check…** | Orient them; confirm they are on track. |
| **You have built…** | Mildly admire what they accomplished. |

No room for “you might”, “feel free to”, “there are several ways”, or “as an exercise, try to figure out”.

**Repository language:** Follow the **target repository’s** language rules (`AGENTS.md`, `docs/terminology.md` if they exist). Tutorial narration, titles, comments, and identifiers match those rules. User-visible UI copy in snippets uses the product’s UI language. Canonical terms and proper names come from that repo’s terminology — do not invent translations. When pointing at the screen, quote the UI.

## Structure of a tutorial

Each course lives in `course.md`. Keep the learning journey end-to-end; a change in one step often cascades through the whole story.

State the purpose on the first line after the title: `**Purpose:** learn only` or `**Purpose:** implement a real app`.

### Opening

- Title names the accomplishment (what we will build or do), not a topic label.
- One-line **Summary** of the finished result — one product, not a list of capabilities.
- **Prerequisites**
  - Learn only: tools and environment the lesson will *not* teach. Prefer none. Never list another tutorial.
  - Implement a real app: the previous tutorial in this series (if any), plus tools the series has not taught yet.
- **Estimated time** so they can commit to the sitting.
- Do not list learning objectives.

### Body

- Numbered steps. Each step is one concrete action (or a tight cluster) with a visible result.
- Commands and code the learner can copy and run as written. An edit to an existing file is a fenced block, not a sentence that describes the edit. See reference.md §8.6.
- Expected output immediately after actions that produce it.
- A short **checkpoint** after each step: what they should now have in front of them.
- Links to explanation or reference are optional asides, never the main path.

### Closing

- Name what they have built.
- Stop. Do not append “next steps”, alternative approaches, or a conceptual recap. If they want more, that is another tutorial, a how-to, or an explanation.

## Author checklist

Before publishing, confirm:

- [ ] Purpose is stated: **learn only** or **implement a real app**.
- [ ] Opens with what **we will accomplish**, not what they will learn.
- [ ] Teaches one thing well: one product, named in the title, the opening, and Done.
- [ ] Standalone if purpose is learn only: a clean-start learner can finish without any other tutorial.
- [ ] Sequential if purpose is implement a real app: continues this repository; names the previous tutorial; uses the real product, not a dummy.
- [ ] One path only: no optional tracks, no “or you can instead”.
- [ ] Every step has a visible, named result.
- [ ] Expected output (or a clear description of it) appears after actions.
- [ ] Likely failure signs are flagged where you know them.
- [ ] The text points out what to **notice**, not only what to **do**.
- [ ] Explanation is one clause plus a link, or absent.
- [ ] No general theory before the concrete case.
- [ ] Steps are copy-paste reliable; versions and filenames are pinned.
- [ ] Every change to an existing file is a fenced block the learner can copy (types, queries, maps, JSX). Do not describe an edit in prose only. A later snippet must not assume a type or import that was only named in a sentence. See reference.md §8.6.
- [ ] Distinct pieces of work have names; code is split into files following `coding-best-practices` for **every** stack in the sitting (if a stack was not there, you researched the internet and added it to that skill first); there is no one-file blob of several jobs and no extra architecture.
- [ ] Later steps edit the same program; a weak version is replaced before the end.
- [ ] Encodings, paths, versions, seeds, and limits are explicit; resources close.
- [ ] Failures this step can hit are visible; missing values are guarded; printed results are inspectable.
- [ ] A learner who only follows directions can finish without prior domain knowledge beyond stated prerequisites.
- [ ] The ending names the thing they built and does not morph into a how-to or lecture.
- [ ] Voice is **we** + imperative **do**.
- [ ] Narration, comments, and identifiers follow the target repo’s language rules; UI copy in snippets uses the product UI language; proper names stay as that repo’s terminology writes them.
- [ ] You (or someone else) have actually run the tutorial from a clean start (learn only) or from the previous sitting’s files (implement a real app).
- [ ] After that run succeeded, throwaway verification artefacts have been removed. Product files stay if the purpose is to implement a real app.
- [ ] Committed README/`docs/` were not updated to mention this sitting, a catalogue, or any gitignored path.

If any box fails, the document is not yet a tutorial that this repository will accept.

## Tutorials are not repo docs

Sittings you write so the developer can implement the app are **private**.
Default location: gitignored `tmp/` (for example `tmp/tutorials/…`).

Do **not** write them into committed product docs:

- Not `README.md` (Getting Started is clone, install, run)
- Not `docs/` (spec, plan, log, architecture, mechanisms, domain model)
- Not `docs/terminology.md` (do not add tutorial or catalogue product terms unless
  the developer explicitly asks)

A clone never has `tmp/`. Linking it from README or spec is a broken link
for everyone else.

When the purpose is **implement a real app**, the sitting grows the product
files. If this skill was called from `software-development` Step 8, **stop
after the sittings exist.** Do not write spec, plan, log, or README. Sittings
may be for application code or for tests (the orchestrator asks separately).
The orchestrator waits until the developer says they are done, **checks**
the tree against the sittings and plan, then continues (tests ask after app
sittings; Steps 9–12 after test sittings only if that check passes).

If this skill was used **standalone**, do not start `software-development`
until the user confirms that skill. That run still does Steps 0–7 first,
then asks implement vs tutorials at Step 8.

## After the developer is done

When they say they are done, hand back to `software-development` for the
**tutorial check**. Do not inspect-and-patch on your own, and do not skip
the check. That skill decides whether the next gate is the tests ask or
Steps 9–12.
See [software-development](../software-development/SKILL.md).

## Additional resources

- Principles, teacher’s contract, code rules: [reference.md](reference.md)
- Language/stack layout and hooks: [coding-best-practices](../coding-best-practices/SKILL.md)
- After the developer is done: [software-development](../software-development/SKILL.md) (check, then tests ask or Steps 9–12)
