# Qwen3 pilot — approved execution and original proposal

Current 2026-10-24 state: seven charged responses are fully reconciled, five frozen cases remain unattempted, and physical RAM below 5.5 GiB blocks further loading. The existing approval/budget is retained without a download, reset or retry. [Current report](C2_QWEN3_STATUS_2026-10-24.md).

## Approval and current execution — 2026-10-21

The human approved this exact download and bounded pilot. The additional model is downloaded and metadata checks passed; the original first 5.5 GiB loading gate blocked before inference (ledger then 0/12). The [live pilot](C2_QWEN3_LIVE_PILOT_2026-10-21.md) subsequently began after RAM qualified. [Current execution report](C2_QWEN3_PILOT_2026-10-21.md) records actual results. The original proposal below is retained as dated planning evidence; its pre-approval statements no longer describe installation status. No new approval is needed for the remaining exact pilot when resources qualify.

## Original proposal

The installed Qwen2.5 1.5B model now reaches ordinary public abstracts, but controlled v4/v5 trials still found wrong role assignments and unsupported fills. This does not prove that further prompting cannot help or that a larger model will solve the problem. A separate bounded comparison would test that hypothesis. **Nothing in this plan has been downloaded, installed, loaded or integrated.** Current fixed-model integration and saved v1–v5 requests remain unchanged.

## Concrete candidate

- Official Ollama tag: [`qwen3:4b-q4_K_M`](https://ollama.com/library/qwen3:4b-q4_K_M), listed as **4.02B, Q4_K_M, approximately 2.6 GB** on 2026-10-20. A tag may change; record the full model digest and exact returned byte size before inference.
- Licence: **Apache 2.0**, stated by both the [official Qwen model card](https://huggingface.co/Qwen/Qwen3-4B) and the Ollama tag. This matches the project's free/open-source preference. Model licences vary by size: [Qwen2.5's 3B tag](https://ollama.com/library/qwen2.5:3b-instruct-q4_K_M) instead carries the Qwen Research Licence.
- Use the existing Ollama CLI only. No Python package or runtime upgrade is planned. Actual compatibility of this exact tag with the installed runtime is **not yet verified**; if an upgrade is needed, stop and obtain separate approval.
- Request `think:false` only after confirming the installed backend/model supports that setting. [Official Ollama thinking controls](https://docs.ollama.com/capabilities/thinking) document discovery through `/api/show` and use of the `think` field. Do not treat hidden thinking text as scientific evidence.

## Memory estimate and safe pilot boundary

The [official architecture configuration](https://huggingface.co/Qwen/Qwen3-4B/raw/main/config.json) has 36 layers, 8 KV heads and head dimension 128. At a proposed **6,144-token context**, an FP16 KV-cache reference calculation is `2 × 36 × 8 × 128 × 6144 × 2 = 905,969,664 bytes` (0.844 GiB). Add approximately 2.4 GiB of weights and estimated 0.5–1 GiB of runtime/scratch overhead: roughly **3.8–4.3 GiB process working memory**, before other applications. These are planning estimates, not published minimum RAM requirements or measurements on this computer. Cache type, runtime buffers and shared mappings can change actual use.

For the documented 8 GB/i3-8100 CPU machine, propose **at least 5.5 GiB actually available before loading** the candidate, serial execution, CPU only, one loaded model and immediate unload. Do not reduce the current model's 4 GiB gate. If the proposed gate cannot be met, retain current work and stop the new load; never close user applications. Reserve at least 6 GB free disk for the new weights and transfer headroom, retaining the old model. CPU latency and scientific quality are unknown; no performance guarantee is made.

A new protocol/configuration must bind model name/digest, context/output settings, thinking policy and prompt. Never replace global legacy model/settings constants in a way that invalidates saved v1–v5 proposals. Keep the current 1.5B model installed. Preserve loopback, cloud-disabled, proxies/redirects/retries-off and temporary-data boundaries. Start with one public abstract; if compatible and resource-qualified, run at most 12 total pilot generations with a fresh ledger, fixed developer labels and untouched holdout. No production research enters the pilot. No default quality promotion until failures are reviewed.

## Exact new authorization needed

Approve downloading **one additional `qwen3:4b-q4_K_M` model (about 2.6 GB, Apache 2.0)** using the existing runtime, retaining the current model, plus a separately bounded **up-to-12-generation CPU/local-only pilot** with the proposed resource gate and versioned configuration. No paid/cloud service, runtime/package upgrade, production data/schema change, Git operation or automatic startup is included. A later bounded role-by-role experiment on the existing model is also possible without a new download, but the completed follow-up's 12-call ledger must not be reset or exceeded.
