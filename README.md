# AI SRE

An AI Site Reliability Engineer: from an incident alert to a verified recovery. We build it layer by layer, following the *AI SRE Engineering Worksheet* (13 layers, 13 artifacts).

## Layout

Each layer has its own folder under `specs/`:

```
specs/layer-NN-<name>/
  conversation-log.md      decisions, open unknowns, owners (worksheet log format)
  artifact-N-<name>.html   the layer's artifact, using the worksheet's required sections
```

| # | Layer | Central question | Artifact |
|---|---|---|---|
| 1 | [Problem Discovery](specs/layer-01-problem-discovery/) | What problem are we actually solving? | A1: Product Requirements Document (`artifact-1-product-requirements.html`) |
| 2 | [Scope and Constraints](specs/layer-02-scope-and-constraints/) | What are we allowed to build? | A2: Scope and Constraints Document (`artifact-2-scope-and-constraints.html`) |
| 3 | [SRE Fundamentals](specs/layer-03-sre-fundamentals/) | How does an incident actually happen? | A3: Incident and Evidence Catalog (`artifact-3-incident-and-evidence-catalog.html`) |
| 4 | [Requirements](specs/layer-04-requirements/) | What must the system do, and how well? | A4: Requirements Specification (`artifact-4-requirements-specification.html`) |
| 5 | [Threat Modeling](specs/layer-05-threat-modeling/) | What can go wrong? | A5: Threat Model (`artifact-5-threat-model.html`) |
| 6 | [System Architecture](specs/layer-06-system-architecture/) | What components do we need? | A6: System Architecture Document (`artifact-6-system-architecture.html`) |
| 7 | [Data, APIs and Events](specs/layer-07-data-apis-events/) | How is the incident lifecycle represented as data? | A7: Data and Interface Specification (`artifact-7-data-and-interface-spec.html`) |
| 8 | [Workflows and State Machines](specs/layer-08-workflows-state-machines/) | How does long-running work survive failure? | A8: Workflow Specification (`artifact-8-workflow-spec.html`) |
| 9 | [Agent Architecture](specs/layer-09-agent-architecture/) | How does the system investigate like an engineer? | A9: Agent Design Specification (`artifact-9-agent-design-spec.html`) |
| 10 | [Inference and Retrieval](specs/layer-10-inference-retrieval/) | How do we run models reliably and give them the right information? | A10: Inference and Retrieval Specification (`artifact-10-inference-and-retrieval-spec.html`) |
| 11 | [Safe Remediation](specs/layer-11-safe-remediation/) | How does a recommendation become a controlled, verified change? | A11: Safe Remediation Specification (`artifact-11-safe-remediation-spec.html`) |
| 12 | [Reliability and Evaluation](specs/layer-12-reliability-evaluation/) | How do we establish that it works under realistic failure? | A12: Reliability and Evaluation Specification (`artifact-12-reliability-and-evaluation-spec.html`) |
| 13 | [Implementation Planning](specs/layer-13-implementation-planning/) | How do we build it? | A13: Complete Implementation Plan (`artifact-13-implementation-plan.html`) |

Progress (the only place status is tracked): [PROGRESS.md](PROGRESS.md)  
How to work in this repo (for any coding agent or person): [AGENTS.md](AGENTS.md)  
Work split and dependency order: [specs/work-split.md](specs/work-split.md)  
Starter prompt for layer owners: [specs/starter-prompt.md](specs/starter-prompt.md)

## Rules (from the worksheet)

- Work layers in order. A layer starts only when the artifacts it is built from exist.
- Every question gets an answer. Every artifact lists the questions each section answers.
- Every assumption is marked **provisional**, with an owner and a validation condition.
- Layer 1 names no technology. Technology choices start in Layer 2.
- Artifacts use the worksheet's section names and layout, in Simplified Technical English (roughly), with software-engineering diagrams where they help.
