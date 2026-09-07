# Better Auth (email + password)

**Applies:** Better Auth as the sign-in system for a Vite React SPA with one Express `/api` app. Not Next.js route handlers, not Firebase Authentication.

**Sources:**

- [Better Auth — Installation](https://www.better-auth.com/docs/installation) (`auth.ts` locations; `toNodeHandler`; mount before `express.json()`)
- [Better Auth — PostgreSQL](https://www.better-auth.com/docs/adapters/postgresql) (`pg` `Pool`; CLI migrate)
- [Better Auth — CLI](https://www.better-auth.com/docs/concepts/cli) (`migrate --config` `--yes`)
- [Better Auth — Express](https://www.better-auth.com/docs/installation#express) (handler before body parser)

## When it applies

Email-and-password sessions in front of Foundation portal (or the same stack). Product rows already live in Postgres with `pg`.

## Tree (only folders that have files)

```
server/
  db.ts                 # one Pool (already)
  auth.ts               # betterAuth({ database: pool }); export const auth
  app.ts                # toNodeHandler(auth) before express.json()
src/
  features/
    auth/
      authClient.ts     # createAuthClient from better-auth/react
      SignInForm.tsx
      SignInGate.tsx
```

Do not add `lib/auth.ts` next to `server/auth.ts`. Do not add `better-sqlite3` or an `auth.sqlite` file when the product database is Postgres.

## Dependency direction

- `server/auth.ts` imports `pool` from `db.ts`. It does not construct a second Pool.
- `server/app.ts` mounts Better Auth, then JSON, then product routes.
- `src/features/auth/` talks to Better Auth over `/api/auth`. It does not import `server/`.
- Other features do not import `features/auth`. `src/app/App.tsx` composes `SignInGate`.

## Database

Pass the existing `pg` Pool:

```ts
import { betterAuth } from "better-auth";
import { pool } from "./db";

export const auth = betterAuth({
  database: pool,
  // ...
});
```

Apply Better Auth’s tables with the CLI (Kysely adapter). Pin the CLI to the same version as `better-auth`:

```powershell
npx --yes auth@1.7.2 migrate --config server/auth.ts --yes
```

Postgres must be running. The CLI creates `user`, `session`, `account`, and `verification` in the same database as product tables.

Do not copy those tables into `sql/schema.sql` or into `sql/migrations/`. Product schema is `node-pg-migrate` once Environments exist; Better Auth owns its own CLI migrate.

## HTTP

Mount the handler **before** `express.json()`. Better Auth reads the body itself. If sign-up hangs, the handler is too late.

On this Vite + Express 5 app, gate `/api/auth` with `req.path.startsWith("/api/auth")` and `toNodeHandler(auth)` so the rest of `app` still reaches Vite. Keep Better Auth on the same origin as the SPA so the session cookie stays first-party.

Product `/api/foundations` routes call `auth.api.getSession({ headers: fromNodeHeaders(req.headers) })`. No session → 401. Put that check in `app.ts` next to the routes. Do not add `server/middleware/`. Import `fromNodeHeaders` from `better-auth/node` (same module as `toNodeHandler`). See [Express — Getting the User Session](https://www.better-auth.com/docs/integrations/express#getting-the-user-session).

## Testing

- **Staff-visible sign-in:** e2e in a browser ([Playwright](https://playwright.dev/docs/intro)) in `e2e/`. Unsigned-in: sign-in copy, no register table. After sign-in: session bar and Foundation register. Assert roles and Swedish copy, not CSS classes.
- **HTTP:** once a runner exists, hit `/api/auth/sign-up/email` / `/api/auth/sign-in/email` through `server/__tests__/`. Do not mock Better Auth. Use the same Docker Postgres.
- Do not add a second auth test stack. Do not assert cookie internals or SQLite files.

## What not to add

- `better-sqlite3` / `auth.sqlite` beside Postgres
- A second `Pool` in `auth.ts`
- Better Auth `CREATE TABLE` copied into `sql/schema.sql` or `sql/migrations/`
- A product migrator whose only job is Better Auth’s tables
- `src/lib/auth.ts` when `server/auth.ts` already exists
