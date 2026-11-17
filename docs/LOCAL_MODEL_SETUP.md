# Local analysis setup — approved execution and original proposal

## Current execution status — 2026-10-20

Follow-up: the user also approved software improvements on this same installed model. Active generation now uses `abstract-quotes-v2`, with unchanged runtime/digest/options. The [new evaluation](QUOTE_FIRST_C2_2026-10-20.md) improves selected-field fidelity but retains omissions/heuristic limitations. The setup history below records the original v1 quality failure; no repeat installation or additional download was performed.

The user explicitly approved this setup. Ollama 0.40.6 and the single specified Qwen model are now installed. The official standalone Windows CLI archive was used to avoid the desktop installer's GUI/updater; its checksum and executable signature were verified. Loopback/cloud-disabled configuration is applied, and six real synthetic generations plus temporary-app integration checks ran. **Technical integration works; model-quality acceptance failed.** Read the [execution/benchmark report](LOCAL_ANALYSIS_BENCHMARK_2026-10-20.md) before interpreting results. The original pre-install inspection/proposal below is retained as dated evidence; it no longer describes an absent backend.

The CLI daemon remains running locally with no loaded model after the benchmark. It has no automatic startup registration. After a reboot, start it explicitly in PowerShell if needed:

```powershell
$env:OLLAMA_HOST = '127.0.0.1:11434'
$env:OLLAMA_NO_CLOUD = '1'
$env:OLLAMA_NUM_PARALLEL = '1'
$env:OLLAMA_MAX_LOADED_MODELS = '1'
Start-Process -FilePath "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" -ArgumentList 'serve' -WindowStyle Hidden
```

Do not launch a second server if the endpoint is already available. The app uses the fixed HTTP endpoint and does not require a Python SDK or CLI PATH changes. Continue checking resources before experimental generation. More models, runtime upgrades and substantive analysis improvements are separate work; this approval does not authorize them automatically.

## Original pre-install proposal

Inspected 2026-10-20. No runtime was installed, no model was downloaded, no model inference was run, and no research content was sent to a model service. This is a concrete setup proposal, not verified working generation.

## Actual machine and environment

- Python 3.14.7, Streamlit 1.66.0, pandas 3.0.6, requests 2.34.2. No installed torch, transformers, llama-cpp-python, gpt4all, onnxruntime or ollama Python distribution was found.
- Windows 10 build 19045 and Intel i3-8100 were confirmed with read-only platform/registry checks. Physical RAM was 8,444,698,624 bytes (about 8 GB); available RAM was 1,716,330,496 bytes at the sampled moment. Availability changes over time. Integrated graphics/no NVIDIA remains inherited documentation: the CIM GPU query was denied.
- No ollama, llama-server, llama-cli, lms or lmstudio command/process was found. Common per-user Ollama/LM Studio installation/model paths were absent; loopback ports 11434, 1234 and 8080 were closed. This bounded inspection does not rule out arbitrary portable installations elsewhere. No private model/cache contents or research database records were inspected.

## Selected candidate and resource budget

