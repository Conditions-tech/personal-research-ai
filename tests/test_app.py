import ast
import io
import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd

from discovery import metadata, providers


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "app.py"
FUNCTIONS_UNDER_TEST = {
    "connect_db", "now_utc", "save_papers", "filter_papers", "papers_to_csv",
}


def load_app_functions():
    # Only storage/UI helpers still require AST isolation. Discovery is importable.
    tree = ast.parse(APP_PATH.read_text(encoding="utf-8"), filename=str(APP_PATH))
    definitions = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in FUNCTIONS_UNDER_TEST
    ]
    missing = FUNCTIONS_UNDER_TEST - {node.name for node in definitions}
    if missing:
        raise AssertionError(f"App definitions not found: {sorted(missing)}")
    namespace = {
        "closing": closing, "datetime": datetime, "pd": pd,
        "sqlite3": sqlite3, "timezone": timezone,
    }
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(APP_PATH), "exec"), namespace)
    namespace.update({
        name: getattr(metadata, name) for name in (
            "clean_text",
            "normalize_doi",
            "normalize_title",
            "make_key",
            "abstract_from_openalex",
            "authors_from_openalex",
            "normalize_openalex",
            "normalize_crossref",
            "openalex_publication_type",
            "crossref_publication_type",
            "filter_search_results",
        )
    })
    namespace.update({
        name: getattr(providers, name)
        for name in ("search_openalex", "search_crossref", "OPENALEX_URL", "CROSSREF_URL")
    })
    return namespace


APP_FUNCTIONS = load_app_functions()


class PublicationYearDefaultTests(unittest.TestCase):
    def test_end_year_default_follows_local_calendar_year_rollover(self):
        tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
        # Execute only the end-year widget assignment, never the app's UI/DB setup.
        assignment = next(
            node for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "year_to"
                    for target in node.targets)
        )
        widget_code = compile(ast.Module(body=[assignment], type_ignores=[]), str(APP_PATH), "exec")
        for local_now, expected_year in (
            (datetime(2026, 12, 31, 23, 59, 59), 2026),
            (datetime(2027, 1, 1), 2027),
        ):
            with self.subTest(local_now=local_now):
                clock = Mock()
                clock.now.return_value = local_now
                widget = Mock()
                exec(widget_code, {"datetime": clock, "st": widget, "use_year_to": True})
                widget.number_input.assert_called_once_with(
                    "To publication year", min_value=1, max_value=9999,
                    value=expected_year, step=1, disabled=False,
                )


class AppFunctionTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch(
            "requests.sessions.Session.request",
            side_effect=AssertionError("Unmocked HTTP request blocked by helper tests."),
        ))
        self.temporary_directory = tempfile.TemporaryDirectory()
        APP_FUNCTIONS["DB_PATH"] = Path(self.temporary_directory.name) / "test.db"
        connection = APP_FUNCTIONS["connect_db"]()
        connection.close()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_normalize_identifiers_and_build_deduplication_keys(self):
        normalize_doi = APP_FUNCTIONS["normalize_doi"]
        normalize_title = APP_FUNCTIONS["normalize_title"]
        make_key = APP_FUNCTIONS["make_key"]

        self.assertEqual(
            normalize_doi(" HTTPS://DOI.ORG/10.1234/ABC "),
            "10.1234/abc",
        )
        self.assertEqual(normalize_doi("doi: 10.1234/ABC"), "10.1234/abc")
        self.assertEqual(
            normalize_title("  Ｃafé: POWER—Systems! "),
            "café power systems",
        )
        self.assertEqual(
            make_key("10.1234/ABC", "ignored", 2024),
            "doi:10.1234/abc",
        )
        self.assertEqual(
            make_key("", "A Study: On Systems", 2024),
            "title:a study on systems|year:2024",
        )
        self.assertNotEqual(make_key("", "Same title", 0), make_key("", "Same title", None))

    def test_normalize_provider_metadata(self):
        openalex = APP_FUNCTIONS["normalize_openalex"]({
            "doi": "https://doi.org/10.1234/ABC",
            "title": "  A  Study ",
            "publication_year": 2024,
            "type": "article",
            "authorships": [{"author": {"display_name": "Ada Researcher"}}],
            "abstract_inverted_index": {
                "systems": [2],
                "Reliable": [0],
                "are": [1],
            },
            "primary_location": {
                "source": {"display_name": "Journal of Tests"},
            },
        })
        self.assertEqual(openalex["record_key"], "doi:10.1234/abc")
        self.assertEqual(openalex["abstract"], "Reliable are systems")
        self.assertEqual(openalex["authors"], "Ada Researcher")
        self.assertEqual(openalex["venue"], "Journal of Tests")
        self.assertEqual(openalex["publication_type"], "")  # A venue name alone is not type evidence.
        self.assertEqual(openalex["work_type"], "article")

        crossref = APP_FUNCTIONS["normalize_crossref"]({
            "DOI": "10.5678/xyz",
            "title": ["Crossref paper"],
            "published-print": {"date-parts": [[2023, 5, 1]]},
            "author": [{"given": "Grace", "family": "Hopper"}],
            "abstract": "<p>Useful <i>abstract</i></p>",
        })
        self.assertEqual(crossref["year"], 2023)
        self.assertEqual(crossref["authors"], "Grace Hopper")
        self.assertEqual(crossref["abstract"], " Useful  abstract  ")
        self.assertEqual(crossref["publication_type"], "")

    def test_crossref_type_mapping_is_explicit_and_does_not_guess(self):
        normalize = APP_FUNCTIONS["normalize_crossref"]
        expected_types = {
            "book-chapter": "book-chapter",
            "proceedings-article": "conference-paper",
            "dissertation": "dissertation",
            "posted-content": "posted-content",
            "journal-article": "journal-paper",
            "peer-review": "",
            "book-section": "",
            "proceedings": "",
            "other": "",
            "new-provider-type": "",
            "article": "",  # Not a Crossref /types value.
            "review": "",  # Not a Crossref /types value.
            "": "",
            None: "",
        }
        for raw_type, expected in expected_types.items():
            with self.subTest(raw_type=raw_type):
                record = normalize({"title": ["Synthetic paper"], "type": raw_type})
                self.assertEqual(record["publication_type"], expected)
                self.assertEqual(record["work_type"], raw_type or "")

        self.assertEqual(APP_FUNCTIONS["crossref_publication_type"]({}), "")
        self.assertEqual(
            APP_FUNCTIONS["crossref_publication_type"]({"type": " BOOK-CHAPTER "}),
            "book-chapter",
        )

    def test_openalex_categories_use_native_types_and_explicit_venue_evidence(self):
        cases = [
            ("article", "journal", "journal-paper"),
            ("review", "journal", "journal-paper"),
            ("article", "conference", "conference-paper"),
            ("review", "conference", "conference-paper"),
            ("conference-paper", None, "conference-paper"),
            ("conference-abstract", "conference", ""),
            ("article", None, ""),
            ("review", "repository", ""),
            ("article", "repository", ""),
            ("editorial", "journal", ""),
            ("book-review", "journal", ""),
            ("preprint", None, "posted-content"),
            ("book-chapter", None, "book-chapter"),
            ("dissertation", None, "dissertation"),
            ("proceedings-article", "conference", ""),  # Crossref-only value.
            ("posted-content", None, ""),  # Crossref-only value.
            (None, "journal", ""),
            ("new-provider-type", "conference", ""),
        ]
        for native_type, venue_type, expected in cases:
            with self.subTest(native_type=native_type, venue_type=venue_type):
                record = APP_FUNCTIONS["normalize_openalex"]({
                    "title": "A journal review at a conference", "type": native_type,
                    "primary_location": {"source": {"type": venue_type}},
                })
                self.assertEqual(record["publication_type"], expected)
                self.assertEqual(record["work_type"], native_type or "")
        for location in (None, {}, {"source": None}, {"source": {}}):
            with self.subTest(location=location):
                self.assertEqual(APP_FUNCTIONS["openalex_publication_type"]({
                    "type": "article", "primary_location": location,
                }), "")

    def test_openalex_request_and_results_apply_year_and_type_filters(self):
        calls = []
        payload = {
            "meta": {"count": 12},
            "results": [
                {"id": "one", "title": "Included", "publication_year": 2020, "type": "article"},
                {"id": "two", "title": "Included upper boundary", "publication_year": 2021, "type": "article"},
                {"id": "three", "title": "Too old", "publication_year": 2019, "type": "article"},
                {"id": "four", "title": "Wrong type", "publication_year": 2021, "type": "book-chapter"},
                {"id": "five", "title": "Too new", "publication_year": 2022, "type": "article"},
                {"id": "six", "title": "Unknown year", "type": "article"},
            ],
        }
        for item in payload["results"]:
            item["primary_location"] = {"source": {"type": "journal"}}

        def mocked_request(url, params):
            calls.append((url, params))
            return payload

        with patch("discovery.providers.request_json", new=mocked_request):
            count, records = APP_FUNCTIONS["search_openalex"](
                "topic",
                10,
                year_from=2020,
                year_to=2021,
                work_types=["journal-paper"],
            )

        self.assertEqual(count, 12)
        self.assertEqual(len(calls), 1)
        self.assertEqual(
            [record["title"] for record in records],
            ["Included", "Included upper boundary"],
        )
        self.assertEqual(calls[0][0], APP_FUNCTIONS["OPENALEX_URL"])
        self.assertEqual(calls[0][1]["per_page"], 10)
        self.assertEqual(
            calls[0][1]["filter"],
            "from_publication_date:2020-01-01,to_publication_date:2021-12-31,type:article|review",
        )

    def test_crossref_keeps_rows_limit_and_filters_normalized_results(self):
        calls = []
        payload = {
            "message": {
                "total-results": 21,
                "items": [
                    {"DOI": "10.1234/paper", "title": ["Conference paper"], "published": {"date-parts": [[2020]]}, "type": "proceedings-article"},
                    {"DOI": "10.1234/thesis", "title": ["Thesis"], "published": {"date-parts": [[2021]]}, "type": "dissertation"},
                    {"DOI": "10.1234/old", "title": ["Too old"], "published": {"date-parts": [[2019]]}, "type": "proceedings-article"},
                    {"DOI": "10.1234/book", "title": ["Wrong type"], "published": {"date-parts": [[2021]]}, "type": "book-chapter"},
                    {"DOI": "10.1234/new", "title": ["Too new"], "published": {"date-parts": [[2022]]}, "type": "proceedings-article"},
                    {"DOI": "10.1234/unknown-year", "title": ["Unknown year"], "type": "proceedings-article"},
                    {"DOI": "10.1234/ambiguous", "title": ["Ambiguous"], "published": {"date-parts": [[2020]]}, "type": "journal-article"},
                ],
            },
        }

        def mocked_request(url, params):
            calls.append((url, params))
            return payload

        with patch("discovery.providers.request_json", new=mocked_request):
            count, records = APP_FUNCTIONS["search_crossref"](
                "topic",
                10,
                year_from=2020,
                year_to=2021,
                work_types=["conference-paper", "dissertation"],
            )

        self.assertEqual(count, 21)
        self.assertEqual(len(calls), 1)
        self.assertEqual(
            [record["title"] for record in records],
            ["Conference paper", "Thesis"],
        )
        self.assertEqual(calls[0][0], APP_FUNCTIONS["CROSSREF_URL"])
        self.assertEqual(
            calls[0][1],
            {"query.bibliographic": "topic", "rows": 10,
             "filter": "from-pub-date:2019-01-01,until-pub-date:2021-12-31,"
                       "type:dissertation,type:proceedings-article"},
        )

    def test_empty_type_filter_keeps_unclassified_records(self):
        records = [
            {"year": 2020, "publication_type": ""},
            {"year": 2021, "publication_type": "journal-paper"},
        ]

        filtered = APP_FUNCTIONS["filter_search_results"](
            records,
            year_from=2020,
            year_to=2021,
            work_types=None,
        )

        self.assertEqual(filtered, records)

    def test_year_bounds_are_inclusive_and_can_be_used_independently(self):
        records = [
            {"year": year, "publication_type": "journal-paper"}
            for year in (2019, 2020, 2021, 2022, None)
        ]
        cases = [
            (None, None, [2019, 2020, 2021, 2022, None]),
            (2020, None, [2020, 2021, 2022]),
            (None, 2021, [2019, 2020, 2021]),
            (2020, 2021, [2020, 2021]),
            (2020, 2020, [2020]),
        ]
        for lower, upper, expected_years in cases:
            with self.subTest(lower=lower, upper=upper):
                filtered = APP_FUNCTIONS["filter_search_results"](
                    records, lower, upper,
                )
                self.assertEqual([paper["year"] for paper in filtered], expected_years)
        self.assertEqual([paper["year"] for paper in records], [2019, 2020, 2021, 2022, None])

    def test_providers_without_filters_keep_unknown_years_and_types(self):
        cases = [
            ("search_openalex", "per_page", {"meta": {"count": 20}, "results": [
                {"title": "No year or type"},
                {"title": "Unknown type", "publication_year": 2020, "type": "other"},
                {},  # No usable record key.
            ]}),
            ("search_crossref", "rows", {"message": {"total-results": 20, "items": [
                {"title": ["No year or type"]},
                {"title": ["Unknown type"], "published": {"date-parts": [[2020]]}, "type": "journal-article"},
                {},
            ]}}),
        ]
        for name, limit_param, payload in cases:
            for selection in (None, []):
                with self.subTest(provider=name, selection=selection):
                    request = Mock(return_value=payload)
                    with patch("discovery.providers.request_json", new=request):
                        count, records = APP_FUNCTIONS[name]("topic", 5, work_types=selection)
                    request.assert_called_once()
                    params = request.call_args.args[1]
                    self.assertEqual(params[limit_param], 5)
                    self.assertNotIn("filter", params)
                    self.assertEqual(count, 20)
                    self.assertEqual(
                        [paper["title"] for paper in records],
                        ["No year or type", "Unknown type"],
                    )

    def test_provider_specific_payloads_match_shared_categories(self):
        categories = [
            "journal-paper", "conference-paper", "book-chapter", "dissertation", "posted-content",
        ]
        oa_types = ["article", "conference-paper", "book-chapter", "dissertation", "preprint"]
        cr_types = ["journal-article", "proceedings-article", "book-chapter", "dissertation", "posted-content"]
        expected_query_types = {
            "journal-paper": ["article", "review"],
            "conference-paper": ["article", "conference-paper", "review"],
            "book-chapter": ["book-chapter"],
            "dissertation": ["dissertation"],
            "posted-content": ["preprint"],
        }
        payloads = {
            APP_FUNCTIONS["OPENALEX_URL"]: {"meta": {"count": 5}, "results": [
                {"title": category, "publication_year": 2020, "type": native_type,
                 "primary_location": {"source": {"type": "journal"}} if category == "journal-paper" else None}
                for category, native_type in zip(categories, oa_types)
            ]},
            APP_FUNCTIONS["CROSSREF_URL"]: {"message": {"total-results": 5, "items": [
                {"title": [category], "published": {"date-parts": [[2020]]}, "type": native_type}
                for category, native_type in zip(categories, cr_types)
            ]}},
        }
        selections = [[category] for category in categories] + [categories[:2], []]
        for selection in selections:
            with self.subTest(selection=selection):
                results = []
                for name in ("search_openalex", "search_crossref"):
                    request = Mock(side_effect=lambda url, params: payloads[url])
                    with patch("discovery.providers.request_json", new=request):
                        _, records = APP_FUNCTIONS[name]("topic", 5, 2020, 2020, selection)
                    request.assert_called_once()
                    results.append([paper["publication_type"] for paper in records])
                    if name == "search_openalex":
                        expected_filter = (
                            "from_publication_date:2020-01-01,"
                            "to_publication_date:2020-12-31"
                        )
                        if selection:
                            native_types = sorted({
                                native_type for category in selection
                                for native_type in expected_query_types[category]
                            })
                            expected_filter += ",type:" + "|".join(native_types)
                        self.assertEqual(request.call_args.args[1]["filter"], expected_filter)
                self.assertEqual(results, [selection or categories] * 2)

    def test_crossref_journal_category_includes_articles_and_reviews_without_subtype_guesses(self):
        payload = {"message": {"total-results": 3, "items": [
            {"title": ["A systematic review"], "type": "journal-article"},
            {"title": ["An original article"], "type": "journal-article"},
            {"title": ["Referee report"], "type": "peer-review"},
        ]}}
        request = Mock(return_value=payload)
        with patch("discovery.providers.request_json", new=request):
            count, records = APP_FUNCTIONS["search_crossref"](
                "topic", 5, work_types=["journal-paper"],
            )
        request.assert_called_once()
        self.assertEqual(count, 3)
        self.assertEqual([record["title"] for record in records],
                         ["A systematic review", "An original article"])
        self.assertEqual([record["work_type"] for record in records], ["journal-article"] * 2)
        self.assertEqual([record["publication_type"] for record in records], ["journal-paper"] * 2)

    def test_provider_empty_responses_do_not_trigger_more_requests(self):
        cases = [
            ("search_openalex", {"meta": {"count": 0}, "results": []}, 0),
            ("search_crossref", {"message": {"total-results": 0, "items": []}}, 0),
            ("search_openalex", {}, None),
            ("search_crossref", {}, None),
        ]
        for name, payload, expected_count in cases:
            with self.subTest(provider=name, payload=payload):
                request = Mock(return_value=payload)
                with patch("discovery.providers.request_json", new=request):
                    result = APP_FUNCTIONS[name]("topic", 5, 2020, 2021, ["book-chapter"])
                request.assert_called_once()
                self.assertEqual(result, (expected_count, []))

    def test_crossref_year_selection_preserves_existing_date_precedence(self):
        cases = [
            ({"published-print": {"date-parts": [[2022]]},
              "published-online": {"date-parts": [[2020]]},
              "published": {"date-parts": [[2019]]}}, 2022),
            ({"published-online": {"date-parts": [[2020]]},
              "published": {"date-parts": [[2019]]}}, 2020),
            ({"published": {"date-parts": [[2019]]}}, 2019),
            ({"published": {"date-parts": [[]]}}, None),
            ({}, None),
        ]
        for dates, expected_year in cases:
            with self.subTest(dates=dates):
                record = APP_FUNCTIONS["normalize_crossref"]({"title": ["Synthetic paper"], **dates})
                self.assertEqual(record["year"], expected_year)

    def test_duplicate_records_merge_sources_and_persist_once(self):
        normalize_openalex = APP_FUNCTIONS["normalize_openalex"]
        normalize_crossref = APP_FUNCTIONS["normalize_crossref"]
        save_papers = APP_FUNCTIONS["save_papers"]

        openalex_record = normalize_openalex({
            "doi": "10.1234/shared",
            "title": "Shared record",
            "publication_year": 2024,
            "type": "article",
        })
        crossref_record = normalize_crossref({
            "DOI": "https://doi.org/10.1234/shared",
            "title": ["A different title from another source"],
            "published": {"date-parts": [[2024]]},
        })

        self.assertEqual(save_papers([openalex_record]), 1)
        self.assertEqual(save_papers([crossref_record]), 0)

        connection = sqlite3.connect(APP_FUNCTIONS["DB_PATH"])
        try:
            rows = connection.execute(
                "SELECT title, source FROM papers"
            ).fetchall()
        finally:
            connection.close()
        self.assertEqual(rows, [("Shared record", "Crossref;OpenAlex")])

    def test_filter_matches_title_or_abstract_as_literal_text(self):
        papers = pd.DataFrame([
            {"title": "Fault. detection", "abstract": None},
            {"title": "Other title", "abstract": "A fault. method"},
            {"title": "FaultX detection", "abstract": "No punctuation match"},
        ])

        filtered = APP_FUNCTIONS["filter_papers"](papers, "fault.")

        self.assertEqual(filtered.index.tolist(), [0, 1])
        unchanged = APP_FUNCTIONS["filter_papers"](papers, "  ")
        self.assertEqual(len(unchanged), 3)
        self.assertIsNot(unchanged, papers)

    def test_null_metadata_is_enriched_without_replacing_existing_evidence(self):
        paper = APP_FUNCTIONS["normalize_crossref"]({
            "DOI": "10.1234/null-metadata", "title": ["Incoming title"],
            "type": "journal-article", "published": {"date-parts": [[2020]]},
            "abstract": "New abstract", "author": [{"given": "Synthetic", "family": "Author"}],
        })
        with closing(sqlite3.connect(APP_FUNCTIONS["DB_PATH"])) as connection, connection:
            connection.execute(
                "INSERT INTO papers VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (paper["record_key"], "Original title", paper["doi"], None, None,
                 None, None, "OpenAlex", None, "original timestamp", "old seen"),
            )
        self.assertEqual(APP_FUNCTIONS["save_papers"]([paper]), 0)
        with closing(sqlite3.connect(APP_FUNCTIONS["DB_PATH"])) as connection:
            row = connection.execute(
                "SELECT title,year,work_type,abstract,authors,url,source,first_saved_utc FROM papers"
            ).fetchone()
        self.assertEqual(row, ("Original title", 2020, "journal-article", "New abstract",
                               "Synthetic Author", "https://doi.org/10.1234/null-metadata",
                               "Crossref;OpenAlex", "original timestamp"))

    def test_failed_batch_rolls_back_insertions_and_source_updates(self):
        original = APP_FUNCTIONS["normalize_openalex"]({
            "doi": "10.1234/rollback", "title": "Existing paper", "publication_year": 2020,
        })
        APP_FUNCTIONS["save_papers"]([original])
        update = dict(original, source="Crossref", abstract="Should roll back")
        new = APP_FUNCTIONS["normalize_crossref"]({"DOI": "10.1234/new", "title": ["New paper"]})
        with closing(sqlite3.connect(APP_FUNCTIONS["DB_PATH"])) as connection:
            before = connection.execute("SELECT * FROM papers ORDER BY record_key").fetchall()
        with self.assertRaises(KeyError):
            APP_FUNCTIONS["save_papers"]([update, new, {"record_key": "invalid"}])
        with closing(sqlite3.connect(APP_FUNCTIONS["DB_PATH"])) as connection:
            after = connection.execute("SELECT * FROM papers ORDER BY record_key").fetchall()
        self.assertEqual(after, before)

    def test_csv_export_is_utf8_with_bom_and_keeps_columns(self):
        papers = pd.DataFrame([
            {"title": "Café paper", "year": 2024},
        ])

        exported = APP_FUNCTIONS["papers_to_csv"](papers)

        self.assertTrue(exported.startswith(b"\xef\xbb\xbf"))
        self.assertIn("Café paper".encode("utf-8"), exported)
        restored = pd.read_csv(io.BytesIO(exported))
        self.assertEqual(restored.columns.tolist(), ["title", "year"])
        self.assertEqual(restored.iloc[0]["title"], "Café paper")


if __name__ == "__main__":
    unittest.main()
