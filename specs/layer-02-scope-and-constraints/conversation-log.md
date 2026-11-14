# Layer 2 · Scope and Constraints — Conversation Log

Built from: Artifact 1. Owner: whole team (coordinator: Dhanush).
Focus: constraints before technology. Every technology named here records the assumption behind it.

## Conversation Log

| Questions | Agent | Conversation link | Decision reached | Open unknowns and owner | Artifact section |
|---|---|---|---|---|---|
| Q2.1 | C | (this session) | V1 serves **one engineering organization** (single tenant). No multi-tenant support. *(Confirmed.)* | None | 2.1, 2.6 |
| Q2.2 | C | (this session) | V1 supports **Python applications only**. | Which Python web framework the reference app uses — Dhanush, Layer 3 fixtures | 2.2 |
| Q2.3 | C | (this session) | V1 supports **both cloud and private infrastructure**. The platform never touches infrastructure directly; every revert and fix goes through the existing CI/CD pipeline (or a config-store version restore, review H1), so the environment type does not change the platform. **The demo runs on internal (private) infrastructure.** | Exact internal setup for the demo — Dhanush, Layer 6 | 2.1, 2.3 |
| Q2.4 | C | (this session) | Integrate with existing monitoring through **APIs and webhooks** (alert events pushed to the platform's listener) and **MCP servers** (agent pulls more information during the investigation). | Which monitoring tools are simulated for V1 — Dhanush, Layer 6 (technology selection) | 2.1, 2.5 |
| Q2.5 | C | (this session) | Platform needs **read access and integrations** to where logs and metrics are stored. Also **traces**: V1 supports distributed systems and microservices (language is Python only), so request journeys across services must be traceable. *(Confirmed:)* read-only credentials for telemetry; least privilege; the platform's own credentials kept in a secret store and never shown to the model (A1 E8). | Trace standard and tool — Dhanush, Layer 6. Secret store choice — Chirag, Layer 5 | 2.3, 2.7 |
| Q2.6 | C | (this session) | Keep a mapping **service → Git repository → CI/CD pipeline** to get deployment history and tie an incident to a deployment. Use MCP servers for Git and CI/CD to **read and to make changes**. Write tools are given to the agent, but **every write goes through checks and human approval**, enforced outside the agent. Revert = re-run the pipeline at the last known-good version, or restore the previous config version in the config store (review H1); fix = a commit on a branch + pull request, deployed by the pipeline after approval; no direct push to the main branch or to production. **Configuration changes are found by Git diff or by reading a config store** (both supported); secret values are never read (A1 E8). | Which config store — Dhanush, Layer 6. How MCP write tools are blocked until approval — Rinisha, Layer 11 | 2.3, 2.5, 2.7 |
| Q2.7 | C | (this session) | V1 uses **sanitized synthetic fixtures** only. No real incident data. | Fixtures must cover incidents A, B, C — Dhanush, Layer 3. Baseline comes from a timed manual run (A1 C1) — Irfan | 2.2, 2.6 |
| Q2.8 | C | (this session) | V1 has **no dashboard**. A **CLI and an HTTP API** are enough. | Where the 2 AM approval happens (chat action, API, CLI) — Rinisha, Layer 11 | 2.3, 2.6 |
| Q2.9 | C | (this session) | **No Kubernetes in V1.** The SRE platform is deployed with **Docker** only. Scale later when load needs it. | Trigger for moving to an orchestrator — Dhanush, Layer 13 | 2.3, 2.6 |
| Q2.10 | C | (this session) | **Modular monolith**, one repository, with clear module boundaries. Microservices would add deployment, monitoring and logging complexity that V1 does not need. A module can be deployed on its own later if its load needs it. | Module boundaries — Dhanush, Layer 6 | 2.3, 2.6 |
| Q2.11 | C | (this session) | **No custom model.** Not enough data or past behaviour to learn from. General models plus retrieval (RAG) are good enough. Revisit when we have enough learned incidents about our own systems. | Trigger to revisit — Irfan, Layer 10 | 2.5, 2.6 |
| Q2.12 | C | (this session) | **Hard constraint: incident data must not go to a new external party (e.g. an external model API); organization-approved hosted tools are allowed (review H3).** So V1 runs models **inside our own infrastructure on our own GPUs** (self-hosted open-weight models). No external model API. Keep the GPU footprint small for V1 (sized to the bounded per-incident loop). Small models (decision gate, embeddings) run on CPU. Claude first advised buying a hosted API; the data rule overrides that. | GPU sizing and which open-weight models (main agent + a different reviewer model, A1) — Irfan, Layer 10. Closed by review H3 (hosted tools allowed) | 2.4, 2.5, 2.7 |
| Q2.13 | C | (this session) | **Multi-tenancy is a non-goal.** It would add: tenant isolation and full data isolation, access control per tenant, more workload and model cost, rate limits, noisy-neighbour problems, queueing, and priority service for premium users. | None | 2.6 |
| Q2.14 | C | (this session) | The **agent has no access to the production environment** and holds no production credentials. Production changes happen only through the CI/CD pipeline after human approval. *(Confirmed:)* the disposable environment is a set of Docker containers built per incident from the same image and config, loaded with synthetic fixtures, with no network route and no credentials to production, destroyed when the incident closes. | Sandbox design — Rinisha, Layer 11 (sandbox architecture) | 2.3 |
| Q2.15 | C | (this session) | Infrastructure is bounded by **fixed, existing hardware**: V1 uses GPUs the organization already has. No new infrastructure spend for V1. | None (assumed reserved: L2-A12) | 2.4 |
| Q2.16 | C | (this session) | The per-incident model budget is **set by experiment**: run the synthetic incident fixtures, measure what the agent actually uses (model calls, tokens, GPU time), then set the cap at that baseline **plus a buffer**. *(Confirmed:)* a provisional hard cap applies during the experiments, so a runaway loop cannot take the GPUs. | Buffer size and provisional cap — Irfan, Layer 10 (inference budgets) | 2.4 |
| Q2.17 | C | (this session) | **3 concurrent incidents** to start; the number is **configurable**; extra incidents are **queued**. *(Confirmed:)* the queue is ordered by severity, then by arrival time. | Queue order — Dhanush, Layer 8 | 2.4 |
| Q2.18 | C | (this session) | An **investigation may run 15–20 minutes** (set to 20 minutes by review M7). Human approval waits, sandbox testing and applying a fix take longer and are **not counted** in this limit. *(Confirmed:)* **two limits** — a shorter phase 1 limit (time to propose the revert, because recovery comes first; provisional start 5 minutes) and the 15–20 minute investigation limit. | Phase 1 value; limit for the fix phase (sandbox test time) — Dhanush, Layer 8; set from the Q2.16 experiments | 2.4 |
| Q2.19 | C | (this session) | All models run on **our own infrastructure**, set up for **high availability**. **No CPU fallback.** If our inference service is down (main or reviewer model), the platform **does not process the incident: it halts and escalates** to a human with the alert and any evidence already collected. Escalation is plain system logic and does not need a model. Data never goes to an outside provider. | HA design for model servers — Irfan, Layer 10 | 2.5 |
| Q2.20 | C | (this session) | **Architecture assumptions are validated by humans only**, never by the AI, because the decision is critical. *(Confirmed:)* every item in Artifact 2 has one label — **Fixed requirement** (with its source, e.g. "no incident data to a new external party"), **Decision** (with rationale), or **Assumption** (provisional, with owner and validation condition). | None | 2.7 |
| Q2.21 | C | (this session) | Team chose PostgreSQL from a literature review: industry standard, proven at large volume, supports many data types. *(Confirmed — separating the two:)* **Decision** "use PostgreSQL" (rationale: industry standard, proven at large volume, supports many data types — from a literature review) **depends on** **Assumption** "V1 data volume fits one PostgreSQL instance" (owner, validated by measuring data per incident in the Q2.16 experiments). If the assumption fails, the decision is reopened; the decision record links to the assumption. | Data volume per incident — Dhanush, Layer 7 | 2.7 |
| Q2.22 | C | (this session) | Team view: no assumption forces an architecture change, because the model endpoint is configurable (own inference or a cloud API by config). *(Confirmed after Claude challenge:)* a cloud API is **not** a config option while the data rule holds. Architecture-breaking assumptions are: the data rule; self-hosted models good enough for multi-step tool use (L2-A8); GPU capacity (L2-A10); pipeline can redeploy an earlier version (L2-A2); sandbox can reproduce the problem (B1); MCP servers exist (L2-A4); an approver is reachable at 2 AM. **Decision:** all model access goes through one model interface, so changing the model is a config change. | Each listed assumption keeps its owner | 2.5, 2.7 |
| Q2.23 | C | (this session) | Record decisions now in each layer's **conversation log** and in the artifact's decisions table. Move to **ADR files** (one file per decision) later. The format must follow the worksheet's conversation-log and artifact templates. Each record has: decision, rationale, label (Fixed requirement / Decision / Assumption), owner, status, validation condition, revisit trigger. | When ADRs start and where they live — team, Layer 13 (repository design) | 2.7 |

## Assumptions (all provisional)

| # | Assumption | Owner | Validate when |
|---|---|---|---|
| L2-A1 | Every Python service has one Git repository and one CI/CD pipeline that can be mapped | Dhanush | Layer 3 fixtures |
| L2-A2 | The CI/CD pipeline can redeploy an earlier version on request | Dhanush | Layer 6 |
| L2-A3 | Monitoring tools can push alert events by webhook and expose data by API or MCP | Dhanush | Layer 6 |
| L2-A4 | MCP servers exist (or can be written) for the chosen monitoring, Git and CI/CD tools | Dhanush | Layer 9 (tool architecture) |
| L2-A6 | Services emit trace context so a request can be followed across services | Dhanush | Layer 3 (observability) |
| L2-A7 | The config store has an API or MCP server with read access to change history, keeps every version, and can restore a previous version | Dhanush | Layer 6 |
| L2-A8 | Open-weight models we can self-host are good enough for the agent and the reviewer (A1 requires a different model for review) | Irfan | Layer 10 |
| L2-A10 | Existing GPUs can hold 2 models × 2 copies (HA) and serve 3 concurrent incidents | Irfan | Q2.16 experiments |
| L2-A11 | 20 minutes is enough for a typical investigation | Dhanush | Q2.16 experiments |
| L2-A12 | The existing GPUs are reserved for the platform, not shared | Dhanush | Before V1 build (Layer 13) |
| L2-A13 | V1 data volume fits one PostgreSQL instance | Dhanush | Q2.16 experiments, Layer 7 |
| L2-A5 | Synthetic fixtures are realistic enough to evaluate diagnosis | Irfan | Layer 12 |

## Where Claude and ChatGPT disagreed
_Pending: ChatGPT pass not done yet (review finding H2)._


## Review fixes applied (2026-11-13 review, team approved)

| Finding | Decision |
|---|---|
| H1 | A revert is either redeploying the last known-good artifact or **restoring the previous config version in the config store**; same gate (review, checks, approval); undo = restore the newer version. L2-A7 extended: the config store keeps versions and can restore one. |
| H3 | **Team decision:** hosted tools that the organization already uses and approved (monitoring, Git, CI/CD, error tracker, chat) are supported; the platform reaches them through allow-listed inbound/outbound network rules; nothing else changes. The data rule means: incident data must not go to a **new** external party (e.g. an external model API). Open item closed. |
| M1 | A revert redeploys an artifact that already passed staging and QA, straight to production after approval. A permanent fix takes the normal path. |
| M2 | The platform opens the PR; the human approver reviews and merges it; the platform can never merge; branch protection needs one human review. |
| M7 | Provisional limits: phase 1 5 min, investigation 20 min, 30 tool calls, 10 GPU-minutes per incident. |
| M8 | L2-A10 counts 2 models × 2 HA copies; recovery work pre-empts fix-phase work. |
| L2, L3, L4, L5, L6 | Chat marked open in Fig 1; production access relabelled Decision; L2-A9 removed; owners = whoever works the validating layer (Chirag's items → Dhanush; L2-A2 and demo setup → Manish); missing open items added. |
| H2 | Acceptance check 4 un-ticked until the ChatGPT pass. |
