# Django URL Shortener

A URL shortener built with Django, following a services-layer architecture that separates URL creation from URL resolution. Built on [cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django), with Docker, PostgreSQL, Redis, and Celery.

## What it does

- Paste a long URL, get back a short, unique code (e.g. `yoursite.com/4pdm00`)
- Visiting a short URL redirects to the original — fast, via a Redis-backed cache
- Logged-in users can view a dashboard of all links they've created, with click counts and last-clicked timestamps

## Short code generation

Short codes are generated deterministically:

1. Hash the long URL (plus an optional salt) with SHA-256.
2. Take the first 6 hex characters of the digest, convert to an integer.
3. Re-encode that integer in base62 (`0-9a-zA-Z`), left-padded to exactly 6 characters.

The same URL always produces the same code on the first attempt (no salt), so shortening the same link twice doesn't create duplicate rows. On a collision — caught via the database's own unique constraint (`short_code` is the model's primary key), not a pre-check — the code retries with a timestamp-based salt, up to 3 attempts, wrapped in `transaction.atomic()` so a failed attempt doesn't leave the connection in a broken state for the next retry.

## Caching

`redirector` checks Redis (via Django's cache framework) before touching Postgres. On a cache miss, it looks up the URL, caches it for 24 hours, and falls through to the database on every subsequent request until the cache expires. This keeps the highest-traffic endpoint in the app — the redirect itself — off the database for the common case.

Click tracking is also decoupled from the request path: instead of writing to Postgres on every redirect, each click increments a per-short-code counter directly in Redis (`cache.incr()`, falling back to `cache.set(key, 1)` on the first click for a given code). A Celery Beat task periodically flushes these pending counters into Postgres in a batch and clears them, so the hot redirect path never blocks on a database write.

## Tech stack

- **Django** — web framework
- **PostgreSQL** — primary datastore
- **Redis** — caching layer for redirect lookups
- **Celery** — background task queue, batches click-count writes so redirects never block on a synchronous database write
- **Docker / Docker Compose** — local development environment
- **pytest / pytest-django** — testing

## Running locally

```bash
docker compose -f docker-compose.local.yml build
docker compose -f docker-compose.local.yml up
```

Run migrations and create a superuser:
```bash
docker compose -f docker-compose.local.yml run --rm django python manage.py migrate
docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser
```

Visit `http://localhost:8000`.

## Running tests

```bash
docker compose -f docker-compose.local.yml run --rm django pytest -v
```

Tests cover the short code generation algorithm (encoding edge cases, determinism, collision retry) and the redirect/caching logic (cache hit vs. miss, click tracking, 404 handling for nonexistent codes) using both unit tests with mocked models and integration tests against a real test database.

## Design decisions worth noting

- **`short_code` is the model's primary key**, not a separate auto-increment ID — it's the field every read query filters on, so it gets Postgres's automatic PK indexing for free, with no redundant column.
- **Collision handling relies on the database's unique constraint, not a `filter().exists()` pre-check** — the pre-check approach has a race window where two concurrent requests can both pass the check before either commits. Catching `IntegrityError` on the actual insert is the only version that's actually race-safe.
- **Redirects use a 302 (temporary) rather than a 301 (permanent) response.** 301s get cached aggressively by browsers, which would silently break click tracking after a user's first visit to a given short link — 302 keeps click counts accurate at the cost of a marginally less SEO-optimal redirect, a deliberate trade-off for an app whose whole value is in its analytics.

## Possible next steps

- Finish wiring the REST API (`ShortenURLView` + `ShortenURLSerializer` exist; needs input validation and endpoint tests)
- Scheduled cleanup of old, unused short links
- Rate limiting on the shorten endpoint to prevent abuse
