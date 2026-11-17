# Schema Version and Migration Policy

Status: documented policy for future implementation, 2026-10-20. No migration runner, startup compatibility check, schema version assignment, or production migration is implemented by this task. Approval to document this policy does not authorize changing database metadata, schema, or records.

## Current verified behavior

`app.py` is the active application. Its `connect_db` function creates `papers` and `searches` with `CREATE TABLE IF NOT EXISTS`, then commits. It does not inspect or set `PRAGMA user_version`, recognize incompatible schemas, or perform upgrades. Existing tables are not validated by `CREATE TABLE IF NOT EXISTS`.

The current code defines these application tables:

| Table | Identity | Other columns |
| --- | --- | --- |
| `papers` | `record_key TEXT PRIMARY KEY` | `title`, `doi`, `year`, `work_type`, `abstract`, `authors`, `source`, `url`, `first_saved_utc`, `last_seen_utc` |
| `searches` | `id INTEGER PRIMARY KEY AUTOINCREMENT` | `query`, `searched_utc`, `source`, `reported_count`, `retrieved_count`, `status`, `note` |

The complete types and constraints are defined by `connect_db`; the table above is an inventory, not a compatibility validator. SQLite also maintains internal objects such as `sqlite_sequence`. The production database's version metadata was not inspected in this task; do not assume its value from the application's lack of versioning code.

## Version convention for a future runner

Use a monotonically increasing positive integer in `PRAGMA user_version` as the application schema version. SQLite provides this field for application use; it does not enforce a migration policy. Do not use or manually modify SQLite's internal `schema_version` counter for this purpose. See the official [user_version](https://www.sqlite.org/pragma.html#pragma_user_version) and [schema_version](https://www.sqlite.org/pragma.html#pragma_schema_version) documentation.

- Reserve version **1** for the exact existing application schema, once its historical fixture and recognition checks have been implemented and reviewed. This document does not stamp any database as version 1.
- A database reporting **0** is only a candidate for legacy recognition. Compare its full expected schema before adopting version 1: columns/types/nullability, primary keys, defaults, indexes, triggers, views, and foreign keys. Explain any SQLite-generated objects explicitly. Do not infer compatibility from table names, row counts, or the version integer alone.
- Stop without writes for unknown shapes, unexpected extra objects, missing required tables, invalid integrity checks, unsupported version gaps, or versions newer than the application supports. Do not silently repair or relabel an unfamiliar database.
- Distinguish creating a deliberately new database from opening an existing file. An empty or incomplete existing database must not be treated as a fresh installation without an explicit recovery decision.
- Each upgrade has one source version and one target version, normally `N` to `N+1`. Apply ordered, reviewed steps; never rerun an applied transformation or silently downgrade. Repeating an upgrade request for an already matching target should verify compatibility and make no changes.
- Keep applied migration definitions immutable and record their source hashes with the associated application snapshot. A correction is a new migration. No extra migration-history table is authorized by this policy.

Introducing version metadata is itself a database change, even when no columns change. Its first adoption needs the same review, backup, isolated tests, and production approval as any other migration.

## Preparation and approval

Prepare the concrete migration and recovery plan before requesting production approval. Existing authorization for that specific plan remains valid; routine implementation and isolated testing do not need repeated permission. A general request to maintain the project does not authorize a new production schema change.

Every proposed migration must record:

- The user-visible reason, source/target versions, affected tables/columns/indexes, exact transformations, and expected count changes, if any.
- Which application snapshot can read and write each schema; the Python and SQLite versions actually tested. Preserve an executable copy of the previous application before switching databases, since Git history is not available in this workspace.
- Data invariants: record keys/DOIs, source merging, nullable values, timestamps, search history, constraints, and the search ID sequence. Any intentional data loss or reclassification needs specific approval.
- The private backup and staged-candidate locations, verification commands/results, required disk space, downtime, failure handling, and rollback procedure. Keep private record text and backup contents out of repository logs and documentation.
- The exact scope of production approval, including metadata adoption, schema/data transformations, and candidate replacement. If an approved plan materially changes, revise the reviewable plan and obtain approval for the additional production changes.

Read-only inspection of schema/version metadata is distinct from migration. Tests must always use temporary databases and synthetic records; production data must not become a fixture or be passed to an experimental migration. Any authorized operational copy remains private user data and is separate from the automated test suite.

## Execution requirements for future implementation

