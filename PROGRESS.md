# Progress Tracker

The **only** place where project status is kept. Other files (README, work split) hold no status.
Update this file whenever a layer moves, a review runs, or an open item is closed.

_Last updated: 2026-11-14_

## Layers

| # | Layer | Owner | Status | Log | Artifact | Notes |
|---|---|---|---|---|---|---|
| 1 | Problem Discovery | Team | Done — review fixes applied; ChatGPT pass pending (H2) | [log](specs/layer-01-problem-discovery/conversation-log.md) | [A1](specs/layer-01-problem-discovery/artifact-1-product-requirements.html) | Revised after first review (recovery first, permanent fix with approval) |
| 2 | Scope and Constraints | Team | Done — review fixes applied; ChatGPT pass pending (H2) | [log](specs/layer-02-scope-and-constraints/conversation-log.md) | [A2](specs/layer-02-scope-and-constraints/artifact-2-scope-and-constraints.html) | |
| 3 | SRE Fundamentals | Dhanush (from Chirag) | Done — review fixes applied; ChatGPT pass pending (H2) | [log](specs/layer-03-sre-fundamentals/conversation-log.md) | [A3](specs/layer-03-sre-fundamentals/artifact-3-incident-and-evidence-catalog.html) | |
| 4 | Requirements | Dhanush (from Chirag) | Done — ChatGPT pass pending (H2) | [log](specs/layer-04-requirements/conversation-log.md) | [A4](specs/layer-04-requirements/artifact-4-requirements-specification.html) | 34 requirements, 5 provisional milestones |
| 5 | Threat Modeling | Chirag | Done — ChatGPT pass pending (H2); consumer review by Dhanush done, fixes applied (2026-11-14) | [log](specs/layer-05-threat-modeling/conversation-log.md) | [A5](specs/layer-05-threat-modeling/artifact-5-threat-model.html) | 18 abuse cases, 23 controls, 16 security tests. Closes M11 (author may approve the revert, not the fix), NFR-08 method (rules-only redaction, fail closed), A1 E8 check, secret store requirements |
| 6 | System Architecture | Dhanush (from Manish) | Done — ChatGPT pass pending (H2); consumer review pending (Rinisha, Irfan) | [log](specs/layer-06-system-architecture/conversation-log.md) | [A6](specs/layer-06-system-architecture/artifact-6-system-architecture.html) | 4 processes (API, worker, executor, sandbox runner), 18 components, 10 ADRs. Temporal + PostgreSQL waiting queue. Revised A2 model rule: cloud providers by config, off by default |
| 7 | Data, APIs and Events | Dhanush (from Manish) | Not started — inputs ready (A4, A6) | | | |
| 8 | Workflows and State Machines | Dhanush | Not started — prep allowed (Sections A, D) | | | Needs A6, A7 |
| 9 | Agent Architecture | Dhanush | Not started | | | Needs A3, A7, A8 |
| 10 | Inference and Retrieval | Irfan | Not started | | | Needs A2, A9 |
| 11 | Safe Remediation | Rinisha | Not started | | | Needs A5, A8, A9 |
| 12 | Reliability and Evaluation | All, by section (Dhanush merges) | Not started | | | Needs A3, A4, A10, A11 |
| 13 | Implementation Planning | Team | Not started | | | Needs A1–A12 |

## Reviews

| Date | Scope | By | Result |
|---|---|---|---|
| 2026-11-12 | A1 | Claude (same session) | 4 contradictions, recovery-first change, 11 new unknowns — all applied |
| 2026-11-13 | A1, A2, A3 + logs | Claude subagent (fresh context) | 3 High, 12 Medium, 9 Low — team approved fixes; all applied except H2 (team action) |
| 2026-11-14 | A5 + log, AGENTS.md | Dhanush with Claude (consumer review) | 3 Medium, 5 Low, 1 L6 action — [all approved and applied](specs/reviews/2026-11-14-a5-review.md) |

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
| Exact escalation rubric and gate limits (A1 E3) | Dhanush | Layer 9 |
| Self-hosted model choice, GPU sizing incl. HA copies | Irfan | Layer 10 |
| Approval channel, timeouts, write-tool enforcement, sandbox design | Rinisha | Layer 11 |
| Run the ChatGPT pass on A1–A3 decisions and record disagreements (H2) | Layer owners | Before submission |
| Fill "Reviewed by" and "Date" on A1–A3 | Team | Before submission |
| Single sign-on, secret store, signing key storage, egress rules (A5 SC-01, SC-06, SC-08, SC-14) | Dhanush | Layer 6 |
| Executor, reconcile, patch policy rules, branch protection, "author" for multi-commit deploys (A5 SC-04, SC-13 to SC-16, SC-20) | Rinisha | Layer 11 |
| Point A1 1.2 / 1.5 self-approval text to the A5 M11 decision (SC-04) | Chirag | Before submission |
| Team walk-through of A5 decisions (work-split rule 4; review R8) | Chirag | Before Layer 11 |
| Confirm A5 additions from Layer 6: AB-19, SC-24, ST-17 (cloud model providers) | Chirag | A5 walk-through |
| Rebalance load: Dhanush owns L3, L4, L6–L9 (311 Qs); Manish has no layer; Chirag owns L5 | Team | Before Layer 7 |
