"""Streamlit review UI; all changes stay in session memory or explicit downloads."""

import streamlit as st

from .analysis import MODEL, generate_analysis, review_analysis
from .local_backend import OllamaLocal
from .memory import require_memory
from .workspace import (
    CLAIM_KINDS, DECISIONS, MAX_REVIEW_BYTES, SUMMARY_FIELDS, annotate_paper, comparison_csv,
    comparison_rows, create_review, export_review, restore_review, screen_paper,
)


def render_review(latest_run):
    st.subheader("Literature review and paper analysis")
    st.caption("Phase C · Screening, reviewer notes and local AI proposals")
    st.warning("Review work is session-only. Download review JSON before closing or restarting the app.")
    st.info("Local AI proposals require a separately installed runtime/model and human review. Full-text analysis is not available.")
    review = st.session_state.get("review_workspace")
    if review is None:
        uploaded = st.file_uploader("Reopen a downloaded review JSON", type=["json"], max_upload_size=10)
        if uploaded is not None and st.button("Reopen review"):
            try:
                st.session_state["review_workspace"] = restore_review(uploaded.getvalue())
            except ValueError as error:
                st.error(str(error))
            else:
                st.rerun()
        if not latest_run or not latest_run["records"]:
            st.info("Run a literature search with results to start a review, or reopen a downloaded review JSON.")
            return
        st.write(f"Candidate run: {latest_run['manifest']['run_id']} — {latest_run['manifest']['query']}")
        with st.form("review_protocol"):
            question = st.text_area("Review question", value=latest_run["manifest"]["query"])
            inclusion = st.text_area("Inclusion criteria", help="Describe which studies are relevant to your question.")
            exclusion = st.text_area("Exclusion criteria", help="Describe grounds for excluding candidates.")
            start = st.form_submit_button("Start review")
        if start:
            try:
                st.session_state["review_workspace"] = create_review(latest_run, question, inclusion, exclusion)
            except ValueError as error:
                st.error(str(error))
            else:
                st.rerun()
        return

    manifest = review["run"]["manifest"]
    st.write(f"Review {review['review_id']} · Source run {manifest['run_id']}")
    st.write("**Review question:**", review["protocol"]["question"])
    st.write("**Inclusion criteria:**", review["protocol"]["inclusion"])
    st.write("**Exclusion criteria:**", review["protocol"]["exclusion"])
    st.caption(f"Search: {manifest['query']} · Captured {manifest['finished_utc']} · Retrieval status: {manifest['status']}")
    if manifest["status"] != "complete":
        st.warning("This discovery run was incomplete. Screening applies only to its retrieved candidates.")
    if latest_run and latest_run["manifest"]["run_id"] != manifest["run_id"]:
        st.info("A newer search is available. This review remains attached to its original captured run.")
    with st.expander("Search settings, coverage and review limitations"):
        st.json(manifest["settings"])
        for item in manifest["coverage_limits"] + review["limitations"]:
            st.write(item)

    records = {r["record_key"]: r for r in review["run"]["records"]}
    key = st.selectbox("Paper to review", list(records),
                       format_func=lambda k: f"{records[k]['title']} — {records[k].get('doi') or k}",
                       key="review_paper")
    record, paper = records[key], review["papers"][key]
    st.write("**Authors:**", record.get("authors") or "Not available")
    st.write("**DOI:**", record.get("doi") or "Not available")
    st.write("**Record key:**", key)
    st.caption("Evidence depth: " + ("abstract-based" if record.get("abstract", "").strip() else "metadata-only"))
    st.text(record.get("abstract") or "No abstract available. Content claims cannot be recorded for this paper.")
    with st.expander("Captured source observations"):
        st.json([p for p in manifest["provenance"] if p["record_key"] == key])

    # Paper-specific forms preserve selection identity and prevent notes crossing papers.
    with st.form(f"screen_{review['review_id']}_{key}"):
        decision = st.selectbox("Screening decision", DECISIONS, index=DECISIONS.index(paper["decision"]))
        reason = st.text_area("Screening reason", value=paper["reason"])
        save = st.form_submit_button("Save screening decision")
    if save:
        try:
            review = screen_paper(review, key, decision, reason)
        except ValueError as error:
            st.error(str(error))
        else:
            st.session_state["review_workspace"] = review
            st.success("Screening decision saved for this session.")

    st.write("**Reviewer-authored paper analysis — default summary format**")
    st.caption("An excerpt must match the captured abstract exactly. You must assess whether it supports your note.")
    field = st.selectbox("Analysis field", SUMMARY_FIELDS, key="review_field")
    note = review["papers"][key]["analysis"][field]
    with st.form(f"analysis_{review['review_id']}_{key}_{field}"):
        kind = st.selectbox("Claim kind", CLAIM_KINDS, index=CLAIM_KINDS.index(note["kind"]))
        text = st.text_area("Analysis note", value=note["text"])
        excerpt = st.text_area("Exact abstract excerpt", value=note["excerpt"])
        save_note = st.form_submit_button("Save evidence note", disabled=not record.get("abstract", "").strip())
    if save_note:
        try:
            review = annotate_paper(review, key, field, kind, text, excerpt)
        except ValueError as error:
            st.error(str(error))
        else:
            st.session_state["review_workspace"] = review
            st.success("Evidence note saved for this session.")

    review = render_ai_analysis(review, key, record)
    rows = comparison_rows(review)
    counts = {d: sum(r["decision"] == d for r in rows) for d in DECISIONS}
    st.caption("Screening: " + " · ".join(f"{d}: {n}" for d, n in counts.items()))
    st.dataframe(rows, hide_index=True, width="stretch")
    review_json = export_review(review)
    if len(review_json) > MAX_REVIEW_BYTES:
        st.warning("This JSON download preserves your work, but it exceeds the 10 MiB reopening limit and cannot be reopened in this app. Keep the backup; start a smaller review for reopening.")
    st.download_button("Download review JSON", data=review_json,
                       file_name=f"review_{review['review_id']}.json", mime="application/json")
    st.download_button("Download comparison CSV", data=comparison_csv(review),
                       file_name=f"review_comparison_{review['review_id']}.csv", mime="text/csv")