1. **Test first.** Freeze a synthetic fixture for each supported historical schema, independent of the current `connect_db` implementation. Rehearse upgrade, failure, and rollback using the criteria below. A fixture regenerated only from the newest app cannot prove historical compatibility.
2. **Preserve the source.** When authorized to proceed, stop the app and close other database clients. Follow [Data and Backup](DATA_AND_BACKUP.md), resolve sidecars, create and verify a fresh pre-change backup, and preserve the matching old application snapshot. Retain both throughout verification.
3. **Stage the upgrade.** Copy the verified backup to a new candidate. Recheck its source version and full schema before any write. Migrate the candidate rather than experimenting on `data/research.db`. Keep the app stopped so no new records diverge from the backup/candidate.
4. **Make each step atomic.** Use an explicit transaction for the schema changes, data transformations, and version update together. With the chosen Python transaction mode configured deliberately, acquire the candidate's write transaction with `BEGIN IMMEDIATE`, recheck preconditions, apply the step, validate its data/schema, set its target `user_version`, read that value back, and commit. On any failure, roll back and stop; never continue from a partial or uncertain state. Test failures both before and after the version update, including commit failure handling.
5. **Respect transaction boundaries.** Do not rely on implicit transaction behavior or assume `executescript` preserves an existing transaction. Its behavior depends on Python's transaction configuration; use tested statement execution and explicit boundaries. Operations requiring separate transaction handling need a separately reviewed plan. See [SQLite transactions](https://www.sqlite.org/lang_transaction.html) and [Python transaction control](https://docs.python.org/3.14/library/sqlite3.html#transaction-control).
6. **Verify the reopened candidate.** Confirm target version and exact schema, integrity, expected counts and record invariants, search ID continuity, and foreign-key checks where applicable. Confirm the compatible application can read, save, deduplicate, and export synthetic migrated data. Counts alone cannot prove records survived correctly.
7. **Replace only with authorization.** Once production approval covers the tested change, use the stopped-app, same-directory candidate replacement and verification procedure in [Data and Backup](DATA_AND_BACKUP.md). Keep the old database backup and application snapshot intact. Recheck the reopened database before resuming normal use; record results without research text.

A future application must check supported schema/version before initialization or any save operation and refuse incompatible databases. Automatic upgrade during Streamlit reruns is outside this policy. The present application has no such check; introducing one is a separate implementation task, and the old application must not be opened against a migrated database without demonstrated compatibility.

## Failure and rollback rules

| Failure point | Required response |
| --- | --- |
| Source recognition, backup, or candidate validation fails | Stop before replacement; preserve the original and report the failed check. |
| An upgrade step fails on the candidate | Roll back that transaction, preserve diagnostic evidence privately, and leave production unchanged. A previously committed step may remain on the candidate; resume only from a verified supported state or build a fresh candidate. |
| Verification fails after replacement, before normal use resumes | Keep the app stopped, preserve the failed database, and stage a fresh candidate from the pre-change backup. Restore the matching previous application and verify the restored database before reopening. |
| Recovery is requested after new records have been saved | Stop writes and preserve the latest state first. Explain the post-backup records that a restore would discard and obtain specific approval or prepare a separate reconciliation plan. Never silently restore an older snapshot. |

Restoring a database backup is the default recovery method. Reverse DDL is not a proven data rollback: dropping a newly populated column, for example, loses its values. Do not offer an automatic downgrade unless a separately approved and tested procedure preserves the required data. Keep recovery copies until the user accepts the result; do not delete them as routine cleanup.

## Required isolated verification for each implemented migration

- Recognize the frozen historical schema accurately; reject mismatched/unrelated schemas and future versions without modifying them.
- Verify successful legacy adoption and each supported ordered upgrade path. An already migrated database must not duplicate records or repeat transformations.
- Compare synthetic records, keys, NULLs, Unicode, timestamps, source values, constraints, indexes/triggers where present, and search IDs before/after. Define every allowed difference in advance.
- Inject failures during transformation and around the version update. Verify committed schema/data/version remain consistent and that the original and backup remain unchanged. Test rejected replacement and recovery when a connection is still open.
- Rehearse backup restoration with the matching old application and test relevant UI/persistence/export paths against a temporary migrated database. Importing the live Streamlit script without an isolated database remains prohibited.

Run the complete existing suite as well. The existing suite verifies application helpers, backup/restore rehearsal, and isolated headless UI behavior; it does **not** verify these future migration requirements. No migration tests are claimed until an actual implementation is approved, written, and executed. Power-loss recovery, storage exhaustion, and cross-version compatibility remain unverified unless specifically exercised.
