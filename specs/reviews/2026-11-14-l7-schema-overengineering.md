# Layer 7 schema review — over-engineering — 2026-11-14

Source: fresh-context subagent review of Artifact 7 (45 tables), the Layer 7 log, the gap fixes (F1–F9) and the feature-coverage report. A5 and A6 were read only to check which tables a security control or ADR needs.
For each item: tick **Approve**, or write your change under **Your change**.

**Status (2026-11-14): S1–S11 approved by Dhanush and applied to Artifact 7 and the Layer 7 log. The 7 under-specified items are also fixed in Artifact 7.2. ERD: `2026-11-14-l7-erd.html` (35 tables; also Figure 1 of Artifact 7).**

## Summary

The core of the schema is sound. The incident life-cycle tables, the immutable approval and execution records, the single `event` table and the "queued row is the outbox" design are already lean. The extra weight sits in four places. (1) Monthly partitioning of four tables for a load of about 3 incidents at a time; as written it also breaks the stated unique key and foreign keys. (2) A second delivery mechanism (`consumer_checkpoint` over the event table) that repeats what Temporal activities already do. (3) A generic stored-response `idempotency_key` table where one column and the existing unique rules do the job. (4) Small tables that are a column, an enum value or a JSONB key (`diagnosis_feedback`, `policy_check`, `sandbox_run`, `model_assignment`, `model_provider`, `service_owner`, `service_repository`, `environment`). No finding removes a security control, an audit rule or an approved feature (F1–F9); each one names the guarantee it keeps. **If every finding is approved: 45 → 35 tables, 0 partitioned tables, 1 delivery mechanism instead of 2.**

---

## Findings (most impact first)

### S1 — Drop monthly partitioning; delete expired rows instead
- **Where:** A7 7.2 "Retention" rule; `event`, `evidence`, `model_call`, `tool_call`; gap fix F9 (G18).
- **Problem:** V1 runs about 3 incidents at a time with tens of events each. That is thousands of rows a year, not millions. Partitioning exists only so retention can remove rows from immutable tables. It has a real cost. A partitioned table needs the partition column in every primary key and unique index. So `unique (stream_id, sequence)` and `id` as the only primary key cannot exist as written. Every foreign key to `evidence`, `tool_call` and `model_call` must also carry the partition column. A job must create partitions ahead of time. A month boundary also cuts an incident in two: dropping a month of `evidence` removes rows that `hypothesis_evidence` of a kept incident still points to.
- **Proposed change:** Plain tables. The retention job runs as the maintenance role and deletes whole incidents older than the limit, in foreign-key order, in one transaction. The `reject_change()` trigger allows `DELETE` only when `current_user` is the maintenance role. It still rejects every `UPDATE`. The job still writes `retention.purged` with the chain checkpoint. Add partitioning only when a delete run is measured as too slow (Layer 12).
- **Guarantee kept:** A5 SC-19: the platform role can only insert and select; no role can update. F9: retention removes data without breaking immutability, and the purge is in the audit record.
- **Effort saved:** Partition management job, composite keys with a partition column on 4 tables and on every table that references them, and a broken unique constraint.
- [x] Approve
- **Your change:**

### S2 — Drop `consumer_checkpoint` and the second outbox
- **Where:** A7 7.6 rules S5 and S6, 7.7 outbox table row 2, 7.8 "Event consumer" row; log Q7.43, Q7.49, Q7.57.
- **Problem:** The table serves four consumers: SSE, notifier, ticket updater, metrics. None needs it. The SSE client keeps its own position (`Last-Event-ID`). Metrics are counters in the process. Chat, pager and ticket messages are sent by workflow steps, and Temporal already retries a step until it succeeds. A6 also says the notifier posts directly to the webhook so that it works when the database is down. A notifier that polls the event table cannot work when the database is down. So the design has two delivery systems for the same messages. The table also grows by one row per consumer per incident.
- **Proposed change:** Delete the table. Outside messages are Temporal activities. The `notification` row records delivery and acknowledgement. SSE reads `event` by sequence. Section 7.7 keeps one outbox: the queued incident row. Rules S5 and S6 become one sentence about the SSE client.
- **Guarantee kept:** No lost notification (A4 NFR-03, NFR-04): Temporal retry plus `notification.delivery_status`. No lost timeline event: the client resumes from its last sequence.
- **Effort saved:** 1 table, a consumer framework (checkpoint, gap check, skip logic), and the duplicate delivery path.
- [x] Approve
- **Your change:**

