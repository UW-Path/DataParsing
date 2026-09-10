# UWPath data pipeline

This repository builds versioned, auditable academic-calendar data for UWPath. The supported
pipeline reads Waterloo's public Kuali catalog, retains the raw responses, and emits normalized
JSON without changing a database.

The original Oracle/Postgres loader remains in the top-level legacy directories for reference.
It drops and recreates tables and is not part of the supported workflow.

## Quick start

Install [uv](https://docs.astral.sh/uv/), then run:

```sh
uv sync --dev
uv run uwpath-data list-kuali-years
uv run uwpath-data snapshot-kuali 2026-2027 \
  --program "Computer Science (BCS)"
```

The snapshot command follows the selected program's course links and recursively includes
courses referenced by prerequisites, corequisites, and antirequisites. Add `--program` more than
once to build a larger slice. Use `--full-catalog` instead to fetch every published program and
every active course; start with a slice as a canary before a multi-thousand-record backfill.

Output is written to `dist/catalogs/<academic-year>/`:

- `raw/` contains the source catalog, indexes, programs, and courses for reproducibility.
- `catalog.json` is the complete normalized artifact.
- `courses.json` and `programs.json` are convenient projections.
- `manifest.json` records content hashes and data-quality results.

After the canary succeeds, backfill several Kuali years in one resumable run:

```sh
uv run uwpath-data backfill-kuali \
  --all-available \
  --full-catalog \
  --output dist/catalogs \
  --resume
```

Existing releases are never trusted silently: `--resume` verifies each one
and confirms that its recorded scope and raw-snapshot policy match before
skipping it. Each new release is also verified in its staging directory before
the atomic swap into `dist/catalogs/`.

The normalized contract is `schema/catalog-v1.schema.json`. Unsupported requirement expressions
are preserved as `manual` rules rather than silently interpreted. A manifest is publishable only
when course codes are unique and every active-catalog reference resolves inside the artifact.
References to retired courses remain visible under `external_course_references`.
`planner_ready` is stricter and remains false while any manual rules exist.

Rebuild a normalized artifact later without touching the network:

```sh
uv run uwpath-data rebuild-kuali 2026-2027 \
  --raw dist/catalogs/2026-2027/raw \
  --program "Computer Science (BCS)" \
  --output dist/rebuilt
```

## Development

```sh
uv run ruff check src tests
uv run pytest
```

Source responses can change without notice. Review raw snapshots and quality metrics before
publishing a new academic year. Existing snapshots are not overwritten unless `--force` is passed.
`--without-raw` is available only for local investigation.

The `*_html` fields are untrusted source material retained for auditing. Consumers must sanitize
them before rendering.

See [`docs/BACKFILL.md`](docs/BACKFILL.md) for the year-by-year migration order, publication gates,
and backend compatibility milestone.

## Legacy loader

`PopulateDatabase.sh`, `CourseParsing/`, `ProgramParsing/`, and `Database/` are the historical
2019-2022 pipeline. They depend on old page layouts, hard-coded calendar years, and direct database
mutation. Keep them isolated while older calendars are migrated into the versioned contract.
