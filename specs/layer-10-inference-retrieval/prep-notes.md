# Layer 10 prep notes (provisional — not a log, not an artifact)

Owner: Irfan. Layer 10 cannot start until A2 and A9 exist.

- Decision model candidate for the escalation gate (GLiNER2.5-Decide, runs on CPU): see [Layer 9 prep notes](../layer-09-agent-architecture/prep-notes.md). Layer 10 decides hosting, sizing and evaluation of it.
- Size the GPUs for 2 self-hosted models (agent + a different reviewer model) × 2 HA copies (Artifact 2, L2-A10).
- **2026-11-14 (Layer 6, Q6.12):** the inference gateway also supports cloud providers (Anthropic, OpenAI-compatible) by configuration only, off by default; no automatic fallback. Self-hosted servers that expose an OpenAI-compatible API use the same adapter. GPU sizing still assumes self-hosted.

## Model, GPU and HA options for the team session (Irfan, 2026-11-14)

Purpose: give the team one page to decide the open items of Artifact 10 (model choice, GPU sizing, serving engine, HA design, CPU models). Nothing here is decided. Sources for models are third-party guides and are **not verified**. Check every model card (size, license, tool calling) before use.

### 1. Inputs the team must give first

| Input | Why | Who knows |
|---|---|---|
| GPU inventory: model, count, memory for each GPU, number of hosts | Sets the largest model and the number of copies (L2-A9, L2-A12) | Dhanush, organization |
| NVIDIA or not | TensorRT-LLM needs NVIDIA. vLLM supports several makers | Organization |
| CPU cores and RAM on the hosts | Decision model and embedding model run on CPU (A2 2.5) | Organization |
| Are the GPUs reserved for the platform? | L2-A12 | Dhanush |
| Network between hosts | Needed for copies on different hosts | Organization |

### 2. Hard filters (from A2, A4, A6)

