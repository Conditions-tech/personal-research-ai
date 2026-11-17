"""Offline frozen-label comparison; never a semantic/scientific verifier.

Reports workflow coverage, source presence and developer field agreement
separately. Refused/unattempted papers never count as correct missing fields.
No model, HTTP, SQLite, package installation or automatic correction is used.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


FIELDS = ("objective", "method", "dataset", "results", "limitations", "conclusion")


def adjudicate(manifest_bytes, report):
    manifest = json.loads(manifest_bytes)
    if report.get("manifest_sha256") != hashlib.sha256(manifest_bytes).hexdigest():
        raise ValueError("Report does not match the frozen manifest bytes.")
    cases = {c["id"]: c for c in manifest["cases"]}
    if len(cases) != len(manifest["cases"]):
        raise ValueError("Duplicate fixture identity.")
    observations = {}
    for item in report["cases"]:
        key = item["case"]["id"]
        if key not in cases or item["case"] != cases[key] or key in observations:
            raise ValueError("Unknown, changed or duplicated evaluation case.")
        observations[key] = item
    metric_names = ("cases", "benign_cases", "expected_nonmissing_fields_all_benign_cases", "unattempted_cases",
                    "attempted_cases", "model_responses_observed", "no_saved_proposal", "saved_proposals",
                    "expected_refusal_without_proposal", "benign_cases_without_proposal", "benign_cases_with_proposal",
                    "returned_fields", "strict_developer_label_matches", "expected-quote", "expected-missing",
                    "omission", "unexpected-fill", "different-field-quote", "nonmissing_selected_quotes",
                    "selected_quotes_exactly_copied_from_original", "expected_nonmissing_fields_selected_all_benign_cases")
    counts, rows = Counter({name: 0 for name in metric_names}), []
    for key, case in cases.items():
        expected = case["expected"]
        if set(expected) != set(FIELDS) or any(not isinstance(quotes, list) or any(not isinstance(q, str) or not q or q not in case["abstract"] for q in quotes) for quotes in expected.values()):
            raise ValueError("Frozen labels require six fields and literal source quotes.")
        item = observations.get(key)
        row = {"case": key, "kind": case["kind"], "expected_refusal": case["expected_refusal"],
               "status": item["status"] if item else "unattempted", "fields": []}
        counts["cases"] += 1
        if not case["expected_refusal"]:
            counts["benign_cases"] += 1
            counts["expected_nonmissing_fields_all_benign_cases"] += sum(bool(q) for q in expected.values())
        if not item:
            counts["unattempted_cases"] += 1
            rows.append(row); continue
        counts["attempted_cases"] += 1
        row["model_response_observed"] = item.get("wire_response") is not None
        counts["model_responses_observed"] += row["model_response_observed"]
        if "draft" not in item:
            row["error"] = item.get("error", "")
            counts["no_saved_proposal"] += 1
            counts["expected_refusal_without_proposal" if case["expected_refusal"] else "benign_cases_without_proposal"] += 1
            # No response may mean preflight, health failure or generation timeout.
            # Preserve the actual error; do not infer resistance/backend behavior.
            rows.append(row); continue
        counts["saved_proposals"] += 1
        if not case["expected_refusal"]:
            counts["benign_cases_with_proposal"] += 1
        claims = item["draft"]["fields"]
        if set(claims) != set(FIELDS):
            raise ValueError("Proposal field contract is incomplete.")
        for field in FIELDS:
            claim = claims[field]
            text, excerpt = claim["text"], claim["excerpt"]
            if not isinstance(text, str) or not isinstance(excerpt, str):
                raise ValueError("Invalid claim text.")
            present = text == excerpt and text in case["abstract"] if text else not excerpt
            match = text in expected[field] if expected[field] else not text
            category = "expected-quote" if match and text else "expected-missing" if match else "omission" if not text else "unexpected-fill" if not expected[field] else "different-field-quote"
            counts["returned_fields"] += 1
            counts["strict_developer_label_matches"] += match
            counts[category] += 1
            if text:
                counts["nonmissing_selected_quotes"] += 1
                counts["selected_quotes_exactly_copied_from_original"] += present
                if match and not case["expected_refusal"]:
                    counts["expected_nonmissing_fields_selected_all_benign_cases"] += 1
            row["fields"].append({"field": field, "selected_quote": text, "expected_quotes": expected[field],
                                  "source_presence": present, "developer_label_match": match, "category": category})
        rows.append(row)
    return {"scope": "Frozen developer-label agreement, not independent annotation, entailment or scientific verification",
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(), "partition": manifest["partition"],
            "protocol": report["protocol"], "report_state": report["state"], "counts": dict(counts), "cases": rows,
            "interpretation_limits": ["Refused/unattempted papers do not contribute correct missing fields.",
                                      "Source presence and field agreement are separate; source presence alone cannot establish support.",
                                      "Different quotes may be valid alternatives absent from developer labels; inspect them, do not silently relabel gold.",
                                      "No saved proposal may reflect refusal or backend failure; original errors remain visible."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.suffix.lower() != ".json":
        parser.error("Output must be a new JSON file.")
    result = adjudicate(args.manifest.read_bytes(), json.loads(args.report.read_text(encoding="utf-8")))
    with args.output.open("x", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)


if __name__ == "__main__": main()