### S3 — Replace the `idempotency_key` table with one column on `incident`
- **Where:** A7 7.2 `idempotency_key`, 7.8 and Figure 4; log Q7.60 to Q7.62 (which replaced G25).
- **Problem:** The table stores the full response of every state-changing POST for 24 hours. It needs a request hash, a 422 rule and a cleanup job. Only one endpoint can create a duplicate: `POST /v1/incidents`, because submissions never group. Every other write is already safe. Alerts have `unique (integration_id, external_alert_id)` and the open-incident index. A second decision gets 409. Cancel, take-over and resolve are signals that do nothing the second time. Admin creates hit a unique name. Two more problems: the log says the key is written "in the same transaction as the effect", but for a decision or a cancel the effect is a Temporal signal, which is not in the transaction. And a stored response body of "create user" holds the one-time password in plain text for 24 hours.
- **Proposed change:** Go back to G25. `incident.idempotency_key` with `unique (created_by_user_id, idempotency_key)`. A repeat returns the existing incident with 202. The header stays optional on other POSTs and is ignored. Same key with another body still returns 422, checked against the incident row.
- **Guarantee kept:** A4 NFR-01 idempotent intake: one submission makes one incident. A5 SC-14 single decision: 409 from the approval tables.
- **Effort saved:** 1 table, a cleanup job, response storage and replay code on every endpoint, Figure 4.
- [x] Approve
- **Your change:**

### S4 — Merge `policy_check` and `sandbox_run` into `review` (one `check` table)
- **Where:** A7 7.1 group "Change", 7.2 `review`; `GET /v1/actions/{id}`.
- **Problem:** Three tables hold the same thing: a verdict about an action, a patch or a diagnosis, shown to the approver. `review` is already generic (`target_type`, `target_id`, `verdict`, `notes`). `policy_check` and `sandbox_run` have no columns in Artifact 7 yet. Each result is also written as an event (`policy.checked`, `sandbox.completed`, `review.completed`).
- **Proposed change:** One table `check`: `id, incident_id, action_id, kind (critic / policy / sandbox), verdict, detail (JSONB), artifact_id (sandbox report), model_call_id (critic only)`. Insert-only. `action_id` is a real foreign key; a diagnosis review uses `diagnosis_id`. This also removes the polymorphic `target_id` that cannot have a foreign key.
- **Guarantee kept:** A5 SC-12 (critic verdict shown), SC-13 (policy checks before review), SC-18 (sandbox result comes from the runner). The approver still sees all three.
- **Effort saved:** 2 tables, 2 sets of models and queries; one query for the approval screen.
- [x] Approve
- **Your change:**

### S5 — Fold model configuration into `integration` and `platform_setting`
- **Where:** A7 7.1 group "Configuration"; F5 table list.
- **Problem:** `model_assignment` has 3 rows for the life of the system (diagnoser, critic, embedding). Its only rule, critic ≠ diagnoser, is checked in application code and returns 409. `model_provider` has the same shape as `integration`: endpoint, secret reference, enabled flag. V1 has two adapters.
- **Proposed change:** `model_assignment` becomes the `platform_setting` key `models`, with a Pydantic model that rejects critic = diagnoser. `model_provider` becomes `integration` rows with `kind = model` and the columns `adapter` and `hosting`. `model_call.model_provider_id` points to `integration`.
- **Guarantee kept:** A5 SC-24: a cloud provider is off by default and needs a second admin (the `config_change` flow still applies to the `integration` row). Reviewer model differs from the main model (A2, SC-12).
- **Effort saved:** 2 tables, 2 admin endpoint groups.
- [x] Approve
- **Your change:**

### S6 — Write a `config_change` row only when a second admin is needed
- **Where:** A7 Figure 2 caption ("every configuration change writes a config_change row and a platform event"); F5.
- **Problem:** Every change is stored twice with before and after values: in `config_change` and in the `config.changed` event. The event is the hash-chained audit record. The row adds nothing for a change that needs no approval.
- **Proposed change:** Keep the table (F5 approved it). Insert a row only for a cloud-provider enable or a login-mode change. All other changes write the platform event only.
- **Guarantee kept:** A5 SC-24 two-admin approval. A5 AST-11: every change is audited with before and after values (in the event).
- **Effort saved:** One write path and one status machine for most admin changes. No table removed.
- [x] Approve
- **Your change:**

