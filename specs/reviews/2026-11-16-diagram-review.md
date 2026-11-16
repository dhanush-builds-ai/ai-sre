# Diagram review of A1–A9 — 2026-11-16

Scope: all 59 figures in Artifacts 1 to 9.

## Method

1. **Layout pass.** 9 agents (Sonnet), one for each artifact. Each one rendered its figures to PDF and fixed overlapping text, text outside its box, lines through boxes, and arrow ends.
2. **Content review.** 27 read-only agents (Sonnet), three for each artifact:
   - **correctness:** the figures against the artifact's own text;
   - **completeness:** can a reader get the key details from the figures alone (AGENTS.md rule);
   - **consistency:** the figures against the Built-from artifacts and the AGENTS.md standing decisions.
3. **Fixes.** 9 fixer agents (Sonnet), one for each artifact, worked from a curated list. Each one checked every item against the source text before it made the change.
4. **Final check by Claude:**
   - all 9 HTML files parse;
   - every SVG is well-formed;
   - no marker ID is used twice in one file;
   - figures are numbered 1 to N, with each caption directly below its figure;
   - the six most-changed figures were rendered and checked: A1 Fig 7, A4 Fig 2, A5 Fig 2, A6 Fig 7, A8 Fig 2, A9 Fig 4.

## Main corrections

| Artifact | Correction |
|---|---|
| A1 | Fig 7: a failed fix proof or a review rejection now closes the incident with the fix as a recommendation (section 1.3). Before, the figure escalated these cases. |
| A3 | Fig 3: the config arrow had the wrong direction. Fig 6: added the triggers "database migration in the deploy", "errors continue after the revert" and "source down". |
| A4 | Fig 2: rebuilt with the missing rules (evidence, approval, a branch for a failed verification, the queue, platform failures). QR-05: the backup times are now an explicit decision; they do not "match A3". |
| A5 | Fig 3: corrected the AB-02 label and the control IDs; added a second attack tree for data leaving the organization. Fig 2: the verifier now reads from Monitoring. The SC-24 and SC-25 rows moved into their control groups in the table. |
| A6 | Fig 1 and Fig 4: the API reply target is p95 ≤ 200 ms (QR-01); the acknowledgement target is p95 ≤ 30 s (NFR-04). The process table is corrected too. Fig 7: added verification as step 13 and the approval timeout. |
| A7 | The incident status `closed` is replaced by the A8 end states `resolved` and `cancelled`. This changes the unique index, the retention rule, the seal rule and the event catalog (`incident.closed` removed). Fig 5: only the workflow writes the incident status. |
| A8 | Fig 2: follows the A9 step order; adds the merge wait for a fix and the timeouts for each step. Fig 4: added the missing cancel transitions; a verification result of inconclusive counts as not recovered. Fig 5: the full list of approval guards. |
| A9 | Fig 3: tool calls now come from the workflow, not only from the diagnoser. Fig 7: field names now match A7. Corrected the revision rules and the sources of the limits. |

## Not changed: owned by later layers

| Finding | Owner |
|---|---|
| A2 Fig 3 shows two approvals for a fix. A2 2.3 says "the merge is the approval" (known conflict F7). | Rinisha, Layer 11 |
| A6: the worker holds read-only tokens, but it also pushes the fix branch and opens the PR. No artifact names the holder of the Git write credential (only branch and PR rights, no merge right). | Rinisha, Layer 11 |
| A1: no text row says what happens when a fix approval gets no answer. The figure escalates; the text must confirm this. | Rinisha, Layer 11 (A1 F1) |

## Skipped

Low-value additions that would crowd the figures. Examples: the severity modifiers in A3, the list of key assumptions in A2, and the full event catalog in A7.
