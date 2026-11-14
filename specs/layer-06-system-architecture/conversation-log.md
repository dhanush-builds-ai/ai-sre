# Layer 6 · System Architecture — Conversation Log

Built from: Artifacts 4 and 5. Owner: Dhanush (from Manish).
Focus: derive the architecture from responsibilities. Parts A and B must be complete before any technology is named in Part C.

> Artifact 5 (Threat Model, Chirag) is done (pulled 2026-11-14). Check 6.7 trust boundaries, Q6.37 and Q6.39 against it.

## Conversation Log

| Questions | Agent | Conversation link | Decision reached | Open unknowns and owner | Artifact section |
|---|---|---|---|---|---|
| Q6.1 | C | (this session) | The API never runs the investigation. It accepts the incident, saves it, puts it on a queue, and answers at once with "accepted" and the incident ID. Workers pull from the queue and run the life cycle. **Saving the record and queueing it are one atomic step** *(confirmed)*, so a crash cannot leave a saved incident that nobody works on, or queued work with no record. | How the atomic save + queue is built — Dhanush, Part C (Q6.26) | 6.2 Container/process |
| Q6.2 | C | (this session) | **Sync (inside the request, p95 ≤ 30 s, A4 Q4.19):** authenticate and authorize the caller *(new, accepted)*, validate the fields, group or remove duplicates, other basic checks, save, queue, reply. **Async (worker):** the whole flow from A1 1.3: evidence, diagnosis, review, revert proposal, approval wait, apply, verify, fix phase. | Who may submit (webhook sender and API caller identity) — Chirag, Layer 5; is the owner notification sync or async — Dhanush, Layer 8 | 6.2, 6.3 |
| Q6.3 | C | (this session) | The API process only takes requests. Workers do the work, split into modules (evidence collection, inference calls, diagnosis, review, sandbox runs, verification). **A separate executor** (A5 name; review R9) is the only part that calls the CI/CD pipeline or the config-store restore; it holds no model access *(accepted from draft)*. | Whether the executor is its own process or a worker module with its own credentials — Dhanush, Part B (Q6.19) | 6.3 Component |
| Q6.4 | C | (this session) | The worker owns: pulling from the queue, the concurrency limit (3, configurable, A2), running steps with a checkpoint after each step, recovery work before fix work, time and cost limits, and resuming after a crash. | Durable workflow design — Dhanush, Layer 8 | 6.3 |
| Q6.5 | C | (this session) | One service per module is overkill: network failures between modules, a deploy and monitor job for each, transactions across services, version drift, and more work for a small team (matches A2 Q2.10). **A module becomes its own deployable only on evidence:** it needs to scale differently, it uses much more memory, or it stalls or harms other parts. Or it needs its own security boundary *(confirmed)*. | Measurement that would trigger a split — Dhanush, Layer 12 | 6.8 Alternatives |
| Q6.6 | C | (this session) | Packages with fixed boundaries (intake, incidents, evidence, diagnosis, review, sandbox, approval, execution, verification). Modules talk only through public interfaces. An automated check enforces the import rules. | Import-check tool — Dhanush, Part C | 6.3 |
| Q6.7 | C | (this session) | Modular monolith (A2 Q2.10): ships fast and keeps clear module boundaries. | None | 6.5 ADR |
| Q6.8 | C | (this session) | One repository, one image, separate entry points (**API, worker, executor**), each in its own container. Shared domain and database modules; one set of migrations; one release. **Containers do not call each other directly; they share work through the database and the queue** *(confirmed)*. This is still a modular monolith with several process types, **not microservices** *(confirmed: separate processes deployed as independent containers in the same system)*. | None | 6.2, 6.5 ADR |
| Q6.9 | C | (this session) | **Intake** (API process): authenticate the caller, validate fields, group duplicates, save and queue in one step, reply. | None | 6.3 Component |
| Q6.10 | C | (this session) | **Incident store:** owns incidents, hypotheses, decisions and approvals; the only module that writes those tables. | Data model — Dhanush, Layer 7 | 6.3 |
| Q6.11 | C | (this session) | **Workflow orchestrator** (worker): checkpoint after each step, resume from the last completed step, concurrency, priority and time limits. | Durable workflow design — Dhanush, Layer 8 | 6.3 |
| Q6.12 | C | (this session) | **Inference gateway:** the only way to a model. Owns the token and GPU budget, timeout plus retry, malformed-output retries, and halt-and-escalate when inference is down. V1 runs the two **self-hosted** models (diagnosis model and a different reviewer model). **New (team):** the gateway also supports **cloud model providers by configuration only**: enable or disable, endpoint, API key, model names. **Off by default.** No code change to switch. Adapters: an **OpenAI-compatible** adapter and an **Anthropic** adapter. **Rules (confirmed):** only a platform admin enables a provider through a reviewed config change, audited, which counts as organization approval; API key in the secret store (config holds the name only, A5 SC-23); provider host added to the egress allow list (SC-08); redaction before every model call (SC-09); **no automatic fallback** to a cloud provider (A2 halt-and-escalate stays); the platform refuses to start if the critic model equals the diagnosis model (A1). Revises A2 — see Conflicts. | Model choice and GPU sizing — Irfan, Layer 10 | 6.3, 6.4, 6.5 ADR, 6.7 |
| Q6.13 | C | (this session) | **Knowledge retriever:** searches runbooks and past incidents; returns passages with their source. | Retrieval method — Irfan, Layer 10 | 6.3 |
| Q6.14 | C | (this session) | **Evidence collector:** one adapter per source, parallel queries, timeout per source, failed source marked "missing", redaction before storage (A5 SC-09), provenance entry per item. | Per-source timeout — Dhanush, Layer 7 | 6.3 |
| Q6.15 | C | (this session) | **Diagnoser:** fixed rules first, then model reasoning with the rubric; ranked hypotheses linked to evidence, or "inconclusive". | Rubric — Dhanush, Layer 9 | 6.3 |
| Q6.16 | C | (this session) | **Critic:** a different model, fresh context, sees only evidence and claim. Its verdict is a signal, never an authorization (A5 Q5.12). | None | 6.3 |
| Q6.17 | C | (this session) | **Sandbox runner:** fresh hardened sandbox per incident (A5 SC-17), no production network, dummy credentials; returns only a test report. | Sandbox design — Rinisha, Layer 11 | 6.3, 6.7 |
| Q6.18 | C | (this session) | **Approval gate** (A5 name): approver rights, timeouts, backup approver, silence is never approval, M11 rule, signed approval bound to the action hash (A5 SC-04, SC-14). | Approval channel — Rinisha, Layer 11 | 6.3, 6.7 |
| Q6.19 | C | (this session) | **Executor** (A5 name): its own process; the only component with write credentials; acts only on a valid signed approval, through the pipeline or the config-store restore (A5 SC-15, SC-16). | Executor design — Rinisha, Layer 11 | 6.2, 6.3, 6.7 |
| Q6.20 | C | (this session) | **Verifier:** reads the alert's signals directly, compares to the pre-incident baseline in plain code; never reuses the diagnoser's conclusions (A5 SC-18). | Watch period — Rinisha, Layer 11 | 6.3 |
| Q6.21 | C | (this session) | **Artifact store** (file or object storage) for large logs, diffs and test outputs. The database keeps a pointer and a hash. Content is redacted before storage. | Product — Dhanush, Part C | 6.3, 6.4 |
| Q6.22 | C | (this session) | **Platform telemetry:** metrics, logs and traces for every component, exposed so humans can watch the AI SRE itself. | Signals and alerts — Dhanush, Layer 12-A | 6.3 |
| Q6.9–Q6.22 (gaps) | C | (this session) | **Four more components (team accepted):** **Audit (provenance) log** — append-only, hash-chained, write-once module (A1 1.3, FR-15, A5 SC-19). **Policy gate** — fixed rules for escalate/continue and patch policy checks (A1 decision policies, A5 SC-13). **Notifier** — pages and escalates humans; must work when the database is down (A4 NFR-03). **Ownership directory** — service → owner, on-call, repository, pipeline, dependencies (A2 Q2.6, A5 SC-03, SC-05). | Notifier path without the database — Dhanush, Part C | 6.3 |
| Q6.23 | C | (this session) | **FastAPI** for the HTTP API, **Pydantic** for validation. CLI with **Typer**, a thin client over the same API (no second code path). | None | 6.4, 6.5 ADR |
| Q6.24 | C | (this session) | **PostgreSQL** (fixed, A2 Q2.21) with **SQLAlchemy** as the ORM. | None | 6.4, 6.5 ADR |
| Q6.25 | C | (this session) | **Alembic** migrations, each in a reviewed PR. Expand first, contract later (backward-compatible), because API and worker containers can briefly run different versions. | None | 6.4, 6.5 ADR |
| Q6.27 | C | (this session) | V1: **self-hosted models behind an OpenAI-compatible inference server** (for example vLLM). **Anthropic adapter** present, off by default (Q6.12). Candidate "Claude and Tinker" **replaced**: Tinker is a fine-tuning service, and A2 excludes custom or fine-tuned models in V1. | Model names, server choice — Irfan, Layer 10 | 6.4, 6.5 ADR |
| Q6.28 | C | (this session) | An internal request/response schema plus **two thin adapters** on the official `openai` and `anthropic` SDKs. No large multi-provider library: too much dependency for two adapters. | None | 6.4, 6.5 ADR |
| Q6.29 | C | (this session) | **BM25** keyword retrieval first, in PostgreSQL full-text search or in the process (no new service). | Final method — Irfan, Layer 10 | 6.4 |
| Q6.30 | C | (this session) | **Hardened Docker container** per incident (A5 SC-17). gVisor is the upgrade option. | Runtime choice — Rinisha, Layer 11 | 6.4, 6.7 |
| Q6.31 | C | (this session) | **OpenTelemetry** instrumentation, **Prometheus** metrics, **Grafana** for the platform's operators only (A2 "no dashboard" is about the product UI and still holds). | Signals and alerts — Dhanush, Layer 12-A | 6.4 |
| Q6.32 | C | (this session) | **Docker Compose**: API, worker, executor, PostgreSQL, Temporal, a fake model server, telemetry. Dependencies with **uv**. | None | 6.4 |
| Q6.33 | C | (this session) | **Avoid in V1:** Kubernetes, Kafka, Redis, Celery/RQ, a separate vector database, a service mesh, splitting into services. Add one only with evidence: a measured bottleneck, a scale limit, or a security boundary (Q6.5). | None | 6.8 Alternatives |
| Q6.23–Q6.33 (extras) | C | (this session) | **Artifact store:** a filesystem Docker volume in V1 (object storage later if needed). **Secret store:** HashiCorp Vault, or the organization's existing store (L5-A2). **Single sign-on:** the organization's OIDC provider (L5-A1). **Notifier:** posts directly to the chat or pager webhook, so it works when the database is down (NFR-03). | L5-A1, L5-A2, L5-A7 validation — Dhanush | 6.4 |
| Q6.26 | C | (this session) | **Temporal** (team choice) runs the incident workflows: durable steps, timers (approval timeouts up to 24 h), retries, cancellation, resume after a crash (A4 NFR-02, A5 SC-16). **No Celery or RQ** *(team asked; Claude advised against)*: Temporal already has durable task queues that its workers poll; a second queue would add a broker (for example Redis) and a second source of truth. **Waiting queue = the incident table in PostgreSQL:** intake saves the incident with status "queued" in one transaction (this is the atomic save + queue of Q6.1). An **admission loop** in the worker starts the next incident when fewer than the limit are running (3, configurable), ordered by severity then age, with **workflow ID = incident ID** so a duplicate start does nothing. Queue cap 20, overflow to humans (A4 NFR-07, QR-07). Temporal stores its own state in the same PostgreSQL server, in a separate database (no new database technology). *(confirmed)* | Recovery pre-empting fix-phase work inside Temporal — Dhanush, Layer 8 | 6.2, 6.4, 6.5 ADR |
| Q6.34 | C | (this session) | Three C4-style views: **context** (6.1), **containers/processes** (6.2), **components** (6.3). Each with a legend and a "how to read" line. | None | 6.1, 6.2, 6.3 |
| Q6.35 | C | (this session) | Container-diagram arrows are labelled with what flows and how (API → PostgreSQL "save incident, status queued, one transaction"; admission loop → Temporal "start workflow, ID = incident ID"; Temporal ↔ worker "poll task queue"). Plus a sequence diagram for fixture A intake → admission → first step. **The executor and the sandbox runner are Temporal workers on their own task queues ("executor", "sandbox")**, so the worker never calls them directly (keeps the Q6.8 rule; Claude draft in the artifact). | None | 6.2 |
| Q6.36 | C | (this session) | Every model call goes through the inference gateway, which fans out to the OpenAI-compatible adapter (self-hosted server on; cloud off) and the Anthropic adapter (off). Off paths drawn dashed with "config: disabled". | None | 6.3 |
| Q6.37 | C | (this session) | Sequence: sandbox runner → test report only → critic → policy gate → approval gate (human signs) → executor checks signature and hash → pipeline or config store. The sandbox has no path to the approval gate or the executor (A5 untrusted zone). | None | 6.7 |
| Q6.38 | C | (this session) | Deployment view: solid boxes = containers (deploy units), dashed boxes = modules (code packages). One image, different entry points; Docker Compose networks shown. **Four processes: API, worker, executor, sandbox runner** *(confirmed)*. The sandbox runner is the only container with Docker access, and has no route to production. | Docker access method (socket proxy or rootless) — Rinisha, Layer 11 | 6.2, 6.7 |
| Q6.39 | C | (this session) | Trust zones reused from A5 Figure 1 (trusted / untrusted / outside); credential holders marked with a key. The executor and the sandbox runner are separate containers because they are security boundaries (Q6.5 rule). | None | 6.7 |

