---
name: bw-help
description: "依据当前项目、已有计划和已加载 Skill，推荐下一步；明确要求执行时移交对应 Skill。"
disable-model-invocation: true
---

# BW Help

Derived from Matt Pocock’s ask-matt (MIT). Before stating what a skill does or recommending a step be skipped, **read that skill's actually loaded SKILL.md**: the summaries here are for orientation only. When a branch is controlled by a referenced file, read that reference too. A Guide or a similarly named global installation is not evidence that the packaged capability works.

## Orient before choosing a flow

1. Distinguish a question about a skill, navigation for a real task, and an explicit request to execute the next step. Without a repo, answer the question; do not create one to give advice.
2. In a project, inspect the effective instructions, actual document root and current status; open the named active plan, not every old plan. Check only task-related code, Git state, ADRs, research, solutions and evidence of an in-progress CE run. A status label alone is not an executable plan or a receipt. For unrelated questions this project scan is unnecessary.
3. Identify the next unresolved decision or unit, then inspect the registered target(s). Read the actual candidate package paths supplied by the host. When the request is about a specific skill, read its body and corresponding user Guide if available. A duplicate provider or missing dependency is a named blocker, not permission to install anything.

## The main flow: idea → ship

- **First connection.** For onboarding, recommend explicit `setup-bw-harness`. For changes to an established project's conventions, use its update branch. Do not interrupt a straightforward self-contained question for setup.
- **What is unsettled?** Ambiguous domain language, scope, or a lasting tradeoff → `grill-with-docs`. Alternative approaches or product directions → `ce-brainstorm`. Choose the interview that answers the open question; do not force both. Carry settled decisions into the same planning context.
- **What already exists?** If a CE run is active, follow `ce-work`'s input/recovery rules with its actual run state. If there is an unfinished implementation-ready plan, read the loaded [CE work input triage](../ce-work/references/input-triage.md) and recommend `ce-work` with the actual canonical plan path. Incomplete design/requirements → enrich that same plan using `ce-plan`; do not invent a second plan. Clear multi-stage work without a plan → `ce-plan`, then normal `ce-work`. A small bounded change can go directly to implementation and relevant validation.
- **Delivery.** Follow the selected native unit, verification, review and shipping path rather than forcing a special caller mode. For commit, push/PR, actionable PR feedback or monitoring, inspect the corresponding loaded `ce-commit`, `ce-commit-push-pr`, `ce-resolve-pr-feedback` or `ce-babysit-pr` entry. Account for actual remote, permissions, WIP and the user's requested scope.

## On-ramps and specialist branches

| Situation | Route; what settles it |
|---|---|
| Reproducible failure or unknown cause | `ce-debug`: existing failing observation, reproduction, root cause and regression evidence. A failed unit in an active plan stays attached to that plan. |
| Algorithm or research hypothesis | Inspect existing topic evidence and conditions; identify an independent vector, oracle or discriminating experiment. Small experiment directly, `tdd` for behavior, or CE planning/work for multi-stage work. A numerical result does not require a UX prototype. |
| A person must experience the interaction, feel or visual result to decide | Inspect `ce-prototype` and its scoping branch. Human judgment, not an automated test or the agent’s guess, settles it. Return the decision to the current contract/plan. |
| Domain or module vocabulary; intentional architecture improvement | `domain-modeling` for terms/ADRs; `codebase-design` for interface, seam and module depth; `improve-codebase-architecture` for a requested survey. These underpin other flows and are not mandatory refactors. |
| A verified fix corrected an assumption; stale knowledge store | For capture, pass the event to native `ce-compound` if its checkpoint has not handled it. For maintenance use its explicit `mode:refresh` (or installed alias). Do not make failed experiments into solutions. |
| Conflicting documents, mixed legacy material, end or interruption | `project-governance check`, `migrate`, or `close` respectively. An ordinary clean task rarely needs an extra permanent artifact. |
| New session, same project | Read status → linked plan and relevant knowledge → current code, Git and evidence. Resume the unfinished unit, not a fresh interview. Portable context when needed → `ce-handoff`. |

## Phase boundaries

At a genuine transition read [PHASE-BOUNDARIES.md](./PHASE-BOUNDARIES.md) before recommending a context switch. Keep the original reasoning from interview to planning when feasible. An active CE controller owns its own recovery, checkpoints and receipts.

## Return or hand off

An advice request ends with **current stage / one recommended next action in the host's actual syntax / evidence / input / done when / then**. Give a second choice only for a real fork. Be specific (the actual file, failure, or unanswered question) and remain read-only.

When the user explicitly asks to carry out the recommendation, perform the handoff in this turn: invoke the **installed** target using the host’s skill tool, or, in instruction-file hosts, read the registered target body as the host does and follow it with the selected input in its own role. This is an actual transition into the target, not implementation inside the router. Pass the concrete plan/path, scope, restrictions, settled decisions and evidence. Honor explicit-only invocation controls: a user request to run a named target is explicit; when a host genuinely requires user selection or offers no invocation route, say precisely what was blocked and give the one working invocation. Do not claim that printing a command executed it. Pi menus commonly expose `/skill:<name>`; use the actual registered namespaced command in Claude Code or the registered skill selector in Codex. Do not fabricate a slash command or run one in a shell.
