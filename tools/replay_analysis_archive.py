"""Offline saved-proposal compatibility audit; no inference or truth claim.

Complete original reviews use normal reopening validation. Other quote archives
permit context-only checks, not reconstruction of history or authentication.
"""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def replay_draft(draft, review=None):
    from review.analysis import MODEL, OPTIONS, strict_json, validate_draft
    from review.workspace import _digest

    context = draft["context"]
    key = context["record_key"]
    generation = draft["generation"]
    if type(draft["format_version"]) is not int:
        raise ValueError("Invalid archived proposal format.")
    row = {"draft_id": draft["draft_id"], "prompt_version": generation["prompt_version"],
           "format_version": draft["format_version"], "status": draft["status"]}
    if review is not None:
        validate_draft(review, key, draft)
        return {**row, "validation_level": "complete-review-reopening", "decision_validated": True}
    # Never manufacture a run whose hash cannot match the absent original.
    # Quote protocols can separately replay their self-contained context, but
    # this cannot verify the complete discovery run or review decision state.
    if generation["prompt_version"] == "abstract-analysis-v1" and draft["format_version"] == 1:
        return {**row, "validation_level": "unreplayed-no-complete-review", "decision_validated": False}
    from review import quote_analysis, quote_analysis_v3, quote_analysis_v4, quote_analysis_v5
    protocols = {module.VERSION: (index, module) for index, module in enumerate(
        (quote_analysis, quote_analysis_v3, quote_analysis_v4, quote_analysis_v5), 2)}
    version = generation["prompt_version"]
    if not isinstance(version, str) or version not in protocols or draft["format_version"] != protocols[version][0]:
        raise ValueError("Unsupported or mismatched archived protocol.")
    body = copy.deepcopy(context); claimed = body.pop("evidence_sha256")
    if _digest(body) != claimed or generation["backend"] != "ollama-local" or generation["model"] != MODEL or generation["endpoint"] != "http://127.0.0.1:11434":
        raise ValueError("Archived context or model binding changed.")
    module = protocols[version][1]
    if generation["request"] != module.build(context, OPTIONS) or draft["fields"] != module.validate(context, strict_json(generation["response"])) or generation["response_sha256"] != _digest(generation["response"]):
        raise ValueError("Archived request, response or fields changed.")
    return {**row, "validation_level": "context-protocol-only", "decision_validated": False}


def find_drafts(value):
    if isinstance(value, dict):
        if {"draft_id", "context", "generation", "fields", "format_version"}.issubset(value):
            yield value
        else:
            for child in value.values():
                yield from find_drafts(child)
    elif isinstance(value, list):
        for child in value:
            yield from find_drafts(child)


def audit(paths):
    from review.workspace import restore_review
    results = []
    for path in paths:
        if path.suffix.lower() != ".json":
            raise ValueError("Audit inputs must be explicit JSON archives.")
        original = path.read_bytes()
        value = json.loads(original)
        complete = restore_review(original) if isinstance(value, dict) and {"run", "run_sha256", "review_id", "papers"}.issubset(value) else None
        drafts = list(find_drafts(value))
        rows = [replay_draft(draft, complete) for draft in drafts]
        if path.read_bytes() != original:
            raise ValueError("An audit input changed while it was read.")
        results.append({"path": str(path), "sha256": hashlib.sha256(original).hexdigest(),
                        "draft_count": len(rows), "drafts": rows})
    all_rows = [row for result in results for row in result["drafts"]]
    levels = {level: sum(row["validation_level"] == level for row in all_rows) for level in
              ("complete-review-reopening", "context-protocol-only", "unreplayed-no-complete-review")}
    return {"kind": "saved-analysis-compatibility-audit-v1", "archives": results,
            "drafts_observed": len(all_rows), "validation_levels": levels,
            "drafts_replayed": len(all_rows) - levels["unreplayed-no-complete-review"],
            "scope": "Complete reviews use normal snapshot/decision validation. Draft-only archives have context-protocol checks only; raw v1 without its complete review is explicitly unreplayed. No inference, scientific verification, authentication or reconstruction of absent history."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.suffix.lower() != ".json":
        parser.error("Output must be a new JSON file.")
    sys.path.insert(0, str(ROOT))
    result = audit(args.reports)
    with args.output.open("x", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)


if __name__ == "__main__": main()