### S7 — Reference tables that are columns: `service_owner`, `service_repository`, `environment`
- **Where:** A7 7.1 group "Reference and ownership".
- **Problem:** `service_owner` links a service to its one owning team; `incident.owner_team_at_start` is already a single value. `service_repository` is one row per service in V1 (one Python app, one repository, one pipeline). `environment` is a lookup table of a few names; `service_environment_config` already lists the environments of each service.
- **Proposed change:** `service.owner_team_id` (plus `backup_team_id` if QR-05 needs it). `service.repo`, `default_branch`, `git_integration_id`, `pipeline_integration_id`, `pipeline_ref`. `environment` becomes a text column in `service_environment_config`; `incident (service_id, environment)` is a composite foreign key to it. Split a table out again when a service needs two owners or two repositories.
- **Guarantee kept:** A5 SC-03 roles from the ownership list; SC-05 scope lock (`service_dependency` stays); F4 ownership directory and its admin API. The composite key is stricter: an incident can only name an environment the service has.
- **Effort saved:** 3 tables, 3 joins on every authorization check.
- [x] Approve
- **Your change:**

### S8 — `diagnosis_feedback` is four columns on `diagnosis`
- **Where:** F8 (G20); A7 group "Cross-cutting".
- **Problem:** One feedback per diagnosis. `diagnosis` is already a mutable table. The `feedback.recorded` event holds who and when.
- **Proposed change:** `diagnosis.feedback_correct (yes / no / partly)`, `feedback_actual_cause`, `feedback_by_user_id`, `feedback_at`. Same endpoint.
- **Guarantee kept:** F8 feature: mark the diagnosis correct or not; audit through the event.
- **Effort saved:** 1 table.
- [x] Approve
- **Your change:**

### S9 — Remove repeated data inside rows
- **Where:** A7 7.2 `event`, `diagnosis`, `model_call`, `budget_entry`.
- **Problem and proposed change:**
  - `event.stream_id`, `incident_id` and `correlation_id` hold the same value on an incident stream. Keep `stream_type` and `incident_id` (null = platform stream). Drop `stream_id` and `correlation_id`. Unique key: `(incident_id, sequence)` plus a partial unique on `sequence` for the platform stream.
  - `event.data` must hold a pointer (`subject_type`, `subject_id`) when a record table exists (`tool_call`, `model_call`, `evidence`, `notification`). It must not copy the record. State this as a rule.
  - `diagnosis.ruled_out (uuid[])` repeats `hypothesis.status = ruled_out`. Drop it.
  - `model_call.budget_entry_id` and `budget_entry.model_call_id` point at each other. Keep `budget_entry.model_call_id` only.
- **Guarantee kept:** A5 SC-19 hash chain and per-stream order are unchanged. Provenance still follows `subject_id` and `causation_id`.
- **Effort saved:** 4 columns, one circular foreign key, and one class of "two copies disagree" bugs.
- [x] Approve
- **Your change:**

### S10 — Drop `LISTEN/NOTIFY`; poll
- **Where:** A7 7.7 "Find pending work", 7.9 "Live updates".
- **Problem:** Both uses already have a poll that makes a missed notify safe (the admission loop and the 15 s SSE heartbeat). So the poll is the real mechanism and the notify is an optimization. It needs a dedicated connection per listener.
- **Proposed change:** Poll every 1 s in the admission loop and in each open SSE stream. Add notify only if 1 s of delay is measured as a problem.
- **Guarantee kept:** A4 acknowledgement p95 ≤ 30 s; no lost event (the read is by sequence).
- **Effort saved:** Listener connections and reconnect handling in two processes.
- [x] Approve
- **Your change:**

### S11 — CloudEvents: keep the field names, drop the claim
- **Where:** A7 7.5; log Q7.44.
- **Problem:** No outside system consumes these events in V1. The only readers are the platform's own CLI and one-line chat messages. `specversion` and `dataschema` are stored or built for nobody.
- **Proposed change:** Say "the JSON uses CloudEvents field names (`id`, `source`, `type`, `subject`, `time`)". Do not store or validate the envelope. Adopt the full specification when a first outside consumer exists.
- **Guarantee kept:** None at risk. Event identity and order come from `id` and `sequence`.
- **Effort saved:** Envelope mapping and its tests.
- [x] Approve
- **Your change:**

