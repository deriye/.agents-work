# generate-explanations — Reference

Detailed Diátaxis explanation rules for the `generate-explanations` skill. The
lean `SKILL.md` holds workflow, voice, file structure, and the publish
checklist. Read this file before writing or reviewing explanation. Apply every
principle. Skip none.

When this file and Diátaxis disagree, Diátaxis wins. Source:
[Diátaxis — Explanation](https://diataxis.fr/explanation/) and
[The difference between reference and explanation](https://diataxis.fr/reference-explanation/).

---

## 1. What explanation is (and is not)

| Explanation **is** | Explanation **is not** |
|---|---|
| A discussion *about* a topic | A tutorial the reader completes by doing |
| Reflection after (or away from) practice | Steps for a real-world task |
| Context, history, reasons, and implications | A catalogue of APIs, flags, or schemas |
| Connections that join fragments of knowledge | Isolated facts the reader looks up while working |
| Bounded by a *why* or a reasonable area of knowledge | An encyclopaedia of everything related |
| Higher and wider than the user's eye-level work | Instruction, recipes, or “do this next” |
| Something one could read away from the product | Something one needs with the product open |

**The unfolding is not the instructing.** Explanation reveals what was implicit or obscured. It weaves a web that holds the rest of the craft together. Without it, knowledge stays loose, fragmented, and anxious. Understanding does not *come from* explanation alone, but explanation is required to form that web.

Do not write “In this explanation you will learn…”. That is a tutorial pose. Frame the topic as something to consider:

> This article is about why retrieval-augmented generation exists, what problem it answers, and what it costs.

A title should accept an implicit (or explicit) *About*: *About user authentication*, *About chunking in RAG*, *About agent harnesses*.

---

## 2. Distinction from reference

Explanation and reference both contain theoretical knowledge. Neither contains steps. Conflating them is the failure Diátaxis warns against on this axis. See [Reference and explanation](https://diataxis.fr/reference-explanation/).

| | Explanation (study) | Reference (work) |
|---|---|---|
| User need | Acquire understanding | Apply knowledge correctly |
| Audience | Someone who has stepped away from the work | Someone in the middle of a task |
| Question | *Can you tell me about…?* | *What exactly is…?* |
| Stance | Discursive, perspectival, connective | Neutral, complete, uninterpreted |
| Form | Discussion around a topic | Description of the machine as it is |
| Typical shape | Prose that circles the subject | Lists, tables, signatures, schemas |
| Opinion | Allowed and often required | Out of place |
| When to read | Away from the product | While using the product |

Complexity does not decide the type. An explanation may be advanced; reference may be elementary. The test is **study vs work**.

If the reader would turn to the page *while executing a task*, it is not explanation. Write reference (or a how-to) instead. If they would turn to it after closing the laptop, to think, it is explanation.

Do not sprinkle explanation into reference, or dump reference into explanation. Expansive examples in a reference page that start answering *why* or *what if* have slipped into the wrong form. Instruction that creeps into explanation has likewise slipped.

---

## 3. The writer’s contract

Explanation sits at a distance from the practitioner's immediate work. That distance is not a defect. It is the point. The material is less *urgent* than a tutorial, how-to, or reference; it is not less *important*.

The writer’s job is to:

1. **Bound the topic** — a real or imagined *why* is a good prompt; otherwise draw a line around a reasonable area and stop there.
2. **Unfold** — bring to light design decisions, history, constraints, and implications that were hidden in the folds.
3. **Connect** — join this topic to neighbouring ones, even outside the immediate subject, when that helps understanding.
4. **Open the subject** — consider alternatives, counter-examples, and other standpoints. Do not close it as a single correct recipe.

You are not responsible for the reader’s next successful action. You *are* responsible for a discussion they can hold onto: coherent, situated, and honestly perspectival.

Open-endedness is the characteristic risk. Tutorials are bounded by what the learner must do, how-tos by the task, reference by the machine. Explanation has none of those rails. Invent a *why*, or accept a finite perimeter, and be satisfied.

---

## 4. Temptations that break explanation

Resist these. They turn the discussion into a different kind of document:

- **Instruction** — “First install… then run…” belongs in a tutorial or how-to. A historical recipe as an *example* is allowed; a procedure the reader is expected to follow is not.
- **Reference dump** — exhaustive APIs, flag tables, and error catalogues belong in reference. Mention a concrete example; do not become the catalogue.
- **Unbounded coverage** — the urge to “cover the topic” swallows neighbouring instruction and description. Draw the line.
- **A single correct way** — explanation must weigh alternatives. One-path certainty is a tutorial or how-to voice.
- **Learning-outcome framing** — “By the end you will be able to…” is a lesson. Explanation does not graduate the reader.
- **Neutrality as a pose** — withholding judgement because “documentation should be objective” leaves the topic unopened. State a perspective and show the others.

Explanation tends to absorb other modes. Keep it closely bounded so instruction and description remain visible in the places they belong.

---

## 5. Required principles

Apply every principle below. Skip none.

### 5.1 Talk *about* the subject

Write *around* the topic, not *through* a procedure. Discuss the bigger picture, history, choices, alternatives, possibilities, and *why* — reasons and justifications.

If you cannot put *About* in front of the title without it sounding odd, the piece is probably a how-to or a tutorial in disguise.

### 5.2 Start from a *why* (or a drawn boundary)

Use a real or imagined *why* as the prompt: *Why do we chunk documents? Why isolate tools in a sandbox? Why keep memory outside the context window?*

If no *why* is available, mark a reasonable area of knowledge and stay inside it. Do not wander until every adjacent idea has been mentioned.

### 5.3 Provide context

Explain why things are so: design decisions, historical reasons, technical constraints. Draw implications. Use specific examples as illumination, not as steps to copy.

Context is what makes isolated facts hold together. Without it, the reader has information and no grasp.

### 5.4 Make connections

Weave a web. Link this topic to neighbouring concepts, to other systems, even to things outside the immediate subject, when the analogy or contrast helps.

An isolated explanation is a lecture. A connected one is understanding.

### 5.5 Admit opinion and perspective

All craft is invested in beliefs and choices. Say so. Understanding comes from a standpoint; other standpoints exist.

Consider alternatives, counter-examples, and contrary opinions. Weigh them. You are opening the topic for consideration, not issuing a decree.

### 5.6 Keep explanation closely bounded

Do not absorb instruction or technical description “for completeness”. Those already have homes. Letting them in interferes with the explanation *and* hides them from the place the reader will look when they need them.

A short factual mention plus a link to reference is allowed. A reference section is not. A one-line pointer to a tutorial is allowed. A walkthrough is not.

### 5.7 Circle the subject

Approach the topic from more than one direction: historical, technical, analogical, critical. A single angle is usually reference in prose clothing, or a how-to with the steps removed.

### 5.8 Write for reflection, not for the next keystroke

The reader should be able to follow the piece away from the product. If a paragraph only makes sense with the IDE open, it has slipped into work-oriented writing.

Success is a change in how they *think about* the craft. It may or may not be immediately applicable the next time they sit down to work. That delay is correct.

### 5.9 Use examples as light, not as a path

Examples illustrate a claim, a trade-off, or a historical practice. They are not a sequence the reader must reproduce. If removing the “run this” implication would collapse the section, it was instruction.

### 5.10 Stay on one topic

One explanation, one bounded area. Related topics get their own pieces and links. A mega-essay that “also covers setup, the API, and a worked example” is four Diátaxis types glued together.

---

## 8. What belongs outside the explanation

| Need | Put it in |
|---|---|
| A guided first success, one path, visible results | Tutorial |
| Getting a real task done, with variants | How-to guide |
| Exact APIs, flags, schemas, error codes, lists of parts | Reference |
| “You will learn X, Y, Z” | Nowhere (do not use this pattern) |
| Install steps, copy-paste commands as the main path | Tutorial or how-to |

A sentence of fact plus a link to reference is allowed. A reference table is not. A nod to “when you are ready to try this, see the tutorial” is allowed. The try-this itself is not.
