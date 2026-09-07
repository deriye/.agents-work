---
name: domain-model
description: >
  Extracts and maintains the domain model — concepts (abstract recurring
  patterns/mechanisms) and entities (persisted relational database tables) —
  that underlie a software feature's intent spec. Use as soon as changes are
  planned (after an intent spec exists at docs/features/<feature>/spec.md,
  before or during implementation planning). Re-run extraction whenever the
  spec changes, before any code is implemented. Outputs to
  docs/domain-model/concepts/<concept>.md and
  docs/domain-model/entities/<entity>.md, with index files at
  docs/domain-model/concepts/index.md and
  docs/domain-model/entities/index.md.
disable-model-invocation: true
---

# Domain Model Extraction

> **This is a delegate skill.** If the task involves writing or changing
> code, load the `software-development` skill **first** — it is the
> orchestrator that calls this skill at the right step (Step 4). Loading
> this skill directly without the orchestrator skips the gates the pipeline
> exists to enforce.

This skill extracts and maintains the **domain model** behind a feature's
intent spec:

- **Concepts** — abstract, recurring ideas/patterns/mechanisms that appear
  across intent specs (e.g. status markers, filtering, wear logging).
- **Entities** — relational database tables that represent things with
  their own identity in the ER model (e.g. item, outfit, wear log).

The model is extracted from the spec, never invented from code. When the
spec changes, the model is re-extracted and updated **before** any code is
implemented.

## When to Use This Skill

Run this skill:

1. **As soon as changes are planned** — after an intent spec exists at
   `docs/features/<feature>/spec.md`, before or during implementation
   planning. The model informs the plan.
2. **Whenever the spec changes** — if the user revises the request and the
   intent spec is updated, re-run extraction and update the model
   **before** implementing the new behavior.
3. **Before implementation of any change** — confirm the model matches the
   current spec; if it does not, update it first.

Do NOT run this skill for changes with no domain impact (e.g. pure refactor
of code structure that leaves the spec, concepts, and entities unchanged).
In that case, note in the plan that the domain model is unchanged.

## Folder Layout

```
docs/
  domain-model/
    concepts/
      index.md            ← index + spec→concept map
      <concept>.md       ← one file per concept
    entities/
      index.md            ← index + entity index + relationships + spec→entity map
      <entity>.md        ← one file per entity
  features/
    <feature>/
      spec.md            ← intent spec (from isdd)
      plan.md            ← implementation plan
  logs/
    index.md            ← index of logs
    <feature>.md         ← implementation log (written AFTER implementation)
```

Feature folders live under `docs/features/`, logs under `docs/logs/`.
Concepts and entities are flat (one file each) under
`docs/domain-model/concepts/` and `docs/domain-model/entities/` respectively.
Each folder has an `index.md` (not `README.md`) that serves as the structured
index and spec→model map.

---

## Step 1: Read the Spec

Read `docs/features/<feature>/spec.md`. Extract:

- The primary subject(s) the feature acts on → candidate **entities**.
- The recurring patterns/mechanisms the feature relies on → candidate
  **concepts**.
- New fields, statuses, flags, or relationships the feature introduces on
  those subjects → entity updates.
- New filter/sort/marker/logging/selection patterns → concept instances.

## Step 2: Scan Existing Model

1. List all `docs/domain-model/concepts/*.md` (excluding `index.md`) and
   `docs/domain-model/entities/*.md` (excluding `index.md`).
2. Read each existing concept/entity definition (or at minimum its first
   paragraph) to know what is already modeled.
3. Build a mental index: which concepts and entities already exist, which
   features they appear in.

## Step 3: Classify Each Candidate

For each candidate surfaced from the spec:

### Concept vs Entity decision

| Signal | Classification |
|--------|----------------|
| It is a thing with its own identity, persisted in its own table, that could exist independently | **Entity** |
| It is a junction/link table existing only to relate two entities | **Not an entity** — document under the relationship in `docs/domain-model/entities/index.md` |
| It is a column/flag on an existing entity (status, tag, count) | **Not an entity** — add as a field on the entity; if it instantiates a recurring pattern, also a concept instance |
| It is an abstract pattern/mechanism that recurs with different subject matter (status markers, filtering, ordering) | **Concept** |
| It is a screen, flow, or feature name | Neither — that is the feature itself |
| It is a pure UI affordance with no domain meaning | Neither |

### New vs Existing

- **Matches an existing concept/entity** → update that file: add the new
  instance, field, or `Appears in` entry. Do not duplicate.
- **Genuinely new** → create a new file.
- **Uncertain** → pick the closest existing match and flag it to the user
  in the summary (Step 6).

## Step 4: Write / Update Concept Files

