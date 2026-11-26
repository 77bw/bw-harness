# Research claims and evidence

Locate the existing note for the object or stable topic. Merge a changed claim into that note, preserving superseded conditions; avoid one file per run. Identify object/version, relevant configuration, input population and what the result does **not** cover. Link a tracked, synthetic or redacted evidence reference and the precise check/command, test-vector ID or revision. State offline vs simulated vs real integration separately; a green simulation alone does not establish production behavior.

| Claim state | Minimum evidence |
|---|---|
| VERIFIED | Observed result and checkable source or repeatable check **under stated conditions**; name the actual outcome. |
| HYPOTHESIS | Proposed explanation plus the next discriminating observation or experiment. Do not write it as a glossary fact or a solved learning. |
| REFUTED | Concrete counterexample/negative result, method and the conditions under which it rules the claim out. |
| STALE | Previous evidence or revision and what changed enough to require a new check. Keep the old claim and limits understandable. |

Example, using synthetic data: “REFUTED — batches always retain input order in simulator 1.2 with two workers. Vector order-02 produced B,A for A,B. This does not test one worker.” If the new version changes scheduling, mark the extension to the new version STALE pending rerun instead of retroactively deleting the observation. If private raw evidence cannot be published, keep it in the controlled location and identify a sanitized reproduction or describe the access/evidence gap.
