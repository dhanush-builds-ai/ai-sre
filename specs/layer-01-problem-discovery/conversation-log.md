# Layer 1 · Problem Discovery — Working Log

Focus rule: people, behaviour, outcomes. No technology/vendor names.

## Conversation Log

| Questions | Agent | Conversation link | Decision reached | Open unknowns and owner | Artifact section |
|---|---|---|---|---|---|
| Q1.1, Q1.2, Q1.3, Q1.4, Q1.5, Q1.6, Q1.7, Q1.8 (Section A) | C | (this session) | See "Decisions A" below | See "Open unknowns / assumptions A" below | 1.1, 1.2, 1.3 (partial) |
| Q1.9–Q1.15 (Section B) | C | (this session) | See "Decisions B" below | See "Open unknowns / assumptions B" below | 1.3, 1.4, 1.5 |
| Q1.16–Q1.19 (Section C) | C | (this session) | See "Decisions C" below | See "Open unknowns / assumptions C" below | 1.4, 1.6, 1.7 |
| Q1.20–Q1.22 (Section D) | C | (this session) | See "Decisions D" below | See "Open unknowns / assumptions D" below | 1.3, 1.4, 1.5 |
| Review of Artifact 1 (affects Q1.11, Q1.12, Q1.13, Q1.15, Q1.16, Q1.18, Q1.19, Q1.20, Q1.21, Q1.22) | C | (this session) | See "Decisions R" below | See "Open unknowns R" below | 1.1–1.7 |

### Decisions A

- **Q1.1 Problem:** The alert system already tells engineers *that* something broke. The unsolved problem is the gap between alert and diagnosis: engineers manually gather logs, recent changes, and past knowledge from separate places before they can form a cause. The alert is the trigger for our system, not the problem. Starting evidence: logs, recent changes, and the alert's breached rule/threshold.
- **Q1.2 Ownership:** Keep a maintained mapping of service → owning team → manager → team members. An incident is routed by looking up the affected service. Within the team, assignment considers availability.
- **Q1.3 Impact:** Alerts page people; severity is driven by business impact (payments/core flows are highest). Serious outages consume more engineering time and prioritisation. Users: impact varies by level — failed payments hurt the business directly; any visible failure erodes user trust. Engineers: a 2 AM page is fatiguing and mentally draining; higher severity means more cognitive load and pressure.
- **Q1.4 Today's manual work:** Collect logs and all related information, consolidate it, then form a hypothesis.
- **Q1.5 Automatable:** Fetching and consolidating evidence (logs, latest changes and their authors, past incidents, knowledge documents) and reasoning over it into a hypothesis.
- **Q1.6 Repetitive vs judgment:** *(Proposed by Claude — team confirmed)* Repetitive = gathering, correlating, summarising, ranking hypotheses. Judgment = deciding to change production, setting business severity, novel/ambiguous cases, customer communication.
- **Q1.7 Needed to find root cause:** Alert details and breached rule, logs, recent changes (with authors), past similar incidents, knowledge documents. *(Claude adds: metrics, config diffs, dependency health.)*
- **Q1.8 Cost of wrong fix:** Symptom may vanish temporarily and resurface; real cause stays unresolved and can escalate to a bigger outage; the unneeded fix can introduce new problems.

### Open unknowns / assumptions A (all provisional)

| # | Item | Type | Owner | Validate when |
|---|---|---|---|---|
| A1 | A service-ownership mapping exists or can be created and kept current | Assumption | TBD (team) | Before Layer 2 closes; check one real team |
| A2 | Alerts always reach the platform in a usable form (rule + threshold) | Assumption | TBD | Layer 3 alert catalogue |
| A3 | Ownership of an unmapped service / stale mapping | Unknown | TBD | Decide fallback in Layer 4 requirements |
| A4 | **Decided:** route to owning team + on-call; change author shown as evidence only, not as assignee | Decision | Team | Revisit if teams find it unhelpful in use |
| A5 | Customer/business impact measurement (users affected, revenue, SLA) | Unknown | Irfan (Layer 12) | Section C (success definition) |

### Decisions B

