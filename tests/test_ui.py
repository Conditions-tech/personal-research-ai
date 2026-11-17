"""Headless UI smoke tests of an unchanged app copy with disposable storage."""

import io
import json
import zipfile
import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import requests
import streamlit as st
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
OPENALEX_URL = "https://api.openalex.org/works"
CROSSREF_URL = "https://api.crossref.org/works"


class StreamlitSmokeTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="research UI ")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        self.app_path = self.root / "app.py"
        self.app_path.write_bytes((ROOT / "app.py").read_bytes())
        self.database = self.root / "data" / "research.db"

        real_connect = sqlite3.connect

        def isolated_connect(database, *args, **kwargs):
            if kwargs.get("uri") or not isinstance(database, (str, Path)):
                raise AssertionError("UI tests require a plain temporary database path.")
            if not Path(database).resolve().is_relative_to(self.root):
                raise AssertionError("UI test attempted a database connection outside its temporary directory.")
            return real_connect(database, *args, **kwargs)

        self.enterContext(patch("sqlite3.connect", side_effect=isolated_connect))
        self.http = self.enterContext(patch(
            "requests.sessions.Session.request",
            side_effect=AssertionError("Unmocked HTTP request blocked by UI tests."),
        ))
        # Keep real rendering while inspecting the bytes handed to the download widget.
        self.download = self.enterContext(patch("streamlit.download_button", wraps=st.download_button))
        self.app = AppTest.from_file(self.app_path, default_timeout=10)

    def run_app(self):
        self.app.run()
        self.assertFalse(self.app.exception, [item.message for item in self.app.exception])

    def widget(self, elements, label):
        return next(element for element in elements if element.label == label)

    def query(self, sql):
        with closing(sqlite3.connect(self.database)) as connection:
            return connection.execute(sql).fetchall()

    def metrics(self):
        return {element.label: element.value for element in self.app.metric}

    def download_args(self, label):
        return next(call.kwargs for call in reversed(self.download.call_args_list)
                    if call.args and call.args[0] == label)

    def configure_search(self):
        self.app.sidebar.text_input[0].set_value("  synthetic topic  ")
        self.app.sidebar.select_slider[0].set_value(5)
        self.widget(self.app.number_input, "From publication year").set_value(2020)
        self.widget(self.app.number_input, "To publication year").set_value(2021)
        self.app.multiselect[0].set_value(["conference-paper"])

    def search(self):
        self.widget(self.app.button, "Search literature").click()
        self.run_app()

    def mock_provider(self, method, url, **kwargs):
        self.assertEqual(method.upper(), "GET")
        payloads = {
            OPENALEX_URL: {
                "meta": {"count": 17},
                "results": [
                    {
                        "title": "Synthetic café paper", "doi": "https://doi.org/10.1234/shared",
                        "publication_year": 2020, "type": "article",
                        "primary_location": {"source": {"type": "conference"}},
                        "abstract_inverted_index": {"Synthetic": [0], "fault.": [1], "abstract": [2]},
                        "authorships": [{"author": {"display_name": "Ada Synthetic"}}],
                    },
                    {
                        "title": "Title match fault.", "doi": "10.1234/title-match",
                        "publication_year": 2021, "type": "conference-paper",
                    },
                    {
                        "title": "Outside selected years", "publication_year": 2019,
                        "type": "conference-paper",
                    },
                    {
                        "title": "Unclassified article", "publication_year": 2020, "type": "article",
                    },
                    {
                        "title": "Synthetic journal paper", "publication_year": 2020, "type": "article",
                        "primary_location": {"source": {"type": "journal"}},
                    },
                ],
            },
            CROSSREF_URL: {
                "message": {"total-results": 23, "items": [
                    {
                        "title": ["Synthetic café paper"], "DOI": "10.1234/shared",
                        "published": {"date-parts": [[2020]]}, "type": "proceedings-article",
                    },
                    {
                        "title": ["Conference method"], "DOI": "10.1234/conference",
                        "published": {"date-parts": [[2021]]}, "type": "proceedings-article",
                    },
                    {
                        "title": ["Synthetic journal record"],
                        "published": {"date-parts": [[2020]]}, "type": "journal-article",
                    },
                ]},
            },
        }
        if url not in payloads:
            raise AssertionError("Unexpected provider URL.")
        response = Mock(spec=requests.Response)
        response.raise_for_status.return_value = None
        response.json.return_value = payloads[url]
        return response

    def load_mock_results(self):
        self.http.side_effect = self.mock_provider
        self.run_app()
        self.configure_search()
        self.search()

    def test_isolation_guards_reject_external_storage_and_unmocked_http(self):
        with self.assertRaises(AssertionError):
            sqlite3.connect(self.root.parent / "blocked-ui-test.db")
        with self.assertRaises(AssertionError):
            requests.get(OPENALEX_URL)
        self.assertFalse(self.database.exists())

    def test_empty_app_renders_controls_tabs_and_zero_metrics(self):
        self.run_app()
        self.assertIn("Personal Research AI", self.app.title[0].value)
        self.assertEqual([tab.label for tab in self.app.tabs], [
            "Saved literature", "Search history", "Coverage & limitations", "Literature review",
        ])
        self.assertEqual(self.metrics(), {
            "Unique saved records": "0", "Records with abstracts": "0", "Searches recorded": "0",
        })
        self.assertEqual(self.app.sidebar.select_slider[0].value, 10)
        self.assertEqual(self.app.multiselect[0].value, ["journal-paper", "conference-paper"])
        self.assertIn("Journal papers (articles and reviews)", self.app.multiselect[0].options)
        self.assertEqual(self.widget(self.app.number_input, "From publication year").value, 2015)
        self.assertEqual(self.widget(self.app.number_input, "To publication year").value, datetime.now().year)
        self.assertIn("No records saved yet.", " ".join(item.value for item in self.app.info))
        self.assertEqual(self.query("SELECT COUNT(*) FROM papers"), [(0,)])
        self.http.assert_not_called()
        self.download.assert_not_called()

    def start_review(self):
        self.widget(self.app.text_area, "Inclusion criteria").set_value("Relevant methods")
        self.widget(self.app.text_area, "Exclusion criteria").set_value("Unrelated population")
        self.widget(self.app.button, "Start review").click()
        self.run_app()

    def test_review_protocol_validation_then_screening_and_evidence_exports(self):
        self.load_mock_results()
        self.widget(self.app.button, "Start review").click()
        self.run_app()
        self.assertIn("inclusion must be nonempty text.", [e.value for e in self.app.error])
        self.start_review()
        self.assertEqual(self.http.call_count, 2)
        self.assertEqual(self.app.session_state["review_workspace"]["run"], self.app.session_state["last_run"])
        key = "doi:10.1234/shared"
        self.app.selectbox(key="review_paper").set_value(key)
        self.run_app()
        self.widget(self.app.selectbox, "Screening decision").set_value("include")
        self.widget(self.app.button, "Save screening decision").click()
        self.run_app()
        self.assertIn("Screening reason must be nonempty text.", [e.value for e in self.app.error])
        self.widget(self.app.selectbox, "Screening decision").set_value("include")
        self.widget(self.app.text_area, "Screening reason").set_value("Relevant methods")
        self.widget(self.app.button, "Save screening decision").click()
        self.run_app()
        self.app.selectbox(key="review_field").set_value("method")
        self.run_app()
        self.widget(self.app.selectbox, "Claim kind").set_value("paper-statement")
        self.widget(self.app.text_area, "Analysis note").set_value("Synthetic method evidence")
        self.widget(self.app.text_area, "Exact abstract excerpt").set_value("Synthetic fault.")
        self.widget(self.app.button, "Save evidence note").click()
        self.run_app()
        review = json.loads(self.download_args("Download review JSON")["data"])
        self.assertEqual(review["papers"][key]["decision"], "include")
        self.assertEqual(review["papers"][key]["analysis"]["method"]["excerpt"], "Synthetic fault.")
        comparison = pd.read_csv(io.BytesIO(self.download_args("Download comparison CSV")["data"]))
        self.assertEqual(comparison.set_index("record_key").loc[key, "method"], "Synthetic method evidence")
        self.assertIn("This discovery run was incomplete.", " ".join(e.value for e in self.app.warning))
        self.assertEqual(self.query("SELECT COUNT(*) FROM searches"), [(2,)])
        self.assertEqual(self.query("SELECT COUNT(*) FROM papers"), [(3,)])

    def test_review_paper_switching_cannot_reuse_another_papers_notes(self):
        self.load_mock_results()
        self.start_review()
        self.app.selectbox(key="review_paper").set_value("doi:10.1234/shared")
        self.run_app()
        self.widget(self.app.selectbox, "Screening decision").set_value("include")
        self.widget(self.app.text_area, "Screening reason").set_value("First paper only")
        self.widget(self.app.button, "Save screening decision").click()
        self.run_app()
        self.app.selectbox(key="review_paper").set_value("doi:10.1234/conference")
        self.run_app()
        self.assertEqual(self.widget(self.app.selectbox, "Screening decision").value, "pending")
        self.assertEqual(self.widget(self.app.text_area, "Screening reason").value, "")
        self.assertTrue(self.widget(self.app.button, "Save evidence note").disabled)
        self.assertIn("Evidence depth: metadata-only", " ".join(e.value for e in self.app.caption))

    def test_later_search_preserves_original_review_and_restored_session_renders(self):
        from review.workspace import export_review, restore_review
        self.load_mock_results()
        self.start_review()
        original = self.app.session_state["review_workspace"]
        self.search()
        self.assertNotEqual(original["run"]["manifest"]["run_id"], self.app.session_state["last_run"]["manifest"]["run_id"])
        self.assertEqual(self.app.session_state["review_workspace"], original)
        self.assertIn("A newer search is available.", " ".join(e.value for e in self.app.info))
        reopened = AppTest.from_file(self.app_path, default_timeout=10)
        reopened.session_state["review_workspace"] = restore_review(export_review(original))
        reopened.run()
        self.assertFalse(reopened.exception)
        self.assertEqual(reopened.session_state["review_workspace"], original)
        self.assertEqual(self.http.call_count, 4)

    def test_invalid_searches_warn_without_requests_or_history(self):
        self.run_app()
        self.app.sidebar.text_input[0].set_value("   ")
        self.search()
        self.assertIn("Enter a research topic first.", [item.value for item in self.app.warning])
        self.app.sidebar.text_input[0].set_value("synthetic topic")
        self.widget(self.app.number_input, "From publication year").set_value(2021)
        self.widget(self.app.number_input, "To publication year").set_value(2020)
        self.search()
        self.assertIn("The starting year cannot be later than the ending year.",
                      [item.value for item in self.app.warning])
        self.assertEqual(self.query("SELECT COUNT(*) FROM searches"), [(0,)])
        self.assertEqual(self.query("SELECT COUNT(*) FROM papers"), [(0,)])
        self.http.assert_not_called()

    def test_mocked_search_filters_saves_deduplicates_and_records_history(self):
        self.load_mock_results()
        self.assertFalse(self.app.error)
        self.assertEqual(self.metrics(), {
            "Unique saved records": "3", "Records with abstracts": "1", "Searches recorded": "2",
        })
        self.assertEqual(self.query("SELECT source FROM papers WHERE doi = '10.1234/shared'"),
                         [("Crossref;OpenAlex",)])
        self.assertEqual(self.query(
            "SELECT source, reported_count, retrieved_count, status FROM searches ORDER BY id"
        ), [("OpenAlex", 17, 2, "partial"), ("Crossref", 23, 2, "partial")])
        self.assertEqual(len(self.app.tabs[0].dataframe[0].value), 3)
        self.assertEqual(len(self.app.tabs[1].dataframe[0].value), 2)
        self.assertEqual(self.app.session_state["last_query"], "synthetic topic")
        self.assertEqual(self.http.call_count, 2)
        oa_request, cr_request = self.http.call_args_list
        self.assertEqual(oa_request.kwargs["params"]["search"], "synthetic topic")
        self.assertEqual(oa_request.kwargs["params"]["per_page"], 5)
        self.assertEqual(oa_request.kwargs["params"]["filter"],
                         "from_publication_date:2020-01-01,to_publication_date:2021-12-31,type:article|conference-paper|review")
        self.assertEqual(oa_request.kwargs["params"]["page"], 1)
        self.assertEqual(cr_request.kwargs["params"], {"query.bibliographic": "synthetic topic", "rows": 5, "cursor": "*",
            "filter": "from-pub-date:2019-01-01,until-pub-date:2021-12-31,type:proceedings-article"})
        messages = " ".join(item.value for item in [*self.app.success, *self.app.warning])
        self.assertIn("candidate matches before local filters", messages)
        self.assertEqual(messages.count("candidate matches before local filters"), 2)
        self.assertIn("This search retrieved 3 unique records across sources", messages)
        note = json.loads(self.query("SELECT note FROM searches ORDER BY id LIMIT 1")[0][0])
        self.assertEqual(note["settings"]["raw_record_budget"], 5)
        self.assertEqual(note["settings"]["publication_types"], ["conference-paper"])
        self.assertEqual(note["retrieval"]["raw_fetched"], 5)
        self.assertEqual(self.query("SELECT work_type FROM papers WHERE doi = '10.1234/shared'"), [("article",)])

        self.search()
        self.assertEqual(self.http.call_count, 4)
        self.assertEqual(self.metrics()["Unique saved records"], "3")
        self.assertEqual(self.metrics()["Searches recorded"], "4")
        self.assertIn("0 new unique records", " ".join(item.value for item in self.app.success))

    def test_journal_category_includes_both_providers_and_excludes_conferences(self):
        self.http.side_effect = self.mock_provider
        self.run_app()
        self.configure_search()
        self.app.multiselect[0].set_value(["journal-paper"])
        self.search()
        self.assertEqual(set(self.app.tabs[0].dataframe[0].value["title"]),
                         {"Synthetic journal paper", "Synthetic journal record"})
        self.assertEqual(self.query("SELECT work_type FROM papers ORDER BY work_type"),
                         [("article",), ("journal-article",)])
        self.assertEqual(self.query("SELECT retrieved_count FROM searches ORDER BY id"), [(1,), (1,)])
        self.assertIn("candidate matches before local filters",
                      " ".join(item.value for item in self.app.warning))
        self.assertEqual(self.http.call_count, 2)

    def test_cleared_categories_include_unclassified_records_without_native_type_filter(self):
        self.http.side_effect = self.mock_provider
        self.run_app()
        self.configure_search()
        self.app.multiselect[0].set_value([])
        self.search()
        titles = set(self.app.tabs[0].dataframe[0].value["title"])
        self.assertIn("Unclassified article", titles)
        self.assertIn("Synthetic journal paper", titles)
        self.assertNotIn("Outside selected years", titles)
        self.assertEqual(self.http.call_args_list[0].kwargs["params"]["filter"],
                         "from_publication_date:2020-01-01,to_publication_date:2021-12-31")
        self.assertEqual(self.http.call_count, 2)

    def test_local_filter_details_and_csv_follow_the_current_view(self):
        self.load_mock_results()
        self.app.text_input(key="local_filter").set_value("fault.")
        self.run_app()
        expected = {"Synthetic café paper", "Title match fault."}
        self.assertEqual(set(self.app.tabs[0].dataframe[0].value["title"]), expected)
        chooser = self.widget(self.app.selectbox, "Choose a paper")
        self.assertEqual(set(chooser.options), expected)
        chooser.select_index(chooser.options.index("Synthetic café paper"))
        self.run_app()
        details = " ".join(item.value for item in self.app.markdown)
        self.assertIn("Synthetic fault. abstract", details)
        self.assertIn("Ada Synthetic", details)
        self.assertIn("https://doi.org/10.1234/shared", details)
        self.assertEqual(len(self.app.get("download_button")), 3)
        download = self.download_args("Download filtered CSV")
        self.assertEqual(download["file_name"], "personal_research_literature.csv")
        self.assertEqual(download["mime"], "text/csv")
        self.assertTrue(download["data"].startswith(b"\xef\xbb\xbf"))
        self.assertEqual(set(pd.read_csv(io.BytesIO(download["data"]))["title"]), expected)

        self.app.text_input(key="local_filter").set_value("no synthetic match here")
        self.run_app()
        self.assertTrue(self.app.tabs[0].dataframe[0].value.empty)
        self.assertEqual(len(self.app.selectbox), 0)
        self.assertTrue(pd.read_csv(io.BytesIO(self.download_args("Download filtered CSV")["data"])).empty)
        self.assertEqual(self.metrics()["Unique saved records"], "3")
        self.assertEqual(self.http.call_count, 2)

    def test_unbounded_years_include_historical_and_unknown_years(self):
        def historical_response(method, url, **kwargs):
            response = Mock(spec=requests.Response)
            response.json.return_value = (
                {"meta": {"count": 2}, "results": [
                    {"id": "https://openalex.org/Wold", "title": "Old record", "publication_year": 1665},
                    {"id": "https://openalex.org/Wunknown", "title": "Unknown year"},
                ]} if url == OPENALEX_URL else {"message": {"total-results": 0, "items": []}}
            )
            return response
        self.http.side_effect = historical_response
        self.run_app()
        self.app.sidebar.text_input[0].set_value("public historical query")
        self.app.checkbox(key="apply_start_year").set_value(False)
        self.app.checkbox(key="apply_end_year").set_value(False)
        self.app.multiselect[0].set_value([])
        self.search()
        self.assertNotIn("filter", self.http.call_args_list[0].kwargs["params"])
        self.assertEqual(self.query("SELECT year FROM papers ORDER BY title"), [(1665,), (None,)])
        notes = [json.loads(row[0]) for row in self.query("SELECT note FROM searches")]
        self.assertTrue(all(n["settings"]["year_from"] is None and n["settings"]["year_to"] is None for n in notes))
        self.assertTrue(self.widget(self.app.number_input, "From publication year").disabled)

    def test_one_sided_historical_bound_is_forwarded(self):
        self.http.side_effect = self.mock_provider
        self.run_app()
        self.configure_search()
        self.widget(self.app.number_input, "From publication year").set_value(1665)
        self.app.checkbox(key="apply_end_year").set_value(False)
        self.search()
        self.assertEqual(self.http.call_args_list[0].kwargs["params"]["filter"],
                         "from_publication_date:1665-01-01,type:article|conference-paper|review")

    def test_identical_titles_can_select_the_second_papers_own_evidence(self):
        self.run_app()
        with closing(sqlite3.connect(self.database)) as connection, connection:
            connection.executemany(
                "INSERT INTO papers VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                [(f"doi:10.1234/same-{i}", "Identical title", f"10.1234/same-{i}", 2020,
                  "journal-article", f"Evidence from paper {i}", f"Author {i}", "Crossref",
                  f"https://doi.org/10.1234/same-{i}", "saved", "seen") for i in (1, 2)],
            )
        self.run_app()
        chooser = self.widget(self.app.selectbox, "Choose a paper")
        self.assertEqual(len(set(chooser.options)), 2)
        chooser.select_index(1)
        self.run_app()
        details = " ".join(item.value for item in self.app.markdown)
        self.assertIn("Evidence from paper 2", details)
        self.assertIn("https://doi.org/10.1234/same-2", details)
        self.assertNotIn("Evidence from paper 1", details)
        self.http.assert_not_called()

    def test_run_bundle_matches_history_counts_and_source_provenance(self):
        self.load_mock_results()
        history = json.loads(self.download_args("Download displayed search history JSON")["data"])
        notes = [json.loads(row["note"]) for row in history]
        self.assertEqual(len({n["run_id"] for n in notes}), 1)
        self.assertTrue(all(n["version"] == 2 for n in notes))
        data = self.download_args("Download latest run bundle")["data"]
        with zipfile.ZipFile(io.BytesIO(data)) as bundle:
            manifest = json.loads(bundle.read("manifest.json"))
            records = pd.read_csv(io.BytesIO(bundle.read("records.csv")))
            provenance = pd.read_csv(io.BytesIO(bundle.read("provenance.csv")))
        self.assertEqual(manifest["run_id"], notes[0]["run_id"])
        self.assertEqual(manifest["counts"], {
            "raw_fetched": 8, "filtered": 4, "unique_in_run": 3,
            "duplicate_filtered_entries": 1, "new_library_records": 3,
        })
        self.assertEqual(len(records), 3)
        self.assertEqual(len(provenance), 4)
        self.assertIn("10.1234/shared", set(provenance["source_id"].dropna()))
        self.assertEqual(set(provenance["provider"]), {"OpenAlex", "Crossref"})
        self.app.text_input(key="local_filter").set_value("nothing matches")
        self.run_app()
        with zipfile.ZipFile(io.BytesIO(self.download_args("Download latest run bundle")["data"])) as bundle:
            self.assertEqual(json.loads(bundle.read("manifest.json"))["counts"]["unique_in_run"], 3)

    def test_rate_limited_source_cools_down_while_other_source_continues(self):
        def rate_limited(method, url, **kwargs):
            if url == OPENALEX_URL:
                response = requests.Response()
                response.status_code = 429
                response.headers["Retry-After"] = "3600"
                raise requests.HTTPError("private query URL", response=response)
            return self.mock_provider(method, url, **kwargs)
        self.http.side_effect = rate_limited
        self.run_app()
        self.configure_search()
        self.search()
        self.search()
        self.assertEqual(self.http.call_count, 3)
        notes = [json.loads(row[0]) for row in self.query(
            "SELECT note FROM searches WHERE source = 'OpenAlex' ORDER BY id")]
        self.assertEqual([n["retrieval"]["requests_attempted"] for n in notes], [1, 0])
        self.assertTrue(all(n["retrieval"]["stop_reason"] == "rate_limited" for n in notes))
        self.assertNotIn("private query", " ".join(m.value for m in self.app.error))
        self.assertEqual(self.metrics()["Unique saved records"], "2")

    def test_legacy_history_and_existing_library_are_preserved_and_counts_stay_separate(self):
        self.run_app()
        with closing(sqlite3.connect(self.database)) as connection, connection:
            connection.execute(
                "INSERT INTO papers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("doi:10.1234/shared", "Previously saved title", "10.1234/shared", 2010,
                 "book-chapter", "", "", "OpenAlex", "", "old first saved", "old last seen"),
            )
            connection.execute(
                "INSERT INTO searches (query,searched_utc,source,reported_count,retrieved_count,status,note) "
                "VALUES (?,?,?,?,?,?,?)", ("legacy query", "old timestamp", "Crossref", 1, 1, "success", "Legacy plain note"),
            )
        self.http.side_effect = self.mock_provider
        self.configure_search()
        self.search()
        self.assertEqual(self.query("SELECT title, first_saved_utc FROM papers WHERE doi='10.1234/shared'"),
                         [("Previously saved title", "old first saved")])
        self.assertEqual(self.query("SELECT note FROM searches WHERE query='legacy query'"), [("Legacy plain note",)])
        with zipfile.ZipFile(io.BytesIO(self.download_args("Download latest run bundle")["data"])) as bundle:
            manifest = json.loads(bundle.read("manifest.json"))
            self.assertEqual((manifest["counts"]["unique_in_run"], manifest["counts"]["new_library_records"]), (3, 2))
        history = json.loads(self.download_args("Download displayed search history JSON")["data"])
        self.assertEqual(len(history), 3)
        self.assertIn("Legacy plain note", [r["note"] for r in history])

    def test_provider_failure_is_recorded_while_other_provider_results_are_saved(self):
        def fail_openalex(method, url, **kwargs):
            if url == OPENALEX_URL:
                raise requests.Timeout("Synthetic provider timeout")
            return self.mock_provider(method, url, **kwargs)

        self.http.side_effect = fail_openalex
        self.run_app()
        self.configure_search()
        self.search()
        self.assertIn("Request timed out", " ".join(item.value for item in self.app.error))
        self.assertEqual(self.metrics()["Unique saved records"], "2")
        self.assertEqual(self.metrics()["Searches recorded"], "2")
        self.assertEqual(self.query(
            "SELECT source, reported_count, retrieved_count, status FROM searches ORDER BY id"
        ), [("OpenAlex", None, 0, "error"), ("Crossref", 23, 2, "partial")])
        self.assertEqual(self.http.call_count, 2)

    def test_malformed_field_cannot_crash_storage_or_pollute_other_source_results(self):
        def malformed_openalex(method, url, **kwargs):
            response = self.mock_provider(method, url, **kwargs)
            if url == OPENALEX_URL:
                response.json.return_value["results"][0]["type"] = {"invalid": "object instead of text"}
            return response

        self.http.side_effect = malformed_openalex
        self.run_app()
        self.configure_search()
        self.app.multiselect[0].set_value([])
        self.search()
        self.assertEqual(self.query(
            "SELECT source, retrieved_count, status FROM searches ORDER BY id"
        ), [("OpenAlex", 0, "error"), ("Crossref", 3, "partial")])
        self.assertEqual(self.query("SELECT DISTINCT source FROM papers"), [("Crossref",)])
        self.assertIn("Invalid provider response", " ".join(item.value for item in self.app.error))
        self.assertEqual(self.http.call_count, 2)

    def test_empty_provider_batches_show_warning_and_successful_search_history(self):
        def empty_response(method, url, **kwargs):
            response = self.mock_provider(method, url, **kwargs)
            response.json.return_value = (
                {"meta": {"count": 0}, "results": []} if url == OPENALEX_URL
                else {"message": {"total-results": 0, "items": []}}
            )
            return response

        self.http.side_effect = empty_response
        self.run_app()
        self.configure_search()
        self.search()
        self.assertFalse(self.app.error)
        self.assertIn("No records were retrieved.", " ".join(item.value for item in self.app.warning))
        self.assertEqual(self.metrics()["Unique saved records"], "0")
        self.assertEqual(self.query("SELECT retrieved_count, status FROM searches ORDER BY id"),
                         [(0, "complete"), (0, "complete")])
        self.http.assert_called()
        self.assertEqual(self.http.call_count, 2)
        self.assertFalse(any(c.args[0] == "Download filtered CSV" for c in self.download.call_args_list))
        with zipfile.ZipFile(io.BytesIO(self.download_args("Download latest run bundle")["data"])) as bundle:
            manifest = json.loads(bundle.read("manifest.json"))
            self.assertEqual(manifest["counts"]["unique_in_run"], 0)
            self.assertEqual(manifest["status"], "complete")

    def test_later_page_failure_saves_earlier_results_and_reports_partial(self):
        def paged_response(method, url, **kwargs):
            if url == OPENALEX_URL and kwargs["params"]["page"] == 2:
                raise requests.Timeout("private query URL must not be displayed")
            response = Mock(spec=requests.Response)
            response.raise_for_status.return_value = None
            response.json.return_value = (
                {"meta": {"count": 120}, "results": [
                    {"title": f"Synthetic paper {i}", "publication_year": 2020,
                     "type": "conference-paper"} for i in range(50)
                ]} if url == OPENALEX_URL else {"message": {"total-results": 0, "items": []}}
            )
            return response

        self.http.side_effect = paged_response
        self.run_app()
        self.configure_search()
        self.app.sidebar.select_slider[0].set_value(100)
        self.search()
        self.assertEqual(self.query(
            "SELECT source, retrieved_count, status FROM searches ORDER BY id"
        ), [("OpenAlex", 50, "partial"), ("Crossref", 0, "complete")])
        self.assertEqual(self.metrics()["Unique saved records"], "50")
        self.assertEqual(self.http.call_count, 3)
        messages = " ".join(item.value for item in self.app.warning)
        self.assertIn("fetched 50 raw entries in 1 pages", messages)
        self.assertIn("Request timed out", messages)
        self.assertNotIn("private query", messages)

    def test_pagination_reaches_later_matching_papers_and_deduplicates_sources(self):
        def paged_response(method, url, **kwargs):
            params = kwargs["params"]
            response = Mock(spec=requests.Response)
            response.raise_for_status.return_value = None
            if url == OPENALEX_URL:
                items = ([{"title": f"Journal candidate {i}", "publication_year": 2020,
                           "type": "article", "primary_location": {"source": {"type": "journal"}}}
                          for i in range(50)] if params["page"] == 1 else [
                    {"title": "Later shared conference", "doi": "10.1234/later",
                     "publication_year": 2020, "type": "conference-paper"}
                ])
                response.json.return_value = {"meta": {"count": 51}, "results": items}
            else:
                items = ([{"title": [f"Journal record {i}"], "type": "journal-article",
                           "published": {"date-parts": [[2020]]}} for i in range(50)]
                         if params["cursor"] == "*" else [
                    {"title": ["Later shared conference"], "DOI": "10.1234/later",
                     "type": "proceedings-article", "published": {"date-parts": [[2020]]}},
                    {"title": ["Another later conference"], "DOI": "10.1234/another",
                     "type": "proceedings-article", "published": {"date-parts": [[2020]]}},
                ])
                response.json.return_value = {"message": {
                    "total-results": 52, "items": items, "next-cursor": "next synthetic page",
                }}
            return response

        self.http.side_effect = paged_response
        self.run_app()
        self.configure_search()
        self.app.sidebar.select_slider[0].set_value(100)
        self.search()
        self.assertEqual(self.http.call_count, 4)
        self.assertEqual(self.metrics()["Unique saved records"], "2")
        self.assertEqual(self.query("SELECT source FROM papers WHERE doi = '10.1234/later'"),
                         [("Crossref;OpenAlex",)])
        self.assertEqual(self.query(
            "SELECT source, retrieved_count, status FROM searches ORDER BY id"
        ), [("OpenAlex", 1, "complete"), ("Crossref", 2, "complete")])
        notes = [json.loads(row[0]) for row in self.query("SELECT note FROM searches ORDER BY id")]
        self.assertEqual([note["retrieval"]["raw_fetched"] for note in notes], [51, 52])
        self.assertIn("This search retrieved 2 unique records across sources",
                      " ".join(item.value for item in self.app.success))


if __name__ == "__main__":
    unittest.main()
