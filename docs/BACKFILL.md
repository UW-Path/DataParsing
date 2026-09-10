# UWPath catalog backfill

The backfill should produce one immutable, versioned artifact per academic year before any data is
loaded into the backend. The frontend stays on its existing routes and data shape until the backend
can serve a compatibility response from a validated artifact.

## Source coverage

| Academic years | Source | Approach |
| --- | --- | --- |
| 2023-2024 through 2026-2027 | Waterloo Kuali catalog | Use the supported `snapshot-kuali` adapter. |
| 2019-2020 through 2022-2023 | Retained legacy HTML and archived calendar pages | Build a separate adapter that emits the same v1 contract; never write directly to the database. |
| Term offerings | Waterloo Open Data, when credentials are available | Add as a separate dated dataset; do not mix offerings with calendar requirements. |

The public Kuali endpoint is not a documented compatibility contract. Every run must retain its raw
responses so parser changes can be tested without repeatedly querying Waterloo.

## Execution order

1. Run a current-year BCS slice as the canary.

   ```sh
   uv run uwpath-data snapshot-kuali 2026-2027 \
     --program "H-Computer Science (BCS)" \
     --output dist/canary
   ```

2. Inspect the manifest, representative rule trees, and all `manual` rules on the selected program.
   Course-level manual rules may describe standing, enrolment, grades, or permissions and must not
   be silently converted into course prerequisites.
3. Run the full current catalog only after the canary passes.

   ```sh
   uv run uwpath-data snapshot-kuali 2026-2027 \
     --full-catalog \
     --output dist/catalogs
   ```

4. Rebuild from `raw/` and verify that `courses.json` and `programs.json` hashes match the network
   run. A timestamp-only change in `catalog.json` is expected.

   ```sh
   uv run uwpath-data verify-catalog dist/catalogs/2026-2027
   uv run uwpath-data compare-catalogs \
     dist/catalogs/2025-2026 \
     dist/catalogs/2026-2027
   ```
5. Repeat newest-to-oldest for the three earlier Kuali years. The resumable runner performs this
   sequence without overwriting an existing release:

   ```sh
   uv run uwpath-data backfill-kuali \
     --all-available \
     --full-catalog \
     --output dist/catalogs \
     --resume
   ```

   Compare course/program counts and rule coverage between adjacent years; investigate large
   deltas before activating any release.
6. Implement the legacy HTML adapter one year at a time, starting with 2022-2023. Preserve each
   original file and map unsupported expressions to `manual` rules. Do not call the old destructive
   database loader as part of this workflow.
7. Add backend import tables keyed by academic year and artifact hash. Load into a staging version,
   validate counts and references, then atomically mark that version active. Keep existing API
   response shapes while this migration is underway.

## Publication gates

A catalog can be published only when all of these are true:

- Runtime JSON Schema validation passes.
- `duplicate_course_codes` and `dangling_course_references` are empty.
- Raw responses are retained and an offline replay succeeds.
- Course and program count deltas from the adjacent year have been reviewed.
- Every program-level `manual` rule has an owner and a disposition.
- A backend staging import returns the same calendar year, counts, and artifact hash.

`external_course_references` are allowed when the referenced code is absent from the active course
index, which commonly happens for retired antirequisites. They remain visible for auditing.
`planner_ready` is a stricter signal: it stays false while any manual rule remains.

## Backend compatibility milestone

Before touching frontend presentation, make the existing frontend work against a backend that can:

- list available academic years;
- serve courses and programs for an explicit year;
- default old requests to a configured active year;
- report the artifact hash and schema version used for a response; and
- roll back by switching the active artifact, without deleting loaded versions.

The first end-to-end release should use the BCS canary. Full-catalog activation follows only after
the same import and route checks pass at full scale.