def render_ai_analysis(review, key, record):
    st.write("**AI-assisted abstract analysis — separate proposals**")
    st.caption("Uses only this captured abstract, never reviewer notes or other papers. No download or external model service is used.")
    st.caption("The default v3 selector uses conservative English field cues and may omit relevant prose. Broader experimental selectors have not passed field-quality checks. Missing means no quote selected, not proof of absent information. Flagged instruction-like sentences are withheld; unfamiliar attacks may pass. Original evidence remains available.")
    st.warning("Experimental analysis: public-abstract evaluation found wrong field assignments and unsupported fills. Exact excerpt matching only verifies text presence. It does not verify scientific support, correct interpretation, numbers in context or absence of hallucinations. Review every field and reject incorrect proposals.")
    st.caption(f"Local model: {MODEL} · CPU · 8,192-token context · up to 4,000 abstract characters, with a conservative UTF-8 byte budget. Long evidence is refused. Generation requires 4 GiB of available RAM.")
    if st.button("Check local analysis backend"):
        try:
            st.session_state["review_local_backend"] = OllamaLocal().inspect()
        except ValueError as error:
            st.session_state.pop("review_local_backend", None)
            st.error(str(error))
    ready = st.session_state.get("review_local_backend")
    if ready:
        st.caption(f"Local runtime {ready['runtime_version']} detected. Model identity is checked again before generation.")
    else:
        st.info("Backend readiness has not been established. See docs/LOCAL_MODEL_SETUP.md for local runtime details.")
    if st.button("Generate AI proposal", disabled=not ready or not record.get("abstract", "").strip()):
        try:
            require_memory()  # Generation loads the model; refuse before RAM is exhausted.
            with st.spinner("Analyzing this abstract locally…"):
                updated = generate_analysis(review, key, OllamaLocal())
        except ValueError as error:
            st.error(str(error))
        else:
            st.session_state["review_workspace"] = updated
            st.rerun()

    drafts = review["papers"][key].get("ai_drafts", [])
    if not drafts:
        st.caption("No AI proposal for this paper. Reviewer notes remain independent.")
        return review
    by_id = {d["draft_id"]: d for d in drafts}
    selected = st.selectbox("AI proposal to review", list(reversed(by_id)),
                            format_func=lambda i: f"{by_id[i]['created_utc']} · {by_id[i]['status']}",
                            key=f"ai_proposal_{review['review_id']}_{key}")
    draft = by_id[selected]
    st.caption(f"Proposal {selected} · {draft['status']} · Abstract-based, not full-text analysis")
    st.caption("Analysis version: " + draft["generation"]["prompt_version"])
    if draft["format_version"] in (3, 4, 5):
        from .quote_analysis_v3 import candidates
        withheld = candidates(draft["context"]["record"]["abstract"])[2]
        if withheld:
            st.warning(f"{len(withheld)} source sentence(s) withheld from model input and quote choices by the instruction heuristic. This proposal uses partial evidence. Inspect the complete original abstract; legitimate research may be flagged.")
    for field, claim in draft["fields"].items():
        st.write(f"**{field.capitalize()} · {claim['kind']}**")
        missing = "No quote selected; inspect the abstract for omitted evidence." if draft["format_version"] in (2, 3, 4, 5) else "Not stated in the available abstract."
        st.text(claim["text"] if claim["kind"] != "missing" else missing)
        if claim["excerpt"]:
            st.text("Exact supporting excerpt: " + claim["excerpt"])
    with st.expander("AI model, prompt and evidence details"):
        st.json(draft["generation"])
        st.json(draft["context"])
    if draft["status"] == "pending":
        with st.form(f"ai_review_{review['review_id']}_{key}_{selected}"):
            checked = st.checkbox("I checked every AI claim, claim kind and excerpt against this abstract")
            note = st.text_area("AI reviewer note")
            accept = st.form_submit_button("Accept AI proposal")
            reject = st.form_submit_button("Reject AI proposal")
        if accept or reject:
            try:
                if accept and not checked:
                    raise ValueError("Check every AI field and its support before accepting the proposal.")
                review = review_analysis(review, key, selected, "accepted" if accept else "rejected", note)
            except ValueError as error:
                st.error(str(error))
            else:
                st.session_state["review_workspace"] = review
                st.rerun()
    else:
        st.text("Reviewer decision: " + draft["review_note"])
    st.caption("Only explicitly accepted AI claims enter the comparison CSV, in ai_ columns. JSON retains all proposals and their decisions. Acceptance never replaces reviewer-authored notes.")
    return review
