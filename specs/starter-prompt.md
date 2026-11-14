# Starter prompt for a layer owner

Copy the block below into your coding agent. Fill in the three `<...>` values. Attach the worksheet PDF with `@` (use your own local path).

```text
@<path to AI_SRE_Engineering_Worksheet_1.pdf>

We are building an AI SRE, following the guidelines and artifact requirements in the attached worksheet. We build layer by layer. I own Layer <N> (<layer name>). Our team repo is this folder. Earlier artifacts and logs are in specs/layer-NN-<name>/. Read every artifact my layer is "Built from" before we start, and keep my layer consistent with them and with the reference scenario (Python web app, deployment changes a config value, HTTP 500s, monitoring detects it). Record any conflict as an explicit decision.

How we work:
1. One section of the layer at a time (the lettered sections A, B, C...). List all the questions of that section. I will bring my team's answers. You clarify, challenge assumptions, and point out what we missed, as the worksheet's method says (frame, knowns, unknowns, assumptions, converse, resolve, commit).
2. Don't go down rabbit holes. This is V1. Keep it simple. If something is for a later layer, say which layer and move on.
3. After each section, log the decisions in specs/layer-NN-<name>/conversation-log.md using the worksheet's format: one row per agent conversation with Questions, Agent, Conversation link, Decision reached, Open unknowns and owner, Artifact section. Also keep the "Where Claude and ChatGPT disagreed" list. Mark every assumption as provisional, with an owner and a condition to validate it.
4. When all sections are done, build the artifact as HTML in specs/layer-NN-<name>/artifact-N-<name>.html. It must follow the worksheet's artifact sheet strictly: the header (Team, Room, Date, Members), "Built from", the required-sections table (Required section, Questions this section answers, Done), the required sections with the exact names and order from the worksheet, the acceptance checks in the worksheet's exact words, then Reviewed by / Date. Put extra material (assumptions, decisions) in an appendix after that, not between sections.
5. Writing style: ASD-STE100 (Simplified Technical English), at least 80% in every artifact. Short sentences (about 20 words or fewer). One idea per sentence. Active voice. Use "must" for rules. Use one word for one meaning, and use the same term every time. No idioms, no filler, no marketing words. Define a technical term once, then reuse it. Use tables and lists for rules, steps and comparisons.
6. Diagrams: add software-engineering diagrams wherever they help the reader see the design, in every artifact. Choose the type that fits the content, and give each a number and a caption placed below the figure box (inline SVG, readable in light and dark mode):
   - use case diagram: actors and what they do with the system
   - swimlane / activity diagram: steps across people and components
   - sequence diagram: messages between components over time
   - state machine diagram: life cycle of an incident, task or approval
   - component / architecture diagram: parts and their links, trust boundaries
   - ER / class diagram: data model
   - flowchart / decision tree: rules and branching
   - deployment diagram: where things run
   Do not add a diagram that only repeats the text. Every diagram must stay consistent with the text and with earlier artifacts.
7. Before you call the artifact done, check it against the worksheet's acceptance checks and tell me which ones are still open.

Are you ready? Start with Section A of Layer <N>: list its questions.
```

## Notes for owners

- Use the worksheet text for the layer's section names. Do not invent sections.
- Layer 1 names no technology. From Layer 2 onward, technology choices are allowed, but record each with the assumption behind it.
- Commit your layer's folder to `main` when the artifact is done. Tell the next layer's owner.
- Order and owners: see [work-split.md](work-split.md).