1. Open-weight, with a license that allows our use.
2. Runs on the existing GPUs: 2 models × 2 HA copies, 3 active incidents (L2-A10).
3. The serving engine offers an OpenAI-compatible server and a tool-call parser for the model (L6-A2). vLLM lists parsers for these families: Qwen (hermes, qwen3_xml), OpenAI gpt-oss, Llama 3 and 4, Mistral, DeepSeek, GLM-4.5 and 4.7, Kimi-K2, IBM Granite, and others ([vLLM tool calling](https://docs.vllm.ai/en/latest/features/tool_calling/)). A model without a parser is out.
4. Multi-step tool use and structured output work (L2-A8). The investigator and the fixer need native tool calling with a JSON schema (L9-A1). Test it. Do not trust a ranking.
5. The reviewer model differs from the main model (A2 2.5). Prefer two different families, so that the two models make different mistakes.

### 3. Shortlist to verify (reported by third-party guides, not verified)

| Family | Reported fit | Note |
|---|---|---|
| Qwen (a 27B to 35B class model) | General and tool use on a 24 to 32 GB GPU | Reported Apache 2.0. Check the version and license |
| OpenAI gpt-oss (20B) | Native function calling, 16 GB GPU | Has a vLLM parser |
| Llama (3.x, 4) | Reliable tool calling in some tests | Sources disagree on versions. Check the license terms |
| GLM, DeepSeek, Kimi | Strong on agent benchmarks | Often too large for a few GPUs. Check size first |
| Gemma, Mistral, Granite | Smaller options | Check the tool-call parser |

The sources disagree on version numbers and several look low quality. Use the list only to pick candidates for our own test (section 6).

### 4. GPU sizing method

**Weights only** (before the KV cache and overhead). Memory = parameters × bytes for each parameter.

| Model size | 16-bit (2 B) | 8-bit (1 B) | 4-bit (0.5 B) |
|---|---|---|---|
| 8B | 16 GB | 8 GB | 4 GB |
| 20B | 40 GB | 20 GB | 10 GB |
| 32B | 64 GB | 32 GB | 16 GB |
| 70B | 140 GB | 70 GB | 35 GB |

For a mixture-of-experts model, all expert weights must fit in memory. Only the active part counts for speed.

**KV cache.** Bytes for each token = 2 × layers × KV heads × head size × bytes for each value. Multiply by the tokens in flight (sequences × context length). Take the numbers from the model config.
Illustration only: 48 layers, 8 KV heads, head size 128, 16-bit gives about 0.2 MB for each token. A 32k context (A4 QR-06) then needs about 6.4 GB for one sequence. Three sequences need about 19 GB.

**Rule for HA.** If one copy fails, the other copy must carry the full load alone. So size each copy for 3 active incidents, not for 1.5.

**Worksheet to fill** after the GPU inventory:

| Item | Main model | Reviewer model |
|---|---|---|
| Model and precision | | |
| Weights (GB) | | |
| KV cache for 3 sequences at 32k (GB) | | |
| Overhead (about 10 to 20%, to measure) | | |
| Memory for one copy (GB) | | |
| Copies (2 for HA) | 2 | 2 |
| Total for 4 servers (GB) | | |
| Fits the inventory? | | |

### 5. HA design options

| Option | How it works | Good | Bad |
|---|---|---|---|
| A. Two active copies, on two hosts | The gateway sends calls to both. Health checks remove a failed copy | Survives a host failure. Uses both copies | Needs two hosts. Each copy must carry the full load |
| B. Active and standby | One copy serves. The standby takes over after a failure | Simple routing | The standby GPUs sit idle. A switch takes time |
| C. Two copies on one host | Two processes on different GPUs | Cheap | A host failure stops everything |

My suggestion: option A if the inventory has two hosts. Otherwise option C with the risk written down. If both copies of a model are down, the platform halts and escalates (A2 2.5). That needs no model.

### 6. Benchmark plan (choose the models and the engine)

1. Pick 2 or 3 candidates for the main model (investigator, diagnoser, fixer) and 2 for the reviewer model (critic), from different families.
2. Build a test set from the synthetic fixtures A, B, and C: one case set for each role (tool requests for the investigator and the fixer, typed outputs for the diagnoser and the critic), and 3 full runs. Test the optional reasoning field on a model without separate reasoning tokens (Artifact 9, 9.1).
3. Measure for each candidate: valid tool-call rate under a JSON schema, valid JSON rate, p50 and p95 latency (A4 QR-03 expects 5 to 30 s), the prefill rate and the decode rate (Artifact 10 uses them for the GPU-seconds estimate), GPU memory, and failures under 3 parallel incidents.
4. Run the same set on vLLM first. Compare a second engine only if vLLM fails a requirement.
5. Write the result in the capability matrix (10.1). This also gives the first numbers for the budget experiments (Q2.16).

### 7. CPU models

| Model | Facts | Note |
|---|---|---|
| Decision model: GLiNER2.5-Decide | **Not used in V1** (Artifact 9, 9.10). It stays a candidate. Facts: 340M parameters, Apache 2.0, runs on CPU. The vendor reports about 167 ms for one short request on a 48-vCPU server ([vendor page](https://fastino.ai/blog/gliner-2-5-decide-open-weight-decision-model)) | The vendor benchmark is internal (about 60% on unseen tasks). Use it as one gate signal only (Layer 9 notes). Validate on our fixtures |
| Embedding model | Needed only when BM25 misses documents because of wording (A6 ADR-09) | Choose later. It must run on CPU. Test on the retrieval test set (10.13) |

### 8. Decisions for the team session

| # | Decision | Needs |
|---|---|---|
| 1 | Candidate models for the benchmark | Section 2 and 3, and the inventory |
| 2 | HA option (A, B, or C) | Number of hosts |
| 3 | Serving engine: start with vLLM | Benchmark result |
| 4 | Hosting of the embedding model, if the team adds it | CPU inventory |
| 5 | Who runs the benchmark, and when | Team |