For each concept the feature touches, create or update
`docs/domain-model/concepts/<concept>.md` using the
[concept file template](templates/model.md#concept-file-template).

Rules:
- The definition must be **abstract** — it should hold for any future
  feature that uses the same pattern, not just this one.
- `Instances` lists every concrete use across the product, with the entity
  (and column) it lives on. Update this when adding a new instance.
- `Appears in` lists every feature whose spec relies on this concept. Add
  the current feature; keep existing entries.
- `Implemented by` lists mechanisms whose runtime behavior instantiates or
  relies on this concept. Add entries when a mechanism is created or
  updated (Step 10 of `software-development`). Leave empty if no mechanism
  implements this concept yet.
- If a concept already exists, edit it in place — do not rewrite from
  scratch unless the definition itself is now wrong.

## Step 5: Write / Update Entity Files

For each entity the feature touches, create or update
`docs/domain-model/entities/<entity>.md` using the
[entity file template](templates/model.md#entity-file-template).

Rules:
- An **entity** is a strong/independent table. Junction tables are NOT
  entities — document them under `## Relationships` on the entities they
  link, and list them in `docs/domain-model/entities/index.md`'s
  relationships table.
- **Storage follows entity naming — one entity, one table.** Each entity
  maps to its own table; do not store two entities in one table with a
  row-type discriminator (e.g. a `kind` column splitting summary pages
  from wiki pages). When a candidate is really two distinct things, model
  them as two entities with two tables, and derive each table name from
  its entity name so storage and model stay in lockstep (e.g.
  `entities/summary-page` → `wiki_summary_pages`, `entities/wiki-page` →
  `wiki_pages`). A shared prefix groups tables that belong to one
  feature/area. Junction tables are the only exception (they link, not
  store entities).
- Columns that implement a concept (status flags, tags) reference the
  concept in their description, e.g. `is_hit — Whether ... (concepts/status-marker)`.
- `Appears in` lists every feature whose spec touches this entity.
- `Implemented by` lists mechanisms whose runtime behavior creates, reads,
  updates, or relies on this entity. Add entries when a mechanism is
  created or updated (Step 10 of `software-development`). Leave empty if no
  mechanism touches this entity yet.
- When updating, add new fields/relationships and the current feature to
  `Appears in`; do not drop existing entries unless a field was removed by
  spec change.

## Step 6: Update Index Files

### `docs/domain-model/concepts/index.md`

Maintain (create if missing) using the
[concepts/index.md template](templates/model.md#conceptsindexmd-template).

- Add new concepts to the table.
- Add or update the current feature's row in the spec→concept map.
- If a feature has no concepts, write `—` in the map.
- Add or update mechanism rows when a mechanism is created or updated
  (Step 10 of `software-development`). If a mechanism touches no concepts,
  write `—` in the concepts column.

### `docs/domain-model/entities/index.md`

Maintain (create if missing) using the
[entities/index.md template](templates/model.md#entitiesindexmd-template).

- Add new entities to the index.
- Add/update junction tables in the relationships table.
- Add/update the `Not separate entities` table for data that lives as
  columns on existing entities (status flags, tags, etc.).
- Redraw the ER diagram if relationships changed.
- Add or update the current feature's row in the spec→entity map.
- Add or update mechanism rows when a mechanism is created or updated
  (Step 10 of `software-development`). If a mechanism touches no entities,
  write `—` in the entities column.

## Step 7: Link Back from the Spec

At the bottom of `docs/features/<feature>/spec.md`, add (or update) a
`## Domain Model` section listing the concepts and entities this feature
touches, so the spec self-documents its model. Use the
[spec "## Domain Model" section template](templates/model.md#spec-domain-model-section-template).

If the feature has no domain impact, write `—` and note why. Leave
`**Mechanisms:**` empty or write `—` if no mechanism implements this
feature's behavior yet (Step 10 of `software-development` may add one
after implementation).

## Step 8: Report to the Caller

Return a concise summary to whatever skill invoked this one:

```
Concepts & entities extracted for "<feature>":

New concepts: <list, or none>
Updated concepts: <list, or none>
New entities: <list, or none>
Updated entities: <list, or none>
Index files updated: docs/domain-model/concepts/index.md, docs/domain-model/entities/index.md
Spec linked: docs/features/<feature>/spec.md (## Domain Model added)

Uncertain / needs user confirmation:
- <item: why it is ambiguous>
```

Flag any classification you were unsure about so the orchestrating skill
can ask the user before implementation proceeds.

---

## Re-extraction on Spec Change

When the intent spec is revised (e.g. the user changes the request mid-flow):

1. Re-read the updated spec.
2. Re-run Steps 1–8 against the new spec.
3. **Update all affected docs before implementation begins** — concepts,
   entities, both `index.md` files (including the mechanism→model maps),
   and the spec's `## Domain Model` section. The implementation plan must
   be re-derived from the updated model, not the old one.
4. If a concept/entity is no longer touched by the spec, **remove the
   feature from its `Appears in` list** (and from the spec→concept /
   spec→entity maps). Do not delete the concept/entity file itself — other
   features may still use it. Only delete a file if the spec change
   eliminates the concept/entity from the product entirely; in that case,
   confirm with the user first.
5. If a mechanism is no longer touched by the spec, **remove the feature
   from the mechanism's `## Appears in features` list** and update the
   mechanism→model maps in both index files. Do not delete the mechanism
   file itself — other features may still rely on it. Only delete a
   mechanism file if the spec change eliminates the mechanism from the
   product entirely; in that case, confirm with the user first.

The rule: **the domain model is the source of truth for the plan.** Code
is only written once the model matches the current spec.

## Best Practices

1. **Extract from the spec, not the code.** The model describes intended
   behavior; if code drifts, that is a plan/log issue, not a model issue.
2. **One concept per recurring pattern.** If two instances could share a
   definition, they are one concept. If they need different definitions,
   they are two.
3. **Names describe the pattern, not a feature.** Good: `status-marker`.
   Bad: `hit-status`.
4. **Entities have their own identity.** If a thing only exists to link
   two other things, it is a relationship, not an entity.
5. **Keep `Appears in` accurate.** It is how traceability flows between
   specs and the model. Stale entries break the map.
6. **Update indexes every time.** A new concept/entity file without an
   index entry is effectively invisible.
7. **Storage follows entity naming.** One entity → one table; never pack
   two entities into one table with a discriminator. When two things are
   distinct, split them into two entities and two tables whose names
   derive from the entity names (a shared feature prefix is fine). This
   keeps the model and the schema readable in lockstep.
