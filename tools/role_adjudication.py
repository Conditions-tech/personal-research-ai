"""Offline v6 evidence audit and frozen-label counters; no semantic guarantee."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def adjudicate(manifest_bytes, report):
    from review.analysis import OPTIONS, evidence_context
    from review.role_analysis_v6 import VERSION, build, validate
    from review.workspace import SUMMARY_FIELDS, export_review, restore_review

    if report.get("protocol") != VERSION or report.get("manifest_sha256") != hashlib.sha256(manifest_bytes).hexdigest():
        raise ValueError("Pilot report does not match this protocol and frozen evidence.")
    manifest = json.loads(manifest_bytes)
    cases = {c["id"]: c for c in manifest["cases"]}
    if len(cases) != len(manifest["cases"]):
        raise ValueError("Duplicate case identity.")
    items = {}
    for item in report["cases"]:
        key = item["case"]["id"]
        if key not in cases or key in items or item["case"] != cases[key]:
            raise ValueError("Unknown, changed or duplicated pilot case.")
        items[key] = item
    counts = Counter({k: 0 for k in ("roles", "validated_roles", "failed_roles", "unattempted_roles",
                                    "expected_supported_roles", "supported_selections", "strict_gold_support",
                                    "predeclared_valid_alternative", "correct_missing", "omission",
                                    "fill_against_declared_missingness", "other_quote_needs_review",
                                    "nonmissing_quotes", "literal_original_quotes")})
    rows = []
    for key, case in cases.items():
        gold, alternatives = case["expected"], case["acceptable_alternate_quotes"]
        for labels in (gold, alternatives):
            if set(labels) != set(SUMMARY_FIELDS) or any(not isinstance(q, list) or any(not isinstance(s, str) or not s or s not in case["abstract"] for s in q) for q in labels.values()):
                raise ValueError("Labels must preserve literal source support for all roles.")
        item = items.get(key)
        if item:
            snapshot = restore_review(export_review(item["review_snapshot"]))
            record_key = item["context"]["record_key"]
            if item["context"] != evidence_context(snapshot, record_key) or item["context"]["record"]["abstract"] != case["abstract"] or any(role not in SUMMARY_FIELDS for role in item["roles"]):
                raise ValueError("Pilot evidence context or roles changed.")
        for role in SUMMARY_FIELDS:
            expected = bool(gold[role] or alternatives[role])
            counts["roles"] += 1
            counts["expected_supported_roles"] += expected
            result = item["roles"].get(role) if item else None
            row = {"case": key, "role": role, "strict_gold": gold[role], "acceptable_alternatives": alternatives[role]}
            if not result:
                counts["unattempted_roles"] += 1
                row["category"] = "unattempted"; rows.append(row); continue
            if "field" not in result:
                counts["failed_roles"] += 1
                row.update(category="refused-or-failed", error=result.get("error", "")); rows.append(row); continue
            if result["request"] != build(item["context"], role, OPTIONS) or result["field"] != validate(item["context"], role, result["generation"]["response"]):
                raise ValueError("Pilot request, response or normalized field changed.")
            quote = result["field"]["text"]
            counts["validated_roles"] += 1
            if quote:
                counts["nonmissing_quotes"] += 1
                counts["literal_original_quotes"] += quote == result["field"]["excerpt"] and quote in case["abstract"]
            if quote in gold[role]:
                category = "strict_gold_support"
            elif quote in alternatives[role]:
                category = "predeclared_valid_alternative"
            elif not quote:
                category = "omission" if expected else "correct_missing"
            else:
                category = "other_quote_needs_review" if expected else "fill_against_declared_missingness"
            counts[category] += 1
            counts["supported_selections"] += category in ("strict_gold_support", "predeclared_valid_alternative")
            row.update(category=category, selected_quote=quote)
            rows.append(row)
    return {"protocol": VERSION, "partition": manifest["partition"], "counts": dict(counts), "roles": rows,
            "limits": "Source/reconstruction checks and developer labels are not independent semantic/scientific validation. Other quotes need human review; missing/failed/unattempted roles never count as correct absence."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.suffix.lower() != ".json":
        parser.error("Output must be a new JSON file.")
    sys.path.insert(0, str(ROOT))
    score = adjudicate(args.manifest.read_bytes(), json.loads(args.report.read_text(encoding="utf-8")))
    with args.output.open("x", encoding="utf-8") as file:
        json.dump(score, file, ensure_ascii=False, indent=2)


if __name__ == "__main__": main()
