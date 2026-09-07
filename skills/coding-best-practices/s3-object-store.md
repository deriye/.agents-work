# S3-compatible Object store (AWS SDK v3)

**Applies:** One small module that `put`s bytes and mints a short-lived GET URL. MinIO on the laptop; S3-compatible storage in an Environment. Not the Firebase Storage SDK. Not an Express byte-proxy of the file.

**Sources:**

- [Generate a presigned URL (AWS SDK for JavaScript v3)](https://aws.amazon.com/blogs/developer/generate-presigned-url-modular-aws-sdk-javascript/) (`getSignedUrl` + `GetObjectCommand`; `expiresIn` in seconds)
- [@aws-sdk/s3-request-presigner](https://github.com/aws/aws-sdk-js-v3/blob/main/packages/s3-request-presigner/README.md) (pair with `S3Client`; default expiry 900s)
- [Amazon S3 — Presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html) (anyone with the URL can use it until it expires)

## When it applies

Document bytes live in an Object store. Metadata lives in Postgres (`documents.object_key`). Staff open a file through a portal route that checks the session, then 302s to a signed GET.

## Tree (only folders that have files)

```
server/
  objectStore.ts    # S3Client, put, signedGetUrl
  documents.ts      # object keys + documents rows; downloadUrl is a portal path
  app.ts            # GET …/documents/:docId/file → 302
```

Do not add `server/s3/` or a second client. Keep `put` and `signedGetUrl` on the same `S3Client`.

## Dependency direction

HTTP (`app.ts`) → `documents.ts` → `objectStore.ts`.

- `objectStore.ts` is the only file that imports `@aws-sdk/client-s3` and `@aws-sdk/s3-request-presigner`.
- `documents.ts` stores the key and returns a same-origin path (`/api/foundations/:id/documents/:docId/file`). It does not return an Object store origin. It also resolves the signed GET for the file route.
- `app.ts` calls that helper and `redirect`s (302). It does not import the S3 client. It does not `GetObject` and stream bytes.

Name the expiry (`60`) next to `getSignedUrl`. Sign with `OBJECT_STORE_ENDPOINT` (the host the staff browser will hit after the 302).

## Testing

- **HTTP:** [supertest](https://www.npmjs.com/package/supertest) in `server/__tests__/app.test.ts`. Session required (Better Auth sign-up cookie). GET file without session → 401. GET file with session → 302 whose `Location` includes `X-Amz-Signature` (or `X-Amz-Credential`). Do not mock the SDK. Do not assert the full signed URL.
- **Staff-visible open:** Playwright in `e2e/`: the file name is a link whose `href` is a portal `/api/foundations/…/documents/…/file` path, not host `:9000`.
- Do not add a second Object store test stack.

## What not to add

- `publicUrl` / a public-read bucket
- Streaming `GetObject` through Express
- A second `S3Client` only for signing
- CloudFront, extra wrapper packages, or vendor-specific SDKs beside `@aws-sdk/client-s3`
