# Accessibility (ship bar)

Usability for people who are not you. Maps onto Nielsen **#1, #4, #6, #7, #9**.
Target **WCAG 2.2 Level AA** unless the product states otherwise.

This is not a full audit skill. For a dedicated compliance scan, use a
specialized a11y skill or axe/Lighthouse — then still fix what inspection finds.

## Non-negotiables

- **Semantics first.** `button`, `a`, `label`, `input`, `table`, headings
  `h1–h6` in order. ARIA only when no native element exists.
- **Name every control.** Icon-only buttons have `aria-label`. Decorative
  images `alt=""` / `aria-hidden`. Meaningful images have real `alt`.
- **Keyboard.** Tab order matches visual order. No keyboard traps except
  inside a dialog that can be escaped. Skip link to main content on app shells.
- **Focus visible** and not covered by sticky UI.
- **Contrast.** Text ≥ 4.5:1 (normal), 3:1 large text and UI components.
  Prefer checking with a contrast tool over eyeballing.
- **Not color alone.** Status, required, selected, and errors also use text
  or icon.
- **Motion.** `prefers-reduced-motion`; no essential info in hover-only or
  animation-only cues.
- **Forms.** Labels, `aria-invalid` + error text tied with `aria-describedby`,
  errors on submit focus the first problem.
- **Windows and dialogs.** Role, labelled, focus trap, restore focus, Escape.
- **Live regions.** `role="status"` polite for non-critical; `role="alert"`
  for urgent. Do not double-announce with a focus move *and* an alert.
- **Zoom.** 200% still usable. No `user-scalable=no`.
- **Language.** `lang` on the document (and on passages in another language).

## Patterns that usually fail

| Pattern | Fix |
|---|---|
| Clickable `div` | `button` or `a` |
| Placeholder-only field | Visible `label` |
| Custom checkbox | Native `input` or APG pattern with checked state |
| `outline: none` without a replacement | `:focus-visible` ring |
| Table as layout | CSS grid/flex; `table` only for tabular data |
| Auto-playing motion | Pause control or reduced-motion cut |
| Modal without focus management | Trap, label, return focus |
| SVG icon button, no name | `aria-label` on the button |

## How to verify (minimum)

1. Unplug the mouse. Complete the primary task.
2. Glance the accessibility tree / headings / landmarks if a browser is available.
3. Check contrast on text, borders of inputs, and focus rings against the actual background.
4. Submit an empty form; confirm errors are announced and focus moves.

If you cannot run a browser, say what you could not verify.
