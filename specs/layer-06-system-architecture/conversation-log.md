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

## Where Claude and ChatGPT disagreed

ChatGPT pass pending (H2).
