# CI/CD and manual production deployment

## Delivery model

GitHub Actions runs tests for pull requests and pushes to `main`. It builds the
container for pull requests without publishing it. After a successful push to
`main`, it publishes two GHCR tags:

- `sha-<full-git-commit>` for an explicit deployment;
- `latest` as a convenient pointer to the newest successful `main` build.

Production deployment must use the full `sha-...` tag. The deployment script
rejects `latest`, so a new image is never installed merely because it was
published.

The production server initiates all communication with GHCR over outbound
HTTPS. GitHub does not need an inbound SSH or HTTP port on the server.

## One-time server setup

Copy these files to one directory on the server:

- `compose.production.yaml`;
- `deploy.sh`;
- `.env` containing the production runtime configuration.

Make the script executable:

```bash
chmod +x deploy.sh
```

For a private GHCR package, create a GitHub token with `read:packages` and log
Docker in once. Do not store the token in `.env` or in the repository:

```bash
read -rsp "GHCR token: " GHCR_TOKEN
printf '%s' "$GHCR_TOKEN" | docker login ghcr.io -u Drumbler --password-stdin
unset GHCR_TOKEN
```

The production `.env` must provide at least:

```dotenv
DB_NAME=calculator_data
DB_USER=calculator_user
DB_PASS=replace_me
CALCULATION_CACHE_TTL=21600
```

`DB_IP`, `DB_PORT`, and `REDIS_URL` are set by the production Compose file.

## Deploy a selected build

Copy the full `sha-...` tag from the successful GitHub Actions run or the GHCR
package page, then run:

```bash
./deploy.sh sha-0123456789abcdef0123456789abcdef01234567
```

The script performs these steps:

1. validates the Compose configuration and the immutable-looking commit tag;
2. pulls the API and migration image;
3. starts PostgreSQL and Redis;
4. applies Alembic migrations;
5. replaces the API container;
6. waits for the API healthcheck.

If migrations fail, the running API is not replaced. If the new API fails its
healthcheck, the script prints its logs and the previous image reference.

## Rollback

An older application image can be selected by running `deploy.sh` with its
previous full `sha-...` tag. Review database migration compatibility first:
rolling back application code does not automatically downgrade the database.

The last successful image reference is recorded in `.deployed-image`.

## Bytecode-only application image

The multi-stage Docker build compiles `app/` and `migrations/` to legacy,
source-adjacent `.pyc` files and removes their `.py` files. The builder and
runtime stages use the same exact Python version because Python bytecode is
version-specific.

Third-party packages in `/opt/venv` retain their source files. Removing source
from all of `site-packages` can break packages that load source or data files at
runtime. Python bytecode is also not encryption and can be decompiled; this
layout is packaging and source-reduction, not a secret-protection boundary.

## Later automated deployment

A GitHub-hosted runner can deploy over SSH only when it has a network route to
the server. With no inbound port, the practical alternative is a self-hosted
runner that maintains an outbound connection to GitHub. Such a runner can
execute repository workflow code on the production machine, so it should be
combined with a protected GitHub Environment, required approval, protected
branches, and a narrowly scoped runner. Manual pull deployment is the safer
initial setup.
