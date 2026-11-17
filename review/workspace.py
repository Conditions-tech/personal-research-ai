"""Phase C snapshots, reviewer notes and separate reviewed AI proposals."""

import copy
import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from uuid import uuid4


SUMMARY_FIELDS = ("objective", "method", "dataset", "results", "limitations", "conclusion")
DECISIONS = ("pending", "include", "exclude", "uncertain")
CLAIM_KINDS = ("missing", "paper-statement", "interpretation")
MAX_REVIEW_BYTES = 10 * 1024 * 1024
LIMITATIONS = [
    "Reviewer-authored notes and separate AI proposals; neither is independent scientific verification.",
    "Available evidence is metadata and abstracts, not full text.",
    "An exact excerpt match does not prove that the excerpt supports a claim.",
    "Provider conflicts and abstract field attribution may be unresolved after merging.",
    "Screening this bounded candidate set does not establish a systematic review or novelty.",
]


def _now():
    return datetime.now(timezone.utc).isoformat()


def _text(value, name, required=False):
    if not isinstance(value, str) or (required and not value.strip()):
        raise ValueError(f"{name} must be {'nonempty ' if required else ''}text.")
    return value.strip()


def _digest(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def create_review(run, question, inclusion, exclusion):
    """Capture an existing make_run result; never use the accumulated library instead."""
    protocol = {name: _text(value, name, required=True) for name, value in (
        ("question", question), ("inclusion", inclusion), ("exclusion", exclusion)
    )}
    snapshot = copy.deepcopy(run)
    manifest, records = snapshot["manifest"], snapshot["records"]
    if type(manifest.get("format_version")) is not int or manifest["format_version"] != 1:
        raise ValueError("A version-one discovery run is required.")
    for field in ("run_id", "query", "started_utc", "finished_utc"):
        _text(manifest[field], field, required=True)
    if manifest["status"] not in ("complete", "partial", "error") or not isinstance(manifest["settings"], dict):
        raise ValueError("Invalid discovery run context.")
    if not isinstance(manifest["coverage_limits"], list):
        raise ValueError("Coverage limitations must be a list.")
    for limit in manifest["coverage_limits"]:
        _text(limit, "Coverage limitation")
    if not records or manifest["counts"]["unique_in_run"] != len(records):
        raise ValueError("A review requires a nonempty, count-consistent discovery run.")
    keys = [r["record_key"] for r in records]
    if any(not isinstance(k, str) or not k.strip() for k in keys) or len(set(keys)) != len(keys):
        raise ValueError("Review record keys must be unique and nonempty.")
    for record in records:
        for field in ("title", "abstract", "doi", "authors", "url", "source"):
            _text(record.get(field, ""), field)
        if record.get("year") is not None and type(record["year"]) is not int:
            raise ValueError("Record years must be integers or missing.")
    for observation in manifest["provenance"]:
        for field in ("record_key", "provider"):
            _text(observation[field], field, required=True)
    provenance_keys = {p["record_key"] for p in manifest["provenance"]}
    if provenance_keys != set(keys):
        raise ValueError("Every candidate must have source provenance in this run.")
    stamp = _now()
    return {
        "format_version": 1, "review_id": uuid4().hex,
        "created_utc": stamp, "updated_utc": stamp,
        "protocol": protocol, "summary_fields": list(SUMMARY_FIELDS),
        "summary_rules": "User-approved default fields; distinguish statements, interpretations and missing information.",
        "run": snapshot, "run_sha256": _digest(snapshot),
        "limitations": list(LIMITATIONS),
        "papers": {key: {
            "decision": "pending", "reason": "", "screened_utc": None,
            "analysis": {field: {"kind": "missing", "text": "", "excerpt": "",
                                 "updated_utc": None} for field in SUMMARY_FIELDS},
        } for key in keys},
    }


def _record(review, key):
    _verify_snapshot(review)
    if key not in review["papers"]:
        raise ValueError("The paper is not part of this review.")
    return next(r for r in review["run"]["records"] if r["record_key"] == key)


def _verify_snapshot(review):
    if _digest(review["run"]) != review["run_sha256"]:
        raise ValueError("The captured discovery evidence has changed.")


def _screening(decision, reason):
    if decision not in DECISIONS:
        raise ValueError("Unknown screening decision.")
    return _text(reason, "Screening reason", required=decision != "pending")


def screen_paper(review, key, decision, reason):
    _record(review, key)
    reason = _screening(decision, reason)
    updated = copy.deepcopy(review)
    stamp = _now()
    updated["papers"][key].update(decision=decision, reason=reason, screened_utc=stamp)
    updated["updated_utc"] = stamp
    return updated


def annotate_paper(review, key, field, kind, text="", excerpt=""):
    record = _record(review, key)
    text, excerpt = _annotation(record, field, kind, text, excerpt)
    updated = copy.deepcopy(review)
    stamp = _now()
    updated["papers"][key]["analysis"][field] = {
        "kind": kind, "text": text, "excerpt": excerpt, "updated_utc": stamp,
    }
    updated["updated_utc"] = stamp
    return updated


def _annotation(record, field, kind, text, excerpt):
    if field not in SUMMARY_FIELDS or kind not in CLAIM_KINDS:
        raise ValueError("Unknown analysis field or claim kind.")
    text = _text(text, "Analysis text", required=kind != "missing")
    excerpt = _text(excerpt, "Evidence excerpt", required=kind != "missing")
    if kind == "missing" and (text or excerpt):
        raise ValueError("Missing information must not contain an analysis claim or excerpt.")
    if kind != "missing" and (not record.get("abstract", "").strip()
                              or excerpt not in record["abstract"]):
        raise ValueError("Use an exact excerpt from this paper's captured abstract.")
    return text, excerpt


def comparison_rows(review):
    """Human notes and explicitly accepted AI claims in distinct columns."""
    rows = []
    _verify_snapshot(review)
    _verify_ai(review)
    for record in review["run"]["records"]:
        key = record["record_key"]
        paper = review["papers"][key]
        row = {"review_id": review["review_id"], "run_id": review["run"]["manifest"]["run_id"],
               **{f: record.get(f) for f in ("record_key", "title", "authors", "year", "doi", "url", "source")},
               "evidence_depth": "abstract-based" if record.get("abstract", "").strip() else "metadata-only",
               "decision": paper["decision"], "reason": paper["reason"]}
        for field in SUMMARY_FIELDS:
            note = paper["analysis"][field]
            row[field] = note["text"] if note["kind"] != "missing" else "Not recorded in available evidence"
            row[field + "_kind"] = note["kind"]
            row[field + "_excerpt"] = note["excerpt"]
        drafts = paper.get("ai_drafts", [])
        accepted = next((d for d in reversed(drafts) if d["status"] == "accepted"), None)
        row["ai_latest_status"] = drafts[-1]["status"] if drafts else "none"
        row["ai_accepted_draft_id"] = accepted["draft_id"] if accepted else ""
        for name in ("model", "model_digest", "runtime_version", "prompt_version"):
            row["ai_" + name] = accepted["generation"][name] if accepted else ""
        row["ai_review_note"] = accepted["review_note"] if accepted else ""
        row["ai_reviewed_utc"] = accepted["reviewed_utc"] if accepted else ""
        for field in SUMMARY_FIELDS:
            for name in ("kind", "text", "excerpt"):
                row[f"ai_{field}_{name}"] = accepted["fields"][field][name] if accepted else ""
        rows.append(row)
    return rows


def _verify_ai(review):
    from .analysis import MAX_DRAFTS, validate_draft
    identifiers = set()
    found = False
    for key, paper in review["papers"].items():
        if "ai_drafts" not in paper:
            continue
        drafts = paper["ai_drafts"]
        if not isinstance(drafts, list) or not 1 <= len(drafts) <= MAX_DRAFTS:
            raise ValueError("Invalid AI proposal collection.")
        found = True
        for draft in drafts:
            validate_draft(review, key, draft)
            if draft["draft_id"] in identifiers:
                raise ValueError("Duplicate AI proposal identifier.")
            identifiers.add(draft["draft_id"])
    if type(review["format_version"]) is not int or review["format_version"] != (2 if found else 1):
        raise ValueError("Review version does not match its AI proposal content.")


def export_review(review):
    comparison_rows(review)  # Verify the captured evidence before exporting.
    return json.dumps(review, ensure_ascii=False, indent=2, allow_nan=False).encode("utf-8")


def restore_review(data):
    """Validate a downloaded workspace; uploaded text is data, never model instructions."""
    if not isinstance(data, bytes) or len(data) > MAX_REVIEW_BYTES:
        raise ValueError("Review JSON must be at most 10 MiB.")

    def unique_pairs(items):
        result = {}
        for name, value in items:
            if name in result:
                raise ValueError("Duplicate review JSON field.")
            result[name] = value
        return result

    def nonfinite(_):
        raise ValueError("Nonfinite review JSON value.")

    def timestamp(value, required=False):
        if value is None and not required:
            return
        if not isinstance(value, str) or datetime.fromisoformat(value).utcoffset() is None:
            raise ValueError("Review actions require timezone-aware timestamps.")

    try:
        saved = json.loads(data, object_pairs_hook=unique_pairs, parse_constant=nonfinite)
        if type(saved["format_version"]) is not int or saved["format_version"] not in (1, 2):
            raise ValueError("Unsupported review format.")
        protocol = saved["protocol"]
        restored = create_review(saved["run"], protocol["question"], protocol["inclusion"], protocol["exclusion"])
        if saved["run_sha256"] != restored["run_sha256"] or saved["summary_fields"] != list(SUMMARY_FIELDS):
            raise ValueError("Review evidence or summary format does not match.")
        if set(saved["papers"]) != set(restored["papers"]):
            raise ValueError("Review decisions do not match the captured candidates.")
        records = {r["record_key"]: r for r in restored["run"]["records"]}
        for key, paper in saved["papers"].items():
            reason = _screening(paper["decision"], paper["reason"])
            restored["papers"][key].update(decision=paper["decision"], reason=reason)
            if set(paper["analysis"]) != set(SUMMARY_FIELDS):
                raise ValueError("Analysis fields do not match the default format.")
            for field, note in paper["analysis"].items():
                text, excerpt = _annotation(records[key], field, note["kind"], note["text"], note["excerpt"])
                restored["papers"][key]["analysis"][field] = {
                    "kind": note["kind"], "text": text, "excerpt": excerpt, "updated_utc": note["updated_utc"],
                }
            restored["papers"][key]["screened_utc"] = paper["screened_utc"]
            if "ai_drafts" in paper:
                restored["papers"][key]["ai_drafts"] = copy.deepcopy(paper["ai_drafts"])
        restored["format_version"] = saved["format_version"]
        _verify_ai(restored)
        review_id = saved["review_id"]
        if not isinstance(review_id, str) or len(review_id) != 32 or any(c not in "0123456789abcdef" for c in review_id):
            raise ValueError("Invalid review identifier.")
        timestamp(saved["created_utc"], required=True)
        timestamp(saved["updated_utc"], required=True)
        for paper in restored["papers"].values():
            timestamp(paper["screened_utc"], required=paper["decision"] != "pending" or bool(paper["reason"]))
            for note in paper["analysis"].values():
                timestamp(note["updated_utc"], required=note["kind"] != "missing")
        restored.update(review_id=review_id, created_utc=saved["created_utc"], updated_utc=saved["updated_utc"])
        return restored
    except (KeyError, TypeError, AttributeError, StopIteration, OverflowError, RecursionError,
            UnicodeError, ValueError) as error:
        # Do not echo arbitrary uploaded research text through parser diagnostics.
        raise ValueError("Invalid review JSON. Use an unchanged exported workspace with supported evidence notes.") from error


def comparison_csv(review):
    rows = comparison_rows(review)
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8-sig")