Use a native Ollama CPU process, connected through the already-installed requests library. This avoids adding a Python inference stack to Python 3.14. The backend interface can later be replaced; the current adapter deliberately accepts only one selected, not yet benchmarked setup candidate. The official [API option definitions](https://github.com/ollama/ollama/blob/main/api/types.go) include num_gpu/num_thread/context controls; this adapter requests zero GPU layers and four CPU threads. No GPU acceleration is assumed.

| Component | Proposed selection | Official facts checked 2026-10-20 |
| --- | --- | --- |
| Runtime | Ollama Windows x64 v0.40.6, recheck before installing | Official [release assets](https://github.com/ollama/ollama/releases/expanded_assets/v0.40.6) list OllamaSetup.exe at about 1.48 GB; [runtime source licence](https://github.com/ollama/ollama/blob/main/LICENSE) is MIT. |
| Model | qwen2.5:1.5b-instruct-q4_K_M | [Official registry](https://ollama.com/library/qwen2.5:1.5b-instruct-q4_K_M): 986 MB, 1.54B parameters, Q4_K_M; [publisher card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) confirms Apache-2.0. This is an open-weight model; training-data openness has not been certified. |
| OS/storage | Existing Windows 10 build 19045; reserve at least 8 GB free disk for installer, runtime, weights and headroom | [Windows requirements](https://docs.ollama.com/windows): Windows 10 22H2 or newer and at least 4 GB for the binary installation, plus model storage. |
| Memory | CPU only, one paper/request, 8,192 context, 1,024 output tokens, four threads, unload after request | **Engineering estimate, not an official minimum or measurement:** budget roughly 2–3 GB additional resident RAM, with at least 4 GB available before benchmarking to leave application/OS headroom. Current available RAM is insufficient for that conservative gate. Larger models/concurrency are not proposed. |

Total proposed downloads are approximately 2.5 GB. Do not infer RAM from download size. There is no measured latency, peak-memory figure, scientific quality score or assurance that this small model will meet acceptance. If it fails, report that before choosing/downloading another model.

## Exact approval needed

Approve downloading and installing the specified official Ollama Windows runtime, downloading the single specified Qwen model, configuring local-only loopback operation, and running a small local benchmark on synthetic/public abstracts with temporary storage. No Python package installation, paid/cloud service, private research transfer, production database change or automatic upgrade is included.

Only after that approval:

1. Recheck release/asset sizes, free memory/disk, licence and installer authenticity/checksum against the official release; install the approved version in the user's account. The sampled official installer SHA-256 is `933794ee1d670137f5116c9de7fc7db092fa97c6b823aba848ddb8a7ea030828`; recheck against the actual version, never reuse it for a different release.
2. Set runtime configuration before starting it: `OLLAMA_HOST=127.0.0.1:11434`, `OLLAMA_NO_CLOUD=1`, `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1`. [Official FAQ](https://docs.ollama.com/faq) documents local-only/cloud disablement and restart requirements. Keep the service bound to loopback. Do not expose a network listener or enable cloud/web tools.
3. Download exactly `ollama pull qwen2.5:1.5b-instruct-q4_K_M`. Record the actual full model digest/version and installed runtime version. No sign-in, cloud alias or Python Ollama SDK is needed. The application never pulls or starts a model service itself.
4. Run a temporary-data benchmark outside the production app/database: an explicit method/result abstract, an abstract missing dataset/results, ambiguous/negative claims, wrong-paper fixtures, numerically changed claims and embedded instructions. Measure elapsed time and peak memory; inspect every nonmissing field against the original abstract. Require valid schema/identity/excerpts, correct missingness and no unsupported findings in this small adjudicated sample. Contract tests passing alone are not scientific acceptance.
5. Use the review tab's **Check local analysis backend**, then generate one proposal and verify human acceptance/rejection plus JSON reopening. Keep this check in an isolated app copy so normal discovery startup cannot touch production storage. Do not declare live integration verified if any step fails. Preserve failed benchmark evidence without private text in logs.

## API and operational limits

The adapter uses the documented [version](https://docs.ollama.com/api-reference/get-version), [model inventory](https://docs.ollama.com/api/tags), [model details](https://docs.ollama.com/api-reference/show-model-details) and [generation](https://docs.ollama.com/api/generate) endpoints. [Structured output schemas](https://docs.ollama.com/capabilities/structured-outputs) help formatting; the application still validates every response. These official API documents were reviewed, but compatibility has not been exercised against a running daemon.

The app fixes the loopback address/model name, refuses remote-model metadata and redirects, disables environment proxies, bounds responses to 32 KiB and performs no retries. Check requests use 2-second connect/3-second read timeouts; generation uses 2/120 seconds. Requests read timeouts are inactivity limits, not a hard total deadline; the local server may continue after client timeout. No cancellation/background queue is implemented. A self-reported model digest is traceability, not independent authentication of the local server or weights. Local runtime logs/downloads remain the user's private files.

The 4,000-character abstract limit, 6,000-character request-prompt limit and conservative UTF-8 byte/token budget refuse oversize evidence instead of trimming it. Prompt formatting reserves 400 tokens plus output capacity; this is not a measured tokenizer benchmark. Generation also rejects truncation/overflow signals. Unknown runtime/model template changes require revalidation. Since 2026-10-26 the app's Generate button refuses before any generation request when available physical RAM is below the same 4 GiB gate (`review/memory.py`); page-file space does not count and the gate is not relaxed. Multilingual/numerical/scientific performance remain acceptance work.
