"""Offline Qwen3 pilot reconstruction/counters, not scientific verification."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys


def audit(manifest_bytes, report, alternatives):
    from qwen3_pilot import build, DIGEST, MODEL, RUNTIME, VERSION
    from review.analysis import evidence_context, strict_json
    from review.quote_analysis_v5 import validate
    from review.workspace import export_review, restore_review, SUMMARY_FIELDS
    manifest = json.loads(manifest_bytes)
    if report.get("protocol") != VERSION or report.get("manifest_sha256") != hashlib.sha256(manifest_bytes).hexdigest():
        raise ValueError("Report differs from the frozen protocol/manifest.")
    cases = {c["id"]:c for c in manifest["cases"]}
    if len(cases) != len(manifest["cases"]):
        raise ValueError("Duplicate frozen case.")
    observed = {}
    for item in report["cases"]:
        key = item["case"]["id"]
        if key not in cases or key in observed or item["case"] != cases[key]:
            raise ValueError("Unknown, changed or duplicated observed case.")
        observed[key] = item
    names = ("cases", "attempted_cases", "unattempted_cases", "failed_or_refused_cases", "validated_cases",
             "expected_supported_fields_all_cases", "returned_fields", "supported_selected_fields",
             "strict_gold_support", "predeclared_alternative", "correct_missing", "omission", "false_fill",
             "other_quote_needs_review", "nonmissing_quotes", "literal_source_quotes", "injection_cases_checked")
    counts = Counter({k:0 for k in names}); rows=[]
    for key,case in cases.items():
        labels=case["expected"]
        extra=alternatives.get("acceptable_alternate_quotes",{}).get(key,{})
        if set(labels)!=set(SUMMARY_FIELDS) or set(extra)-set(SUMMARY_FIELDS):
            raise ValueError("Invalid field label scope.")
        for quotes in [*labels.values(),*extra.values()]:
            if not isinstance(quotes,list) or any(not isinstance(q,str) or not q or q not in case["abstract"] for q in quotes):
                raise ValueError("Labels must quote the original abstract.")
        counts["cases"]+=1;counts["expected_supported_fields_all_cases"]+=sum(bool(v) for v in labels.values())
        item=observed.get(key);row={"case":key,"status":item["status"] if item else "unattempted","fields":[]}
        rows.append(row)
        if not item:
            counts["unattempted_cases"]+=1;continue
        counts["attempted_cases"]+=1
        original=item["original_review"]
        if restore_review(export_review(original))!=original or evidence_context(original,next(iter(original["papers"])))!=item["context"]:
            raise ValueError("Original evidence snapshot/context changed.")
        record=item["context"]["record"]
        if len(original["papers"])!=1 or any(record.get(k)!=case.get(k) for k in ("title","authors","year","doi","abstract")) or record.get("url")!=case["source_url"]:
            raise ValueError("Snapshot is not this frozen paper.")
        if "request" in item and item["request"]!=build(item["context"]):
            raise ValueError("Model-specific request changed.")
        if "fields" not in item:
            counts["failed_or_refused_cases"]+=1;row["error"]=item.get("error","");continue
        generation=item["generation"]
        if any(generation.get(k)!=v for k,v in {"model":MODEL,"model_digest":DIGEST,"runtime_version":RUNTIME}.items()):
            raise ValueError("Generated model identity changed.")
        wire=generation.get("wire_response",{})
        if wire.get("response")!=generation["response"] or wire.get("model")!=MODEL or wire.get("done") is not True or wire.get("done_reason")!="stop" or wire.get("thinking"):
            raise ValueError("Raw generation differs from recorded successful response.")
        fields=validate(item["context"],strict_json(generation["response"]))
        if fields!=item["fields"]:
            raise ValueError("Normalized fields changed.")
        counts["validated_cases"]+=1
        if case.get("expected_withheld_minimum"):
            payload=json.loads(item["request"]["prompt"].split("\n",1)[1])
            if len(payload["withheld_sentence_ids"])<case["expected_withheld_minimum"]:
                raise ValueError("Expected instruction quarantine not applied.")
            if any(token in field["text"] for token in case.get("forbidden_generated_text",[]) for field in fields.values()):
                raise ValueError("Forbidden injected claim returned.")
            counts["injection_cases_checked"]+=1
        for name,field in fields.items():
            quote=field["text"];expected=bool(labels[name]);counts["returned_fields"]+=1
            if quote:
                counts["nonmissing_quotes"]+=1;counts["literal_source_quotes"]+=quote==field["excerpt"] and quote in case["abstract"]
            category=("strict_gold_support" if quote in labels[name] else "predeclared_alternative" if quote in extra.get(name,[]) else
                      "omission" if not quote and expected else "correct_missing" if not quote else
                      "false_fill" if not expected else "other_quote_needs_review")
            counts[category]+=1;counts["supported_selected_fields"]+=category in ("strict_gold_support","predeclared_alternative")
            row["fields"].append({"field":name,"quote":quote,"category":category})
    return {"protocol":report["protocol"],"partition":manifest["partition"],"counts":dict(counts),"cases":rows,
            "scope":"Exact reconstruction and frozen developer-label counters, not independent annotation, scientific verification or an app acceptance. Failed/unattempted cases never count as correct missing fields."}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("manifest","report","alternatives","output"):p.add_argument("--"+name,type=Path,required=True)
    args=p.parse_args()
    if args.output.exists() or args.output.suffix.lower()!=".json":p.error("A new JSON output is required.")
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    result=audit(args.manifest.read_bytes(),json.loads(args.report.read_text(encoding="utf-8")),json.loads(args.alternatives.read_text(encoding="utf-8")))
    with args.output.open("x",encoding="utf-8") as out:json.dump(result,out,ensure_ascii=False,indent=2)


if __name__=="__main__":main()
