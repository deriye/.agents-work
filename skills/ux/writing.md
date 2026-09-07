# UX writing

Words are part of the interface. Heuristic **#2** (language), **#9** (errors),
**#10** (help). Follow the target repo’s terminology file when one exists.

NN/g errors:
[Error-Message Guidelines](https://www.nngroup.com/articles/error-message-guidelines/)
and [Hostile Patterns in Error Messages](https://www.nngroup.com/articles/hostile-error-messages/).

## Quality bar

Each string should be **purposeful, clear, concise, and respectful**.

- Say what the person can do, not how the system is implemented.
- One idea per sentence. Prefer verbs on actions (`Save`, `Filter`, `Delete`).
- Specific over generic (`Save foundation` > `Continue` > `OK` > `Submit`).
- Sentence case for UI chrome unless the product already uses another convention.
- No exclamation marks in routine UI. No humor in errors (it goes stale).
- Do not blame the user. Avoid `invalid`, `illegal`, `you forgot`.
- Do not ship developer schema: `uuid`, `null`, HTTP codes, stack traces.

UI language is whatever the product’s users read. Identifiers, files, comments,
and docs stay in the repo’s code language. Do not mix them.

## Errors (#9)

| Do | Don’t |
|---|---|
| Put the message next to the field | Only a remote toast |
| What happened + what to do | `An error occurred` |
| Preserve typed input | Wipe the form |
| Redundant cue: text + icon + field border | Color alone |
| Error styling only for real errors | Red on optional hints |
| Show after a real mistake | Error on blur of an empty field |
| Modal only when they must stop | Modal for a typo |
| Human language; codes for diagnostics only | `ERR_VALIDATION_3` as the title |

**Constructive:** if you can offer a one-click fix (matched city for a ZIP,
retry, restore draft), offer it.

**Hostile (NN/g):** premature errors, error styling on non-errors, piling
asterisk + red outline + inline message on an untouched required field.

## Empty states (#1, #10)

An empty view is a moment of help, not a blank card.

- Say why it is empty (none yet, filter too tight, no permission, error).
- Give the next step (`Clear filters`, `Add …`, `Change dates`).
- Do not decorate with unrelated illustration or fake stats.
- Filtered-empty ≠ first-run-empty — different copy, different action.

## Buttons, links, destructive actions

- Button names the outcome (`Delete record`, not `Yes`).
- Links name the destination. Don’t use “click here”.
- Destructive: exact object + consequence. Confirm or offer undo.
- Loading keeps the same verb (`Saving…`), not a generic spinner-only control.

## Forms

- Labels are nouns the user knows. Help text is one short line, not a paragraph.
- Placeholder is an example (`Jan Eriksson`), never the only label.
- Required vs optional: one convention, applied before submit.
- Success is quiet and specific (`Saved` / what changed), then the person
  continues the job.

## Tone

- Neutral and adult. Staff tools: precise > charming.
- Positive without pep: state the threshold, not the user’s failure
  (“Spend 50 more for free shipping”, not “You didn’t spend enough”).
- Match severity: a network outage is not the place for a mascot bit
  unless the product is already that brand *and* no data is at risk.

## Checklist before shipping copy

- [ ] A new person in the role understands every label
- [ ] Errors are readable aloud (screen reader and a tired human)
- [ ] Empty and error states have a next step
- [ ] No two buttons on one view share an ambiguous name
- [ ] Terminology matches the product’s source of truth, if it has one
