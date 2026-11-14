# Layer 7 feature-coverage review — 2026-11-14

Reviewer: Claude (subagent), for Dhanush (Layer 7 owner).
Scope: does the Layer 7 data model (log Q7.1–Q7.27, 34-table list in Q7.18, login decision) and the Section C API draft support every feature that A1–A6 specify?
Sources read: A1–A6 artifacts, `specs/layer-07-data-apis-events/conversation-log.md`, the Section C draft (given in the request, not yet in the log), `PROGRESS.md`.
No existing file was changed. Every item below is a proposal. The team decides.

Labels used in this report:
- **Required** = an artifact (A1–A6) or a Layer 7 decision asks for it. The source is given.
- **Suggested (not required)** = no artifact asks for it. It is a proposal only.

---

## 1. Summary

| Item | Count |
|---|---|
| Features checked | 62 |
| Covered | 19 |
| Partial | 26 |
| Missing | 17 |
| Gaps found | 28 (G1–G28) |
| High | 11 (G1–G8, G10–G12) |
| Medium | 10 (G9, G13–G21) |
| Low | 7 (G22–G28) |

Main findings:

1. **The actor is not defined anywhere.** Q7.16 says an event has an "actor", but no type, ID or rule. Cancel, take-over, severity change, config change and admin actions have no actor columns. A5 SC-19 and ST-15 ("every step has an entry with an actor") cannot pass yet. (G1)
2. **Platform-level audit has no home.** Login, lockout, 403, user changes and config changes are not about an incident. The event table is keyed by incident (Q7.16, Q7.22). The hash chain required by SC-19 is not in the event record. There is no admin audit query endpoint. (G2, G3)
3. **The setup side of the platform has no API.** Users, teams, team members, service ownership, on-call, integrations, MCP servers, model providers, limits and knowledge documents have tables (some) but no write path. (G4–G9)
4. **The approver cannot see what they approve.** There is `POST /v1/actions/{id}/decisions` but no `GET /v1/actions/{id}`. The approver needs the action, its hash, evidence for and against, the critic verdict and the undo path (A5 SC-12, SC-14). (G10)
5. **Two human checkpoints from A1 have no endpoint:** confirm or change severity, and close/resolve an incident that a human took over or that was escalated. (G11, G13)
6. **Fix approval by PR merge** needs a link from a Git identity to a platform user. Without it, the platform cannot check that the merger is an eligible approver and not the author (A2 2.3, A5 SC-04). (G12)

The alert-vs-incident model is sound (section 6). It needs an alert state (firing / resolved) to cover the "alert must clear" and self-recovery paths. (G14)

---

## 2. Feature coverage matrix

Status: **Covered** = tables and endpoints exist and the actor is recorded. **Partial** = data or API exists but a part is missing. **Missing** = no table or no endpoint.

### 2.1 Intake, grouping, routing

| # | Feature | Source | Tables | Endpoints | Status | Gap |
|---|---|---|---|---|---|---|
| F1 | Receive signed alert webhook per source | UC1, FR-01, SC-02, NFR-01 | alert, incident | POST /v1/alerts | Partial — per-source secret and rotation have no store | G6, G17 |
| F2 | Engineer submits an incident | FR-01, FR-03 | incident | POST /v1/incidents | Partial — where the `(caller, idempotency_key)` unique key lives is not said | G25 |
| F3 | Reject a submission with a missing field, with a reason | FR-03 | — | problem+json 4xx | Covered | — |
| F4 | Group duplicate alerts into one open incident | FR-02, Q7.20 | alert, incident (partial unique index) | POST /v1/alerts → `grouped` | Covered (window open, Section D/E) | — |
| F5 | Alert-resolved signal; "the alert must clear" | A1 1.6, A1 1.3 (self-recovery) | alert (no state column) | POST /v1/alerts (no resolved handling) | Partial | G14 |
| F6 | Map an alert to a service and environment | FR-03, Q7.2 | service, environment | — | Partial — no alias / label mapping from the alert payload to a service | G7 |
| F7 | Find owning team, manager, members | A1 1.2, UC1 | service_owner, team, team_member | none | Partial — read in workflow only, no CRUD | G5, G7 |
| F8 | Read the on-call schedule | A1 1.2, E1, SC-03 | oncall_snapshot | none | Missing — no source, no sync, no fixture entry path | G8 |
| F9 | Fallback owner for an unmapped service | FR-03 | — | — | Partial — "platform team on-call" is not stored anywhere | G6 |
| F10 | Queue by severity then age; cap 20; overflow to humans | NFR-07, QR-07, ADR-03 | incident (status queued) , notification | GET /v1/incidents?status= | Covered (limits config: G6) | — |
| F11 | Human confirms or changes severity (non-blocking) | A1 1.3, 1.5 checkpoint | incident.severity | none | Missing | G11 |
| F12 | Owner notified; acknowledgement latency measured | NFR-04, A3 3.10 | notification, event | none for ack | Partial | G15 |

### 2.2 Investigation and diagnosis

