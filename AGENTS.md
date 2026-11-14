# AGENTS.md

Guidance for any coding agent (Claude Code, Codex, Cursor, ChatGPT, and others) and for human contributors working in this repository. Claude Code reads it directly (checked with Claude Code 2.1.322), so the repo has no `CLAUDE.md`.

## What this repo is

A **design-spec repository** for an AI SRE (incident alert → diagnosis → approved, verified recovery). There is no application code, build, lint or test yet. The work is producing 13 layered specification artifacts that follow the *AI SRE Engineering Worksheet* (a PDF that is **not** in the repo — each layer owner attaches it from a local path). Implementation is planned in Layer 13.

Team: Chirag, Manish, Dhanush, Rinisha, Irfan. Layer owners and dependency order are in `specs/work-split.md`; the prompt a layer owner uses to drive a session is `specs/starter-prompt.md` — read it before working on any layer, it defines the working method.

## Layout and flow

```
specs/layer-NN-<name>/
  conversation-log.md      one row per agent conversation + assumptions table
  artifact-N-<name>.html   the layer's artifact (standalone HTML)
```

- `PROGRESS.md` is the only place status is tracked (layer status, review findings, open items carried across layers). Update it whenever a layer moves. Review notes live in `specs/reviews/`; layer prep notes in `specs/layer-NN-*/prep-notes.md`.
- A layer may start only when every artifact it is **Built from** exists (table in `work-split.md`). Read all of those artifacts first and stay consistent with them; record any conflict as an explicit decision.
- Reference scenario every layer must stay consistent with: Python web app, a deployment changes a config value, HTTP 500s, monitoring detects it.

## Working method (per layer)

1. Go one lettered worksheet section at a time (A, B, C…): list its questions, take the team's answers, then clarify, challenge assumptions and point out gaps. Keep it V1-simple; defer anything belonging to a later layer by naming that layer.
2. After each section, append rows to `conversation-log.md`: `Questions | Agent | Conversation link | Decision reached | Open unknowns and owner | Artifact section`. Agent is `C` (Claude), `G` (ChatGPT), or both, as the worksheet says. Keep the "Where Claude and ChatGPT disagreed" section.
3. Every assumption is **provisional**, with an ID (`L<N>-A<k>`), an owner, and a validation condition. From Layer 2 on, every item carries exactly one label: **Fixed requirement** (with source), **Decision** (with rationale), or **Assumption**.
4. When all sections are done, build the artifact HTML.

## Artifact HTML rules

- Structure, in this order: title + "Built from"; header table (Team, Breakout room, Date, Members); required-sections table (`Required section | Questions this section answers | Done`); the required sections with the worksheet's **exact** names and order (do not invent sections); "Acceptance checks before submission" in the worksheet's exact words; Reviewed by / Date; then an Appendix for assumptions and decisions (never between sections).
- Before calling an artifact done, check it against the acceptance checks and report which are still open.
- Copy the `<style>` block from the latest artifact (`specs/layer-02-…/artifact-2-…html`) so all artifacts share one look: CSS variables on `:root` with a `prefers-color-scheme: dark` override, `.sec` section badges, `.qs` "Answers: Q…" lines, `.L .F/.D/.A` label chips, `.note`/`.no` callouts, and `.fig` wrappers for diagrams.
- Diagrams are inline SVG using the shared `svg .box/.hum/.bad/.okb/.uc/.ln/...` classes (colours come from variables, so they work in light and dark). Each diagram gets a number and a caption (`.cap`), uses the type that fits (use case, swimlane, sequence, state machine, component, ER, flowchart, deployment), and must not just repeat the text.
- Writing style: ASD-STE100 Simplified Technical English (≥80%): sentences of ~20 words or fewer, one idea per sentence, active voice, "must" for rules, one term per meaning used consistently, no idioms/filler/marketing words. Prefer tables and lists for rules, steps and comparisons.

## Standing decisions to respect (from A1/A2)

- Layer 1 names no technology. Technology appears from Layer 2 on, each with its assumption recorded.
- Incident data must not go to an external party that the organization has not approved. Organization-approved hosted tools (monitoring, Git, CI/CD, error tracker, chat) are allowed through allow-listed network rules (A2 2.7). Models: V1 runs self-hosted open-weight models on existing GPUs. All model access goes through one inference gateway, which also supports cloud providers (Anthropic, OpenAI-compatible) by configuration only — **off by default**, enabled only by a platform admin through a reviewed config change, key in the secret store, host on the egress allow list, redaction before every call. No CPU fallback and no automatic cloud fallback (inference down → halt and escalate). Reviewer model must differ from the main model (A2 2.1, 2.5, L6 Q6.12).
- Agent never touches production directly and holds no production credentials. All writes go through checks and human approval enforced outside the agent; recovery = redeploy the last known-good artifact through the pipeline (emergency path skips staging and QA, because that artifact already passed them) **or** restore the previous config version in the config store; fix = branch + PR, merged by the human approver (never the platform) and deployed by the pipeline. Only the executor calls the pipeline or the config store (A2 2.3, A5 SC-15).
- V1: single tenant, Python apps only, synthetic sanitized fixtures, CLI + HTTP API (no dashboard), Docker (no Kubernetes), modular monolith, PostgreSQL, 3 configurable concurrent incidents (queued by severity, then arrival).

## Reading the worksheet

The PDF has 72 pages. Each layer is its questions, then a conversation-log template page, then the artifact sheet (required sections + acceptance checks). Layer start pages: L1 3, L2 7, L3 11, L4 16, L5 21, L6 25, L7 30, L8 36, L9 41, L10 47, L11 53, L12 60, L13 67. If your agent cannot read the PDF directly (no `pdftotext`/`pypdf` installed), extract the text with macOS PDFKit:

```sh
osascript -l JavaScript -e 'ObjC.import("PDFKit");
var d=$.PDFDocument.alloc.initWithURL($.NSURL.fileURLWithPath("<path to worksheet.pdf>"));
var o=[];for(var i=10;i<15;i++)o.push(ObjC.unwrap(d.pageAtIndex(i).string));o.join("\n")'
```

## Git

Contributors without write access work from a fork. Remotes: `upstream` = `dhanush-builds-ai/ai-sre` (team repo), `origin` = the contributor's fork. Work on a branch, sync with `git fetch upstream && git rebase upstream/main`, and open a PR with `gh pr create --repo dhanush-builds-ai/ai-sre --base main`. When a layer's artifact is done and merged, tell the next layer's owner.
