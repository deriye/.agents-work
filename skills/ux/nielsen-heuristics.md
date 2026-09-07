# Nielsen’s 10 usability heuristics — inspection probes

Canonical article:
[10 Usability Heuristics for User Interface Design](https://www.nngroup.com/articles/ten-usability-heuristics/)
(Jakob Nielsen; names/descriptions updated 2020 by NN/g; heuristics stable since 1994).

How to run the method:
[Heuristic Evaluations: How to Conduct](https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/).

Paraphrase for inspection. Credit Nielsen / NN/g. Do not paste NN/g articles.

A heuristic **violation is a candidate issue**. NN/g: context can justify a
tradeoff (e.g. a hamburger menu vs recognition). Do not assume the design is
one of the rare exceptions without evidence.

## 1. Visibility of system status

The design should always keep users informed about what is going on, through
appropriate feedback within a reasonable amount of time.

**Probes**

- Does every consequential action get immediate feedback (save, filter, send, delete)?
- Are pending, success, and failure visible — not only a spinner that never resolves?
- Can the person answer “where am I, what is selected, what happens next?”
- Do filters, tabs, and modes show the current state without opening a menu?
- After async work, is the new state announced (and not only a color change)?

**Typical 3–4:** silent save failure; filter applied with no result count; submit
button that does nothing for seconds.

## 2. Match between the system and the real world

Speak the users’ language. Familiar words and concepts, not internal jargon.
Natural mapping; logical order.

**Probes**

- Would a new user in this role understand every label without a glossary?
- Do names match the domain the *user* uses, or the database / org chart?
- Is information ordered the way the task unfolds?
- Do icons mean what they look like, or do they need a legend?

**Typical 3–4:** staff tool using engineering identifiers as the only name;
destructive “OK” on a dialog whose title is jargon.

## 3. User control and freedom

People err. They need a clearly marked emergency exit without an extended process.
Undo/redo; Cancel; discoverable way out.

**Probes**

- Can they cancel mid-flow without losing the rest of their work?
- Is there undo for reversible actions, and confirm-or-undo for destructive ones?
- Does Escape close overlays, and does focus return to the trigger?
- Can they get back from detail to list without resetting filters?
- Are they trapped in a modal with no obvious close?

**Typical 3–4:** wizard with no back; overlay with no close; navigation that
wipes query state.

## 4. Consistency and standards

Same words, situations, and actions should mean the same thing. Follow platform
and industry conventions (Jakob’s Law: people spend more time in *other* products).

**Probes**

- Internal: one pattern for primary action, one for danger, one for filters?
- External: links look like links; buttons look like buttons; search is where
  people expect search?
- Does the same data use the same format everywhere (dates, money, names)?

**Typical 3–4:** primary action is a link on one screen and a button on another;
clicking a row sometimes navigates and sometimes selects.

## 5. Error prevention

Better than a good error message: prevent the problem. Slips (inattention) vs
mistakes (wrong mental model). Constraints, defaults, confirmations for costly acts.

**Probes**

- Are destructive actions confirmed, or undoable with a safe window?
- Do defaults match the common case?
- Are easy slips blocked (accidental double submit, send without required files)?
- Is paste allowed? Is valid-looking input not silently truncated?
- Are constraints visible *before* submit (required, limits) without punishing exploration?

**Typical 3–4:** delete with no undo or confirm; submit disabled with no
explanation; data loss on refresh.

## 6. Recognition rather than recall

Minimize memory load. Options, actions, and needed information should be visible
or easy to retrieve. Humans have limited short-term memory.

**Probes**

- Are field labels visible when the field is filled (not placeholder-only)?
- Must they remember values from a previous step that the UI could show?
- Are recent items, suggestions, or current filters visible?
- Is key navigation hidden behind an unmarked control?

**Typical 3–4:** placeholder-only labels; multi-step form that hides earlier
answers; filters that cannot be seen once applied.

## 7. Flexibility and efficiency of use

Accelerators for experts, hidden from novices. Tailor frequent actions.
Multiple ways when the task is frequent.

**Probes**

- Keyboard: can a repeat user complete the main task without the mouse?
- Does Enter submit the obvious single-field form?
- Are frequent actions (search, filter, new item) one click or fewer?
- Power-user paths must not be the *only* path.

**Typical 2–3:** no keyboard path on a daily staff tool; extra wizard steps
that cannot be skipped. Catastrophe only if the only path is unusable.

## 8. Aesthetic and minimalist design

Do not show information that is irrelevant or rarely needed. Extra units compete
with what matters. Not “flat design” — focus on the task.

**Probes**

- What can you remove without hurting the job?
- Does decoration, surplus stats, or extra chrome steal attention from the
  primary action?
- Is hierarchy obvious: one primary action per view?
- Does dense data (tables) still have a scannable first column and restrained
  secondary data?

**Typical 2–3:** competing CTAs; dashboard ornaments. Raise severity if clutter
hides the only path forward.

## 9. Help users recognize, diagnose, and recover from errors

Plain language (no codes), precise problem, constructive next step. Visible
treatment so the message is noticed.

See [writing.md](writing.md) for copy rules. NN/g:
[Error-Message Guidelines](https://www.nngroup.com/articles/error-message-guidelines/).

**Probes**

- Is the message next to the source, not only in a toast across the page?
- Does it say what happened and what to do, without blame?
- Is input preserved?
- Are errors timed after a real mistake, not on exploring an empty field?

**Typical 3–4:** “Error 500”; silent validation; form wipe; color-only error.

## 10. Help and documentation

Best if none is needed. When needed: searchable, task-focused, concise, concrete
steps, in context at the moment of need.

**Probes**

- Can inline help replace a manual for this task?
- Is help next to the confusing control, not only in a distant FAQ?
- Do empty states tell the next step, not only “nothing here”?

**Typical 2–3:** opaque control with no explanation. Raise if the task cannot
be completed without undocumented knowledge.

## Mapping extra checks onto the 10

Do not invent an 11th–15th heuristic. Fold common extras in:

| Extra concern | Heuristic |
|---|---|
| Affordances / “is this clickable?” | #4, #6 |
| Structure / grouping | #2, #8 |
| Color-only status | #1, #9 + [accessibility.md](accessibility.md) |
| Forgiving inputs | #3, #5 |
| Content / microcopy | #2, #9, #10 + [writing.md](writing.md) |
