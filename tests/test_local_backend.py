"""Ollama wire-contract tests with synthetic in-memory responses only."""

import json
import unittest
from unittest.mock import Mock, patch

import requests

from review.analysis import MODEL, OPTIONS, build_request
from review.local_backend import BackendError, ENDPOINT, OllamaLocal
from review.workspace import create_review
from test_analysis import response_for
from test_review import fixture_run


class LocalBackendTests(unittest.TestCase):
    def setUp(self):
        self.review = create_review(fixture_run(), "q", "i", "e")
        self.key = next(iter(self.review["papers"]))
        self.session = Mock()
        self.session.__enter__ = Mock(return_value=self.session)
        self.session.__exit__ = Mock(return_value=False)
        self.enterContext(patch("requests.Session", return_value=self.session))
        self.enterContext(patch("requests.sessions.Session.request", side_effect=AssertionError("Live HTTP blocked.")))
        self.responses = {
            "/api/version": {"version": "test-runtime"},
            "/api/tags": {"models": [{"name": MODEL, "digest": "a" * 64}]},
            "/api/show": {"details": {"format": "gguf", "parameter_size": "1.5B", "quantization_level": "Q4_K_M"}},
            "/api/generate": {"model": MODEL, "done": True, "done_reason": "stop", "prompt_eval_count": 100,
                              "response": json.dumps(response_for(self.review, self.key))},
        }
        self.status = 200
        self.session.request.side_effect = self.respond

    def respond(self, method, url, **kwargs):
        self.assertTrue(url.startswith(ENDPOINT + "/api/"))
        payload = self.responses[url[len(ENDPOINT):]]
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.status_code = self.status
        response.iter_content.return_value = [json.dumps(payload).encode()]
        return response

    def test_health_check_sends_no_paper_or_generation_and_records_identity(self):
        result = OllamaLocal().inspect()
        self.assertEqual(result["model_digest"], "a" * 64)
        self.assertEqual(result["runtime_version"], "test-runtime")
        self.assertEqual([c.args[1] for c in self.session.request.call_args_list], [
            ENDPOINT + "/api/version", ENDPOINT + "/api/tags", ENDPOINT + "/api/show"])
        self.assertNotIn("abstract", str(self.session.request.call_args_list))

    def test_generation_is_loopback_serial_bounded_no_proxies_redirects_pulls_or_retries(self):
        request = build_request(self.review, self.key)
        result = OllamaLocal().generate(request)
        self.assertEqual(json.loads(result["response"])["record_key"], self.key)
        self.assertFalse(self.session.trust_env)
        calls = self.session.request.call_args_list
        self.assertEqual(len(calls), 5)
        generate = next(c for c in calls if c.args[1].endswith("/api/generate"))
        self.assertEqual(generate.kwargs["json"], {**request, "model": MODEL})
        self.assertEqual(generate.kwargs["timeout"], (2, 120))
        for call in calls:
            self.assertFalse(call.kwargs["allow_redirects"])
            self.assertTrue(call.kwargs["stream"])
            self.assertNotIn("pull", call.args[1])

    def test_timeout_connection_and_http_failures_are_sanitized_and_not_retried(self):
        for error in [requests.Timeout("PRIVATE PROMPT"), requests.ConnectionError("PRIVATE PROMPT")]:
            self.session.request.reset_mock()
            self.session.request.side_effect = error
            with self.assertRaises(BackendError) as caught:
                OllamaLocal().inspect()
            self.assertNotIn("PRIVATE", str(caught.exception))
            self.assertEqual(self.session.request.call_count, 1)
        self.session.request.side_effect = self.respond
        for status in [302, 404, 429, 500]:
            self.status = status
            with self.subTest(status=status), self.assertRaises(BackendError):
                OllamaLocal().inspect()

    def test_missing_or_cloud_model_is_rejected_before_paper_content_is_sent(self):
        for models in [[], [{"name": MODEL, "digest": "bad"}],
                       [{"name": MODEL, "digest": "a" * 64, "remote_host": "https://example.com"}],
                       [{"name": MODEL, "digest": "a" * 64, "remote_model": "cloud"}], "invalid"]:
            self.responses["/api/tags"] = {"models": models}
            self.session.request.reset_mock()
            with self.subTest(models=models), self.assertRaises(BackendError):
                OllamaLocal().generate(build_request(self.review, self.key))
            self.assertFalse(any(c.args[1].endswith("/api/generate") for c in self.session.request.call_args_list))

    def test_wrong_quantization_or_remote_show_rejected(self):
        for show in [{}, {"remote_model": "cloud", "details": {}},
                     {"details": {"format": "gguf", "parameter_size": "7B", "quantization_level": "Q4_K_M"}}]:
            self.responses["/api/show"] = show
            with self.subTest(show=show), self.assertRaises(BackendError):
                OllamaLocal().inspect()

    def test_truncated_wrong_model_or_context_overflow_generation_rejected(self):
        original = dict(self.responses["/api/generate"])
        for change in [{"done": False}, {"done_reason": "length"}, {"model": "other"},
                       {"prompt_eval_count": OPTIONS["num_ctx"] - OPTIONS["num_predict"]}, {"prompt_eval_count": True}, {"response": {}},
                       {"prompt_eval_count": None}]:
            self.responses["/api/generate"] = {**original, **change}
            with self.subTest(change=change), self.assertRaises(BackendError):
                OllamaLocal().generate(build_request(self.review, self.key))

    def test_model_change_during_generation_is_rejected(self):
        def changed(method, url, **kwargs):
            result = self.respond(method, url, **kwargs)
            if url.endswith("/api/generate"):
                self.responses["/api/tags"]["models"][0]["digest"] = "b" * 64
            return result
        self.session.request.side_effect = changed
        with self.assertRaisesRegex(BackendError, "changed during generation"):
            OllamaLocal().generate(build_request(self.review, self.key))

    def test_invalid_json_and_oversize_responses_do_not_echo_backend_body(self):
        response = self.respond("GET", ENDPOINT + "/api/version")
        self.session.request.side_effect = None
        self.session.request.return_value = response
        for chunks in [[b"PRIVATE RESEARCH NOT JSON"], [b'{}' * 20000], [b'{"version":1,"version":2}']]:
            response.iter_content.return_value = chunks
            with self.subTest(size=sum(map(len, chunks))), self.assertRaises(BackendError) as caught:
                OllamaLocal().inspect()
            self.assertNotIn("PRIVATE", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