| # | Feature | Source | Tables | Endpoints | Status | Gap |
|---|---|---|---|---|---|---|
| F13 | Collect evidence per source, parallel, timeout, "missing" | UC2, FR-04, NFR-12 | evidence, tool_call, artifact | (worker) | Covered (per-source timeout config: G6) | — |
| F14 | Provenance per evidence item, re-runnable query | A1 1.3, FR-04, Q7.4 | evidence, tool_call | GET …/provenance/{type}/{id} | Covered | — |
| F15 | Redaction before store, show, model; fail closed | NFR-08, SC-09 | evidence.redaction_version, status | — | Covered | — |
| F16 | Injection flag in the audit record | SC-10, ST-01 | event | events endpoint | Covered if the event type exists | G27 |
| F17 | Tool call rejected outside allow list or scope, logged | SC-05, SC-07, ST-02 | tool_call | events endpoint | Partial — tool_call needs status `rejected` + reason | G27 |
| F18 | Hypotheses with evidence for and against, ranked | UC3, FR-05–FR-07 | hypothesis, hypothesis_evidence | only via events / provenance | Partial — no direct read | G16 |
| F19 | Inconclusive result with a missing list | FR-08 | diagnosis | only via events | Partial (read) | G16 |
| F20 | Knowledge documents and past incidents for retrieval | UC2, ADR-09, SF-4 | knowledge_document, incident | none | Missing — no create / update / delete / re-index path | G9 |
| F21 | Model call record, budget charged | Q7.14, NFR-11 | model_call, budget_entry | — | Covered | — |
| F22 | Budget reserve / actual / release; stop at limit | NFR-06, QR-06, SC-21 | budget_entry | none | Partial — no read endpoint; limits not stored | G6, G24 |
| F23 | Critic review by a different model | UC4, SC-12, Q6.16 | review, model_call | — | Covered | — |
| F24 | Patch-writing step has a named agent role | FR-09 | patch, model_call | — | Partial — A6 has no patch-author component | G28 |

### 2.3 Change, approval, execution, verification

| # | Feature | Source | Tables | Endpoints | Status | Gap |
|---|---|---|---|---|---|---|
| F25 | Propose an action (redeploy, config restore, fix PR) | UC4, Q7.7 | action | — | Covered | — |
| F26 | Patch, reproduction test, sandbox report | FR-09, FR-10 | patch, sandbox_run, artifact | — | Covered | — |
| F27 | Policy checks before review | SC-13 | policy_check | — | Covered | — |
| F28 | Approver sees action, hash, evidence for/against, critic verdict, undo path | SC-12, SC-14, RR-2 | action, review, policy_check, hypothesis_evidence | none | Missing — no `GET /v1/actions/{id}` | G10 |
| F29 | List pending approvals for me | FR-11 | approval_request | GET /v1/approvals?status=pending | Covered | — |
| F30 | Approve / reject with hash, reason, password re-entry | FR-11, SC-14, SC-25, Q7.10 | approval, approval_request | POST /v1/actions/{id}/decisions | Covered | — |
| F31 | Approval expiry, backup approver after timeout | QR-05, A1 1.5 | approval_request | — | Partial — timeouts and backup order not stored; eligible approvers per stage not recorded | G6, G26 |
| F32 | M11: author may approve revert, not fix | SC-04, ST-07 | approval | — | Partial — needs Git identity → user | G12 |
| F33 | Fix approval = human merges PR; platform never merges | A2 2.3, FR-11, SC-20 | patch (PR URL, head SHA) | none | Missing — no merge detection, no merger identity | G12 |
| F34 | Platform admin and platform identity cannot approve | SC-04, ST-06 | approval | — | Partial — needs actor type check and admin flag | G1, G4 |
| F35 | Single use of an approval | SC-14, Q7.23 | approval_use | — | Covered | — |
| F36 | Executor dispatch, idempotency, intent record, reconcile | SC-15, SC-16, Q7.11 | execution_attempt | — | Covered | — |
| F37 | Verify on alert signals vs baseline | UC6, FR-13, SC-18 | verification | — | Covered | — |
| F38 | Undo a fix when errors return (new approved action) | A1 1.3 | action | — | Partial — no link from the undo action to the action it undoes | G23 |
| F39 | Pipeline / config-store target per service | A2 2.1 ("a mapping links each repository to its pipeline") | service_repository | none | Partial — no pipeline or config-store key column | G7 |

### 2.4 Human control, escalation, reporting

| # | Feature | Source | Tables | Endpoints | Status | Gap |
|---|---|---|---|---|---|---|
| F40 | Stop at any step; record who and why | UC9, FR-14 | event | POST …/cancel | Partial — reason not required in the draft; actor undefined | G1, G13 |
| F41 | Take over the incident | UC9, A1 1.5 | event | POST …/takeover | Partial — who may call is not said; actor undefined | G1, G13 |
| F42 | Human closes / resolves an escalated or taken-over incident | A1 1.3 (every red path ends with a human), A3 3.10 life cycle | incident | none | Missing | G13 |
| F43 | Escalation with a clear note (what was checked, what is missing) | UC7, FR-08, A3 3.10 | diagnosis, notification, event | events | Covered | — |
| F44 | Time-based escalation path (on-call → manager) | A3 Fig 4, L3-A3 | notification | none | Partial — no ack, no manager link stored | G15, G5 |
| F45 | Notify humans when the database is down | NFR-03, A6 notifier | notification | — | Partial — notification rows cannot be written during the outage | G27 |
| F46 | Timeline of every read, claim, decision, action | FR-15 | event | GET …/events, SSE | Covered (actor: G1) | — |
| F47 | Closing report: root cause, fix, audit trail | A1 1.3, A1 1.6 demo | artifact (no kind for it) | none | Missing | G19 |
| F48 | Timeline export | A1 1.3 ("hands over the incident record") | event | GET …/events (paged JSON) | Partial — Suggested: one-file export | G19 |
| F49 | Diagnosis accuracy label (was the diagnosis correct?) | A1 1.6, A1 C3 | none | none | Missing | G20 |
| F50 | Recovered without action (self-recovery) | A1 1.3, E7 | incident status, verification | — | Partial — needs alert-resolved signal | G14 |

### 2.5 Identity, access, administration