## Assumptions (all provisional)

| # | Assumption | Owner | Validate when |
|---|---|---|---|
| L6-A1 | Temporal, with its state in PostgreSQL, runs reliably at V1 load (3 running incidents, queue of 20) on one host | Dhanush | Layer 8 (workflow fault tests) |
| L6-A2 | An OpenAI-compatible inference server can serve the chosen open-weight main and reviewer models | Irfan | Layer 10 (model choice) |
| L6-A3 | A filesystem volume is enough for the artifact store in V1 (size and retention) | Dhanush | Layer 7 (retention), Layer 12 (capacity) |

Inherited and now owned here: L5-A1 (SSO), L5-A2 (secret store), L5-A7 (webhook signing) — Dhanush.

## Candidate stack decisions (record as ADRs in 6.5)

| Responsibility | Candidate | Team decision |
|---|---|---|
| Backend API | FastAPI | Accept |
| Validation | Pydantic | Accept |
| Database | PostgreSQL | Accept |
| ORM | SQLAlchemy | Accept |
| Migrations | Alembic | Accept |
| Workflow engine | Temporal | Accept (waiting queue in PostgreSQL, Q6.26) |
| Model providers | Claude and Tinker | Replace: self-hosted models behind an OpenAI-compatible server; Anthropic adapter off by default |
| Retrieval | BM25 | Accept |
| Execution | Restricted sandbox | Accept: hardened Docker container |
| Metrics | Prometheus | Accept |
| Dashboard | Grafana | Accept (operators only) |
| Tracing | OpenTelemetry | Accept |
| Development environment | Docker Compose | Accept |
| Dependency management | uv | Accept |

## Conflicts with earlier artifacts (explicit decisions)

| Earlier artifact says | Layer 6 decides | Status |
|---|---|---|
| A2 2.7 / Q2.12: incident data must not go to a new external party (for example an external model API). AGENTS.md: self-hosted models only. | The inference gateway can use a cloud model provider (Anthropic or OpenAI-compatible) when enabled by configuration. Off by default. | **Explicit decision (team, 2026-11-14).** A2 2.1, 2.5 and log, A5 (AB-19, SC-24, ST-17) and AGENTS.md updated. V1 still runs self-hosted. |

## Where Claude and ChatGPT disagreed

ChatGPT pass pending (H2).
