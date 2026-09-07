# Express (HTTP + multer)

**Applies:** A small Express app that serves JSON APIs and, when needed, `multipart/form-data` file uploads. Not Nest, not Fastify.

**Sources:**

- [multer middleware (Express)](https://expressjs.com/en/resources/middleware/multer.html) (`multipart/form-data`; `.single`; `memoryStorage`; `limits`; `MulterError`)
- [expressjs/multer](https://github.com/expressjs/multer) (`fileSize` default is Infinity; set it)
- [Express — Error handling](https://expressjs.com/en/guide/error-handling.html) (four-argument handler)
- [MDN — Using FormData](https://developer.mozilla.org/en-US/docs/Web/API/FormData/Using_FormData_Objects) (do not set `Content-Type` on `fetch`; the browser sets the boundary)
- [supertest](https://www.npmjs.com/package/supertest) (`request(app)`, `.attach` for multipart, async/await)

## When it applies

Route modules under `server/`. JSON for fields. Multipart for files that go to object storage.

## Tree (only folders that have files)

```
server/
  app.ts            # create the app, JSON parser, routes, error handler
  listen.ts         # bind a port (prod / Environment)
  <entity>.ts       # queries or object-store writes for one concern
  __tests__/        # after the first HTTP or schema test
    app.test.ts
    documents.test.ts
```

Do not add `server/middleware/` or `server/uploads/` until a second upload route exists. Put the multer instance next to the one route that uses it.

## Dependency direction

HTTP (`app.ts`) → entity module → `db.ts` / object store.

- `express.json()` is global for JSON routes. It does not parse multipart.
- Multer runs **only** on the upload route (`.single("file")`). Never `app.use(multer())`.
- The entity module receives bytes (`Uint8Array` / `Buffer`), a file name, and a content type. It does not read `req`.

## JSON vs multipart

| Body | Parser | Limit measures |
|---|---|---|
| Foundation fields | `express.json({ limit })` | JSON text |
| A file | `multer({ storage: memoryStorage(), limits })` | Raw file bytes |

Do not send file bytes as base64 inside JSON. That inflates the body by about one third and makes the JSON limit the file cap.

`memoryStorage()` when the next step is object storage (`put`). Do not write a temp file on disk first. Cap `fileSize` and `files` (usually `files: 1`). The default `fileSize` is unlimited.

The browser `FormData` field name and `multer.single("…")` must match. Do not set `Content-Type` on `fetch`; the boundary is part of that header.

## Errors

Multer calls Express error handling. In the four-argument handler, `err instanceof multer.MulterError` and `err.code === "LIMIT_FILE_SIZE"` is the over-size case. Return 413 and a UI-language message. Do not leave Multer’s English `File too large` as the staff-facing string if the rest of the UI is in another language.

## Testing

- **Over-size:** POST a body larger than `fileSize`; expect 413 and the staff-facing copy. Do not mock multer.
- **Happy path:** POST `multipart/form-data` with field `file`; expect 201 and the stored file name in the list. [`supertest`](https://www.npmjs.com/package/supertest) `request(app).post(…).attach("file", …)` (same API as SuperAgent). Prefer async/await and assert `status` / visible JSON (`error`, `fileName`). Do not assert object-store keys or other internals.
- Put HTTP tests in `server/__tests__/app.test.ts`. Schema CHECK tests belong in `server/__tests__/documents.test.ts`, not in the HTTP file.
- **Staff-visible upload:** e2e in a browser ([Playwright](https://playwright.dev/docs/intro)) in `e2e/` once a runner exists.
- If the repo has no runner yet, do not add a second test stack. Add tests where the app’s tests will live.

## What not to add

- Global multer middleware
- Disk `dest` when the destination is already object storage
- A second JSON-with-base64 upload next to multipart
- `busboy` by hand when multer is already the Express adapter
- Unlimited `fileSize`
