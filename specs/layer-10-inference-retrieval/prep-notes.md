# Layer 10 prep notes (provisional — not a log, not an artifact)

Owner: Irfan. Layer 10 cannot start until A2 and A9 exist.

- Decision model candidate for the escalation gate (GLiNER2.5-Decide, runs on CPU): see [Layer 9 prep notes](../layer-09-agent-architecture/prep-notes.md). Layer 10 decides hosting, sizing and evaluation of it.
- Size the GPUs for 2 self-hosted models (agent + a different reviewer model) × 2 HA copies (Artifact 2, L2-A10).
- **2026-11-14 (Layer 6, Q6.12):** the inference gateway also supports cloud providers (Anthropic, OpenAI-compatible) by configuration only, off by default; no automatic fallback. Self-hosted servers that expose an OpenAI-compatible API use the same adapter. GPU sizing still assumes self-hosted.