- **Q1.9 Immediately after incident:** An alert from the organisation's existing alerting channels (email, chat, ticket — any) is the trigger. The platform then starts investigating on its own: collect relevant documents and evidence, analyse recent changes, consult past incidents and knowledge documents.
- **Q1.10 Explanation → remediation:** The platform must be able to interact with the environment (read evidence, and make changes), observe the effect of its actions, and reason again — a loop until the goal is met, bounded by guardrails.
- **Q1.11 Authorisation:** Any write or system-affecting change happens only after explicit human approval. (Also answers Q1.10's control side.)
- **Q1.12 Verifying a repair:** Before applying: a separate reviewer agent with fresh context reviews the proposed change adversarially; the incident is reproduced in a non-production environment and the fix is shown to work there; human approves. *(Team confirmed: after applying, verify in production using the same signals that raised the alert — see gap below.)*
- **Q1.13 Missing telemetry:** Say plainly that there is not enough information to determine the cause; never guess confidently. Escalate to a human with a clear explanation of what was checked and what is missing.
- **Q1.14 Assistant vs platform:** An assistant mostly gathers, consolidates and reasons. A platform also acts on the environment, reacts to the results, and loops until the mission is done, inside enforced guardrails.
- **Q1.15 Trust:** Every claim carries its evidence (provenance); a complete audit trail; low confidence is stated and escalated rather than hidden.

### Open unknowns / assumptions B (all provisional)

| # | Item | Type | Owner | Validate when |
|---|---|---|---|---|
| B1 | A safe non-production copy of the app can reproduce incidents | Assumption | TBD | Layer 2 (Q2.14) |
| B2 | Post-repair check in production uses the original alert signals staying healthy for a set period | Decision (period TBD) | Team | Section C (success definition) |
| B3 | **Decided:** loop bounded by time, steps and cost; on limit, escalate to human. Numbers TBD | Decision | TBD | Layer 2 (Q2.16, Q2.18) |
| B4 | **Decided:** every change must have a defined undo path before approval. Reproduction-failure handling TBD | Decision | TBD | Q1.22 / Layer 11 |
| B5 | **Decided:** approver is either the on-call engineer or the service owner | Decision | Team | Q1.22 |

### Decisions C

- **Q1.16 Smallest useful product (V1):** Investigate, analyse, explain findings, suggest a fix, verify the fix before applying, apply only with human approval, then monitor the same signals to confirm resolution. When evidence is insufficient, say so and escalate instead of guessing.
- **Q1.17 Demo:** Use the reference scenario (config change → HTTP 500s). *(Team confirmed:)* alert arrives → owner identified → evidence gathered and shown → hypothesis with evidence and confidence → fix proposed and shown working in a non-production copy → fresh-context review → human approves → fix applied → same signals watched until healthy → incident summary with full audit trail. Plus a second short run with missing evidence, showing the "not enough information, escalating" behaviour.
- **Q1.18 Outcomes:** Time to diagnose, time to recover, how often the diagnosis was correct, and on-call time saved — each compared against today's baseline. *(Targets and baseline numbers TBD.)*
- **Q1.19 Prohibited:** (1) Any production change or deployment without human approval. (2) Leaking sensitive data or secrets. *(Team confirmed:)* (3) Acting outside the affected service. (4) Deleting data. (5) Disabling or silencing alerts and monitoring. (6) Changing access or permissions. (7) Claiming success without independent verification. (8) Applying any change that has no undo path (B4).

### Open unknowns / assumptions C (all provisional)

| # | Item | Type | Owner | Validate when |
|---|---|---|---|---|
| C1 | Today's baseline: time to diagnose and recover without the platform | Unknown | TBD | Before success targets are fixed; measure from past incidents |
| C2 | Target values for each outcome measure | Unknown | Team | After C1 |
| C3 | How "diagnosis was correct" is judged (who decides, against what) | Unknown (deferred, agreed) | Team | Layer 12 evaluation |
| C4 | Period signals must stay healthy after a fix (B2), and how long the monitor runs | Unknown | Team | With C2 |
| C5 | Prohibited list items 3–8 | Decision (confirmed) | Team | — |

### Decisions D

- **Q1.20 End-to-end sequence:** Same as the confirmed demo sequence (alert → owner → evidence → hypothesis + confidence → fix proven in non-production copy → fresh-context review → human approval → apply → watch same signals → summary + audit trail). *(Failure branches, confirmed:)* (a) Evidence insufficient → state so, hand to human with what was checked. (b) Fix fails non-production proof or review → no apply; report and escalate. (c) Errors persist after apply → use undo path, escalate. (d) Loop limit hit → escalate.
- **Q1.21 Preserving information:** A provenance record for every resource accessed and what was fetched, kept in a separate store so everything is traceable and auditable. *(Confirmed: one record per incident; entries are append-only; kept after the incident closes; sensitive values are never stored in it — consistent with the secrets prohibition.)*
- **Q1.22 Human checkpoints:** Approval of any fix; confirming severity; any write change; any irreversible change; any deletion. **Team decision: no allow list in V1.** Every production change goes through human approval, every time.

### Open unknowns / assumptions D (all provisional)

| # | Item | Type | Owner | Validate when |
|---|---|---|---|---|
| D1 | **Decided:** allow list removed. Every production change needs human approval | Decision | Team | Revisit after V1 if approval fatigue appears |
| D3 | Retention period for incident records | Unknown | TBD | Layer 2/7 |

### Decisions R (review of Artifact 1)

- **Contradictions fixed:** deletion and irreversible changes are prohibited in V1 (checkpoint rows removed). "Act outside the affected service" means a write; reading related services is allowed. Problem statement no longer promises "no risk"; it says no change without approval, and every change has an undo path.
- **Recovery first:** V1 restores service before root cause by reverting the most recent change to the last known-good version, with approval.
- **Permanent fix in V1 (team decision, revised):** after recovery, the platform proposes a permanent fix, proves it in a non-production copy, a different model reviews it, and the platform applies it only after human approval, then verifies the same signals again. If the fix fails proof or review, cannot be reproduced, or is declined, the service stays on the reverted version and the incident closes with the fix as a recommendation. If errors return after the fix, the fix is undone and the incident escalates.
- **Non-production reproduction** is not required for a revert (optional check only). It is required to prove a permanent fix.
- **Approval timeout:** if the approver does not answer in a set time, the backup approver is asked. Silence is never approval.
- **Severity** comes first from the alert; human confirms in parallel; it does not block.
- **Baseline fallback:** timed manual run of the reference scenario if no past incidents exist.
- **Cost per incident** added as an outcome measure.
- **Reviewer** uses a different model from the main agent.
- **E3 decision policies (researched):** Type 1 / Type 2 decisions (one-way / two-way door) decide how careful an action must be: Type 2 (reversible) actions such as a revert need approval; Type 1 (irreversible) actions are prohibited in V1. System 1 / System 2 thinking decides escalation: fast fixed rules first, then a rubric with context and guidance; a gate (low score, new kind of incident, conflicting evidence) sends the incident to a human.
- **E5 takeover:** a human can stop the platform or take over at any step.
- **E6:** related alerts are grouped into one incident.
- **E7:** a self-recovered incident is marked "recovered without action", watched, and still gets a root-cause report.
- **E8 (confirmed):** platform never reads secret values (name + changed/unchanged via fingerprint only); secrets and personal data removed before evidence is stored, shown, or sent to a model; record keeps source location + cleaned extract.
- **E9:** the approver can be the author of the change.
- **E10:** the platform listens for alert events and does not depend on any channel; findings go to the alert's channel and the incident record.
- **E11 (confirmed):** add wrong-change rate (revert or fix) and escalation rate as safety measures.
- **Owners named** for every assumption, by the layer where each is validated (see artifact appendix).

### Open unknowns R

| # | Item | Type | Owner | Validate when |
|---|---|---|---|---|
| E1 | On-call schedule exists and can be read | Assumption | Dhanush | Layer 3 |
| E2 | Past incidents and knowledge documents are accurate and current | Assumption | Irfan | Layer 10 |
| E3 | Exact escalation rules, rubric content, and gate limits. The method for the System 2 gate is chosen in Layer 9/10 (Layer 1 names no technology; candidate notes moved to `specs/layer-09-agent-architecture/prep-notes.md`) | Unknown | Dhanush (with Irfan for model choice) | Layer 9 / Layer 10 |
| E4 | "Normal level" for the recovery check; low-traffic handling | Unknown | Rinisha | Layer 11 |
| E6 | Alert-grouping rule | Unknown | Dhanush | Layer 7 |
| E7 | Watch period for a self-recovered incident | Unknown | Dhanush | Layer 8 |
| E8 | Secrets and personal data handling: check against threats | Decision | Chirag | Layer 5 |
| E11 | Wrong-change rate and escalation rate: set targets | Decision | Irfan | Layer 12 |
| F1 | Approval timeout values and backup approver order | Unknown | Rinisha | Layer 11 |
| F2 | Platform cost per incident | Unknown | Irfan | Layer 10 |
| M11 | Must self-approval be forbidden for SEV1? (separation of duties) | Unknown | Chirag | Layer 5 |

### Where Claude and ChatGPT disagreed
_Pending: ChatGPT pass not done yet (review finding H2)._


## Review fixes applied (2026-11-13 review, team approved)

- H1: revert also covers restoring the previous config version in the config store (same gate).
- H2: acceptance check 4 un-ticked until the ChatGPT pass is done.
- M10: model names removed from this Layer 1 log; moved to Layer 9 prep notes.
- M11: self-approval rationale recorded; separation-of-duties check sent to Layer 5 (Chirag).
- M12: "decision policies" = Type 1/2 and System 1/2; "decision model" is reserved for the ML classifier (Layer 2+).
- L1: "may not be the only cause" wording. L5: Chirag's items now owned by Dhanush. L6: A5 business-impact measure restored. L9: stale placeholder removed.
