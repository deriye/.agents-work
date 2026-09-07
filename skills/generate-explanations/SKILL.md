---
name: generate-explanations
description: >-
  Generate and review Diátaxis explanation: discursive, bounded, about a
  topic (why, context, alternatives). Use when writing, editing, or reviewing
  explanation.md, background, discussion, conceptual guides, or "about"
  material. Do not use for tutorials, how-to guides, or API/reference catalogues.
---

# Generate Explanations

Write and review **understanding-oriented** Diátaxis explanation. It is a
discursive treatment of a subject that permits **reflection**. Its purpose is
not to get the reader through a lesson, not to complete a task, and not to
look up a fact. Its purpose is to deepen and broaden understanding: to bring
clarity, light, and context.

The document does not have to be titled *Explanation*. *Discussion*,
*Background*, *Conceptual guide*, or *Topics* are valid names for the same
kind of writing.

Load this skill when authoring or reviewing explanation. Apply every principle
in [reference.md](reference.md). Skip none. The author checklist is the gate
before publishing.

## When to use

Use this skill when the user:

- Asks to write, generate, edit, or review explanation, background, discussion, a conceptual guide, topics, or `explanation.md`
- Asks *why* something is so, for context, history, trade-offs, or alternatives
- Wants an “about …” piece someone could read away from the product

## When not to use

Do not blend modes. Classify first:

- **Tutorial** (numbered steps, one path, `course.md`, “we will …”) → load `generate-tutorials` instead
- **How-to** (real-world task, variants, *if this then that*) → stop. There is no how-to skill yet
- **Reference** (APIs, flags, schemas, error catalogues while executing a task) → stop. There is no reference skill yet

If the reader would turn to the page *while executing a task*, it is not
explanation. If you cannot put *About* in front of the title without it
sounding odd, the piece is probably a how-to or a tutorial in disguise.

Do not write “In this explanation you will learn…”. That is a tutorial pose.
Frame the topic as something to consider.

## Workflow

1. **Classify.** Confirm the request is study (acquire understanding), not work. If not, follow “When not to use”.
2. **Read [reference.md](reference.md)** before writing: what explanation is, the writer’s contract, temptations, and required principles (5.1–5.10).
3. **Write or edit** the explanation file to the structure and language below. One topic, one *why* or drawn boundary.
4. **Run the author checklist.** If any box fails, the document is not yet Diátaxis explanation — fix it before declaring done.

## Language

Use this voice throughout.

| Pattern | Why |
|---|---|
| **The reason for x is that historically, y…** | Explain causes, not steps. |
| **W is better than z, because…** | Judgement is allowed; give the grounds. |
| **An x in system y is analogous to a w in system z. However…** | Context and connection. |
| **Some practitioners prefer w (because z). That can be a good approach, but…** | Weigh alternatives; do not hide them. |
| **An x interacts with a y as follows: …** | Unfold internals so *why it behaves* is visible. |
| **This is about…** | Name the topic, not the learning outcome. |
| **In this picture… From another angle…** | Circle the subject. |

Prefer discursive prose over numbered procedures. Imperative *do* is the tutorial/how-to voice; keep it out except inside a clearly marked historical or illustrative example.

Avoid “First, install…”, “Now run…”, “You will learn…”, “As an exercise…”, and exhaustive “the parameters are:”.

## Structure of an explanation

Each explanation lives in its own markdown file (for example `explanation.md` beside a related `course.md`, or a standalone topic file). It must make sense without the reader having just completed a tutorial — though it may assume they have *some* encounter with the craft, as reflection depends on something prior.

### Opening

- Title works with *About* in front of it. It names a topic, not an accomplishment and not a task.
- One or two sentences that state **what this is about** and the *why* or boundary that limits it.
- Optional: who this discussion is for (someone who has used the thing, or is ready to think about it) — not a list of tools to install.
- Do not list learning objectives, prerequisites-as-lessons, or estimated hands-on time.

### Body

- Prose organised by aspects of the topic (history, problem, trade-offs, alternatives, implications), not by numbered actions.
- Connections and analogies where they clarify.
- Concrete examples used as illustration.
- Explicit perspectives: a recommended view, and the views it is not.
- Links out to tutorials, how-tos, and reference for the work-oriented needs this piece must not swallow.

### Closing

- Restate the picture: what belongs together, what the main trade-off is, what remains a live disagreement.
- Stop. Do not append a tutorial, a how-to, or an API appendix. Optional links to related explanations or to the practical docs are enough.

## Author checklist

Before publishing, confirm:

- [ ] Title accepts *About …* and names a topic, not a task or an accomplishment.
- [ ] Opens with what this is **about**, not what the reader will learn or build.
- [ ] Bounded by a *why* or a stated perimeter; it does not try to cover everything nearby.
- [ ] Discusses context: history, design decisions, constraints, implications.
- [ ] Makes connections to other concepts or systems.
- [ ] Weighs alternatives, counter-examples, or other perspectives; opinion is visible and grounded.
- [ ] No numbered procedure the reader is expected to follow.
- [ ] No API/flag/schema catalogue; facts that must be exact live in reference and are linked.
- [ ] Examples illustrate; they are not a path to copy.
- [ ] Readable away from the product — a discussion, not a cockpit card.
- [ ] Voice is discursive (*why*, *however*, *some prefer*), not imperative *do*.
- [ ] Ending restates the picture and does not morph into a tutorial, how-to, or reference dump.

If any box fails, the document is not yet Diátaxis explanation.

## Additional resources

- Principles, writer’s contract, temptations: [reference.md](reference.md)