| # | Feature | Source | Tables | Endpoints | Status | Gap |
|---|---|---|---|---|---|---|
| F51 | Own login, lockout, rate limit, audit | SC-25, ST-18 | user, local_credential, session | POST /v1/auth/login, /logout | Partial — unlock, password reset and change have no endpoint | G4 |
| F52 | SSO login (OIDC, CLI device-code) | SC-01, L5-A1 | user, session | none | Missing — no device-code / callback endpoints | G21 |
| F53 | Password re-entry (or SSO re-login) to approve | SC-25 | session | decisions endpoint | Partial — SSO re-auth path not defined | G21 |
| F54 | Create user (admin only, no self-signup) | SC-25, ST-18 | user | "/v1/users mentioned" | Missing | G4 |
| F55 | Disable user, revoke sessions | SC-25 (implied by admin-created accounts) | user, session | none | Missing | G4 |
| F56 | Platform admin role assignment | SC-03 | none (no column) | none | Missing | G4 |
| F57 | Team and team-membership management | SC-03, A1 1.2 | team, team_member | none | Missing | G5 |
| F58 | Service ownership directory CRUD (service, env, owner, dependency, repo) | A1 A1, A2 2.1, SC-05, A6 ownership directory | service, environment, service_owner, service_dependency, service_repository | none | Missing | G7 |
| F59 | Role check on every request; 403 + audit | SC-03, ST-04 | event | 403 problem+json | Partial — 403 has no incident, so no event stream | G2 |
| F60 | Admin queries the audit record; each query logged | SC-19 | event | none | Missing | G3 |
| F61 | Platform config (integrations, MCP, models, limits, SSO, retention) | A2 2.1, 2.4, 2.5, SC-24, Q6.12 | none ("repository, reviewed PR") | none | Missing | G6 |
| F62 | Cloud provider off by default; critic ≠ diagnoser check | SC-24, ST-17 | none | none | Missing | G6 |
| F63 | Retention 1 year / 90 days | Q7 retention row | artifact.retention_class | none | Partial — conflicts with immutability triggers | G18 |
| F64 | Health, readiness, platform metrics | NFR-10, NFR-11 | — | /livez, /readyz, /metrics | Covered | — |
| F65 | Backup and restore | NFR-09 | — | — (operations) | Covered (no API needed) | — |

(F-numbers above 62 are operational rows that need no new data; the summary count uses F1–F62.)

---

## 3. Gaps

Each gap: severity, what is missing, proposed tables and columns, proposed endpoints (method, path, who may call), audit and actor effect, conflicts with earlier artifacts.

### G1 — No strict actor model (High)
- **Missing:** Q7.16 names an "actor" field with no type or rule. Hypothesis has "creator (rule ID or model-call ID)". Approval has "approver". Artifact has "creator". Cancel, take-over, severity change, notification, config and user changes have no actor at all. A5 ST-15 needs "every step … has an entry with an actor". FR-12 needs "actor is always the pipeline or the config store, never the agent". FR-14 needs "who and why".
- **Proposal:** one actor block (section 4) on every event row, NOT NULL, with CHECK constraints. Business tables keep a typed FK only where a database rule needs it (for example `approval.approver_user_id NOT NULL`).
- **Endpoints:** none new. Every write endpoint fills the actor from the authenticated caller. The API never accepts an actor from the request body.
- **Audit effect:** this is the audit fix. It makes ST-15 and FR-12 checkable with one query.
- **Conflicts:** none. It refines Q7.16.

### G2 — Events that are not about an incident have no home (High)
- **Missing:** Q7.16 and Q7.22 key every event by incident and sequence per incident. Login, logout, lockout, password reset, 403 on a list call, user and team changes, config changes and audit queries have no incident. SC-25 and SC-19 require audit events for these.
- **Proposal:** add `stream` to `event`: `stream_type` (`incident` | `platform`) and `stream_id` (the incident ID, or a fixed platform stream ID). The sequence number is per stream. `incident_id` stays, NULL for platform events, with a CHECK that it equals `stream_id` when `stream_type = incident`.
- **Endpoints:** see G3.
- **Audit effect:** every SC-25 and admin event gets a sequence and a chain.
- **Conflicts:** Q7.22 "every table carries incident_id". Record an exception for `event` (platform stream) and for the reference, identity and config tables.

### G3 — Hash chain and admin audit query are missing (High)
- **Missing:** SC-19 requires an append-only, **hash-chained** record, queried by an administrator through the CLI or API, with each query logged. Q7.16 lists no hash fields. The draft API has no cross-incident audit endpoint.
- **Proposed columns on `event`:** `prev_hash`, `hash` (SHA-256 over the canonical row plus `prev_hash`), per stream. Insert takes a per-stream advisory lock so the chain has no fork.
- **Proposed endpoints:**

| Method | Path | Who may call | Notes |
|---|---|---|---|
| GET | /v1/audit/events?stream=&actor_type=&actor_id=&type=&from=&to=&after= | Platform admin | Cross-stream query. Writes an `audit.queried` event with the filter. |
| GET | /v1/audit/verify?stream= | Platform admin | Re-computes the chain; returns the first bad sequence (ST-15). Also logged. |

- **Conflicts:** none. Q7.21 immutability stays; the chain adds tamper evidence for a database administrator (ST-15).

### G4 — User management (High)
- **Missing:** create, list, read, update, disable, unlock, password reset, password change, platform-admin flag. Only "admin-only /v1/users" is named.
- **Proposed columns on `user`:** `id`, `username` (unique), `display_name`, `email`, `status` (`active` | `disabled` | `locked`), `is_platform_admin` (bool), `auth_mode` (`local` | `sso`), `sso_subject` (unique, nullable), `created_at`, `created_by_*` (actor), `disabled_at`, `disabled_reason`, `version`. On `local_credential`: `password_hash`, `failed_count`, `locked_until`, `must_change` (bool), `changed_at`.
- **Delete vs disable:** disable only. A user row is referenced by approvals and events (FK RESTRICT). Disable revokes every session in the same transaction. Hard delete is not offered in V1.
- **Proposed endpoints:**

