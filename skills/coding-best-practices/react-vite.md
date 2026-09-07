# React + Vite + TypeScript

**Applies:** Vite React SPA (`create-vite` `react-ts` or equivalent). Not Next.js App Router.

**Sources:**

- [React — File Structure](https://legacy.reactjs.org/docs/faq-structure.html) (colocate; no official tree; avoid deep nesting)
- [React — Custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks) (`use` prefix)
- [Bulletproof React — project structure](https://github.com/alan2207/bulletproof-react/blob/master/docs/project-structure.md) (features + shared `components`; unidirectional flow)
- [Vitest — Getting Started](https://vitest.dev/guide/) (Vite’s test runner)
- [Vitest — Features](https://vitest.dev/guide/features.html) (`jsdom` / `happy-dom` for DOM; install separately)
- [Vitest — Testing in Practice](https://vitest.dev/guide/learn/testing-in-practice.html) (one test file per module; sibling `__tests__/` or next to the file — stay consistent)
- [Bulletproof React — where tests live](https://github.com/alan2207/bulletproof-react/issues/52) (sibling `__tests__/` keeps source folders scannable)
- [Kent C. Dodds — Colocation](https://kentcdodds.com/blog/colocation) (tests near the module; e2e at repo root)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) (`render` + queries; not Enzyme)
- [Playwright — Introduction](https://playwright.dev/docs/intro) (e2e in a real browser)
- Community consensus: organize by **feature**, not by file type; promote to shared on about the **third** consumer

## Tree (only folders that have files)

```
src/
  main.tsx
  theme.css                 # global tokens; next to the Vite entry
  vite-env.d.ts
  app/                      # composition: which screen, providers later
    App.tsx
    AppShell.tsx            # nav chrome — only if App.tsx is the sole importer
    AppShell.css
  components/               # shared UI; no domain imports
    TopBar.tsx
    Btn.tsx
    Chip.tsx
    Card.tsx
    TextField.tsx
    DataTable.tsx
    ui.css                  # control classes; tokens stay in theme.css
    __tests__/              # after the first shared-component test
      DocumentList.test.tsx
  features/
    <feature>/              # one product capability; files flat at first
      Screen.tsx
      api.ts
      __tests__/            # after the first unit/component test in this folder
        Screen.test.tsx
        api.test.ts
  hooks/                    # create on first generic shared hook only
```

Vite entry stays `src/main.tsx`. Do not add `src/app/` until `App.tsx` moves there. Do not add `src/hooks/` until a generic `use*` exists.

## Dependency direction

`components` and `hooks` (shared) → `features` → `app`.

- Features may import `components/` and shared `hooks/`.
- Features must not import `app/`.
- Shared `components/` and `hooks/` must not import `features/` or `app/`.
- Features must not import other features. Compose them in `app/`.

## AppShell vs TopBar

Two different “shells”:

- **`app/`** = application layer (`App.tsx`, later providers/router).
- **`AppShell`** = visual nav chrome.

Put `AppShell` in `app/` **only when `App.tsx` is the only importer**. Feature screens must not wrap themselves in it.

Page title, count, and actions are page state. Put a dumb **`TopBar`** in `components/`. The feature renders `TopBar`; `App` wraps `AppShell`.

If screens still import `AppShell`, keep it in `components/` until you lift chrome to `App.tsx`.

Do not also add `layouts/`. One chrome file is enough.

## Features

- Name the folder after the capability (`auth`, `billing`), not `pages/` or `containers/`.
- Keep files **flat** inside the feature until it is large (~15 files). Then add `components/` or `api/` *inside that feature*.
- Do not wrap a single feature in an extra `features/` child named `shared`.
- Feature-owned HTTP lives in `features/<name>/api.ts`, not `src/api/`.
- Seed data, formatters, and filter helpers that name the domain stay in the feature.

## Components

- `src/components/` = reusable, **no domain words** in imports (no entity names, no feature API).
- Do not put feature screens in `components/`.
- Do not nest `components/ui/` unless you adopt a kit that requires it (shadcn). Primitives sit directly in `components/`.
- No barrel `index.ts` files.

## Hooks

Official React: a function that calls other Hooks is named `useX`. If it calls no Hook, it is a plain function (`parseLabel`, not `useLabel`).

| Kind | Where |
|---|---|
| Stateful logic for one feature | `features/<name>/useThing.ts` (flat; add `hooks/` only if several) |
| Generic, no domain words, used by ~3+ callers | `src/hooks/useDebounce.ts` |

- Default: keep `useState` / `useEffect` **in the component**.
- Extract a custom hook when a second caller needs the same state, or the component is mostly effects and hard to read.
- Do not put a feature list hook in `src/hooks/`.
- One hook per file once extracted.
- `src/hooks/` does not exist until the first generic shared hook.

## CSS

- Tokens: `src/theme.css` (imported from `main.tsx`).
- Controls: `src/components/ui.css`.
- Shell layout: colocated `AppShell.css`.
- Prefer classes over inline `style={{}}` except where layout math needs it.

## Testing

- **Unit:** [Vitest](https://vitest.dev/guide/). One `*.test.ts` per module under test, in a **sibling `__tests__/`** folder (same directory as the source). Default environment is Node. Vitest also allows `utils.test.js` beside the file; this stack uses `__tests__/` so source files stay easy to scan ([Vitest — Testing in Practice](https://vitest.dev/guide/learn/testing-in-practice.html), [Bulletproof React #52](https://github.com/alan2207/bulletproof-react/issues/52)).
- **Component:** `*.test.tsx` in that same sibling `__tests__/`. Use `jsdom` (install `jsdom`; set `environment` or a `@vitest-environment jsdom` comment) and [`@testing-library/react`](https://testing-library.com/docs/react-testing-library/intro/) (`render`, `screen`, roles/text). Put `@vitejs/plugin-react` on the Vitest config so JSX transforms. Query the DOM the way staff would (empty copy, table headers, labelled controls). Do not assert CSS class names or component internals. Do not enable Vitest Browser Mode while Playwright already covers journeys in `e2e/`.
- **E2E:** [Playwright](https://playwright.dev/docs/intro) for user-visible journeys. Files in `e2e/` at the repo root (`testDir: "./e2e"`; Playwright’s installer uses `e2e` when `tests` already exists). Do not put Playwright files under `src/` ([Kent C. Dodds — Colocation](https://kentcdodds.com/blog/colocation): e2e does not map to one source file). Do not add `e2e/` until the first e2e test.
- Assert **behavior**: roles, visible copy, HTTP status. If someone refactors internals and the staff-visible result is unchanged, the test should still pass.
- If the repo already has a runner, **use that**. Do not add a second framework.
- If neither exists and tests are in scope, add Vitest and Playwright from their official guides. Do not invent a runner.
- Do not add empty `__tests__/` “for later.” Do not add a repo-root `src/test/` that mirrors `src/`. Do not add a test file for every `.tsx` “to match the tree.”

## What not to add

- Empty `store/`, `lib/`, `types/`, `utils/`, `routes/`, `assets/`, `layouts/`
- `app/router.tsx` and `routes/` at the same time (pick one, when a router exists)
- Design-playground leftovers (option catalogs, direction flags, theme switchers for comparing looks)
- Path aliases (`@/`) while the tree is shallow
- A shared types package only to DRY a client row type with the server

## Growing the tree

| Need | Add |
|---|---|
| Second screen | Compose in `app/App.tsx`; keep chrome in `AppShell` |
| Sign-in | `features/auth/` |
| Next product module | sibling `features/<name>/` |
| Fetch wrapper used by two features | then `src/lib/http.ts` |
| Debounce used by two features | then `src/hooks/useDebounce.ts` |
| Real URL router | `app/router.tsx` (or the router’s file convention), not a second `routes/` folder |
| Unit/component test | Sibling `__tests__/Module.test.ts(x)` |
| First e2e journey | `e2e/` + Playwright |
