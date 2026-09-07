# Docker (Dockerfile + Compose)

**Applies:** A Node Express app with a Vite `dist`, Docker Postgres, and Compose files. Not Kubernetes, not nginx in front of the app.

**Sources:**

- [Docker — Multi-stage builds](https://docs.docker.com/build/building/multi-stage/) (`FROM … AS`; `COPY --from`; `--target`)
- [Compose — Startup order](https://docs.docker.com/compose/how-tos/startup-order/) (`depends_on` + `condition: service_healthy`)
- [Compose — `healthcheck`](https://docs.docker.com/reference/compose-file/services/#healthcheck) (`pg_isready`)
- [Compose — `depends_on`](https://docs.docker.com/reference/compose-file/services/#depends_on)
- [OWASP — Node.js Docker Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/NodeJS_Docker_Cheat_Sheet) (`.dockerignore`; `npm ci`; pin the image; copy `package-lock.json` before source)
- [Express — Serving static files](https://expressjs.com/en/starter/static-files.html) (`express.static`; SPA `index.html` after `/api`)

## When it applies

The Environment host is `server/listen.ts` in one image. The laptop keeps a separate Compose file for Postgres and MinIO. Coolify builds the portal Compose file.

## Tree (only folders that have files)

```
Dockerfile
.dockerignore
.npmrc                      # legacy-peer-deps=true (better-auth vs vitest 5)
docker-compose.local.yml    # laptop: Postgres + MinIO; host Vite or listen.ts
docker-compose.portal.yml   # Environment: Postgres + api
```

Do not add `nginx/`. Do not add a MinIO service to `docker-compose.portal.yml`.

## Dependency direction

- **Laptop:** `docker-compose.local.yml` publishes Postgres `5432` and MinIO `9000`. Vite or `listen.ts` runs on the host and uses `127.0.0.1`.
- **Environment:** `docker-compose.portal.yml` has `postgres` and `api` only. `api` uses `DATABASE_URL` on service `postgres`. Object store is env (S3 on Coolify; MinIO defaults only when `listen.ts` runs on the laptop).
- The Dockerfile `build` stage runs `npm ci` and `npm run build`. The `api` stage copies `dist`, `server/`, and `sql/`, then `npm ci --omit=dev`.
- `listen.ts` serves `dist` with `express.static` after the `/api` JSON 404. Coolify’s proxy targets container port `8080`.

## Dockerfile

- Pin `node:22.23.1-bookworm-slim`.
- Copy `package.json`, `package-lock.json`, and `.npmrc` before the rest of the source.
- `npm ci` in `build`; `npm ci --omit=dev` in `api`.
- `.npmrc` is `legacy-peer-deps=true` so `npm ci` in the image does not ERESOLVE (`better-auth` optional vitest 2–4 vs vitest 5).
- `.dockerignore`: `node_modules`, `dist`, `tmp`, `.git`.
- `api` waits until Postgres is healthy, then product migrate, Better Auth migrate (CLI already in `node_modules`), then `tsx server/listen.ts`.
- Do not `npx --yes auth@…` at container start (that downloads on every boot).

## Compose

- Laptop file: `docker-compose.local.yml`. After migrations exist, do not mount `sql/schema.sql` on `initdb.d`. Delete `sql/schema.sql`. Laptop MinIO `minio-init` sets anonymous access to `none` (not `download`).
- Portal file: `docker-compose.portal.yml`. Postgres healthcheck `pg_isready`. `api` `depends_on` with `condition: service_healthy`.
- Do not publish Postgres on the portal file. Publish `8080:8080` on `api` for a laptop image run; Coolify proxies to `8080`.
- Separate volume name (`portal-postgres`) so the laptop `postgres-data` volume is untouched.

## Testing

- `docker compose -f docker-compose.portal.yml config --services` lists `postgres` and `api` only.
- `npm run migrate` against laptop Postgres; `pgmigrations` lists the files; a second `up` applies nothing new.
- `npm run build` then `tsx server/listen.ts` on `8080` with laptop Compose up: sign-in at `http://localhost:8080/`, then Foundation register.
- Do not add a second Compose test stack. Do not assert image IDs.

## What not to add

- nginx (or Caddy) in the portal Compose file
- MinIO / `minio-init` in the portal Compose file
- `mc anonymous set download` on the laptop bucket
- `docker-entrypoint-initdb.d` next to `node-pg-migrate`
- Unpinned `node:latest`
- `npm install` in the image instead of `npm ci`