| Method | Path | Who may call |
|---|---|---|
| POST | /v1/users | Platform admin. Returns a one-time password (own login), `must_change = true`. |
| GET | /v1/users, /v1/users/{id} | Platform admin; any user for `GET /v1/users/me` |
| PATCH | /v1/users/{id} (display name, email, is_platform_admin) | Platform admin; If-Match version. An admin cannot remove their own admin flag if they are the last admin. |
| POST | /v1/users/{id}/disable, /enable | Platform admin; reason required |
| POST | /v1/users/{id}/unlock | Platform admin |
| POST | /v1/users/{id}/password-reset | Platform admin; sets a one-time password, revokes sessions |
| POST | /v1/users/me/password | The user; needs the current password |

- **Bootstrap:** the first admin is created by a CLI command run inside the API container (`ai-sre admin bootstrap`), only when no admin exists. It writes a platform event with actor type `platform`, component `bootstrap`.
- **Audit:** every call writes a platform-stream event with before/after (password hashes never in the payload).
- **Conflicts:** SC-04 says the platform admin cannot approve. With `is_platform_admin` on a normal user, decide: is an admin who is also on call blocked from approving? Recommendation: the admin flag is held by a separate admin account, so the rule stays simple. Record as a Layer 7 decision; Chirag confirms (A5).

### G5 — Team and membership management (High)
- **Missing:** no API for `team` or `team_member`. Roles in SC-03 come from these.
- **Proposed columns:** `team(id, name, manager_user_id, is_platform_team bool, version)`; `team_member(team_id, user_id, added_at, added_by_*)`. `is_platform_team` marks the fallback owner team (FR-03).
- **Proposed endpoints:** `POST/GET/PATCH /v1/teams`, `POST /v1/teams/{id}/members`, `DELETE /v1/teams/{id}/members/{user_id}` (removes the link, the event keeps history). Who: platform admin. Suggested (not required): the team manager may manage their own team members.
- **Audit:** platform-stream events with before/after.
- **Conflicts:** A1 1.2 says the list is "maintained". This gives the maintenance path.

### G6 — Platform configuration has no store and no API (High)
- **Missing:** everything in A2 2.1, 2.4, 2.5, A4 limits, A5 SC-02/SC-24/SC-25 config, A6 Q6.12. Q7.18 puts "platform config" in the repository by reviewed PR. The owner now expects APIs and a store.
- **Proposal:** section 5.
- **Conflicts:** Q7.18 ("not tables: platform config"), A5 SC-24 ("reviewed configuration change"), A5 AST-10. Section 5 resolves these as a recommendation.

### G7 — Ownership directory CRUD and mappings (High)
- **Missing:** no write path for `service`, `environment`, `service_owner`, `service_dependency`, `service_repository`. No pipeline or config-store mapping (A2 2.1). No mapping from an alert payload (labels such as `job`, `app`) to a service.
- **Proposed columns:** `service(id, name, tier, version)`; `service_alias(service_id, source_integration_id, external_name)` (unique per source); `service_repository(service_id, git_integration_id, repo, default_branch, pipeline_integration_id, pipeline_ref)`; `service_environment_config(service_id, environment_id, config_store_integration_id, config_key_prefix)`; `service_dependency(service_id, depends_on_service_id)`; `service_owner(service_id, team_id)`.
- **Proposed endpoints:** `POST/GET/PATCH /v1/services`, `PUT /v1/services/{id}/owner`, `PUT /v1/services/{id}/dependencies`, `PUT /v1/services/{id}/repositories`, `PUT /v1/services/{id}/aliases`, `POST/GET /v1/environments`. Who: platform admin. GET: any logged-in user (names only; Suggested). Suggested (not required): `POST /v1/services:import` (one YAML file) for the fixtures.
- **Audit:** platform-stream events with before/after. An incident stores the owner team and versions it used at start (Q7.2), so a later change does not rewrite history.
- **Conflicts:** none. Closes the A6 "Ownership directory" write side.

### G8 — On-call schedule source (High)
- **Missing:** A1 E1 and A3 open item. SC-03 roles depend on on-call "at that time". `oncall_snapshot` has no source and no write path.
- **Proposal:** replace `oncall_snapshot` by `oncall_shift(team_id, user_id, level primary|backup, starts_at, ends_at, source manual|integration, source_ref, synced_at)`. Two ways to fill it:
  1. A sync job reads the pager tool through an `oncall` integration (G6) and writes shifts. Actor: platform, component `oncall_sync`.
  2. An admin enters shifts (fixtures, and organizations without a pager tool).
- **Endpoints:** `GET /v1/oncall?team=&at=` (any logged-in user), `PUT /v1/teams/{id}/oncall` (platform admin; replaces future shifts), `POST /v1/admin/oncall/sync` (platform admin; forces a sync).
- **Audit:** the approval already stores the approver's role at decision time (Q7.10). Routing writes an `incident.routed` event with the resolved on-call user IDs. That event replaces the "snapshot" purpose.
- **Conflicts:** none. Closes A1 E1 for data; the real source stays an assumption.

### G9 — Knowledge documents (Medium)
- **Missing:** UC2 and ADR-09 use runbooks. `knowledge_document` exists, but no path adds, updates, removes or re-indexes it. A5 SF-4 lists planted text in knowledge documents as an attack surface, so who added a document matters.
- **Proposal (recommend option A):**
  - A. Runbooks live in a Git repository (an integration). A sync job indexes them. Changes are reviewed by PR, like prompts (A5 AST-10). Columns: `knowledge_document(id, source git|upload|incident, source_ref (repo path + commit SHA), title, service_id null, content_hash, artifact_id, indexed_at, status active|removed)`.
  - B. Upload by API: `POST /v1/knowledge-documents` (platform admin, or Suggested: owning team), `DELETE` = mark removed.
- **Endpoints:** `GET /v1/knowledge-documents` (any logged-in user), `POST /v1/admin/knowledge/sync` (platform admin).
- **Audit:** every evidence item from retrieval cites `knowledge_document.id` and `content_hash`, so the provenance shows the exact version read.
- **Conflicts:** none. Layer 10 (Irfan) owns indexing.

