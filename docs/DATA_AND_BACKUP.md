# Data and Backup

## Data locations and contents

- `data/research.db` is the active SQLite database, resolved relative to `app.py`.
- `papers` stores normalized scholarly metadata and first/last-seen timestamps.
- `searches` stores user queries and per-provider time, counts, status, and notes. Treat this as private research activity data.
- `exports/` is created by the app but is not used by the current CSV download, which streams a file to the browser.
- Search topics are sent to OpenAlex and Crossref. Do not use confidential or personal queries.

At the 2026-10-20 audit, schema-only/count-only inspection found 25 paper rows and 4 search rows. No record contents were inspected for this documentation.

## Backup

Keep backups private and outside the repository. The root `.gitignore` excludes local data and exports, but ignore rules are not encryption or access control.

Use SQLite's backup API to create a new destination. The procedure below opens an existing source read-only, checks integrity and required tables, refuses to overwrite any destination, and closes all connections. Choose an existing private destination directory and a unique filename. Returned counts contain no research text; record them privately alongside the backup date and application version.

The following definitions are executed directly by the isolated backup tests. Defining them performs no database access. They can be pasted into a Python session before the example call below.

<!-- backup-workflow:start -->
```python
from contextlib import closing
from pathlib import Path
import sqlite3


def verify_database(connection):
    if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
        raise ValueError("Database integrity check failed.")
    tables = {
        row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    if not {"papers", "searches"}.issubset(tables):
        raise ValueError("Expected research tables are missing.")
    return {
        table: connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        for table in ("papers", "searches")
    }


def copy_database(source_path, destination_path):
    source_path = Path(source_path).resolve(strict=True)
    destination_path = Path(destination_path).resolve()
    with closing(sqlite3.connect(source_path.as_uri() + "?mode=ro", uri=True)) as source:
        verify_database(source)
        # Exclusive creation also refuses the source itself as the destination.
        with destination_path.open("xb"):
            pass
        with closing(sqlite3.connect(destination_path)) as target:
            source.backup(target)
            return verify_database(target)
```
<!-- backup-workflow:end -->

Example invocation from the project root, after choosing your own private destination (this production example was **not** executed):

```python
counts = copy_database("data/research.db", r"D:\PrivateBackups\research-YYYYMMDD-HHMMSS.db")
print(counts)
```

Any exception means the operation has not been verified. A failure after destination creation may leave an incomplete file; keep it separate and choose a new filename for a retry. Never use a failed copy for restore. The checks verify integrity and the two table names, not a schema-version compatibility policy or the scientific correctness of records.

SQLite's [backup API](https://www.sqlite.org/backup.html) creates a consistent snapshot, including committed WAL data. For simple operational verification, stop the app before backup so counts stay stable. The tests also cover committed WAL changes while another connection remains open; continuous concurrent writes and interrupted/disk-full backups have not been tested. Do not substitute a raw file copy while the app is running: the [WAL file is part of persistent database state](https://www.sqlite.org/wal.html#the_wal_file).

## Restore

Replacing `data/research.db` requires explicit approval from the data owner. This task rehearsed replacement only inside a temporary directory; it did not back up or restore production data.

1. Stop Streamlit and close every connection/tool using the database. If `research.db-wal`, `research.db-shm`, or `research.db-journal` remains, stop here. Do not delete sidecars or replace just the main file; resolve recovery first.
2. Run `copy_database` from the current database to a new private **pre-restore backup**. Verify success and record the counts. This preserves changes made since the selected older backup.
3. Run `copy_database` from the selected backup to a new candidate such as `data/research-restore-candidate.db`. The source stays read-only; the existing database remains in place. Compare the candidate's returned counts with the selected backup's recorded counts, not with today's database. Confirm that the backup belongs to this application/schema before proceeding.
4. With approval and all connections still closed, replace the current main file with the verified candidate using a same-directory file replacement (Python's `Path.replace` is exercised in the temporary-data rehearsal). Keep the selected backup and the pre-restore backup unchanged. Do not run a production replacement as part of routine tests.
5. Verify integrity and counts again, then start the app and check saved literature and search history. If verification fails, keep the app stopped and preserve the failed candidate for investigation.

For rollback, keep the app stopped, stage a **new** candidate from the pre-restore backup with `copy_database`, and repeat the same approved replacement and verification process. A restore or rollback discards changes made after its source backup, so retain the pre-replacement copy each time. The tests verify restoration of schema, synthetic records, and the search ID sequence, followed by rollback to the newer temporary state. Production UI verification and crash/power-loss recovery remain untested.

## Verification: 2026-10-20

`python -m unittest discover -s tests -p test_backup.py -v` passed all five backup tests on Python 3.14.7. The full command `python -m unittest discover -s tests -v` passed all 21 tests. Tests create disposable databases using only the active app's extracted `connect_db` definition and execute the marked workflow definitions above; the full application is never imported. They cover schema/data/ID-sequence restoration and rollback, committed WAL data, missing and invalid sources, required tables, existing destinations, and source-as-destination refusal. The source path also exercises spaces, Unicode, and URI escaping.

No production backup or restore was performed. Production research records were not read by these tests. A protected-file hash comparison confirms the application, database, historical scripts, and requirements are unchanged. Testing does not establish crash recovery, disk-full handling, continuous-write performance, or compatibility with future schemas or other Python versions.

## Schema safety

The app currently creates its two tables with `CREATE TABLE IF NOT EXISTS`; there is no schema version, migration runner, or automated migration rollback. The manual data-restore procedure above does not introduce schema migration support. Do not change the schema until a migration and tested backup/restore plan has explicit approval. Tests must create databases under temporary directories and must never connect to `data/research.db`.

The [Schema Migration Policy](SCHEMA_MIGRATIONS.md) documents requirements for a future implementation, including legacy recognition, application compatibility, atomic version updates, candidate verification, and recovery. The backup verifier above checks integrity and table names; it is not the full schema compatibility validator required by that policy.
