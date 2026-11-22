# Progress Tracker

The **only** place where project status is kept. Other files (README, work split) hold no status.
Update this file whenever a layer moves, a review runs, or an open item is closed.

_Last updated: 2026-11-22_

## Layers

| # | Layer | Owner | Status | Log | Artifact | Notes |
|---|---|---|---|---|---|---|
| 1 | Problem Discovery | Team | Done — review fixes applied; ChatGPT pass pending (H2) | [log](specs/layer-01-problem-discovery/conversation-log.md) | [A1](specs/layer-01-problem-discovery/artifact-1-product-requirements.html) | Revised after first review (recovery first, permanent fix with approval) |
| 2 | Scope and Constraints | Team | Done — review fixes applied; ChatGPT pass pending (H2) | [log](specs/layer-02-scope-and-constraints/conversation-log.md) | [A2](specs/layer-02-scope-and-constraints/artifact-2-scope-and-constraints.html) | |
| 3 | SRE Fundamentals | Dhanush (from Chirag) | Done — review fixes applied; ChatGPT pass pending (H2) | [log](specs/layer-03-sre-fundamentals/conversation-log.md) | [A3](specs/layer-03-sre-fundamentals/artifact-3-incident-and-evidence-catalog.html) | |
| 4 | Requirements | Dhanush (from Chirag) | Done — ChatGPT pass pending (H2) | [log](specs/layer-04-requirements/conversation-log.md) | [A4](specs/layer-04-requirements/artifact-4-requirements-specification.html) | 34 requirements, 5 provisional milestones |
| 5 | Threat Modeling | Chirag | Done — ChatGPT pass pending (H2); consumer review by Dhanush done, fixes applied (2026-11-14) | [log](specs/layer-05-threat-modeling/conversation-log.md) | [A5](specs/layer-05-threat-modeling/artifact-5-threat-model.html) | 20 abuse cases, 25 controls, 19 security tests. Closes M11 (author may approve the revert, not the fix), NFR-08 method (rules-only redaction, fail closed), A1 E8 check, secret store requirements |
| 6 | System Architecture | Dhanush (from Manish) | Done — ChatGPT pass pending (H2); consumer review pending (Rinisha, Irfan) | [log](specs/layer-06-system-architecture/conversation-log.md) | [A6](specs/layer-06-system-architecture/artifact-6-system-architecture.html) | 4 processes (API, worker, executor, sandbox runner), 18 components, 10 ADRs. Temporal + PostgreSQL waiting queue. Revised A2 model rule: cloud providers by config, off by default |
| 7 | Data, APIs and Events | Dhanush (from Manish) | Done — ChatGPT pass pending (H2); consumer review pending (Rinisha, Irfan) | [log](specs/layer-07-data-apis-events/conversation-log.md) | [A7](specs/layer-07-data-apis-events/artifact-7-data-and-interface-specification.html) | 35 tables (after the S1–S11 schema review), CloudEvents envelope, outbox via queued row + event table, idempotency table, SSE timeline. Gap review F1–F9 applied. Revised A5 login (SC-25) and config (SC-24) |
| 8 | Workflows and State Machines | Dhanush | Done — ChatGPT pass pending (H2); consumer review pending (Rinisha, Irfan) | [log](specs/layer-08-workflows-state-machines/conversation-log.md) | [A8](specs/layer-08-workflows-state-machines/artifact-8-workflow-specification.html) | Incident workflow + one child per action; 7 incident and 13 action states; signals not Temporal cancel; one retry owner; intent-then-dispatch reconciliation; no notifier spool (A7 updated) |
| 9 | Agent Architecture | Dhanush | Done (2026-11-16) — ChatGPT pass pending (H2); consumer review pending (Rinisha, Irfan) | [log](specs/layer-09-agent-architecture/conversation-log.md) | [A9](specs/layer-09-agent-architecture/artifact-9-agent-design-specification.html) | PydanticAI agents on Temporal; code coordinator; 4 agents (investigator, diagnoser, critic, fixer) + 3 code skills; baseline evidence by code; ≤ 3 rounds, ≤ 2 revisions, 30 requests / 30 tool calls; no agent write tools; escalation rubric closed (A1 E3). A7 and A8 updated |
| 10 | Inference and Retrieval | Irfan | Done (2026-11-17, PR #2 merged; review fixes applied by Dhanush) — open values in Appendix B (model choice, GPU sizing, HA, budget values, retrieval targets); ChatGPT pass pending (H2) | [log](specs/layer-10-inference-retrieval/conversation-log.md) | [A10](specs/layer-10-inference-retrieval/artifact-10-inference-and-retrieval-spec.html) | One gateway, 7 result statuses (A7 result extended: refused, error; gateway_status). Anthropic adapter present, off by default; cloud rules for every hosting = cloud integration; no fallback to another model. Temporal only retry owner; call timeout = min(60 s, time left) (A8 updated). Hard budget caps, no emergency reserve. One model request in flight per incident (A9). BM25 over Git runbooks, index revision on evidence. Raw evidence kept 1 year (A7 changed) |
| 11 | Safe Remediation | Rinisha | Not started | | | Needs A5, A8, A9 |
| 12 | Reliability and Evaluation | All, by section (Dhanush merges) | Not started | | | Needs A3, A4, A10, A11 |
| 13 | Implementation Planning | Team | Not started | | | Needs A1–A12 |

## Reviews

| Date | Scope | By | Result |
|---|---|---|---|
| 2026-11-12 | A1 | Claude (same session) | 4 contradictions, recovery-first change, 11 new unknowns — all applied |
| 2026-11-13 | A1, A2, A3 + logs | Claude subagent (fresh context) | 3 High, 12 Medium, 9 Low — team approved fixes; all applied except H2 (team action) |
| 2026-11-14 | A5 + log, AGENTS.md | Dhanush with Claude (consumer review) | 3 Medium, 5 Low, 1 L6 action — [all approved and applied](specs/reviews/2026-11-14-a5-review.md) |
| 2026-11-14 | L7 tables and API vs A1–A6 features | Claude subagent (fresh context) | 62 features, 28 gaps (11 High) — [F1–F9 approved and applied](specs/reviews/2026-11-14-l7-gap-fixes.md) |
| 2026-11-14 | L7 schema, over-engineering + full ERD | Claude subagents (Fable, fresh context) | 11 findings, 7 spec gaps; 45 → 35 tables — [S1–S11 approved and applied](specs/reviews/2026-11-14-l7-schema-overengineering.md); [ERD](specs/reviews/2026-11-14-l7-erd.html) |
| 2026-11-15 | Diagrams of A1–A8: do they explain the artifact; layout | Claude subagents (one per artifact) | No artifact was explained by its diagrams alone. Added an "at a glance" Figure 1 to each of A1–A6 and A8 and 3 new figures to A7 (contracts, API checks and roles, event order); improved and renumbered the rest; fixed overlaps and overflow. A1 swimlane step numbers now match the journey list (list step 17 split into apply and watch, so 19 steps) |
| 2026-11-16 | Diagrams of A1–A9: layout, correctness, completeness, consistency ([note](specs/reviews/2026-11-16-diagram-review.md)) | 9 layout + 27 review + 9 fixer subagents (Sonnet); Claude check | All 59 figures checked. Fixed wrong facts (A1 failed-fix path, A3 config arrow, A5 AB-02 label and IDs, A6 reply target 200 ms vs 30 s) and gaps in every artifact. A7 incident status `closed` replaced by the A8 end states (index, retention, events). Open: Git write credential holder; fix-approval no-answer rule; F7 (all Layer 11) |
| 2026-11-17 | PR #2 Layer 10: template, drift against A2/A4–A9, diagrams ([note](specs/reviews/2026-11-17-l10-pr2-review.md)) | Dhanush with Claude + 3 Sonnet reviewers | Request changes, then merged and fixed by Dhanush. Owner decisions D1–D4 (A7 result extended; no emergency reserve; raw evidence 1 year; dynamic call timeout). A7, A8, A9 updated; pending.md folded into Appendix B |
| 2026-11-21 | A2 decisions by Dhanush, carried into A1–A10 and the logs | Dhanush with Claude | Cloud provider is the default, self-hosted by configuration; USD 10 (cloud) or 20 GPU-minutes (self-hosted) per incident; 100 tool calls; a dummy application with simulated failures replaces synthetic fixtures; a web dashboard (A6 ADR-11, A5 SC-26, AB-21, ST-20, RR-10). |
| 2026-11-21 | A1 review by Dhanush: failures with no change to revert; Fig 3 step 1 | Dhanush with Claude | Decision: diagnose, recommend an action (restart, more memory), escalate; V1 keeps 2 write actions; a resource increase goes through the fix path. A1 1.3/1.5/1.7, Fig 1, Fig 3 updated. A7 and A9 add `diagnosis.cause_kind` and `recommended_action`; the A9 recovery map returns no action for `not_change`. |
| 2026-11-22 | A7 schema review by Dhanush: remove redundant tables, cancel API, SSE start | Dhanush with Claude | 35 tables → 29 (no service_alias, service_environment_config, config_change, approval_request, approval_use, verification). Explicit cancel endpoint. SSE first request, client restart and server restart rules. A8 and A9 names updated. |
| 2026-11-22 | A8 review by Dhanush: fix after merge, timeouts | Dhanush with Claude | A fix has no Execute step: the human merges and the existing CI/CD deploys; the platform reads the PR and the pipeline run, then verifies. Timeouts are 6 values in one setting `timeouts`; model request 180 s (was 60 s). A4 QR-03, A7, A9, A10 updated. |

## Open findings from the 2026-11-13 review

Proposed fixes and approval boxes: [specs/reviews/2026-11-13-review-fixes.md](specs/reviews/2026-11-13-review-fixes.md). Status: **team approved; fixes applied and verified by a fresh-context subagent on 2026-11-13** (second pass fixed the gaps it found: pipeline-only wording, data-rule wording, 20-minute limit, Incident B rollback ID, owners, M11 log row, Layer 10 note). Only H2 remains (team action).

| ID | Sev | Finding | Status |
|---|---|---|---|
| H1 | High | Config revert cannot work: re-running the pipeline at an old commit pulls the current bad config from the config store. A2 has no "restore config version" write action. | Fixed |
| H2 | High | Worksheet method needs Claude **and** ChatGPT per question; only Claude used, so the "disagreements recorded" check is ticked only by omission. No real conversation links. | Open — check 4 un-ticked in A1–A3; team must run the ChatGPT pass |
| H3 | High | Data-rule scope (does it cover existing external tools?) still open; A2 Figure 1 answers it by drawing everything inside the boundary. | Fixed |
| M1 | Med | A revert through the pipeline would wait for staging + QA at 2 AM; no emergency path defined. | Fixed |
| M2 | Med | Who merges the fix pull request, and does human approval equal PR approval? | Fixed |
| M3 | Med | A3 fixtures clash: A's broken config is v42, and B runs on "v42 unchanged". | Fixed |
| M4 | Med | A3 Incident A alert fires at 4 min, but the incident rule needs > 5 min. | Fixed |
| M5 | Med | A3 Incident C: code version "Unknown" vs "9c8d7e"; "errors spread across instances" not supported by evidence. | Fixed |
| M6 | Med | Layer 3 assumptions not closed (L2-A6 trace context, A1 E1 on-call, A1 A2 alert fields, L2-A1); Incident C contradicts L2-A6 without a note. | Fixed |
| M7 | Med | A2 says loop limits are "given" but has no step limit or cost value (A1 B3). | Fixed |
| M8 | Med | GPU capacity ignores HA copies; a 4th SEV1 can wait ~20 min in the queue, which breaks recovery-first. | Fixed |
| M9 | Med | A3 appendix states platform decisions; Layer 3 must not design the platform — reword as constraints forwarded to L4/L11. | Fixed |
| M10 | Med | Layer 1 log names a model (GLiNER / Jev) — Layer 1 must be technology-free; move to L9/L10 prep notes. | Fixed |
| M11 | Med | Self-approval allowed without rationale or a threat check (L5). | Fixed |
| M12 | Med | "Decision model" means two things (Type/System frameworks in A1; an ML model in A2). | Fixed |
| L1–L9 | Low | Overclaim in A1 1.3; chat shown as an interface in A2 Fig 1; A2 "Production access" mislabelled Fixed; L2-A9 stale; owners not matching work split; some log items missing from artifacts; A3 Q3.15 "matches A1" wording; reference-scenario fix scope; "Reviewed by" blank on all artifacts. | Fixed |

## Open items carried across layers

| Item | Owner | Due |
|---|---|---|
| Is every deployment and config change recorded with time and version, and where? | Dhanush | Layer 6/7 |
| Exact escalation rubric and gate limits (A1 E3) | Dhanush | Closed in L9 log Q9.38 (2026-11-16) |
| Cloud model choice (main and reviewer) and price configuration for the default; open-weight models and GPU sizing incl. HA copies for the self-hosted option; native JSON tool calling (L9-A1); need for a reasoning field; injection detector method | Irfan | Layer 10 |
| Confirm the defaults `deploy_wait` 30 min and `watch_period` 10 min, and how the existing CI/CD reports the deployment of a merged commit | Rinisha | Layer 11 |
| Confirm the write-once `approval` row (one row from request to decision) and single use by the partial unique index meet A5 SC-14 and SC-19 | Chirag | A5 walk-through |
| Confirm the 2026-11-21 A5 changes: SC-24 (cloud default), SC-26, AB-21, ST-20, RR-10 (provider keeps prompts) | Chirag | A5 walk-through |
| Confirm the dashboard technology (A6 ADR-11: server-rendered pages, htmx, SSE) and list the dashboard pages | Dhanush | Layer 13 |
| Build the dummy application (`shop-api`, `orders`) and the failure simulations for incidents A, B, C | Dhanush | Before the Q2.16 experiments |
| Approval channel, timeouts, write-tool enforcement, sandbox design | Rinisha | Layer 11 |
| Run the ChatGPT pass on A1–A3 decisions and record disagreements (H2) | Layer owners | Before submission |
| Fill "Reviewed by" and "Date" on A1–A3 | Team | Before submission |
| Single sign-on, secret store, signing key storage, egress rules (A5 SC-01, SC-06, SC-08, SC-14) | Dhanush | Layer 6 |
| Executor, reconcile, patch policy rules, branch protection, "author" for multi-commit deploys (A5 SC-04, SC-13 to SC-16, SC-20) | Rinisha | Layer 11 |
| Point A1 1.2 / 1.5 self-approval text to the A5 M11 decision (SC-04) | Chirag | Before submission |
| Team walk-through of A5 decisions (work-split rule 4; review R8) | Chirag | Before Layer 11 |
| Confirm A5 changes from Layers 6 and 7: AB-19, AB-20, SC-01, SC-04, SC-24, SC-25, AST-11, TA-8, RR-6, ST-17, ST-18, ST-19 | Chirag | A5 walk-through |
| Fix approval record: signed approval vs "merge is the approval" (A2 2.3, L7 F7) | Rinisha | Layer 11 |
| Git write credential for the fix branch and PR (holder, branch/PR rights only, no merge); fix-approval "no answer" rule in A1 text | Rinisha | Layer 11 |
| PydanticAI version pin and Temporal spike on incident A (L9-A3) | Dhanush | Layer 13 |
| Evaluation harness, simulation labels, seeded-fault simulations, final agent targets (L9-A2, A4–A7) | Irfan, Dhanush | Layer 12 |
| Rebalance load: Dhanush owns L3, L4, L6–L9 (311 Qs); Manish has no layer; Chirag owns L5 | Team | Before Layer 7 |