### G10 — Approver cannot read the action (High)
- **Missing:** no `GET /v1/actions/{id}`. The decisions endpoint needs `action_hash`, so the client must get it first. SC-12 says the approval screen shows evidence for and against. RR-2 depends on this.
- **Proposed endpoints:**

| Method | Path | Who may call | Returns |
|---|---|---|---|
| GET | /v1/actions/{id} | Viewer of the service | kind, absolute target, precondition, undo path, risk class, `action_hash`, diagnosis summary, supporting and contradicting evidence IDs with redacted summaries, critic verdict, policy-check results, sandbox report link (fix), PR URL and head SHA (fix), approval request status and expiry |
| GET | /v1/incidents/{id}/actions | Viewer | list |

- **Audit:** reads are not events (Suggested: log approval-screen reads as `action.viewed`, so RR-2 can measure "approved without reading").
- **Conflicts:** none.

### G11 — Severity confirm / change (High)
- **Missing:** A1 1.5 lists "confirm or change the severity" as a V1 human checkpoint. No endpoint exists. Severity also drives the queue order (NFR-07).
- **Proposed columns on `incident`:** `severity`, `severity_source` (`alert` | `human`), `severity_confirmed` (bool).
- **Endpoint:** `POST /v1/incidents/{id}/severity {severity, reason}` — submitter role of that service (SC-03). Goes to the workflow as a signal (Q7.24), or updates the queued row directly when the incident is still queued (Layer 8 decides).
- **Audit:** `incident.severity_changed` with before/after, actor, reason.
- **Conflicts:** none. Layer 8: does a severity raise re-order a queued incident at once? (Recommend yes.)

### G12 — Fix merge and external identities (High)
- **Missing:** A2 2.3: "The human approver reviews and merges it. The merge is the approval for the fix." A5 SC-04: the author must not approve the fix. A5 SC-20: deployed commit must equal approved SHA. The platform must know **who merged** and map that Git user to a platform user. No table maps external identities. No endpoint or poll receives merge events.
- **Proposed table:** `user_identity(user_id, system git|chat|pager|sso, external_id, verified_at, added_by_*)`, unique `(system, external_id)`. Platform admin manages it: `PUT /v1/users/{id}/identities`.
- **Merge detection:** recommend a poll by the worker (pull request state by URL), so no new inbound surface. Suggested alternative: `POST /v1/integrations/{id}/webhook` for Git events, signed like SC-02.
- **Record:** the platform-signed approval (password re-entry, head SHA) stays the authorization record. The merge is a second check: merger maps to the same eligible user (or any eligible non-author user), merged SHA equals approved SHA. Mismatch → escalate.
- **Actor:** merge event has actor type `user` (mapped) with `via = external:git`, or actor type `external` with `external_id` when not mapped (then escalate).
- **Conflicts:** A2 2.3 ("merge is the approval") and A5 SC-14 (platform-signed approval) both apply to a fix. Layer 11 (Rinisha) must say which one is the record. Recommendation above: the signed approval is the record; the merge must match it.

### G13 — Stop, take-over and human close (Medium)
- **Missing:** cancel has no required reason (FR-14: "records who and why"). Who may call cancel and take-over is not said. No endpoint ends an incident after a human takes over or after an escalation; every red path in A1 "ends with a human" but the record never closes.
- **Proposed columns on `incident`:** `owner_user_id` (set by take-over), `closed_at`, `resolution` (`recovered` | `recovered_without_action` | `fixed` | `fix_recommended` | `handled_by_human` | `cancelled` | `not_processed`), `resolution_note`.
- **Endpoints:**

| Method | Path | Who may call |
|---|---|---|
| POST | /v1/incidents/{id}/cancel {reason} | Submitter role of the service. Suggested: platform admin too, as an emergency stop. |
| POST | /v1/incidents/{id}/takeover {reason} | Submitter role of the service |
| POST | /v1/incidents/{id}/resolve {resolution, note} | The taking-over user, or an approver of the service, only in a human-owned state |

- **Audit:** each writes an event with actor and reason. Take-over sets `on_behalf_of` for later human actions? No: after take-over the human acts as themselves.
- **Conflicts:** none. Layer 8 owns the allowed transitions.

### G14 — Alert state and resolved signals (Medium)
- **Missing:** A1 1.6: "The alert must clear." A1 1.3 self-recovery. Monitoring tools send "resolved" notifications on the same webhook. The `alert` table has no state, so a resolved payload could open a new incident or be lost.
- **Proposed columns on `alert`:** `status` (`firing` | `resolved`), `starts_at`, `ends_at`, `received_at`, `source_timestamp`, `fingerprint`, `incident_id`, `payload_artifact_id`. Each delivery is a row in `alert_delivery(alert_id, received_at, status, signature_ok, payload_hash)` (Suggested; or store deliveries as events).
- **Behaviour:** a resolved payload never opens an incident. It updates the alert and sends an `alert.resolved` signal to the workflow. The verifier still decides recovery on its own query (SC-18); the resolved signal is evidence only.
- **Endpoint:** same `POST /v1/alerts`; response `status: resolved_recorded`.
- **Conflicts:** none.

### G15 — Notifications and acknowledgement (Medium)
- **Missing:** A3 3.10 life cycle has "acknowledged". NFR-04 measures acknowledgement. A3 Figure 4 is a time-based escalation path. `notification` has no ack.
- **Proposed columns on `notification`:** `recipient_user_id`, `channel` (chat | pager), `kind` (owner | approval | escalation | overflow | self_alert), `sent_at`, `delivery_status`, `external_ref`, `acked_at`, `acked_by_user_id`.
- **Endpoint:** `POST /v1/incidents/{id}/ack` — submitter role of the service. Suggested (not required): ack from the pager tool by poll.
- **Audit:** `incident.acknowledged` event.
- **Conflicts:** none. Layer 11 sets the escalation order (A1 F1).

