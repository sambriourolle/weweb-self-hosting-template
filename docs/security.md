# Security and data

This is an experimental local scaffold, not a security certification or production deployment guide.

## Secrets and supplied exports

- Copy `.env.example` to `.env` and replace every `CHANGE_ME` value with a different random secret. No example value is usable as a credential.
- Do not commit `.env`, `imports/`, backups, dumps, test results, or built images containing a private export. The first four paths are ignored by Git; `.env*` is excluded from Docker build contexts.
- Inspect exports before copying them. Their code can contain integration configuration or secrets even though this scaffold excludes `.env*` during its own build.
- Build copies are ephemeral Docker layers but still contain your application code. Do not publish or share a resulting image without a separate audit.

## Network and authentication scope

The only tested network scope is loopback HTTP: `BIND_ADDRESS=127.0.0.1`, `APP_URL=http://127.0.0.1:8080`, and `LOCAL_HTTP=true`. The preparer relaxes cookie settings only for that mode.

For a LAN or public deployment, terminate HTTPS, set the public `APP_URL`, set `LOCAL_HTTP=false`, restrict network exposure, and verify login, session renewal, logout, CORS/origin behaviour, and uploads in the browser. Do not treat an open port or a healthy container as an authentication review.

The compose defaults enable the tested email provider settings, but they do not create an administrator or otherwise guarantee that sign-up is safe for your export. Review the first-account and sign-up flow in the exported app before exposing it to anyone else.

## Storage and recovery

PostgreSQL and MinIO use named Docker volumes. They persist across `docker compose down`; they are deleted by `docker compose down -v`.

The MinIO application user is separate from the root user. Its policy is deliberately broad across both buckets in this stack and is not an isolation boundary between mutually untrusted applications.

PostgreSQL initialization SQL runs only when the database volume is new. It must include the schema required by your exact export, including WeWeb Auth tables when applicable. A code export plus an empty SQL directory is not a working application.

Persistence is not backup. Keep independent PostgreSQL and MinIO backups, protect them at least as carefully as production data, and restore-test them in a separate environment before relying on them. No recovery procedure is validated or shipped here.

For operational checks, see [troubleshooting](troubleshooting.md). For deliberately supported export boundaries, see [compatibility](compatibility.md).
