# Layer 10 prep notes (provisional — not a log, not an artifact)

Owner: Irfan. Layer 10 started after A2 and A9 existed. Open items: [pending.md](pending.md).

- Decision model candidate for the escalation gate (GLiNER2.5-Decide, runs on CPU): see [Layer 9 prep notes](../layer-09-agent-architecture/prep-notes.md). **Update 2026-11-17:** A9 (9.10) says no decision model in V1. It stays a candidate.
- Size the GPUs for 2 self-hosted models (agent + a different reviewer model) × 2 HA copies (Artifact 2, L2-A10).
- **2026-11-14 (Layer 6, Q6.12):** the inference gateway also supports cloud providers (Anthropic, OpenAI-compatible) by configuration only, off by default; no automatic fallback. Self-hosted servers that expose an OpenAI-compatible API use the same adapter. GPU sizing still assumes self-hosted.

## Model and GPU sizing method (for the team session)

**Inputs needed:** GPU type, count, memory for each GPU, number of hosts, NVIDIA or not, CPU cores and RAM.

**Filters:** open-weight and a license that allows our use; a tool-call parser in the serving engine ([vLLM list](https://docs.vllm.ai/en/latest/features/tool_calling/)); valid JSON tool requests under a JSON schema (L9-A1); the critic model differs from the diagnoser and fixer models. Model lists in blogs are not verified. Test candidates on fixtures A, B, and C.

**Weights only** (bytes per parameter: 2 for 16-bit, 1 for 8-bit, 0.5 for 4-bit):

| Model size | 16-bit | 8-bit | 4-bit |
|---|---|---|---|
| 8B | 16 GB | 8 GB | 4 GB |
| 32B | 64 GB | 32 GB | 16 GB |
| 70B | 140 GB | 70 GB | 35 GB |

A mixture-of-experts model keeps all expert weights in memory. **KV cache** = 2 × layers × KV heads × head size × bytes per value, for each token in flight (numbers from the model config). Illustration: 48 layers, 8 KV heads, head size 128, 16-bit gives about 0.2 MB per token, so a 32k context needs about 6.4 GB, and 3 sequences about 19 GB.

**HA rule:** each copy must carry the full load of 3 incidents alone.

| HA option | Good | Bad |
|---|---|---|
| Two active copies on two hosts | Survives a host failure | Needs two hosts |
| Active and standby | Simple routing | Idle GPUs, switch time |
| Two copies on one host | Cheap | A host failure stops everything |

**Benchmark (decides models, engine, estimate rates):** per role (investigator, diagnoser, critic, fixer): valid tool-call rate, valid JSON rate, p50 and p95 latency (A4 QR-03 expects 5 to 30 s), prefill and decode rates, GPU memory, failures under 3 parallel incidents. Start with vLLM. Add a second engine only if vLLM fails a requirement.