### G16 — No direct read of investigation records (Medium)
- **Missing:** UC3 "show a hypothesis, its evidence and its confidence". Today only the events stream and the provenance endpoint return them.
- **Endpoints:** `GET /v1/incidents/{id}/evidence`, `/hypotheses`, `/diagnoses` (active first), each paged. Who: viewer of the service.
- **Conflicts:** none. Thin read views over existing tables.

### G17 — Webhook secret rotation (Medium)
- **Missing:** SC-23 requires rotation. A signed source needs two valid secrets during a rotation, or webhooks fail.
- **Proposed columns on the alert-source integration:** `secret_ref`, `next_secret_ref`, `next_valid_from`. Intake accepts either during the overlap.
- **Endpoint:** `POST /v1/admin/integrations/{id}/rotate-secret {next_secret_ref}` and `POST …/finish-rotation` — platform admin.
- **Audit:** config-change event (names of refs only).

### G18 — Retention conflicts with immutability (Medium)
- **Missing:** Q7.21 rejects UPDATE and DELETE on event, evidence, artifact and others. The retention row says incident records 1 year, raw artifacts 90 days. No path deletes them.
- **Proposal:** partition `event`, `evidence`, `model_call`, `tool_call` by month. A retention job, under a separate maintenance database role, drops whole partitions past retention and deletes artifact files. It writes a `retention.purged` platform event with the range and the last hash of the removed chain segment, so the chain stays verifiable from that checkpoint.
- **Endpoints:** none required. Retention values live in platform settings (G6).
- **Conflicts:** Q7.21 needs one sentence: "only the maintenance role drops whole partitions after retention".

### G19 — Closing report and export (Medium)
- **Missing:** A1 1.3: "It writes a report with the root cause, the fix, and the full audit trail."
- **Proposal:** the report is an `artifact` of kind `incident_report` (Markdown), written at close by the platform. No new table.
- **Endpoints:** `GET /v1/incidents/{id}/report` (viewer). Suggested (not required): `GET /v1/incidents/{id}/events?format=ndjson` for a one-file export.

### G20 — Diagnosis correctness label (Medium)
- **Missing:** A1 1.6 "diagnosis accuracy" and A1 C3 ("who decides that a diagnosis was correct"). No table holds the human verdict.
- **Proposed table:** `diagnosis_feedback(incident_id, diagnosis_id, correct yes|no|partly, actual_cause, by_user_id, at)`.
- **Endpoint:** `POST /v1/incidents/{id}/feedback` — approver or owner of the service, after close.
- **Conflicts:** C3 is open (Irfan, Layer 12). This gives the data slot only.

### G21 — SSO endpoints and re-authentication (Medium)
- **Missing:** SC-01 device-code flow for the CLI, and "log in again with single sign-on" to approve. No endpoints.
- **Endpoints:** `POST /v1/auth/device` (start), `POST /v1/auth/device/token` (poll), `GET /v1/auth/oidc/callback`. Session gets `auth_time`. The decisions endpoint requires `auth_time` within N minutes in SSO mode instead of a password.
- **User creation in SSO mode:** recommend admin pre-provisions the user with `sso_subject`; first login with an unknown subject is refused. This keeps "no self-signup" in both modes.
- **Conflicts:** L5-A1 stays open.

### G22 — Service accounts (Low)
- **Missing:** SC-02: "Platform service accounts are separate from human identities." Alert sources are covered by integrations. No other machine caller exists in V1.
- **Proposal:** none for V1. An alert source is an `integration`; its actor is `external`. Add API service accounts only when a machine client other than a webhook appears.

### G23 — Undo action link (Low)
- **Proposed column:** `action.undoes_action_id` (nullable FK). An undo is a new action with its own approval (A1: every production change needs approval).

### G24 — Budget visibility (Low)
- **Endpoint:** `GET /v1/incidents/{id}/budget` — viewer. Returns limits, reserved, used, per kind. Suggested (not required); NFR-11 already exposes the totals as metrics.

### G25 — Idempotency key storage (Low)
- **Proposal:** `incident.submitted_by_user_id` + `incident.idempotency_key`, unique together (Q7.20). For admin writes use If-Match on `version` instead of an idempotency key.

### G26 — Approval request detail (Low)
- **Proposed columns on `approval_request`:** `stage` (primary | backup), `eligible_user_ids` (resolved at creation), `expires_at`, `escalated_at`. The gate re-checks rights at decision time (SC-03), so the list is evidence, not authority.

### G27 — Event and record details (Low)
- `tool_call.status` needs `rejected` with `reject_reason` (ST-02).
- Event types must include: `injection.flagged`, `authz.denied`, `auth.login_succeeded/failed`, `auth.locked`, `config.changed`, `user.*`, `team.*`, `service.*`, `audit.queried`, `retention.purged`.
- NFR-03: the notifier sends while the database is down; it writes the `notification` rows and events after the database returns (from a local spool). Layer 8 designs the spool.

### G28 — Patch-author role not named (Low)
- **Missing:** FR-09 needs a model to write the patch. A6 has diagnoser and critic only.
- **Proposal:** add agent role `fixer` to the actor enum, or state that the diagnoser writes the patch. Layer 9 decides.

---

## 4. Proposed uniform actor model

Every event row carries this block. Columns are NOT NULL unless marked.

