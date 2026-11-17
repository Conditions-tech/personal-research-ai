"""Rehearse the documented workflow against disposable app-schema databases."""

import ast
import hashlib
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_documented_workflow():
    text = (ROOT / "docs" / "DATA_AND_BACKUP.md").read_text(encoding="utf-8")
    section = text.split("<!-- backup-workflow:start -->", 1)[1]
    section = section.split("<!-- backup-workflow:end -->", 1)[0]
    code = section.split("```python\n", 1)[1].split("```", 1)[0]
    tree = ast.parse(code)
    if not all(isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef)) for node in tree.body):
        raise AssertionError("Workflow definitions must have no top-level actions.")
    namespace = {}
    exec(compile(tree, "DATA_AND_BACKUP.md", "exec"), namespace)
    return namespace


class DatabaseBackupTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="research backup ")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.source = self.root / "source #café.db"
        self.copy_database = load_documented_workflow()["copy_database"]

        # Compile only schema initialization, never app imports or UI setup.
        tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
        definition = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "connect_db"
        )
        namespace = {"sqlite3": sqlite3, "DB_PATH": self.source}
        exec(compile(ast.Module(body=[definition], type_ignores=[]), "app.py", "exec"), namespace)
        with closing(namespace["connect_db"]()) as connection, connection:
            connection.executemany(
                "INSERT INTO papers (record_key, title, source, first_saved_utc, last_seen_utc) "
                "VALUES (?, ?, ?, ?, ?)",
                [
                    ("test:one", "Synthetic café paper", "OpenAlex", "test-time", "test-time"),
                    ("test:two", "Synthetic conference paper", "Crossref", "test-time", "test-time"),
                ],
            )
            connection.execute(
                "INSERT INTO searches (query, searched_utc, source, status) VALUES (?, ?, ?, ?)",
                ("synthetic topic", "test-time", "OpenAlex", "success"),
            )

    def snapshot(self, path):
        with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as connection:
            return tuple(connection.iterdump())

    def digest(self, path):
        return hashlib.sha256(path.read_bytes()).digest()

    def test_backup_restore_and_rollback_preserve_schema_records_and_sequence(self):
        original_state = self.snapshot(self.source)
        original_digest = self.digest(self.source)
        backup = self.root / "backup.db"
        self.assertEqual(self.copy_database(self.source, backup), {"papers": 2, "searches": 1})
        self.assertEqual(self.snapshot(backup), original_state)
        self.assertEqual(self.digest(self.source), original_digest)
        backup_digest = self.digest(backup)

        # Simulate later activity that must be preserved in a pre-restore copy.
        with closing(sqlite3.connect(self.source)) as connection, connection:
            connection.execute("DELETE FROM papers WHERE record_key = ?", ("test:two",))
            connection.execute(
                "INSERT INTO searches (query, searched_utc, source, status) VALUES (?, ?, ?, ?)",
                ("later synthetic topic", "later-test-time", "Crossref", "success"),
            )
        newer_state = self.snapshot(self.source)
        self.assertNotEqual(newer_state, original_state)
        rollback = self.root / "pre-restore.db"
        self.assertEqual(self.copy_database(self.source, rollback), {"papers": 1, "searches": 2})
        rollback_digest = self.digest(rollback)

        candidate = self.root / "restore-candidate.db"
        self.assertEqual(self.copy_database(backup, candidate), {"papers": 2, "searches": 1})
        self.assertEqual(self.snapshot(candidate), original_state)
        self.assertEqual(self.snapshot(self.source), newer_state)
        # Both paths are explicitly inside the disposable directory.
        candidate.replace(self.source)
        self.assertEqual(self.snapshot(self.source), original_state)

        rollback_candidate = self.root / "rollback-candidate.db"
        self.assertEqual(self.copy_database(rollback, rollback_candidate), {"papers": 1, "searches": 2})
        rollback_candidate.replace(self.source)
        self.assertEqual(self.snapshot(self.source), newer_state)
        self.assertEqual(self.digest(backup), backup_digest)
        self.assertEqual(self.digest(rollback), rollback_digest)

    def test_missing_source_does_not_create_a_database_or_destination(self):
        missing = self.root / "missing.db"
        destination = self.root / "backup.db"
        with self.assertRaises(FileNotFoundError):
            self.copy_database(missing, destination)
        self.assertFalse(missing.exists())
        self.assertFalse(destination.exists())

    def test_existing_destination_and_source_as_destination_are_refused(self):
        destination = self.root / "already-exists.db"
        destination.write_bytes(b"preserve this existing file")
        source_digest = self.digest(self.source)
        destination_digest = self.digest(destination)
        for target in (destination, self.source):
            with self.subTest(target=target.name), self.assertRaises(FileExistsError):
                self.copy_database(self.source, target)
        self.assertEqual(self.digest(self.source), source_digest)
        self.assertEqual(self.digest(destination), destination_digest)

    def test_invalid_and_unrelated_databases_are_rejected_before_destination_creation(self):
        corrupt = self.root / "invalid.db"
        corrupt.write_bytes(b"this is not a SQLite database")
        unrelated = self.root / "unrelated.db"
        with closing(sqlite3.connect(unrelated)) as connection, connection:
            connection.execute("CREATE TABLE unrelated (id INTEGER)")
        for source, error in ((corrupt, sqlite3.DatabaseError), (unrelated, ValueError)):
            with self.subTest(source=source.name):
                destination = self.root / (source.stem + "-backup.db")
                with self.assertRaises(error):
                    self.copy_database(source, destination)
                self.assertFalse(destination.exists())

    def test_backup_includes_committed_wal_data_with_writer_connection_open(self):
        with closing(sqlite3.connect(self.source)) as writer:
            self.assertEqual(writer.execute("PRAGMA journal_mode=WAL").fetchone()[0], "wal")
            writer.execute(
                "INSERT INTO searches (query, searched_utc, source, status) VALUES (?, ?, ?, ?)",
                ("synthetic WAL topic", "test-time", "Crossref", "success"),
            )
            writer.commit()
            self.assertGreater(Path(str(self.source) + "-wal").stat().st_size, 0)
            expected_state = tuple(writer.iterdump())
            backup = self.root / "wal-backup.db"
            self.assertEqual(self.copy_database(self.source, backup), {"papers": 2, "searches": 2})
            self.assertEqual(self.snapshot(backup), expected_state)


if __name__ == "__main__":
    unittest.main()