---

## Under-specified (will cause rework)

1. **Columns live in a review note.** Artifact 7.2 gives no columns for about 20 tables (`policy_check`, `sandbox_run`, `oncall_shift`, `diagnosis_feedback`, all reference, identity and configuration tables). It points to the gap review. The artifact must list them.
2. **Partitioned tables contradict the stated keys** (see S1). If S1 is rejected, 7.2 must show the real keys with the partition column.
3. **One decision per approval request is not enforced.** "409 already decided" needs `unique (approval_request_id)` on `approval`. `approval_use.execution_attempt_id` has no foreign key, and the rule for attempt 2 with the same approval is not written.
4. **Per-stream hash chains do not detect a deleted stream or a cut tail.** Each chain only proves its own middle. Write the head hash of each incident stream into the platform stream at close, or use one chain. This is a gap in SC-19, not a simplification.
5. **"Running incidents keep the config they started with" has no storage.** `platform_setting` keeps only the latest value. Simplest fix: the workflow reads the settings once at start and carries them as workflow input; `incident.config_versions` records the version numbers.
6. **`approve_by_approver` CHECK only tests a label that the application writes.** It does not prove the user had the role. Say so, or check against the `approval` row.
7. **Polymorphic references have no foreign key** (`review.target_id`, `event.subject_id`). This conflicts with the "composite foreign keys" rule in 7.2. S4 fixes `review`; state the exception for `event`.

---

## Table by table

| # | Current table | Verdict | Finding |
|---|---|---|---|
| 1 | service | keep (gains owner and repository columns) | S7 |
| 2 | environment | merge into service_environment_config (text column) | S7 |
| 3 | team | keep | |
| 4 | service_owner | merge into service | S7 |
| 5 | service_dependency | keep (real many-to-many; SC-05) | |
| 6 | service_repository | merge into service | S7 |
| 7 | service_alias | keep (unique per source) | |
| 8 | service_environment_config | keep | |
| 9 | knowledge_document | keep (F6) | |
| 10 | user | keep | |
| 11 | local_credential | keep (keeps the hash out of user reads and audit payloads; SC-25) | |
| 12 | team_member | keep (real many-to-many) | |
| 13 | session | keep (revocation on disable; SC-25) | |
| 14 | user_identity | keep (F7) | |
| 15 | incident | keep (gains idempotency_key) | S3 |
| 16 | alert | keep | |
| 17 | evidence | keep, not partitioned | S1 |
| 18 | tool_call | keep, not partitioned | S1 |
| 19 | hypothesis | keep | |
| 20 | hypothesis_evidence | keep (real many-to-many with a role) | |
| 21 | diagnosis | keep (gains feedback columns, loses ruled_out) | S8, S9 |
| 22 | review | becomes `check` | S4 |
| 23 | model_call | keep, not partitioned | S1, S9 |
| 24 | action | keep | |
| 25 | patch | keep | |
| 26 | policy_check | merge into `check` | S4 |
| 27 | sandbox_run | merge into `check` | S4 |
| 28 | approval_request | keep (mutable request; immutable decision) | |
| 29 | approval | keep (SC-14) | |
| 30 | approval_use | keep (3 columns give single use by a primary key; SC-14) | |
| 31 | execution_attempt | keep (SC-16) | |
| 32 | verification | keep (SC-18) | |
| 33 | event | keep, not partitioned, fewer columns (SC-19) | S1, S9 |
| 34 | artifact | keep | |
| 35 | budget_entry | keep (SC-21; reserve before a call needs a ledger) | S9 |
| 36 | notification | keep (F8 acknowledgement) | S2 |
| 37 | oncall_shift | keep (F4; SC-03) | |
| 38 | diagnosis_feedback | merge into diagnosis | S8 |
| 39 | consumer_checkpoint | drop | S2 |
| 40 | idempotency_key | drop (column on incident) | S3 |
| 41 | integration | keep (gains kind = model) | S5 |
| 42 | model_provider | merge into integration | S5 |
| 43 | model_assignment | merge into platform_setting | S5 |
| 44 | platform_setting | keep | S5 |
| 45 | config_change | keep, fewer rows (SC-24) | S6 |

No table becomes a view. The timeline and the budget total are already queries, not tables.

**Count:** 45 − 2 dropped (S2, S3) − 8 merged (S4: 2, S5: 2, S7: 3, S8: 1) = **35 tables**.