| Column | Values | Rule |
|---|---|---|
| `actor_type` | `user` \| `agent` \| `platform` \| `external` | Required |
| `actor_id` | user ID; model_call ID; component name; integration ID | Required. FK where the type has a table. |
| `actor_role` | user: `viewer` \| `submitter` \| `approver` \| `platform_admin` (role used for this action, at this time). agent: `diagnoser` \| `critic` (\| `fixer`, G28). platform: `intake` \| `admission` \| `orchestrator` \| `evidence_collector` \| `policy_gate` \| `approval_gate` \| `executor` \| `verifier` \| `sandbox_runner` \| `notifier` \| `oncall_sync` \| `retention_job` \| `bootstrap`. external: `monitoring` \| `git` \| `cicd` \| `config_store` \| `pager` | Required. CHECK per type. |
| `on_behalf_of_type`, `on_behalf_of_id` | nullable | Set when a component acts for a person. Example: the executor dispatches for approval X → on behalf of `approval`/X. A pipeline outcome callback → on behalf of `execution_attempt`/Y. |
| `auth_method` | `password` \| `sso` \| `webhook_hmac` \| `webhook_token` \| `internal` | Required for `user` and `external`. |
| `session_id` | nullable | For `user` actions. |
| `request_id` | nullable | API request ID; joins to platform logs and traces. |
| `reason` | nullable text | Required by CHECK for event types: cancel, takeover, reject, self-approval, severity change, disable user, config change, resolve. |

Rules:

1. The API fills the actor from the authenticated caller. A request body can never set it.
2. `agent` actor ID is always a `model_call` ID. The model name, provider and prompt version come from that row. So "which model said this" is one join.
3. Approval: `actor_type` must be `user` and `actor_role` must be `approver`. A CHECK enforces it. This makes "platform admin and platform identity cannot approve" (SC-04) a database rule, not only a code rule.
4. Production change (`execution_attempt` dispatch): `actor_type = platform`, `actor_role = executor`, on behalf of the approval. FR-12 check = one query: no execution event with another actor.
5. Fix merge: `actor_type = user` (mapped through `user_identity`), `auth_method = external:git` noted in payload; unmapped → `external` and escalate (G12).
6. Business tables that need a database rule keep a typed FK as well (`approval.approver_user_id`, `incident.owner_user_id`, `diagnosis_feedback.by_user_id`). The event block is the source for "who did it" everywhere else.

Who-did-what map for the owner's list:

| Action | actor_type / role | Extra |
|---|---|---|
| Alert received | external / monitoring, ID = integration | auth_method webhook_hmac or webhook_token |
| Incident submitted | user / submitter | session_id, idempotency key in payload |
| Evidence collected | platform / evidence_collector | on behalf of tool_call; the requesting model call in causation ID |
| Hypothesis, diagnosis | agent / diagnoser (or platform / policy_gate for a rule) | model_call ID or rule ID |
| Review verdict | agent / critic | model_call ID |
| Policy check | platform / policy_gate | rule ID in payload |
| Approve / reject | user / approver | auth_method, reason |
| Dispatch, reconcile | platform / executor | on behalf of approval |
| Pipeline or config-store result | external / cicd or config_store | on behalf of execution_attempt |
| Verification | platform / verifier | — |
| Cancel, take-over, resolve, severity, ack | user / submitter or approver | reason |
| Config change | user / platform_admin | before/after, reason |
| Login, lockout | user (or `external` with attempted username when the user is unknown) | auth_method, IP in payload |

---

## 5. Proposed config architecture

### 5.1 The tension

- Q7.18: platform config lives in the repository, changed by reviewed PR.
- A5 SC-24 and A2 2.5: a cloud provider is enabled "through a reviewed configuration change, with an audit entry".
- A5 AST-10: prompts, policy rules and the tool allow list change only by reviewed PR.
- The owner now expects admin APIs and a data store for config.

### 5.2 Recommendation (not a decision): hybrid, split by risk

| Kind of config | Where | Changed by | Why |
|---|---|---|---|
| Prompts, policy rules, redaction rules, tool allow list per phase, escalation rubric | Repository (unchanged) | Reviewed PR + deploy | A5 AST-10. These are security controls (SC-07, SC-09, SC-13). Code review is the right gate. |
| Users, teams, members, service ownership, mappings, on-call (manual), external identities | Database | Admin API (G4, G5, G7, G8, G12) | Organization data. Changes often. Not a security control by itself. |
| Integrations (monitoring, logs, metrics, traces, error tracker, Git, CI/CD, config store, chat, pager, on-call), MCP servers, limits, timeouts, retention, grouping window, fallback team, login mode, SSO settings | Database | Admin API, every change audited with before/after | The owner's request. Operators change these without a release. |
| Cloud model provider **enable**, login mode change | Database | Admin API **plus a second platform admin approves** the change | Satisfies "reviewed" in SC-24 without a PR. Limits TA-8 (one rogue admin). |
| Secrets (webhook secrets, API keys, OIDC client secret, integration tokens) | Secret store only | Secret-store tools | SC-23. The database holds the secret **name** (reference) only. |
| Egress allow list | Network rules (Docker network / firewall) | Infrastructure change | SC-08 is outside the platform. A cloud provider needs this too, so enabling one is never a single database flag. |

### 5.3 Tables

Keep it small: four tables.

| Table | Columns (main) |
|---|---|
| `integration` | id, kind (monitoring, logs, metrics, traces, error_tracker, git, cicd, config_store, chat, pager, oncall), name, transport (http_api, mcp_http, webhook_in), endpoint, auth_secret_ref, next_secret_ref, next_valid_from, allowed_tools (JSONB, MCP only; must be a subset of the repository allow list), timeout_ms, settings (JSONB + schema_version), enabled, version |
| `model_provider` | id, adapter (openai_compatible, anthropic), hosting (self_hosted, cloud), endpoint, key_secret_ref, enabled (default false when hosting = cloud), version |
| `model_assignment` | role (diagnoser, critic, embedding), provider_id, model_name, version. Rule: critic (provider, model) ≠ diagnoser (provider, model); checked on every change and at start (SC-24, ST-17) |
| `platform_setting` | key, value (JSONB, Pydantic schema per key), version. Keys: `login_mode`, `sso` (issuer, client_id, client_secret_ref, scopes), `limits` (concurrency 3, queue 20, phase-1 5 min, investigation 20 min, incident 60 min, tool calls 30, GPU-min 10, tokens 200k/64k/32k), `approval` (revert valid 30 min, fix 24 h, backup after 10/15 min), `retention`, `grouping_window`, `fallback_team_id`, `source_timeouts` |
| `config_change` | id, target (table + key/id), before, after (secret refs only, never values), status (proposed, approved, applied, rejected), requires_second_admin, proposed_by, reviewed_by, reason, applied_at. Immutable after `applied` or `rejected`. Each state writes a platform-stream event. |

