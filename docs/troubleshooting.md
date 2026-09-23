# Troubleshooting

Start with the configuration and unit checks; neither exposes `.env` values:

```sh
python3 -m unittest discover -s tests/unit -v
docker compose --env-file .env.example config --quiet
```

## `ERREUR DE COMPATIBILITÉ` during a build

The export does not match a required file or exact patch signature. Read [compatibility](compatibility.md), identify the changed path, and compare it with your export version. Do not delete signature checks or apply a broad search-and-replace. Extend the preparer only with a focused fixture test and a bounded patch.

## Missing `package-lock.json`, `npm ci`, or frontend build failures

Both Dockerfiles copy `package.json` and `package-lock.json` before running `npm ci`. Supply export roots that contain those files and the expected build scripts. This scaffold does not generate lockfiles or repair arbitrary package dependency trees.

## Database starts but the application fails

Check that `imports/database/` contained your SQL before PostgreSQL created its volume. Initialization scripts run once, so adding SQL later changes nothing in the existing database. Inspect container logs without pasting credentials, confirm the expected schemas/tables exist, then use an explicit migration or a disposable fresh-volume test. Do not erase real data with `docker compose down -v` to retry initialization.

## Login, signup, or session does not work

Confirm that `APP_URL` exactly matches the address in the browser, including its port, and rebuild after changing it. For the default loopback mode, keep `LOCAL_HTTP=true`. For HTTPS deployment, set the final HTTPS `APP_URL`, set `LOCAL_HTTP=false`, and test cookies and the actual sign-up/login workflow in the browser.

The scaffold does not create an account. Account behaviour depends on the supplied backend export, schema, and workflows; the compose provider variables are only inputs to that export.

## Uploads or files fail

Verify that the backend export is configured for `aws-s3`, and that bucket names, prefixes, region, and application credentials in `.env` match the export's expected variables. MinIO initialization creates the configured buckets without removing existing objects. Test upload and download through the browser, not only the MinIO service.

## Services start but state disappears after recreation

Use `docker compose down` or `docker compose up -d --force-recreate`, not `down -v`, when testing normal persistence. Check that the named `postgres-data` and `minio-data` volumes remain. Named volumes are local persistence only; recover from an independently tested backup if data has been removed.

## What to include in a report

Provide the redacted failure message, export versions, the failing stage, and whether the database volume was new or existing. Exclude `.env`, SQL containing data or credentials, dumps, private exports, and user files.
