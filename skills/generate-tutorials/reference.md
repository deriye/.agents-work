# generate-tutorials — Reference

Detailed tutorial rules for the `generate-tutorials` skill. The lean
`SKILL.md` holds workflow, purpose, voice, `course.md` structure, and the
publish checklist. Read this file before writing or reviewing a tutorial.
Apply every principle. Skip none. Where a principle splits by purpose, follow
the branch that matches the sitting.

Source: [Diátaxis — Tutorials](https://diataxis.fr/tutorials/) and
[The difference between a tutorial and how-to guide](https://diataxis.fr/tutorials-how-to/).

When this file and Diátaxis disagree about a **learn only** tutorial, Diátaxis wins.

When the purpose is to **implement a real app**, section 5.11’s sequential rule is the house rule: the sitting does not have to be standalone. Every other Diátaxis rule in this file still applies.

---

## 1. What a tutorial is (and is not)

| A tutorial **is** | A tutorial **is not** |
|---|---|
| A lesson the learner completes by doing | A how-to guide with forks and variants |
| An experience that builds confidence | An explanation of how something works |
| One sitting with a managed path to a successful result | A catalogue of options, APIs, or alternatives |
| Concrete: *this* action, *this* result | Abstract: general patterns, theory, “it depends” |
| The teacher’s responsibility for success | The learner’s responsibility to already know what to ask |
| Standalone **when the purpose is to learn only** | A sequel **when the purpose is to learn only** |
| Sequential **when the purpose is to implement a real app** | A dummy example that is not the product **when the purpose is to implement a real app** |

**The doing is not the learning.** In a learning tutorial, the learner builds a working thing so they can acquire names, tools, workflows, and the *feeling of doing*. In an implementation tutorial, they build the product itself so they can keep it.

Do not write “In this tutorial you will learn…”. That is presumptuous. State what we will **accomplish**:

> In this tutorial, we will create and deploy a scalable web application. Along the way we will encounter containerisation tools and services.

---

## 2. Distinction from a how-to guide

Tutorials and how-to guides both give steps. They serve different needs. Conflating them is the most common documentation failure Diátaxis warns against. See [Tutorials and how-to guides](https://diataxis.fr/tutorials-how-to/).

| | Tutorial (study or guided implementation) | How-to guide (work) |
|---|---|---|
| User need | Acquire skill, or add one named capability to the app under guidance | Accomplish a task, choosing among variants |
| Audience | Learner (any skill level) | Already-competent practitioner |
| Path | One line, no forks | Branches: *if this, then that* |
| Setting | Learning: contrived and repeatable. Implementation: this repository, this product. | The real world, any project |
| Unexpected | Eliminated | Prepared for |
| Responsibility | The teacher | The user |
| Language | Concrete and particular | General |
| Safety | Learning: always possible to start again. Implementation: we edit the same program; keep a reversible step where we can. | Often one chance |

Complexity does not decide the type. A tutorial may be advanced; a how-to guide may be basic. The test is **guided one-path sitting vs unsupervised work**.

If the reader must already know the right question, or must choose among real-world variants, it is not a tutorial. Write a how-to guide instead.

An implementation tutorial is still a tutorial. It is not a how-to guide just because the artefact is the real app.

---

## 3. The teacher’s contract

Nearly all responsibility falls on the author. The learner’s only job is to be attentive and follow directions. There is no obligation on them to understand, remember, or “figure it out”.

The exercise must be:

1. **Meaningful** — the learner has a sense of achievement.
2. **Successful** — they can complete it.
3. **Logical** — the path makes sense from step to step.
4. **Usefully complete** — they encounter every action, concept, and tool they need to become familiar with.

You cannot stand beside them. Design so that **things cannot go wrong** if they follow the steps. Test by watching real users do the tutorial; you will not find every gap yourself.

When the purpose is to **learn only**: after the run succeeds, remove the testing environment and the artefacts that run produced. The published lesson must leave a clean start.

When the purpose is to **implement a real app**: leave the product files in the repository. Remove only throwaway verification folders you created outside the app (for example under `tmp/_verify-*`).

---

## 4. Anti-pedagogical temptations

Resist these. They break the lesson:

- **Abstraction and generalisation** — patterns emerge from concrete work; do not start with them.
- **Explanation** — a tutorial is not the place for it. One short clause is enough; link out.
- **Choices** — one path, one command, one library, one way.
- **Information** — do not dump background the learner did not ask for.
- **Several accomplishments** — one sitting finishes one product, taught well. A second product is another tutorial.

The first rule of teaching: **do not try to teach**. Provide an experience through which they can learn. Only the pupil can learn.

---

## 5. Required principles

Apply every principle below. Skip none. Where a principle splits by purpose, follow the branch that matches the sitting.

### 5.1 Show where they will be going

Open by describing the finished result, in first-person plural. Let them picture the destination so each step feels like progress toward it.

### 5.2 Deliver visible results early and often

Every step must produce a comprehensible, meaningful result — however small. Understanding comes from connecting cause and effect. Do not stack several unseen actions before the first check.

### 5.3 Maintain a narrative of the expected

At every action the learner wonders: *did this work?* Answer that.

- “You will notice that…”
- “After a few moments, the server responds with…”
- Show actual or exact expected output.
- Flag likely mistakes: “If the output doesn’t show …, you have probably forgotten to…”
- Prepare them for surprises: “The command will probably return several hundred lines of logs.”

### 5.4 Point out what they should notice

Learners are too busy doing to observe. Close the learning loop in passing: a changed prompt, a new file, a number that grew. Observation is part of the craft.

### 5.5 Target the *feeling of doing*

Skill is joined-up purpose, action, thinking, and result. Tasks must tie those together so the work starts to feel like a confident rhythm — something they might want to repeat.

### 5.6 Encourage and permit repetition

Where possible, make a step reversible so they can run it again and see the same result. Repetition establishes the feeling of doing. Prefer operations they can undo over one-way traps.

### 5.7 Ruthlessly minimise explanation

They are focused on following directions. Explanation distracts and blocks learning.

Enough:

> We’re using HTTPS because it’s more secure.

Then link to a separate explanation. Put theory where they can find it when *they* want it — not when you want to tell it.

### 5.8 Focus on the concrete

Stay on *this* problem, *this* action, *this* result. General patterns will emerge on their own. All learning moves from the particular toward the abstract; do not reverse that direction.

When the purpose is to implement a real app, the concrete case is the product: real names, real fields, real files. Do not invent a dummy stand-in.

### 5.9 Ignore options and alternatives

Do not mention other commands, other APIs, other approaches. Guide them to the conclusion. Everything else belongs in a how-to or reference.

### 5.10 Aspire to perfect reliability

Confidence is built layer by layer and is easily shaken. If they follow the steps and do not get the promised result, they lose confidence in the tutorial, the tutor, and themselves.

Pin versions, paths, and expected output. Avoid steps that depend on the learner’s machine, network, or prior knowledge unless you have already established those in the lesson (or, for an implementation tutorial, in a previous tutorial of the same series).

### 5.11 Standalone (learn only) or sequential (implement a real app)

**If the purpose is to learn only**, the tutorial is standalone.

A learner who has never seen this repository must be able to start from a clean environment and finish without having completed any other tutorial.

Do not require “the project from the previous course”, leftover files, or knowledge taught only elsewhere. If this lesson needs an artefact, recreate it here or ship it in this course folder. Prerequisites name tools and environment (Python, an API key), not other lessons.

A catalogue may list related tutorials. Each `course.md` still stands alone. Optional links to other lessons belong after they have already succeeded — never on the critical path.

**If the purpose is to implement functionality for a real app**, the tutorial is sequential.

It continues the same repository and the same program. Prerequisites name the previous tutorial in this series (and the tools that series already established). Do not recreate the app. Do not use a dummy project. Later sittings edit the files earlier sittings created.

The first tutorial in an implementation series creates the app in this repository. Every later tutorial starts from that app.

A catalogue lists the series in order. The order is the critical path.

### 5.12 Teach one thing well

A tutorial has one accomplishment. Early steps may set up the environment or produce a small result on the way, but the sitting finishes **one** product, taught thoroughly.

If the opening summary needs “and” to list two finished capabilities, write two tutorials.

When the purpose is to learn only, the second sitting recreates a small starting point.

When the purpose is to implement a real app, the second sitting starts from the files the first sitting left behind.

The title, the “In this tutorial, we will…” sentence, and the Done line name that same one thing.

---

## 8. Code the learner copies

The learner will imitate the snippets. Concrete is not the same as careless. Keep each program small and particular — and write it the way a careful practitioner would write a small program.

### 8.1 Name the pieces

Give each distinct piece of work a name. A function, a variable, a file — not one undifferentiated block when the step has several jobs.

When those pieces would live in separate files in a small, well-structured program in this language, put them in separate files. See 8.5.

Do not invent architecture the lesson does not need. Do not golf the code down to a trick either.

### 8.2 Grow the same program

When a later step adds a concern, change the code they already have. Do not paste a second copy of the whole program under a new name.

A weak or unsafe version is allowed only when the **next step replaces it**. Do not leave that version as the finished code.

In an implementation series, “the same program” means the product in this repository, across sittings.

### 8.3 Be explicit

Say the encoding, the path, the version, the seed, the limit. Do not rely on a default that differs across machines.

Name a number that appears in more than one place. Pass a value into a constructor rather than poking at internals afterwards. Open a resource in a way that closes it.

### 8.4 Fail in view

If this step can fail, show the failure. Catch the error that actually happens here. Do not swallow every error; do not let a missing value crash the rest of the sitting when a guard would do.

What they print or save should be a value they can read — the number, the string, the list they just made — not an opaque object they cannot inspect.

### 8.5 Split code into files

The learner will copy the layout as well as the lines. A working program dumped into one file teaches them to keep everything in one file.

Before writing snippets, load [`coding-best-practices`](../coding-best-practices/SKILL.md). Identify **every** language and stack this sitting writes (UI, SQL, CSS, tests — each counts). A file for one stack does not skip the others.

- For **each** stack that **is** in coding-best-practices, follow that file. Split the code into files the way it says (module boundaries and naming). Do not invent extra layers, folders, or packaging the sitting does not need.
- For **each** stack that **is not** in coding-best-practices, research the internet for the best practices. After that research, add them to coding-best-practices (see that skill’s “Adding a stack”). Then write that stack’s snippets against the file you added. Do not imitate an earlier sitting’s SQL (or other stack) instead of lookup.

Each file should hold one coherent job.

A first step may live in one file while there is only one job. The step that introduces a second job extracts it into a named file. Later steps edit those same files.

**Learn only:** do not introduce a file or layout whose *existence* is the product of a later sitting. Recreate the files this sitting needs.

**Implement a real app:** introduce only the files this sitting needs. Leave files from earlier sittings in place and edit them. Do not scaffold a second app next to the product.

### 8.6 Show the edit as code

The learner copies fenced blocks. They skip sentences that describe an edit.

When a later step changes a file that already exists, put the new code in a fenced block. Show whatever they must type: the type, the query, the map, the JSX. A sentence such as “Open `src/api.ts`. Add `createdAt` to `Row`” is not a step.

If the change is small, show the replacement fragment. If several places in the same file must stay in sync (type, `SELECT`, `RETURNING`, return object), show each fragment or the whole file. Do not leave one of those places as prose.

Do not split one change across a sentence and a later snippet that already assumes the sentence was done. If JSX reads `row.createdAt`, the `Row` type that includes `createdAt` is in a fenced block too — not only “Add `createdAt: string` to `Row`.”

---

## 9. What belongs outside the tutorial

| Need | Put it in |
|---|---|
| Why it works, concepts, rationale | Explanation |
| Exact APIs, flags, schemas, error codes | Reference |
| Getting a real task done, with variants | How-to guide |
| “You will learn X, Y, Z” | Nowhere (do not use this pattern) |
| How a clone runs the app | Repo `README.md` (product only — not this sitting) |
| Spec, plan, log, architecture | Product `docs/` via software-development (not a sitting catalogue) |

A sentence of rationale plus a link is allowed. A section of rationale is not.

Implementation sittings default to gitignored `tmp/`. Do not link that
folder (or `course.md`) from README, spec, plan, log, or terminology.
