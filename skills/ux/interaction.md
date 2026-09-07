# Interaction checklist

Practical controls, states, and motion. Use these *under* Nielsen’s heuristics,
especially #1 status, #3 control, #5 prevention, #7 efficiency.

Drawn from common production rules (including Vercel’s
[Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines))
and the same inspection mindset as heuristic evaluation. Prefer the repo’s
design system when it already specifies a pattern.

## Keyboard and focus

- Every flow is keyboard-operable. Follow WAI-ARIA APG for composite widgets
  (tabs, menus, dialogs, grids) instead of inventing keys.
- Visible, unobscured focus (`:focus-visible`). Sticky chrome must not cover it.
- Dialogs trap focus, Escape closes, focus returns to the trigger.
- Hit target ≥ 24px (pointer); ≥ 44px on touch. If the drawing is smaller,
  expand the hit area.
- Never disable zoom.
- Do not use a `div`/`span` with a click handler for navigation — use a link
  so open-in-new-tab works. Buttons for actions, links for places.

## Forms

- Every control has a visible `<label>` (or programmatic name). Placeholder is
  not a label.
- Clicking the label focuses the control. Checkbox/radio: label + control share
  one generous target.
- Do not pre-disable submit to “prevent errors.” Let them submit, then show
  errors and focus the first invalid field.
- Disable submit only while the request is in flight; keep the original label
  and show a loading state (`Save` → `Saving…`).
- Do not block typing or paste. Validate; explain.
- `autocomplete` and meaningful `name` on fields that should autofill.
- `spellcheck="false"` on emails, codes, usernames.
- Correct `type` / `inputmode`. Text size ≥ 16px on mobile inputs (or equivalent
  so iOS does not zoom).
- Required fields: mark before submit; do not scream error styling on an
  untouched empty field.
- Warn before leaving with unsaved edits.

## Async and status (#1)

- Spinner/skeleton: brief show-delay (~150–300ms) and minimum visible time
  (~300–500ms) so fast responses do not flicker.
- Skeletons match the final layout (no jump).
- Optimistic update only when failure is unlikely; on failure, roll back and
  say so.
- Announce async results (`aria-live="polite"` for toasts and inline validation).
- Ellipsis character `…` on ongoing work and on actions that need more input
  (`Rename…`).

## Navigation and state (#3, #6)

- Persist filter/tab/pagination/search in the URL when the person would expect
  share, refresh, or Back to work.
- Back/Forward should restore scroll where the platform allows it.
- Deep-link states that look like pages, not only `useState`.
- Gestures (drag, swipe) need a click/keyboard equivalent unless the gesture
  *is* the task.

## Motion

- Honor `prefers-reduced-motion`.
- Prefer CSS (`transform`, `opacity`). Never `transition: all`.
- Motion explains cause and effect, or is deliberate delight — not decoration
  on every hover.
- Animations are interruptible by input.
- Autoplay >5s with other content needs pause/stop/hide.

## States every screen owes

Design empty, sparse, dense, loading, error, forbidden, and success — not only
populated happy path. No dead ends: every screen offers a next step or a way
out.

## Touch and pointer

- `touch-action: manipulation` on controls to avoid double-tap zoom.
- No dead zones: if it looks interactive, it is. If part of a control looks
  clickable, it is.
- Tooltips: delay the first in a group; peers after that may open immediately.
  Do not put essential information in hover-only UI.

## i18n (when the product is localized)

- Format dates, numbers, and money with locale APIs, not handwritten strings.
- Language from `Accept-Language` / `navigator.languages`, not IP.
- Mark brand and product names `translate="no"` when browser translate would
  mangle them.
- Keyboard shortcuts must be documented for non-QWERTY layouts.
