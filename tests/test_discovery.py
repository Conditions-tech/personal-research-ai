"""Discovery adapter contracts; all provider I/O is injected or mocked."""

import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from discovery import providers


ROOT = Path(__file__).resolve().parents[1]


def provider_cases():
    common = {"publication_year": 2020, "type": "article",
              "primary_location": {"source": {"type": "journal"}}}
    oa = [
        {"title": "Synthetic retained", "doi": "10.1234/shared", **common},
        {"title": "Synthetic duplicate", "doi": "10.1234/shared", **common},
        {"title": "Outside years", **common, "publication_year": 2022},
        {"title": "Wrong category", **common, "type": "dissertation"},
        {},
    ]
    cr = [
        {"title": ["Synthetic retained"], "DOI": "10.1234/shared",
         "type": "journal-article", "published": {"date-parts": [[2020]]}},
        {"title": ["Synthetic duplicate"], "DOI": "10.1234/shared",
         "type": "journal-article", "published": {"date-parts": [[2020]]}},
        {"title": ["Outside years"], "type": "journal-article",
         "published": {"date-parts": [[2022]]}},
        {"title": ["Wrong category"], "type": "proceedings-article",
         "published": {"date-parts": [[2020]]}},
        {},
    ]
    return [
        (providers.OpenAlexAdapter, providers.search_openalex, providers.OPENALEX_URL,
         {"meta": {"count": 100, "next_cursor": "unused"}, "results": oa},
         "server-filtered-candidates"),
        (providers.CrossrefAdapter, providers.search_crossref, providers.CROSSREF_URL,
         {"message": {"total-results": 100, "next-cursor": "unused", "items": cr}},
         "server-filtered-candidates"),
    ]


class DiscoveryAdapterTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch(
            "requests.sessions.Session.request",
            side_effect=AssertionError("Unmocked HTTP request blocked by adapter tests."),
        ))

    def test_import_in_fresh_interpreter_has_no_ui_storage_or_external_side_effects(self):
        script = """
import os
import pathlib
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])

def guard(event, args):
    if event in ("sqlite3.connect", "socket.connect", "socket.getaddrinfo", "os.mkdir"):
        raise AssertionError("Discovery import attempted external I/O: " + event)
    if event == "open":
        mode, flags = args[1], args[2]
        if isinstance(mode, str) and any(c in mode for c in "wax+"):
            raise AssertionError("Discovery import attempted a file write.")
        if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            raise AssertionError("Discovery import attempted a file write.")

sys.addaudithook(guard)
from discovery import metadata, providers, retrieval, runs
assert not {"app", "streamlit", "pandas", "sqlite3"}.intersection(sys.modules)
assert not list(pathlib.Path.cwd().iterdir())
print("discovery import isolated")
"""
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, "-B", "-c", script, str(ROOT)],
                cwd=directory, capture_output=True, text=True, timeout=30,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "discovery import isolated")

    def test_batch_distinguishes_raw_filtered_and_reported_without_deduplication(self):
        for factory, _, url, payload, scope in provider_cases():
            with self.subTest(provider=factory.name):
                original = copy.deepcopy(payload)
                request = Mock(return_value=payload)
                adapter: providers.SourceAdapter = factory(request)
                batch = adapter.search("public synthetic query", 5, 2020, 2021, ["journal-paper"])
                request.assert_called_once()
                self.assertEqual(request.call_args.args[0], url)
                self.assertNotIn("cursor", request.call_args.args[1])
                self.assertEqual(batch.provider, factory.name)
                self.assertEqual(batch.reported_total, 100)
                self.assertEqual(batch.total_scope, scope)
                self.assertEqual(batch.fetched_count, 5)
                self.assertEqual(batch.filtered_count, 2)
                self.assertEqual([r["record_key"] for r in batch.records], ["doi:10.1234/shared"] * 2)
                self.assertEqual([r["source"] for r in batch.records], [factory.name] * 2)
                self.assertEqual(payload, original)

    def test_crossref_server_filters_widen_start_year_and_keep_exact_local_filtering(self):
        cases = [
            ({}, None),
            ({"year_from": 2020}, "from-pub-date:2019-01-01"),
            ({"year_from": 1}, "from-pub-date:0001-01-01"),
            ({"year_to": 1791}, "until-pub-date:1791-12-31"),
            ({"work_types": ["journal-paper"]}, "type:journal-article"),
            ({"year_from": 2020, "year_to": 2021, "work_types": list(providers.CROSSREF_QUERY_TYPES)},
             "from-pub-date:2019-01-01,until-pub-date:2021-12-31,type:book-chapter,type:dissertation,"
             "type:journal-article,type:posted-content,type:proceedings-article"),
        ]
        for kwargs, expected in cases:
            with self.subTest(kwargs=kwargs):
                request = Mock(return_value={"message": {"total-results": 0, "items": []}})
                batch = providers.CrossrefAdapter(request).search_page("topic", 5, **kwargs)
                self.assertEqual(request.call_args.args[1].get("filter"), expected)
                self.assertEqual(batch.total_scope,
                                 "query-matches" if expected is None else "server-filtered-candidates")
        # Online the year before print is requested by the widened bound and kept by
        # print-year precedence; a record dated only to that earlier year is still excluded.
        items = [
            {"title": ["Printed in range"], "DOI": "10.1234/print", "type": "journal-article",
             "published-print": {"date-parts": [[2020]]}, "published-online": {"date-parts": [[2019]]}},
            {"title": ["Earlier year"], "DOI": "10.1234/early", "type": "journal-article",
             "published": {"date-parts": [[2019]]}},
        ]
        request = Mock(return_value={"message": {"total-results": 2, "items": items}})
        batch = providers.CrossrefAdapter(request).search_page("topic", 5, 2020, 2021, ["journal-paper"])
        self.assertEqual([r["title"] for r in batch.records], ["Printed in range"])
        self.assertEqual((batch.fetched_count, batch.reported_total), (2, 2))

    def test_unknown_totals_and_empty_batches_remain_distinct(self):
        for factory, _, _, payload, _ in provider_cases():
            for empty_payload in ({}, {"meta": None, "message": None}):
                with self.subTest(provider=factory.name, payload=empty_payload):
                    request = Mock(return_value=empty_payload)
                    batch = factory(request).search("topic", 5)
                    request.assert_called_once()
                    self.assertIsNone(batch.reported_total)
                    self.assertEqual((batch.fetched_count, batch.filtered_count, batch.records), (0, 0, []))
            for total in (None, 0):
                with self.subTest(provider=factory.name, total=total):
                    if factory is providers.OpenAlexAdapter:
                        payload["meta"]["count"] = total
                    else:
                        payload["message"]["total-results"] = total
                    batch = factory(Mock(return_value=payload)).search("topic", 5, 2020, 2021, ["journal-paper"])
                    self.assertEqual(batch.reported_total, total)
                    self.assertEqual(batch.filtered_count, 2)  # Never infer totals from the sample.

    def test_legacy_entrypoints_preserve_total_and_record_tuple(self):
        for factory, search, _, payload, _ in provider_cases():
            with self.subTest(provider=factory.name):
                with patch("discovery.providers.request_json", return_value=payload) as request:
                    result = search("topic", 5, 2020, 2021, ["journal-paper"])
                request.assert_called_once()
                self.assertIsInstance(result, tuple)
                self.assertEqual(len(result), 2)
                self.assertEqual(result[0], 100)
                self.assertEqual([r["record_key"] for r in result[1]], ["doi:10.1234/shared"] * 2)

    def test_adapter_errors_propagate_without_retry_or_empty_success(self):
        errors = [
            requests.Timeout("synthetic timeout"),
            requests.ConnectionError("synthetic connection failure"),
            requests.HTTPError("synthetic HTTP failure"),
            ValueError("synthetic invalid JSON"),
            KeyError("synthetic unsupported category"),
        ]
        for factory in (providers.OpenAlexAdapter, providers.CrossrefAdapter):
            for error in errors:
                with self.subTest(provider=factory.name, error=type(error).__name__):
                    request = Mock(side_effect=error)
                    with self.assertRaises(type(error)) as raised:
                        factory(request).search("topic", 5)
                    self.assertIs(raised.exception, error)
                    request.assert_called_once()

    def test_transport_preserves_timeout_headers_and_http_failure(self):
        params = {"query": "synthetic"}
        for http_error in (None, requests.HTTPError("synthetic 429")):
            with self.subTest(http_error=http_error):
                response = Mock(spec=requests.Response)
                response.raise_for_status.side_effect = http_error
                response.json.return_value = {"synthetic": True}
                with patch("discovery.providers.requests.get", return_value=response) as get:
                    if http_error is None:
                        self.assertEqual(providers.request_json(providers.CROSSREF_URL, params), {"synthetic": True})
                        response.json.assert_called_once_with()
                    else:
                        with self.assertRaises(requests.HTTPError) as raised:
                            providers.request_json(providers.CROSSREF_URL, params)
                        self.assertIs(raised.exception, http_error)
                        response.json.assert_not_called()
                get.assert_called_once_with(
                    providers.CROSSREF_URL, params=params, headers=providers.HEADERS, timeout=45,
                )
                response.raise_for_status.assert_called_once_with()

    def test_json_decode_failure_propagates(self):
        error = requests.exceptions.JSONDecodeError("synthetic invalid JSON", "", 0)
        response = Mock(spec=requests.Response)
        response.json.side_effect = error
        with patch("discovery.providers.requests.get", return_value=response) as get:
            with self.assertRaises(requests.exceptions.JSONDecodeError) as raised:
                providers.request_json(providers.OPENALEX_URL, {})
        self.assertIs(raised.exception, error)
        get.assert_called_once()
        response.raise_for_status.assert_called_once_with()

    def test_injected_requesters_do_not_change_other_adapters(self):
        request_one = Mock(return_value={"meta": {"count": 3}, "results": []})
        request_two = Mock(return_value={"meta": {"count": 9}, "results": []})
        first, second = providers.OpenAlexAdapter(request_one), providers.OpenAlexAdapter(request_two)
        self.assertEqual(first.search("one", 5).reported_total, 3)
        self.assertEqual(second.search("two", 5).reported_total, 9)
        request_one.assert_called_once()
        request_two.assert_called_once()


if __name__ == "__main__":
    unittest.main()
