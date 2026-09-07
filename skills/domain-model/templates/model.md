# Domain Model Templates

Reference templates for `domain-model` skill outputs. Copy and fill in.

## Concept file template

For `docs/domain-model/concepts/<concept>.md`:

```markdown
# <Concept Name>

**Id:** `concepts/<concept>`

<One-paragraph definition: what the pattern is, stated abstractly. Describe
the mechanism, not any single feature. Note whether it is user-set vs
derived, explicit vs inferred, persistent vs session-only — whatever is
definitional about this pattern.>

## Instances in this product

| Instance | Entity | Meaning |
|----------|--------|---------|
| <name> | `entities/<entity>` (`<column>` if applicable) | <what this instance expresses> |

## Appears in

- <feature-name>
- <feature-name>

## Implemented by

- mechanisms/<mechanism>
- mechanisms/<mechanism>
```

## Entity file template

For `docs/domain-model/entities/<entity>.md`:

```markdown
# <Entity Name>

**Id:** `entities/<entity>`

**Table:** `<table_name>`

<One-paragraph description: what this thing is in the domain.>

## Fields

| Field | Description |
|-------|-------------|
| id | Primary key |
| <field> | <what it stores; reference `concepts/<concept>` if a field implements a concept> |
| created_at | When the record was created |

## Relationships

- **<Related entity>** — <cardinality> with `entities/<related>` via `<junction table>`.<attributes on the relationship, referencing concepts if applicable>.

## Appears in

- <feature-name>
- <feature-name>

## Implemented by

- mechanisms/<mechanism>
- mechanisms/<mechanism>
```

## concepts/index.md template

For `docs/domain-model/concepts/index.md`:

```markdown
# Concepts

<definition paragraph — an abstract, recurring idea/pattern/mechanism
that appears across intent specs. Reference with ids like
`concepts/status-marker`. For concrete objects, see entities.>

## Definition

<short "what is a concept" paragraph>

## What belongs in entities instead

<one paragraph — persisted relational entities belong in entities; junction
tables are not entities either>

| Id | Name |
|----|------|
| `concepts/<c>` | [Name](<c>.md) |
| ... | ... |

## Spec → concept map

| Intent spec | Concepts |
|-------------|----------|
| <feature> | `<concept>`, `<concept>` |
| ... | ... |

## Mechanism → model map

| Mechanism | Concepts | Entities |
|-----------|----------|----------|
| mechanisms/<mechanism> | `concepts/<c>` | `entities/<e>` |
| ... | ... | ... |
```

## entities/index.md template

For `docs/domain-model/entities/index.md`:

```markdown
# Entities

<definition paragraph — relational database entities; reference with ids
like `entities/outfit`. For abstract recurring patterns, see concepts.>

## Definition

<short "what is an entity" paragraph — strong/independent tables; junction
tables are not entities>

## Entity index

| Id | Table | Description |
|----|-------|-------------|
| `entities/<e>` | `<table>` | <short description> |
| ... | ... | ... |

## Relationships (not entities)

| Table | Links | Attributes on the relationship |
|-------|-------|--------------------------------|
| `<junction>` | `entities/a` ↔ `entities/b` | <attrs; ref concepts if applicable> |
| ... | ... | ... |

## Not separate entities

| Data | Stored as |
|------|-----------|
| <data> | <where it actually lives> |
| ... | ... |

## ER diagram

\`\`\`
<ascii ER diagram — entities and junction tables>
\`\`\`

## Spec → entity map

| Intent spec | Entities |
|-------------|----------|
| <feature> | `<entity>`, `<entity>` |
| ... | ... |

## Mechanism → model map

| Mechanism | Concepts | Entities |
|-----------|----------|----------|
| mechanisms/<mechanism> | `concepts/<c>` | `entities/<e>` |
| ... | ... | ... |
```

## spec "## Domain Model" section template

Append to `docs/features/<feature>/spec.md`:

```markdown
## Domain Model

- **Concepts:** `concepts/<c>`, `concepts/<c>`
- **Entities:** `entities/<e>`, `entities/<e>`
- **Mechanisms:** `mechanisms/<m>`, `mechanisms/<m>`
```
