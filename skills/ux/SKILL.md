---
name: ux
description: >-
  Evaluate and improve usability using Jakob Nielsen's 10 heuristics, Nielsen
  severity ratings (0–4), interaction design, UX writing, and WCAG accessibility.
  Use when reviewing UX, auditing an interface, conducting a heuristic evaluation,
  judging usability, writing or fixing microcopy, error messages, empty states,
  forms, focus, keyboard access, or when the user mentions Nielsen, NN/g, heuristics,
  usability problems, or accessibility.
---

# UX

Judge **how the product behaves for a person doing a task**. Looks are secondary.
Visual craft belongs to `frontend-design` / `huashu-design`. This skill owns
usability, interaction, copy, and access.

Heuristics and severity come from Jakob Nielsen / Nielsen Norman Group. Credit:
[Ten usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/).
You may use the heuristics in your own work; do not paste NN/g articles verbatim.

If the target repo has `AGENTS.md` or `docs/terminology.md`, follow those for
vocabulary and process. This skill does not replace a development pipeline.

## Modes

| User intent | Do this |
|---|---|
| Review / audit / “is this usable?” | Evaluate → report. Do **not** change code unless asked. |
| Improve / fix UX | Evaluate → agree scope → implement → verify. |
| New UI | Design against the heuristics **before** coding; then implement. |
| Copy only | Load [writing.md](writing.md). |

Default: **report first**. Heuristic evaluation is an inspection method, not a
license to restyle the product.

## Workflow

1. **Scope.** Name the user, the job, the device, and the flow. Prefer one
   task on one surface (NN/g: narrow scope). If unknown, state assumptions.
2. **Walk the task.** First pass: learn the flow. Second pass: inspect. Cover
   empty, loading, sparse, dense, error, permission, and success — not only
   the happy path. Use the running UI when a browser is available.
3. **Inspect all 10 heuristics.** Use the table below. For probes and examples,
   read [nielsen-heuristics.md](nielsen-heuristics.md).
4. **Also check** interaction, writing, and access (load the matching file
   when the surface needs it):
   - Controls, forms, focus, motion, URL → [interaction.md](interaction.md)
   - Labels, errors, empty states, tone → [writing.md](writing.md)
   - Keyboard, names, contrast, semantics → [accessibility.md](accessibility.md)
5. **Rate severity after listing problems**, not while hunting. Use Nielsen’s
   0–4 scale and the three factors (frequency, impact, persistence).
6. **Report** with the template below. Heuristics are guidelines, not laws;
   a violation is a candidate issue. Context can justify a tradeoff — say so,
   and do not bet the design is a rare exception (Nielsen).
7. **This method does not replace user research.** Flag what you still need
   to see a person do.

Independent evaluation first: do not let an existing mock, brand PDF, or
another agent’s aesthetic direction override a usability failure.

## Nielsen’s 10 heuristics

Source: [NN/g](https://www.nngroup.com/articles/ten-usability-heuristics/).
Names and definitions follow that page (updated 2020; heuristics unchanged
since 1994).

| # | Heuristic | Fail if… |
|---|---|---|
| 1 | Visibility of system status | The person cannot tell what just happened, what is selected, or what the system is doing. |
| 2 | Match between the system and the real world | Copy, order, or icons use internal jargon or fight the user’s mental model. |
| 3 | User control and freedom | No clear way out, undo, cancel, or back; easy to get trapped. |
| 4 | Consistency and standards | Same action has different names or patterns; fights platform conventions. |
| 5 | Error prevention | Slips and mistakes are easy; destructive actions lack a check; bad defaults. |
| 6 | Recognition rather than recall | Needed options, labels, or prior choices are hidden; memory is required. |
| 7 | Flexibility and efficiency of use | Experts cannot go faster; frequent actions cannot be accelerated. |
| 8 | Aesthetic and minimalist design | Extra chrome, clutter, or decoration competes with the task. |
| 9 | Help users recognize, diagnose, and recover from errors | Errors are coded, blamed, delayed, or give no next step. |
| 10 | Help and documentation | The UI needs a manual that is not searchable, in-context, or stepwise. |

Inspect **every** heuristic. Do not stop after the first three.

## Severity (Nielsen 0–4)

Source: [How to rate the severity of usability problems](https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/).

Severity combines **frequency** (rare vs common), **impact** (easy vs hard to
overcome), and **persistence** (once vs every time). Optionally note business
or trust impact.

| Score | Meaning |
|---|---|
| 0 | Not a usability problem |
| 1 | Cosmetic — fix if time |
| 2 | Minor — low priority |
| 3 | Major — high priority |
| 4 | Catastrophe — fix before release |

A single evaluator’s ratings are noisy (Nielsen). Say so. Prefer fewer, sharper
findings over a laundry list of 1s.

**Ship bar:** do not treat a 4 as optional. Several 3s on the primary task
usually block “done.”

## Report template

```markdown
# UX review: [surface / flow]

**User:** …
**Job:** …
**Device / context:** …
**Assumptions:** …

## Verdict
[One paragraph: can they finish the job? What blocks them?]

## Findings
| ID | Severity | Heuristic | Evidence | Why it hurts | Fix |
|----|----------|-----------|----------|--------------|-----|
| F1 | 3 | #5 Error prevention | [file:line or screenshot] | … | … |

## Strengths
- …

## Copy notes
- …

## Access notes
- …

## Still needs a person
- [What heuristic inspection cannot prove]
```

Evidence must be specific (control, state, file:line, or what you clicked).
“Feels off” is not a finding.

## Implement (only if asked)

Fix **3s and 4s** first. Do not restyle as a substitute for a usability fix.

- Prefer native controls (`button`, `a`, `label`, `input`) over ARIA theatre.
- Keep the user’s input; never wipe a form because validation failed.
- Match platform patterns unless the repo’s design system already defines one.
- Verify the same flow in the browser: keyboard-only, empty, error, success.
- If you changed UI behavior, hunt regressions on other screens that share
  that state or component.

## Anti-patterns for the agent

- Rewriting visual language when the request was a usability review.
- Inventing features to “delight” instead of clearing the task.
- Error copy that blames the user (`invalid`, `illegal`) or shows raw codes.
- Blocking paste, disabling zoom, or using `div`+click as a link.
- Color-only status (filter chips, validation, required fields).
- Premature inline errors on blur of an empty field.
- Skipping empty/error/loading states because the happy path looks fine.

## Sources

Load [sources.md](sources.md) for NN/g URLs and the other skills this draws from.
When a Nielsen article would change a finding, fetch the live page rather than
trusting memory.
