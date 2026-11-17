"""Bounded retrieval with synthetic pages, fake clocks and blocked live HTTP."""

import json
import unittest
from unittest.mock import Mock, patch

import requests

from discovery.providers import CrossrefAdapter, OpenAlexAdapter
from discovery.retrieval import RetrievalBudget, retrieve, retry_after_seconds
from datetime import datetime, timezone


def oa_page(titles, total=100):
    return {"meta": {"count": total}, "results": [
        {"title": title, "publication_year": 2020, "type": "conference-paper"}
        for title in titles
    ]}


def cr_page(titles, cursor=None, total=100):
    return {"message": {"total-results": total, "next-cursor": cursor, "items": [
        {"title": [title], "published": {"date-parts": [[2020]]},
         "type": "proceedings-article"} for title in titles
    ]}}


class FakeClock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class BoundedRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch(
            "requests.sessions.Session.request",
            side_effect=AssertionError("Live HTTP blocked by retrieval tests."),
        ))
        self.clock = FakeClock()

    def run_retrieval(self, adapter, budget=None, **kwargs):
        return retrieve(
            adapter, "  synthetic topic  ", budget or RetrievalBudget(10, 2),
            2020, 2021, ["conference-paper"],
            sleep_fn=self.clock.sleep, clock_fn=self.clock, **kwargs,
        )

    def test_openalex_basic_pages_preserve_filters_and_stop_on_final_page(self):
        request = Mock(side_effect=[oa_page(["one", "two"], 3), oa_page(["three"], 3)])
        result = self.run_retrieval(OpenAlexAdapter(request))
        params = [call.args[1] for call in request.call_args_list]
        self.assertEqual([p["page"] for p in params], [1, 2])
        self.assertEqual({k: v for k, v in params[0].items() if k != "page"},
                         {k: v for k, v in params[1].items() if k != "page"})
        self.assertNotIn("cursor", params[0])
        self.assertNotIn("api_key", params[0])
        self.assertEqual(params[0]["search"], "synthetic topic")
        self.assertEqual(params[0]["filter"],
                         "from_publication_date:2020-01-01,to_publication_date:2021-12-31,type:article|conference-paper|review")
        self.assertEqual((result.status, result.stop_reason), ("complete", "source_exhausted"))
        self.assertEqual((result.reported_total, result.fetched_count, result.filtered_count), (3, 3, 3))
        self.assertEqual(self.clock.now, 1)

    def test_crossref_uses_latest_cursor_and_identical_query_and_rows(self):
        request = Mock(side_effect=[cr_page(["a", "b"], "cursor A", 4),
                                    cr_page(["c", "d"], "cursor B", 4),
                                    cr_page([], None, 4)])
        result = self.run_retrieval(CrossrefAdapter(request))
        self.assertEqual([call.args[1] for call in request.call_args_list], [
            {"query.bibliographic": "synthetic topic", "rows": 2, "cursor": cursor,
             "filter": "from-pub-date:2019-01-01,until-pub-date:2021-12-31,type:proceedings-article"}
            for cursor in ("*", "cursor A", "cursor B")
        ])
        self.assertEqual((result.status, result.fetched_count, result.pages_completed), ("complete", 4, 3))

    def test_raw_budget_includes_locally_excluded_records_and_duplicates(self):
        payload = oa_page(["same", "same"], 500)
        payload["results"][0]["publication_year"] = 1990
        request = Mock(return_value=payload)
        result = self.run_retrieval(OpenAlexAdapter(request), RetrievalBudget(4, 2))
        self.assertEqual(request.call_count, 2)
        self.assertEqual((result.status, result.stop_reason), ("partial", "record_budget"))
        self.assertEqual((result.fetched_count, result.filtered_count, result.unique_count), (4, 2, 1))

    def test_non_multiple_budget_never_changes_crossref_rows_or_overfetches(self):
        request = Mock(return_value=cr_page(["a", "b"], "next"))
        result = self.run_retrieval(CrossrefAdapter(request), RetrievalBudget(3, 2))
        request.assert_called_once()
        self.assertEqual((result.fetched_count, result.stop_reason), (2, "record_budget"))

    def test_page_and_time_budgets_prevent_additional_requests(self):
        for budget, expected in ((RetrievalBudget(10, 2, max_pages=1), "page_budget"),
                                  (RetrievalBudget(10, 2, max_seconds=0.5), "time_budget")):
            with self.subTest(reason=expected):
                request = Mock(return_value=oa_page(["a", "b"]))
                result = self.run_retrieval(OpenAlexAdapter(request), budget)
                request.assert_called_once()
                self.assertEqual((result.status, result.stop_reason), ("partial", expected))

    def test_slow_request_finishes_but_no_request_starts_after_deadline(self):
        def slow_request(url, params):
            self.clock.now += 2
            return oa_page(["a", "b"])
        request = Mock(side_effect=slow_request)
        result = self.run_retrieval(OpenAlexAdapter(request), RetrievalBudget(10, 2, max_seconds=1))
        request.assert_called_once()
        self.assertEqual(result.stop_reason, "time_budget")
        self.assertEqual(result.filtered_count, 2)

    def test_later_failure_keeps_earlier_pages_without_leaking_exception_urls(self):
        for failure in (requests.Timeout("secret query in URL"),
                        requests.ConnectionError("private URL"),
                        ValueError("private payload")):
            with self.subTest(failure=type(failure).__name__):
                request = Mock(side_effect=[oa_page(["a", "b"]), failure])
                result = self.run_retrieval(OpenAlexAdapter(request))
                self.assertEqual((result.status, result.requests_attempted, result.pages_completed), ("partial", 2, 1))
                self.assertEqual(result.filtered_count, 2)
                note = result.history_note(RetrievalBudget(10, 2), 2020, 2021, ["conference-paper"])
                self.assertNotIn("private", note)
                self.assertNotIn("secret", note)

    def test_access_rate_limit_and_server_errors_do_not_retry(self):
        for code in (401, 403, 429, 500):
            with self.subTest(code=code):
                response = requests.Response()
                response.status_code = code
                request = Mock(side_effect=requests.HTTPError("private URL", response=response))
                result = self.run_retrieval(CrossrefAdapter(request))
                request.assert_called_once()
                reason = "rate_limited" if code == 429 else "provider_error"
                self.assertEqual((result.status, result.stop_reason, result.pages_completed), ("error", reason, 0))
                self.assertEqual(result.error, f"HTTP {code}")

    def test_unknown_total_is_not_zero_and_empty_result_is_scoped_completion(self):
        for factory, payload in ((OpenAlexAdapter, oa_page([], None)),
                                  (CrossrefAdapter, cr_page([], total=None))):
            with self.subTest(provider=factory.name):
                request = Mock(return_value=payload)
                result = self.run_retrieval(factory(request))
                request.assert_called_once()
                self.assertIsNone(result.reported_total)
                self.assertEqual((result.status, result.filtered_count), ("complete", 0))

    def test_full_pages_with_missing_or_cyclic_cursor_are_partial(self):
        cases = [([cr_page(["a", "b"])], "cursor_missing", 1),
                 ([cr_page(["a", "b"], "*" )], "cursor_repeated", 1),
                 ([cr_page(["a", "b"], "A"), cr_page(["c", "d"], "B"),
                   cr_page(["e", "f"], "A")], "cursor_repeated", 3)]
        for pages, reason, count in cases:
            with self.subTest(reason=reason, count=count):
                request = Mock(side_effect=pages)
                result = self.run_retrieval(CrossrefAdapter(request))
                self.assertEqual((result.status, result.stop_reason, request.call_count), ("partial", reason, count))

    def test_changing_and_contradictory_totals_cannot_establish_completion(self):
        for pages, changed in (([oa_page(["a", "b"], 3), oa_page(["c"], 4)], True),
                                ([oa_page(["a"], 100)], False)):
            with self.subTest(changed=changed):
                result = self.run_retrieval(OpenAlexAdapter(Mock(side_effect=pages)))
                self.assertEqual((result.status, result.stop_reason), ("partial", "inconsistent_response"))
                self.assertEqual(result.total_changed, changed)
                self.assertEqual(result.reported_total, pages[0]["meta"]["count"])

    def test_malformed_response_is_not_empty_success(self):
        for factory, payloads in (
            (OpenAlexAdapter, [{}, [], {"meta": {}, "results": None},
                               {"meta": {}, "results": [None]}, oa_page([], True)]),
            (CrossrefAdapter, [{}, {"message": None},
                               {"message": {"items": "bad"}}, cr_page([], cursor=5)]),
        ):
            for payload in payloads:
                with self.subTest(provider=factory.name, payload=payload):
                    result = self.run_retrieval(factory(Mock(return_value=payload)))
                    self.assertEqual((result.status, result.stop_reason, result.pages_completed), ("error", "invalid_response", 0))

    def test_oversized_page_is_rejected(self):
        request = Mock(return_value=oa_page(["a", "b", "c"]))
        result = self.run_retrieval(OpenAlexAdapter(request))
        self.assertEqual((result.status, result.stop_reason, result.fetched_count), ("error", "invalid_response", 0))

    def test_invalid_json_is_an_invalid_response_and_preserves_prior_pages(self):
        request = Mock(side_effect=[oa_page(["a", "b"]),
                                    requests.exceptions.JSONDecodeError("private", "", 0)])
        result = self.run_retrieval(OpenAlexAdapter(request))
        self.assertEqual((result.status, result.stop_reason, result.error),
                         ("partial", "invalid_response", "Invalid provider response"))
        self.assertEqual(result.filtered_count, 2)

    def test_note_round_trips_settings_counts_and_scope_without_cursors(self):
        budget = RetrievalBudget(4, 2)
        result = self.run_retrieval(CrossrefAdapter(Mock(return_value=cr_page(["a", "b"], "private cursor"))), budget)
        note = result.history_note(budget, 2020, 2021, ["conference-paper"])
        parsed = json.loads(note)
        self.assertEqual(parsed["settings"]["raw_record_budget"], 4)
        self.assertEqual(parsed["settings"]["publication_types"], ["conference-paper"])
        self.assertEqual(parsed["retrieval"]["total_scope"], "server-filtered-candidates")
        self.assertEqual(parsed["retrieval"]["raw_fetched"], result.fetched_count)
        self.assertNotIn("private cursor", note)

    def test_invalid_budget_query_and_years_fail_before_io(self):
        for kwargs in ({"max_records": 0}, {"max_records": 251}, {"max_records": True},
                       {"page_size": 51}, {"max_pages": 6}, {"max_seconds": float("nan")},
                       {"max_seconds": 121}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                RetrievalBudget(**kwargs)
        request = Mock()
        adapter = OpenAlexAdapter(request)
        with self.assertRaises(ValueError):
            retrieve(adapter, "  ", RetrievalBudget())
        with self.assertRaises(ValueError):
            retrieve(adapter, "topic", RetrievalBudget(), 2022, 2020)
        request.assert_not_called()

    def test_historical_optional_bounds_and_missing_years(self):
        for bounds, expected in [
            ((None, None), ["Old", "Unknown", "Recent"]),
            ((None, 1800), ["Old"]),
            ((1800, None), ["Recent"]),
            ((700, 1700), ["Old"]),
        ]:
            with self.subTest(bounds=bounds):
                payload = {"meta": {"count": 3}, "results": [
                    {"id": "Wold", "title": "Old", "publication_year": 1665},
                    {"id": "Wunknown", "title": "Unknown"},
                    {"id": "Wrecent", "title": "Recent", "publication_year": 2020},
                ]}
                request = Mock(return_value=payload)
                result = retrieve(OpenAlexAdapter(request), "public history", RetrievalBudget(5),
                                  *bounds, work_types=None)
                self.assertEqual([r["title"] for r in result.records], expected)
                params = request.call_args.args[1]
                if bounds == (None, None):
                    self.assertNotIn("filter", params)
                elif bounds == (700, 1700):
                    self.assertEqual(params["filter"],
                                     "from_publication_date:0700-01-01,to_publication_date:1700-12-31")

    def test_final_page_exceeding_reported_total_is_partial(self):
        result = self.run_retrieval(OpenAlexAdapter(Mock(return_value=oa_page(["one"], 0))))
        self.assertEqual((result.status, result.stop_reason), ("partial", "inconsistent_response"))
        self.assertEqual((result.fetched_count, result.filtered_count), (1, 1))

    def test_provenance_tracks_native_id_page_and_classification(self):
        first, second = oa_page(["one", "two"], 3), oa_page(["three"], 3)
        first["results"][0]["id"] = "https://openalex.org/W123"
        result = self.run_retrieval(OpenAlexAdapter(Mock(side_effect=[first, second])))
        self.assertEqual([p["page"] for p in result.provenance], [1, 1, 2])
        self.assertEqual(result.provenance[0]["source_id"], "https://openalex.org/W123")
        self.assertEqual(result.provenance[0]["raw_type"], "conference-paper")
        self.assertEqual(result.provenance[0]["publication_type"], "conference-paper")
        self.assertEqual(result.provenance[1]["source_id"], "")
        self.assertTrue(result.started_utc)
        self.assertTrue(result.finished_utc)

    def test_429_after_success_keeps_pages_and_numeric_cooldown(self):
        response = requests.Response()
        response.status_code = 429
        response.headers["Retry-After"] = "120"
        request = Mock(side_effect=[cr_page(["a", "b"], "cursor"), requests.HTTPError(response=response)])
        result = self.run_retrieval(CrossrefAdapter(request))
        self.assertEqual((result.status, result.stop_reason), ("partial", "rate_limited"))
        self.assertEqual((result.fetched_count, result.filtered_count, result.retry_after_seconds), (2, 2, 120))
        self.assertEqual(request.call_count, 2)

    def test_retry_after_date_and_untrusted_header_are_sanitized(self):
        response = requests.Response()
        response.headers["Retry-After"] = "Tue, 20 Oct 2026 12:01:00 GMT"
        now = datetime(2026, 10, 20, 12, tzinfo=timezone.utc)
        self.assertEqual(retry_after_seconds(response, now), 60)
        for value in ("private URL?key=secret", "-5", "", "1" * 5000):
            response.headers["Retry-After"] = value
            self.assertEqual(retry_after_seconds(response, now), 60)

    def test_doi_without_title_is_fetched_but_not_a_saveable_filtered_record(self):
        request = Mock(return_value={"message": {"total-results": 1, "items": [
            {"DOI": "10.1234/no-title", "type": "journal-article"},
        ]}})
        result = retrieve(CrossrefAdapter(request), "topic", RetrievalBudget(5))
        self.assertEqual((result.fetched_count, result.filtered_count, result.unique_count), (1, 0, 0))

    def test_invalid_years_and_scalar_titles_cannot_enter_phase_c_evidence(self):
        cases = [(CrossrefAdapter, {"message": {"total-results": 1, "items": [
                    {"title": "A malformed scalar title", "DOI": "10.1234/scalar"}
                 ]}}), (OpenAlexAdapter, {"meta": {"count": 1}, "results": [
                    {"title": ["Malformed OpenAlex title"]}
                 ]})]
        for year in (True, 2020.5, "2020", {}, [], 2**63, -(2**63)-1):
            cases.append((OpenAlexAdapter, oa_page(["Paper"], 1)))
            cases[-1][1]["results"][0]["publication_year"] = year
            cases.append((CrossrefAdapter, cr_page(["Paper"], total=1)))
            cases[-1][1]["message"]["items"][0]["published"]["date-parts"][0][0] = year
        for factory, payload in cases:
            with self.subTest(provider=factory.name, payload=payload):
                result = retrieve(factory(Mock(return_value=payload)), "synthetic", RetrievalBudget(5))
                self.assertEqual((result.status, result.stop_reason, result.filtered_count),
                                 ("error", "invalid_response", 0))

    def test_unbounded_source_integer_years_are_not_restricted_to_ui_input_range(self):
        for year in (-100, 0, 10000):
            payload = oa_page(["Paper"], 1)
            payload["results"][0]["publication_year"] = year
            result = retrieve(OpenAlexAdapter(Mock(return_value=payload)), "synthetic", RetrievalBudget(5))
            self.assertEqual(result.records[0]["year"], year)
            self.assertIn(f"year:{year}", result.records[0]["record_key"])

    def test_non_text_metadata_is_rejected_before_it_can_reach_storage(self):
        for factory, fields in (
            (OpenAlexAdapter, ("doi", "id", "type")),
            (CrossrefAdapter, ("DOI", "URL", "type", "abstract", "container-title")),
        ):
            for field_name in fields:
                with self.subTest(provider=factory.name, field=field_name):
                    payload = (oa_page(["Synthetic"], 1) if factory is OpenAlexAdapter
                               else cr_page(["Synthetic"], total=1))
                    item = payload["results"][0] if factory is OpenAlexAdapter else payload["message"]["items"][0]
                    item[field_name] = {"invalid": "synthetic non-text metadata"}
                    result = retrieve(factory(Mock(return_value=payload)), "synthetic", RetrievalBudget(5))
                    self.assertEqual((result.status, result.stop_reason, result.records),
                                     ("error", "invalid_response", []))

    def test_nullable_author_name_parts_are_missing_information_not_a_page_failure(self):
        payload = cr_page(["Synthetic"], total=1)
        payload["message"]["items"][0]["author"] = [
            {"given": None, "family": "Researcher"}, {"given": "Solo", "family": None},
        ]
        result = retrieve(CrossrefAdapter(Mock(return_value=payload)), "synthetic", RetrievalBudget(5))
        self.assertEqual(result.status, "complete")
        self.assertEqual(result.records[0]["authors"], "Researcher; Solo")

    def test_invalid_bound_and_category_arguments_fail_before_requests(self):
        for factory in (OpenAlexAdapter, CrossrefAdapter):
            for kwargs in ({"year_from": "2020"}, {"year_to": True}, {"year_from": 0},
                           {"year_to": 10000}, {"work_types": ["unsupported-category"]}):
                with self.subTest(provider=factory.name, kwargs=kwargs):
                    request = Mock(return_value=oa_page([], 0) if factory is OpenAlexAdapter else cr_page([], total=0))
                    with self.assertRaises(ValueError):
                        retrieve(factory(request), "synthetic", RetrievalBudget(5), **kwargs)
                    request.assert_not_called()

    def test_abstract_index_cannot_silently_overwrite_or_reorder_invalid_positions(self):
        for index in ({"A": [0], "B": [0]}, {"A": [-1]}, {"A": [True]}, {"A": ["0"]}):
            with self.subTest(index=index):
                payload = oa_page(["Synthetic"], 1)
                payload["results"][0]["abstract_inverted_index"] = index
                result = retrieve(OpenAlexAdapter(Mock(return_value=payload)), "synthetic", RetrievalBudget(5))
                self.assertEqual((result.status, result.stop_reason), ("error", "invalid_response"))

    def test_search_context_snapshots_the_category_selection(self):
        selection = ["conference-paper"]
        result = retrieve(OpenAlexAdapter(Mock(return_value=oa_page([], 0))), "  synthetic  ",
                          RetrievalBudget(5), work_types=selection)
        selection.append("journal-paper")
        self.assertEqual(result.query, "synthetic")
        self.assertEqual(result.settings_snapshot["publication_types"], ["conference-paper"])

    def test_bare_openalex_doi_has_a_usable_resolver_url(self):
        payload = oa_page(["Synthetic"], 1)
        payload["results"][0]["doi"] = "10.1234/BARE"
        result = retrieve(OpenAlexAdapter(Mock(return_value=payload)), "synthetic", RetrievalBudget(5))
        self.assertEqual(result.records[0]["url"], "https://doi.org/10.1234/bare")


if __name__ == "__main__":
    unittest.main()
