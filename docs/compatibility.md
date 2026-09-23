# Compatibility

This scaffold intentionally supports a narrow, tested export shape. It does not promise compatibility with every WeWeb version, integration, workflow topology, or deployment target.

## Tested shape

The preparer has been exercised with exports that provide:

- Node `24.12.0` runtime images; a backend with `src/index_server.ts`.
- `weweb-auth`, `weweb-storage`, and `aws-s3` backend integration files at the paths checked by `scripts/prepare.py`.
- Hono workflow routes whose API metadata uses `/api/...` paths and `{parameter}` placeholders.
- A Vite frontend with `vite.config.js`, `src/extensions/**/package.json`, and `@weweb-internal/...` extension imports.

The pinned infrastructure images are PostgreSQL `17.7-bookworm`, MinIO `RELEASE.2025-06-13T11-33-47Z`, MinIO Client `RELEASE.2025-07-21T05-28-08Z`, Nginx `1.29.3-alpine`, and Node `24.12.0-bookworm-slim`.

## Build-time changes

`prepare.py` copies both supplied exports into an image build directory. It excludes `.env*`, `.git`, `node_modules`, and selected build/cache directories, then applies these changes to the copies:

- register the AWS S3 integration and pass the configured MinIO endpoint with path-style addressing;
- allow non-secure cookies only while `LOCAL_HTTP=true`;
- merge workflow path parameters with query or body parameters;
- normalize `/api/...` metadata paths for the backend and support the observed frontend `/api/api/...` request shape in Nginx;
- add Vite aliases for exported internal extensions and rewrite observed extension `/config` imports.

The source exports are never edited by this process.

## Intentional failures

Every text replacement must match exactly once. Missing files, changed signatures, an unknown Vite alias block, or no matching internal frontend extension ends the build with `ERREUR DE COMPATIBILITÉ`. A failure is safer than starting an export with an assumed patch.

Do not remove those checks to force a build. Compare the new export with the supported signature, add a focused fixture test for the changed export shape, then add a bounded, versioned patch. An application can still require project-specific workflow or frontend configuration that this scaffold cannot infer.

The `/api/api` Nginx rule exists because that request shape was observed in the tested export. Different route topologies require a deliberate compatibility extension and test, not a guessed proxy rule.

See [troubleshooting](troubleshooting.md) for safe diagnostics and [security and data](security.md) before sharing logs or images.
