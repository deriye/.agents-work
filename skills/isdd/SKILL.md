---
name: isdd
description: >
  Intent Spec Driven Development (ISDD). Use when the user wants to define, create,
  or update a feature. Manages intent specifications at docs/<feature>/spec.md.
  Checks existing specs before creating new ones. Outputs user/UX-focused intent
  specs with no implementation details. Implementation planning is gated until
  explicitly requested.
disable-model-invocation: true
---

# Intent Spec Driven Development (ISDD)

> **This is a delegate skill.** If the task involves writing or changing
> code, load the `software-development` skill **first** — it is the
> orchestrator that calls this skill at the right step (Step 1). Loading
> this skill directly without the orchestrator skips the gates the pipeline
> exists to enforce.

A skill for capturing user-facing features as intent specifications before any
implementation planning occurs. Features are described from a UX/user perspective
and stored in `docs/<feature>/spec.md`.

## When to Use This Skill

Use this skill when the user:

- Describes a new capability, behavior, or experience they want
- Says "I want a feature that...", "Can we add...", "Users should be able to..."
- Mentions updating or changing something that sounds like an existing feature
- Shares a product idea, user story, or requirement
- Wants to create a specification, intent doc, or feature description

**Do NOT use this skill for:**
- Code reviews, refactoring, or bug fixes (unless the fix introduces new user-facing behavior)
- Purely technical tasks with no user-facing change (e.g., "migrate to pnpm")
- Architecture or infrastructure decisions (unless framed as a user-visible feature)

## Workflow

### Step 1: Scan for Existing Specs

Before doing anything else, discover existing feature specs:

1. Search the current workspace for all `docs/**/spec.md` files
2. Extract the feature name and `## Context` + `## Desired Behavior` from each
3. Build a lightweight index of existing user intents

### Step 2: Compare Against User Request

Analyze the user's request and compare it to the existing spec index:

- **Same user goal, same interaction pattern** → This is likely an **update** to an existing feature
- **Different user goal, different outcome, or different primary actor** → This is a **new feature**
- **Uncertain** → Flag the closest match and ask the user

**Reference:** See `feature-separation.md` for detailed guidelines and examples.

### Step 3: Decide and Notify

**If update detected:**
```
This sounds like it relates to the existing feature "<feature-name>".
Should I update that spec instead of creating a new one?
```

**If new feature:**
```
I'll create a new intent spec for "<proposed-feature-name>".
```

### Step 4: Generate Folder Name

Convert the feature description to kebab-case automatically:

- Lowercase everything
- Replace spaces and punctuation with hyphens
- Remove articles (a, an, the) if they appear at the start
- Keep it concise (3–6 words ideal)

**Examples:**
- "User can reset password via email" → `user-password-reset-via-email`
- "Admin dashboard for viewing analytics" → `admin-analytics-dashboard`
- "The ability to export data as CSV" → `export-data-as-csv`

**If the user wants to override:** Accept their folder name suggestion and use it.

### Step 5: Write the Intent Spec

Create `docs/<kebab-case-name>/spec.md` using the template in `templates/spec.md`.

**Rules for writing specs:**
- **No implementation details.** Do NOT mention libraries, frameworks, APIs, databases, caching layers, architecture patterns, or specific technologies.
- **User/UX perspective only.** Describe what the user experiences, not how the system delivers it.
- **Required sections:** `Context`, `Desired Behavior`, `Boundaries`, `Success Criteria`
- **Optional sections:** Add or remove sections if the feature demands it (e.g., `User Flow` for multi-step interactions, `Edge Cases` for complex logic, `Constraints` for business rules). The template is a starting point, not a cage.
- **Clarity over brevity.** Prefer explicit descriptions over vague shorthand.

### Step 6: Gate Implementation

After the spec is written, STOP. Do NOT produce an implementation plan, code, architecture diagram, or technical suggestions.

**Only proceed to implementation planning when the user explicitly asks**, e.g.:
- "Create an implementation plan for `<feature>`"
- "How would we build `<feature>`?"
- "What's the next step for `<feature>`?"

When that happens, read the spec first, then produce an implementation plan.
Store implementation plans at `docs/<feature>/plan.md`.

## Template

See `templates/spec.md` for the base intent specification template.

## Feature Separation Guidelines

See `feature-separation.md` for detailed rules on distinguishing new features
from updates to existing features.

## Best Practices

1. **One spec per user-facing capability.** If a request bundles multiple distinct
capabilities, suggest splitting them into separate specs.

2. **Names describe value, not mechanism.** Good: `offline-reading-mode`. Bad: `service-worker-caching`.

3. **Keep specs implementation-agnostic.** A spec written today should still be valid
if the tech stack changes tomorrow.

4. **Update existing specs rather than duplicating.** If a user request extends an
existing feature, prefer updating the original spec over creating a new one.

5. **Specs are living documents.** It's okay to revise a spec as understanding improves.
Just update the file in place.
