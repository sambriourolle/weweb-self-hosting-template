# Self-host a known-compatible WeWeb export

> **Experimental, unofficial scaffold.** It runs the frontend and backend exports **you provide**. This repository contains no WeWeb export, application data, database schema, user, object, or secret.

This is a deliberately narrow Docker Compose setup for one tested family of WeWeb exports: Node 24, a Hono backend using WeWeb Auth and `aws-s3`, plus a Vite frontend with WeWeb internal extensions. It fails the build when the expected export signatures are absent rather than silently producing a partly patched application. It is not a general WeWeb self-hosting solution, a production hardening guide, or an offline installer.

## What it runs

- PostgreSQL 17.7 and MinIO with persistent Docker volumes.
- Your actual frontend behind Nginx, exposed only at `127.0.0.1:8080` by default.
- Your actual backend, reachable through the frontend at `/api`.
- Build-time preparation of copies of your exports. Source exports are not edited.

The build removes copied `.env*` files, ignores common generated directories, and applies exact, signature-checked patches for the tested export shape: S3 driver registration and MinIO endpoint support, loopback HTTP cookies, workflow path parameters and route normalization, and frontend extension aliases. See [compatibility](docs/compatibility.md).

## Before you start

You need Docker Compose, the root directories of **your own** frontend and backend exports, and SQL for **your own** database. Code exports alone do not contain the PostgreSQL schema, WeWeb Auth tables, application rows, or MinIO objects.

Place one or more `*.sql` files in `imports/database/` before the first startup. For an app using WeWeb Auth, the SQL must create the `auth` schema and tables expected by that exact backend export. Generate or export the schema from a source you control and test it in a disposable project.

Do not copy exports that contain credentials without reviewing them first. The repository ignores `imports/` and `.env`; Docker also excludes `.env*` from its build context. Those safeguards do not make an unreviewed export safe.

## Setup

```sh
git clone https://github.com/sambriourolle/weweb-self-hosting-template.git
cd weweb-self-hosting-template
cp .env.example .env
# Edit .env. Replace every CHANGE_ME with a distinct random value.
# Example generator (do not reuse its output): openssl rand -base64 36
```

Copy the *contents* of each export root into the matching empty import directory. Use a non-destructive copy command appropriate for your platform; do not use a command that deletes destination files unless you have inspected and intentionally chosen that behaviour. For example, after checking the source and destination:

```sh
cp -a /path/to/frontend-export/. imports/frontend/
cp -a /path/to/backend-export/. imports/backend/
cp -a /path/to/database-sql/. imports/database/
```

Then build and start:

```sh
docker compose up --build
```

There is no separate prepare command: both Dockerfiles run `scripts/prepare.py` during their builds. Open the exact URL in `APP_URL` (default: <http://127.0.0.1:8080>).

## Configuration and first use

`APP_URL` is both the browser origin and a frontend build argument. It must match the URL users visit, including the port. Change it only before a rebuild.

The supplied defaults bind the frontend to loopback and set `LOCAL_HTTP=true`. They are intended only for same-machine HTTP testing. For LAN or Internet access, use HTTPS, a safe origin, `LOCAL_HTTP=false`, network controls, and explicit authentication testing; changing `BIND_ADDRESS` alone is not sufficient. This scaffold does not claim TLS, public deployment, or offline-build support.

There are no application credentials or accounts in this repository. The compose file passes the tested WeWeb Auth defaults (`PROVIDER_EMAIL_ENABLED=TRUE`, email verification disabled, signup not disabled), but the actual first-login and account-creation experience is determined by your backend export, its SQL, and its workflows. If your export does not support those settings, it will not become functional merely because these variables exist.

MinIO creates the configured buckets and a separate application user. Configure bucket names, prefixes, and integrations to match your export in `.env`.

## Data, initialization, and backups

`imports/database/*.sql` is processed by the PostgreSQL image **only when its data volume is first created**. Editing SQL after initialization is not a migration. Write and test an explicit migration for an existing database; do not use `docker compose down -v` as a way to reinitialize data.

`docker compose down` keeps the named PostgreSQL and MinIO volumes. `docker compose down -v` removes them and destroys the database and stored objects.

Volumes provide persistence, not backups. Back up PostgreSQL and MinIO independently before upgrades, and validate a restore into a separate environment. This repository does not provide a verified backup or recovery procedure.

## Verify your export

```sh
python3 -m unittest discover -s tests/unit -v
docker compose --env-file .env.example config --quiet
# After startup (do not print .env values):
curl -i http://127.0.0.1:8080/api/auth/get-session
```

The session endpoint should not return a 5xx response, but that alone does not validate your schema, authentication, workflows, or storage. In the exported browser application, test account flow, an authenticated API route, upload and retrieval through S3, then recreate the services with `docker compose up -d --force-recreate` and test persistence again.

## Operations and help

- [Compatibility](docs/compatibility.md) — the exact supported export shape and intentional build failures.
- [Security and data](docs/security.md) — secrets, local HTTP scope, storage policy, and backups.
- [Troubleshooting](docs/troubleshooting.md) — common build, initialization, origin, and persistence checks.

When reporting a compatibility issue, include export versions and a redacted error. Never attach `.env`, real SQL, database dumps, user data, or a private export.

## License

This repository's scripts, Dockerfiles, and documentation are MIT-licensed. Your WeWeb exports remain subject to their own licenses and terms; provide them locally and do not redistribute them here.
