# Layer 10 · Pending items

Status of every open item of Layer 10 (updated 2026-11-17). Artifact 10 and the log are complete as a draft. The sections marked ☐ in the artifact close when the items below close. All starting values stay provisional until then (same as Artifacts 2 and 4).

Status values: **Needs decision** (a choice must be made), **Needs confirmation** (a fact must be confirmed), **Needs measurement** (a value comes from a test or benchmark), **To validate** (an assumption).

## A. Needs confirmation (earlier artifacts)

| # | Pending | Related | Status | Description |
|---|---|---|---|---|
| P1 | Mapping of gateway statuses to Artifact 7 results | Q10.14, Q10.17 to Q10.21; section 10.2 | Needs decision | Artifact 7, table `model_call`, column `result` has 3 values: `valid`, `malformed`, `timeout`. The gateway (10.2) has 6 statuses: `completed` (model finished), `length_limit` (model hit the token limit, output cut), `interrupted` (stream ended without a completion signal), `refused` (model refused the task, a normal result), `invalid_output` (JSON truncated or breaks the schema), `error` (call failed, for example server error or 401). Proposed mapping: completed → valid; invalid_output, length_limit, interrupted → malformed (cause in `parse_error`); refused → valid (content holds a refusal block). No A7 value fits `error`. Open choice: add `refused` and `error` to A7, or accept the mapping and store the exact gateway status in the raw output. |
| P2 | One model request at a time for each incident | Q10.31; section 10.6; L10-A11 | Needs confirmation | Artifact 9 (9.1): the coordinator calls the agents in a fixed order, and each model request is one Temporal activity. It does not say that an incident never sends two model requests at once. The per-incident limit in 10.6 and the number of requests in flight on the model server (3 active incidents) assume one. |
| P3 | Reproduction after 90 days | Q10.64; section 10.12; A7 L7-A3 | Needs decision | Artifact 7 keeps raw evidence content for 90 days and incidents and events for 1 year. After 90 days the evidence row and its hash stay, but the content is gone. Q10.64 asks for a reproduction months later. What stays: `model_call` (model name and version, prompt version, input hash, tokens), `tool_call`, evidence hashes, and index revisions (rebuilt from Git commit SHAs). What is lost: the raw evidence content, so a re-run with the same input is not possible. Open choice: accept this limit, or keep raw evidence longer. |

## B. Needs decision (team session)

| # | Pending | Related | Status | Description |
|---|---|---|---|---|
| P4 | Main and reviewer models, GPU sizing | Q10.1, Q10.24; section 10.1; L2-A8, L2-A10, L6-A2 | Needs decision | Not chosen. Constraints: open-weight with a license that allows our use; runs on the existing GPUs with 2 models × 2 HA copies and 3 concurrent incidents; the serving engine has a tool-call parser for the model; the critic model differs from the diagnoser and fixer models (A7, A9 9.2). Needs the GPU inventory (GPU type, count, memory, number of hosts). |
| P5 | High-availability design | Q10.6; section 10.1; A2 2.5 | Needs decision | A2 requires more than one copy of each model server. Options: two active copies on two hosts; active and standby; two copies on one host. Each copy must carry the full load of 3 incidents alone. Depends on the number of hosts. |
| P6 | Serving engine | Q10.8; section 10.1 | Needs decision | vLLM is the main candidate (OpenAI-compatible server, tool-call parsers, paged KV cache, continuous batching). SGLang, TensorRT-LLM, and TGI are other candidates. Chosen by a benchmark on fixtures A, B, and C. |
| P7 | CPU capacity and people to run GPU serving | L10-A3, L10-A9; Q10.4 | To validate | Assumption: the organization has people to run the serving software (related to L2-A9), and CPU capacity for an embedding model if it is added. |
| P8 | Synthetic runbook set | Q10.40; section 10.9; L10-A6 | Needs decision | A2 allows only synthetic fixtures. Runbooks come from the knowledge repository in Git (A7 `knowledge_document`). Which runbooks V1 uses, and who writes them, is not defined. |
| P9 | Emergency budget reserve | Q10.28; section 10.5; L10-A5 | Needs decision | A pool outside the incident budgets, for emergencies. Which cases qualify, and who approves, is not defined. |

## C. Needs measurement (benchmark or experiments)

| # | Pending | Related | Status | Description |
|---|---|---|---|---|
| P10 | Native tool calling and the reasoning field | Section 10.2; L9-A1 | Needs measurement | The main model must give valid JSON tool requests under a JSON schema. If not, the coordinator asks for one structured output for each step. A model without separate reasoning tokens may get an optional reasoning field (A9 9.1). Tested in the model benchmark (P4). |
| P11 | Prefill and decode rates of each model | Q10.29; section 10.5 | Needs measurement | The GPU-seconds estimate for a reservation = input tokens ÷ prefill rate + output tokens ÷ decode rate. Both rates come from the benchmark. |
| P12 | Final budget values and buffer | Q10.27, Q10.28; section 10.5; L4-A3 | Needs measurement | Starting values: 10 GPU-minutes, 30 tool calls, 30 model requests, 200k input and 64k output tokens, 32k context for each call (A2 2.4, A4 QR-06, A9 L9-A5). Final value = measured baseline × 1.5 (A4 QR-06). The provisional hard cap during experiments has no value yet. |
| P13 | Fix-phase time limit | Q10.32; section 10.7; A2 2.4 | Needs measurement | A2 leaves it unset. Phase 1 is 5 minutes, the investigation 20 minutes, the whole incident 60 minutes. |
| P14 | Share of the 32k tokens for each context part | Q10.57; section 10.11 | Needs measurement | The role contexts are defined (10.11). The token share of the baseline context, tool summaries, and records is not. |
| P15 | BM25 in the process, or PostgreSQL full-text search | Q10.50; section 10.9; A6 Q6.29 | Needs measurement | A6 allows both. PostgreSQL ranks in a different way from BM25. If used, the retrieval test (10.13) must show that it meets the targets. |
| P16 | Retrieval target values | Q10.51; section 10.13; L10-A8 | Needs measurement | A4 sets no retrieval target. Targets for Recall@10, Precision@10, and MRR are set after the first measurement on the labeled set. |
| P17 | Trigger to review a custom model | Q10.5; section 10.4 | Needs decision | A2 says to revisit the custom model when enough learned incidents exist. The number of incidents is not defined. |
| P18 | Detector for injected instructions | Section 10.11; A9 open item | Needs decision | The first detector is rules-based (known phrases and role markers). It only flags. A better method is open (Layer 12). |

## D. Assumptions to validate

| # | Pending | Related | Status | Description |
|---|---|---|---|---|
| P19 | L10-A4, A7, A8, A10 | Sections 10.4, 10.8, 10.9, 10.13 | To validate | The model server reports usage in every response, including streamed and failed ones (A4). BM25 alone misses few documents because of wording (A7). A labeled test set can be built from incidents A, B, and C (A8). Tinker weights can be downloaded and the license allows self-hosting, only if the custom model is revisited (A10). |

## E. Process

| # | Pending | Related | Status | Description |
|---|---|---|---|---|
| P20 | ChatGPT pass, team review, pull request merge | Acceptance checks 1, 4, 6 | Pending | The ChatGPT pass is not done (review finding H2). The team has not reviewed Artifact 10. The pull request is not merged. |
