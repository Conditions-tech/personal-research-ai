"""Run evidence/export acceptance checks with synthetic data only."""

import copy
import io
import json
import unittest
import zipfile
from unittest.mock import Mock, patch

import pandas as pd

from discovery.providers import CrossrefAdapter, OpenAlexAdapter
from discovery.retrieval import RetrievalBudget, RetrievalResult, retrieve
from discovery.runs import history_note_for_run, make_run, run_bundle


class RunEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch(
            "requests.sessions.Session.request",
            side_effect=AssertionError("Live HTTP blocked by run evidence tests."),
        ))

    def make_results(self, year_to=None):
        budget = RetrievalBudget(5)
        oa = {"meta": {"count": 2}, "results": [
            {"id": "https://openalex.org/W1", "doi": "10.1234/shared", "title": "Synthetic café",
             "publication_year": 1665, "type": "article",
             "primary_location": {"source": {"type": "journal", "display_name": "Synthetic journal"}}},
            {"id": "https://openalex.org/W2", "title": "Unknown year"},
        ]}
        cr = {"message": {"total-results": 2, "items": [
            {"DOI": "10.1234/shared", "title": ["Other provider title"], "type": "journal-article",
             "author": [{"given": "Synthetic", "family": "Author"}],
             "published": {"date-parts": [[1665]]}},
            {"DOI": "10.1234/third", "title": ["Third record"], "published": {"date-parts": [[1700]]}},
        ]}}
        return budget, [
            retrieve(OpenAlexAdapter(Mock(return_value=oa)), "public query", budget, year_to=year_to),
            retrieve(CrossrefAdapter(Mock(return_value=cr)), "public query", budget, year_to=year_to),
        ]

    def test_manifest_counts_merge_and_no_input_mutation(self):
        budget, results = self.make_results()
        original = copy.deepcopy([r.records for r in results])
        run = make_run("public query", budget, results, new_records=3)
        manifest = run["manifest"]
        self.assertEqual(manifest["status"], "complete")
        self.assertEqual(manifest["counts"], {
            "raw_fetched": 4, "filtered": 4, "unique_in_run": 3,
            "duplicate_filtered_entries": 1, "new_library_records": 3,
        })
        self.assertNotIn("reported_total", manifest["counts"])
        self.assertEqual(run["records"][0]["title"], "Synthetic café")
        self.assertEqual(run["records"][0]["authors"], "Synthetic Author")
        self.assertEqual(run["records"][0]["source"], "Crossref;OpenAlex")
        self.assertEqual([r.records for r in results], original)

    def test_history_shared_id_settings_counts_and_provider_specific_evidence(self):
        budget, results = self.make_results(year_to=1800)
        run = make_run("public query", budget, results, year_to=1800, new_records=2)
        notes = [json.loads(history_note_for_run(r, run)) for r in results]
        self.assertEqual({n["run_id"] for n in notes}, {run["manifest"]["run_id"]})
        self.assertTrue(all(n["version"] == 2 for n in notes))
        self.assertEqual(notes[0]["settings"]["year_from"], None)
        self.assertEqual(notes[0]["settings"]["year_to"], 1800)
        self.assertEqual(notes[0]["provenance"][0]["source_id"], "https://openalex.org/W1")
        self.assertEqual(notes[1]["provenance"][0]["source_id"], "10.1234/shared")
        self.assertTrue(all(p["provider"] == "OpenAlex" for p in notes[0]["provenance"]))
        self.assertNotIn("cursor", json.dumps(notes))
        self.assertNotIn("abstract", notes[0])  # No raw payload/snapshot added to the history note.

    def test_bundle_round_trip_preserves_keys_unicode_counts_and_provenance(self):
        budget, results = self.make_results()
        run = make_run("public query", budget, results, new_records=3)
        with zipfile.ZipFile(io.BytesIO(run_bundle(run))) as bundle:
            self.assertEqual(set(bundle.namelist()), {"manifest.json", "records.csv", "provenance.csv"})
            self.assertEqual(json.loads(bundle.read("manifest.json")), run["manifest"])
            records = pd.read_csv(io.BytesIO(bundle.read("records.csv")))
            evidence = pd.read_csv(io.BytesIO(bundle.read("provenance.csv")))
        self.assertEqual(len(records), 3)
        self.assertEqual(len(evidence), 4)
        self.assertEqual(records.iloc[0]["title"], "Synthetic café")
        self.assertEqual(set(evidence["record_key"]), set(records["record_key"]))
        self.assertEqual(set(evidence["provider"]), {"OpenAlex", "Crossref"})

    def test_empty_and_failed_runs_export_without_claiming_success(self):
        budget = RetrievalBudget(5)
        failed = retrieve(OpenAlexAdapter(Mock(side_effect=ValueError("invalid"))), "public query", budget)
        run = make_run("public query", budget, [failed], new_records=0)
        self.assertEqual(run["manifest"]["status"], "error")
        with zipfile.ZipFile(io.BytesIO(run_bundle(run))) as bundle:
            self.assertTrue(pd.read_csv(io.BytesIO(bundle.read("records.csv"))).empty)
            self.assertTrue(pd.read_csv(io.BytesIO(bundle.read("provenance.csv"))).empty)

    def test_new_run_ids_and_unknown_insertions_are_not_fabricated(self):
        budget, results = self.make_results()
        first = make_run("public query", budget, results)
        second = make_run("public query", budget, results)
        self.assertNotEqual(first["manifest"]["run_id"], second["manifest"]["run_id"])
        self.assertIsNone(first["manifest"]["counts"]["new_library_records"])

    def test_run_cannot_relabel_existing_results_with_other_queries_or_settings(self):
        budget, results = self.make_results()
        for query, changed_budget, settings in (
            ("different topic", budget, {}),
            ("public query", RetrievalBudget(10), {}),
            ("public query", budget, {"year_to": 1800}),
            ("public query", budget, {"work_types": ["journal-paper"]}),
        ):
            with self.subTest(query=query, settings=settings), self.assertRaises(ValueError):
                make_run(query, changed_budget, results, **settings)

    def test_history_note_cannot_relabel_the_actual_retrieval_settings(self):
        budget, results = self.make_results()
        with self.assertRaises(ValueError):
            results[0].history_note(budget, 1900, None, None)

    def test_duplicate_providers_and_impossible_insertions_are_rejected(self):
        budget, results = self.make_results()
        with self.assertRaises(ValueError):
            make_run("public query", budget, [*results, results[0]])
        for count in (-1, True, 4, 1.5):
            with self.subTest(count=count), self.assertRaises(ValueError):
                make_run("public query", budget, results, new_records=count)

    def test_history_cannot_attach_another_result_with_the_same_provider_name(self):
        budget, results = self.make_results()
        run = make_run("public query", budget, results)
        for change in ({"query": "another query"}, {"started_utc": "a different attempt"}):
            other = copy.deepcopy(results[0])
            for key, value in change.items():
                setattr(other, key, value)
            with self.subTest(change=change), self.assertRaises(ValueError):
                history_note_for_run(other, run)

    def test_missing_retrieval_context_and_unknown_history_provider_are_rejected(self):
        budget, results = self.make_results()
        missing_context = RetrievalResult(provider="OpenAlex", pages_completed=1, requests_attempted=1)
        with self.assertRaises(ValueError):
            make_run("public query", budget, [missing_context])
        run = make_run("public query", budget, results)
        with self.assertRaises(ValueError):
            history_note_for_run(RetrievalResult(provider="Unknown"), run)


if __name__ == "__main__":
    unittest.main()
