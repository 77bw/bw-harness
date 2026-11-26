# Phase boundaries

A **phase** is a chunk of work inside a session: the interview, the implementation, the QA. The decision to change contexts belongs at the gap between completed phases. Mid-phase, continue or split a bounded side task; keep the parent reasoning and CE run alive.

## The tree

Work top to bottom at the boundary. The first **yes** wins.

1. **Can you continue in this session?** If the next phase needs the current one as its primary source, or there is enough useful context to finish it reliably, continue. An interview → planning transition usually needs the actual tradeoffs, not a compressed guess. There is no fixed token threshold.
2. **Is the context genuinely irrelevant to what comes next?** A fresh context is cheap only when the old reasoning is disposable. Before changing, confirm that accepted decisions, evidence and the next unit can be located. Never discard a pending decision or detach a native run just to tidy chat.
3. **Does the work need to travel?** When changing host, repo, or person, or passing a portable side investigation, use the installed `ce-handoff` if needed. Carry pointers and their significance. If the same project's plan and status suffice, do not create a duplicate permanent handoff.
4. **Can a bounded task run independently?** Delegate a task with clear inputs and a checkable result using the host's supported subagent mechanism. Preserve the parent session; do not substitute a new controller for an existing CE one.
5. **Otherwise, condense at the boundary.** Use the host's supported context feature; preserve accepted decisions, conditional research evidence, relevant references, blockers and the next action. Distinguish hypotheses from facts. When reopening, recheck against Git and current artifacts.

Every substitution of a summary for the actual conversation loses some reasoning. Do not reduce a CE run ID, verification contract or receipt to a generic “done”; use its source when resuming.