Effect on running incidents: the workflow reads `limits` and model assignments at incident start and stores the config version it used on the incident (`incident.config_versions` JSONB). A change applies to new incidents. Concurrency and queue cap apply at once.

### 5.4 Endpoints (all platform admin)

| Method | Path | Notes |
|---|---|---|
| GET/POST/PATCH | /v1/admin/integrations[/{id}] | If-Match version. Validates the endpoint against the egress list (warning only). |
| POST | /v1/admin/integrations/{id}/test | Runs a read-only health call. Suggested (not required). |
| POST | /v1/admin/integrations/{id}/rotate-secret, /finish-rotation | G17 |
| GET/POST/PATCH | /v1/admin/model-providers[/{id}] | Enabling a cloud provider creates a `config_change` in `proposed` |
| GET/PUT | /v1/admin/model-assignments | critic ≠ diagnoser check; 409 problem+json on violation |
| GET/PUT | /v1/admin/settings/{key} | Schema-validated; `login_mode` needs a second admin |
| GET | /v1/admin/config-changes?status= | — |
| POST | /v1/admin/config-changes/{id}/approve, /reject | A different platform admin than the proposer; reason required |

### 5.5 Implications for A5 (for Chirag to confirm)

| A5 item | Change needed |
|---|---|
| SC-24 | "Through a reviewed configuration change" → "through the admin API; a second platform admin approves; a config-change event records before/after." Egress list and secret store parts stay. |
| AST-10 | Unchanged. Add a new asset row: "Platform configuration in the database (integrations, models, limits, ownership)", property I, kept in PostgreSQL, changed only by admin API with audit. |
| TA-8 (rogue admin) | More reach now (integrations, ownership, on-call). Controls: second-admin review for cloud provider and login mode; audit with before/after; admin cannot approve (SC-04). Residual: a rogue admin can change ownership to make a friend an approver. Recommend: ownership changes for a service with an open incident do not apply to that incident (it keeps its start values, Q7.2). |
| SC-19 | "admin change" is already listed. Add "audit queries" and "config change before/after". |
| ST-17 | Add: enabling a cloud provider by one admin stays `proposed`; no traffic until a second admin approves and the egress rule exists. |
| New test (Suggested) | ST-19: a platform admin sets the critic model equal to the diagnoser model through the API → 409, no change, audit event. |
| Q7.18 log | "Not tables: platform config (repository)" → split as in 5.2. |

Alternative the team may prefer: keep cloud-provider enablement and login mode as repository files (reviewed PR), and put everything else in the database. This is simpler (no `config_change` approval flow). It keeps SC-24 unchanged. The cost: two places to look for config.

---

## 6. Alerts vs incidents

The model is sound:

- One `alert` row per `(source, external_alert_id)` (Q7.20). One incident groups many alerts by the open-incident partial unique index on `(service, environment, alert_rule)`. A duplicate becomes an alert row linked to the open incident, and evidence for it (FR-02). This matches A1 E6 and FR-02.
- The alert ID is a source reference only; the incident ID is platform-generated (Q7.1). Good: an engineer submission has no alert.
- Gaps: alert state and resolved deliveries (G14); alias mapping from alert labels to a service (G7); per-source secret and rotation (G6, G17).
- Check: the grouping key uses `alert_rule`, but an engineer submission has no rule. State what the key is for a submitted incident (recommend: submissions never group; Layer 7 Section D).
- Check: an alert that arrives after its incident is closed opens a new incident (the partial index covers open incidents only). State this, and link the two by `related_incident_id` (Suggested, not required).

---

## 7. Tables in the 34-list that look unused or redundant

| Table | Finding | Recommendation |
|---|---|---|
| oncall_snapshot | No source and no writer. Its purpose (who was on call when) is served by `approval` role-at-time and the routing event. | Replace with `oncall_shift` (G8). |
| knowledge_document | Used by retrieval, but no writer. | Keep; add the sync or upload path (G9). |
| service, environment, team, team_member, service_owner, service_dependency, service_repository | Used, but no write path. | Keep; add CRUD (G5, G7). |
| local_credential | Used only in own-login mode. | Keep. |
| session | Used for logout and revocation. | Keep; add `auth_time` (G21). |
| review | Overlaps `model_call` for the critic, but holds the verdict. | Keep. Name clash with "reviewed config change"; consider `critic_review`. |
| approval_request / approval / approval_use | Three tables, each justified by immutability and single use (Q7.23). | Keep. |
| event | Doubles as the audit record. | Keep; add stream, hash chain, actor block (G1–G3). |

No table in the list is unused by every feature. The new tables proposed here: `user_identity`, `oncall_shift` (replaces `oncall_snapshot`), `service_alias`, `service_environment_config`, `diagnosis_feedback`, `integration`, `model_provider`, `model_assignment`, `platform_setting`, `config_change` (Suggested: `alert_delivery`). Net: 34 − 1 + 10 = 43 tables.

---

## 8. Not checked

- The Layer 7 worksheet questions (PDF pages 30–35) were not read; this review checks feature coverage only, not worksheet completeness.
- Section D (events) and Section E (outbox) are not drafted yet, so event types and delivery were checked only against Q7.16.
- Figures in the artifacts were not rendered.
