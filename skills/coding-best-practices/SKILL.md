---
name: coding-best-practices
description: >-
  Canonical language/stack coding conventions (folder layout, modules,
  hooks, shared vs feature code, testing). Use when writing or changing
  application code or tests, authoring tutorial snippets, choosing src/
  structure, placing hooks, or when generate-tutorials, software-development,
  or frontend-design emit code. If this skill has no file for a stack this
  change writes, or that stack file has no Testing section, research the
  internet, add it here, then follow it. Run lookup for every stack in the
  change, not one primary stack.
---

# Coding Best Practices

Source of truth for **how to structure and write code** for a language/stack.
Other skills do not invent a folder tree. They look it up here.

## When to use

Load this skill (and the matching stack file) whenever you:

- Write or change application source or tests
- Author tutorial `course.md` snippets the learner will copy
- Place a hook, component, API client, layout file, or test file
- Choose or grow `src/` layout
- Choose a test runner or e2e tool for a stack

## Lookup (every time)

1. Identify **every** language + stack this change writes, not one “primary” stack. A sitting or pass can be more than one (example: React + Vite + TypeScript **and** PostgreSQL). SQL, CSS, and tests each count if you are writing them.
2. For **each** stack: if a file exists in the index below, **read it and follow it**. Do not re-research layout that is already recorded. Still run step 4 if Testing is missing. A file for React does **not** skip Postgres (or any other stack in the same change).
3. If **that** stack file is missing:
   - Research current practice on the internet (official docs first, then a widely cited community source such as Bulletproof React for React).
   - Add a stack file here using [Adding a stack](#adding-a-stack).
   - Then write **that stack’s** code against that file.
4. If the stack file exists but has **no Testing section** (or none that covers this kind of test):
   - Research current testing practice for that stack (official docs first).
   - Add a **Testing** section to the stack file (unit/component vs e2e, default tools, where files live).
   - Then write tests against that section.
5. If the repo already has files, **match existing names** in that repo. This skill is the default for new layout; do not rename a mature tree unless the user asked.

Do not create empty folders “for later.” Do not copy an enterprise starter’s unused `store/`, `lib/`, `hooks/`, `types/`, `utils/` directories.

## Index of stacks

| Stack | File |
|---|---|
| React + Vite + TypeScript | [react-vite.md](react-vite.md) |
| PostgreSQL + `pg` | [postgres.md](postgres.md) |
| Express + multer | [express.md](express.md) |
| Better Auth | [better-auth.md](better-auth.md) |
| Docker (Dockerfile + Compose) | [docker.md](docker.md) |
| S3-compatible Object store | [s3-object-store.md](s3-object-store.md) |

## Adding a stack

Create `coding-best-practices/<stack-id>.md` (lowercase, hyphens). Add a row to the index above.

Each stack file must include:

- **Sources** (URLs) you used
- **When it applies**
- **Folder tree** (only folders that have a job)
- **Dependency direction** (what may import what)
- **Where hooks / components / API live**
- **Testing** (unit/component vs e2e; default tools; where test files live; what not to add)
- **What not to add** (empty layers, barrels, premature shared)

Keep one stack per file. Update in place when practice changes; do not duplicate.

## Who loads this

| Skill | When |
|---|---|
| `software-development` | Step 8 (implement app and tests) |
| `generate-tutorials` | Before writing copy-paste code (rule 8.5), including test sittings |
| `frontend-design` | When emitting React/Vite (or other recorded stack) UI |

Those skills must run the lookup above **for every stack in the change**. They must not skip research + add when **any** of those stacks is absent **or** when Testing is missing from that stack file. Imitating an earlier sitting’s SQL (or CSS, or tests) is not a substitute for lookup.
