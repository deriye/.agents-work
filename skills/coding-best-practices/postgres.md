# PostgreSQL (schema + `pg`)

**Applies:** PostgreSQL as the product database, reached with the ordinary Postgres protocol (`pg` or equivalent). Not an ORM schema, not Firebase SQL Connect / GraphQL.

**Sources:**

- [PostgreSQL — Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html) (`CHECK`, `FOREIGN KEY`, `ON DELETE CASCADE`)
- [PostgreSQL — Comparison functions](https://www.postgresql.org/docs/current/functions-comparison.html) (`num_nonnulls`)
- [PostgreSQL — Partial indexes](https://www.postgresql.org/docs/current/indexes-partial.html)
- [node-postgres (`pg`)](https://node-postgres.com/)
- [node-pg-migrate — CLI](https://salsita.github.io/node-pg-migrate/cli) (`up`, `--migrations-dir`, `DATABASE_URL`)
- [node-pg-migrate — SQL files](https://salsita.github.io/node-pg-migrate/migration-loading-strategies) (`-- Up Migration` / `-- Down Migration`)
- Exclusive arc (one nullable FK per parent + `CHECK`): [Hashrocket — exclusive belongs-to](https://hashrocket.com/blog/posts/modeling-polymorphic-associations-in-a-relational-database). Do **not** use `owner_type` + `owner_id` without an FK ([GitLab — polymorphic associations](https://gitlab.com/gitlab-org/gitlab/-/blob/master/doc/development/database/polymorphic_associations.md)).

## When it applies

Relational tables, foreign keys, and constraints. Application code maps rows; it does not invent columns the schema does not have.

## Tree (only folders that have files)

```
sql/
  migrations/
    001_foundations-and-documents.sql
server/
  db.ts                 # one Pool; connection string, not a second client
  <entity>.ts           # queries for one table (list/create/update/delete)
  __tests__/            # after the first HTTP or schema test
    documents.test.ts
```

Until a migration tool is in the repo, keep one `sql/schema.sql` and Docker `docker-entrypoint-initdb.d`. Once Environments (or any hosted Postgres) exist, add `node-pg-migrate` and `sql/migrations/`, then delete `sql/schema.sql`. Do not add `models/` or an ORM “for later.”

Table names follow the entity (plural `snake_case`). One entity, one table.

## Dependency direction

Schema → query module → HTTP.

- After migrations exist, `sql/migrations/` is the source of truth for columns and constraints. Apply with `npm run migrate` (`node-pg-migrate up -m sql/migrations`) against `DATABASE_URL`.
- Delete `sql/schema.sql`. Do not mount it on `docker-entrypoint-initdb.d`.
- `server/<entity>.ts` talks to one table (or a documented join). It imports `pool` from `db.ts`.
- HTTP (`server/app.ts`) calls those functions. It does not embed SQL.
- The UI never talks to Postgres.
- Better Auth tables are not product migrations. That library’s CLI migrate owns `user` / `session` / `account` / `verification`.

## Keys and delete

Every relationship that can be a foreign key **is** a foreign key, as soon as the parent table exists. A UUID column with no `REFERENCES` is not a key.

- Child that cannot exist without the parent: `ON DELETE CASCADE` (official: delete the referencing rows with the referenced row).
- Independent rows: `ON DELETE RESTRICT` / `NO ACTION` (default).
- Optional pointer: `ON DELETE SET NULL`.

Do not leave a “placeholder” FK column without `REFERENCES` once the parent table exists.

## Exactly one owner (exclusive arc)

When one row belongs to **exactly one** of a small, fixed set of parents (for example a Document owned by a Foundation **or** an Application **or** a Project):

1. One nullable FK column per parent, each `REFERENCES … ON DELETE CASCADE`.
2. A `CHECK` that exactly one is set:

```sql
CONSTRAINT documents_one_owner CHECK (
  num_nonnulls(foundation_id, application_id, project_id) = 1
)
```

`num_nonnulls` is the Postgres spelling ([comparison functions](https://www.postgresql.org/docs/current/functions-comparison.html)). The `(col IS NOT NULL)::int + … = 1` form is the same rule; prefer `num_nonnulls`.

3. Partial indexes for “list by this parent,” so nulls are not stored:

```sql
CREATE INDEX documents_foundation_id_idx
  ON documents (foundation_id)
  WHERE foundation_id IS NOT NULL;
```

Use this when the child **shape is the same** (same columns) and the parent set is named and small. Split into three tables only when the child rows are different kinds of data, or the parent set will keep growing.

**Do not** store `owner_type TEXT` + `owner_id UUID` with no `REFERENCES`. The database cannot check that the id exists.

## Queries

- Parameterized queries (`$1`, `$2`). Never concatenate user input into SQL.
- `RETURNING` on `INSERT`/`UPDATE` when the caller needs the row.
- Guard a missing `RETURNING` row; do not assume `rows[0]`.
- Map `snake_case` columns to the application’s field names in the query module, not in the React tree.

## Testing

- **Constraints:** against a real Postgres (Docker is enough). Insert a row that must fail the `CHECK` or a missing parent FK; expect the error. Do not mock the constraint. For an exclusive-arc CHECK, cover zero owners and two owners; Postgres reports `23514` (`check_violation`). Put the tests in `server/__tests__/documents.test.ts`. Do not call `pool.end()` in `afterAll` when more than one file uses `pool` — that closes it for later files. Vitest 5 `globalSetup` teardown runs in a different isolate, so it cannot end the workers’ pool; let the process exit.
- **Queries:** same database; call `list`/`create` from `server/<entity>.ts` (or the HTTP route) in the repo’s test runner once one exists.
- **Migrations:** `npm run migrate` against Docker Postgres; `pgmigrations` lists the files that ran; `\dt` lists the product tables. Run `up` a second time; no second apply. Do not mock the migrator. Do not add pgTAP.
- **User-visible upload/list:** e2e in a browser ([Playwright](https://playwright.dev/docs/intro)) in `e2e/`, not SQL asserts alone. Assert roles, copy, and HTTP status — not CSS classes.
- If the repo has no runner yet, do not add pgTAP or a second database just for schema tests. Add tests in the stack already chosen for the app (Vitest + Docker Postgres, or Playwright). Do not add empty `sql/tests/`.

## What not to add

- `owner_type` / `owner_id` polymorphic columns
- Three FKs with no `CHECK` (zero, two, or three owners would be legal)
- An ORM or query builder
- Better Auth `CREATE TABLE` inside `sql/migrations/`
- Edits to a migration file that already ran on any database
- Duplicate tables that store the same columns for each parent
- A second Postgres client next to `db.ts`
- `docker-entrypoint-initdb.d` next to `node-pg-migrate` (two apply paths)

## Growing the schema

| Need | Add |
|---|---|
| First hosted / Environment Postgres | `node-pg-migrate`; `sql/migrations/`; stop `initdb.d` |
| New parent table | New file in `sql/migrations/`; `REFERENCES` + `CASCADE` on children; `npm run migrate` |
| Exclusive owner among existing parents | Nullable FKs + `num_nonnulls` + partial indexes (new migration) |
| List by parent | Partial index `WHERE <fk> IS NOT NULL` (new migration) |
| First schema test | `server/__tests__/<entity>.test.ts`; hit Docker Postgres; do not `pool.end()` per file |
