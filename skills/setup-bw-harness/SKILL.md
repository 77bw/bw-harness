---
name: setup-bw-harness
description: "接入 BW 工作流、合并已有项目约定、更新旧 BW 配置，或只读诊断项目接入情况。"
disable-model-invocation: true
---

# Setup BW Harness

Derived from Matt Pocock’s setup-matt-pocock-skills (MIT; revision and differences in the package lock). This is a prompt-driven skill, not a deterministic script. Explore, present what you found, confirm material choices with the user, then write. Preserve the project's code, tests and tools.

## 0. Establish scope

Resolve the target directory named by the user, else the working directory. Locate seeds beside **this loaded SKILL.md**, not relative to the target. Identify the installed BW copy of CE, not an unrelated global copy. Missing resources or ambiguous duplicate providers are blockers for the affected action.

- Explicit onboarding: use the default invocation for empty **or existing** projects. Edit project workflow documents, not application code. A request to preview proposals (in any mode) ends before the first write.
- `update`: reconcile existing BW settings and user edits in place.
- `check`: perform only steps 1 and 2 and read-only verification. No writes, Git init, installs, repairs, tests that produce artifacts, or status updates.
- `migrate`: inspect enough to identify the sources, then hand off to the installed `project-governance migrate`. Setup does not move historical knowledge.

If the input is only an obsolete generator command or flags (for example `new --api`), explain that the generator was removed. Stop without onboarding, writing or installing; a generator invocation does not authorize a different operation.

Confirm the project is not the installed pack or the wrong enclosing checkout. If inside a larger Git root, identify the intended boundary before writing there or initializing a nested repo. Ordinary work does not implicitly run setup.

## 1. Explore

Look at the current repo to understand its starting state. Read whatever exists; don't assume:

- Resolve Git top-level, worktree, branch, HEAD, staged/unstaged/untracked work, and remote presence. Redact credentials and query strings before returning any remote URLs; never print secrets.
- Follow the root instruction files and their includes. Which file actually contains the working agreements? Is there already an `## Agent skills` or a v1.0 BW block? Inspect links/symlinks without following them outside scope for writes.
- Open the actual CE config. Resolve `docs_root` from tracked-layout `.compound-engineering/config.yaml` only (otherwise `docs`); check real paths/components. Use the installed [CE health check](../ce-setup/scripts/check-health) (**without** cache warming, from the project) as applicable. Invalid root: name the invalid setting, stop artifact writes until corrected; a local override never repairs it.
- Locate existing domain rules, GLOSSARY or GLOSSARY-MAP, legacy CONTEXT/MAP or CONCEPTS, ADRs, workflow, tracker, status, active plans, topic research and solutions. Resolve actual domain paths separately from CE's root. Prefer single context unless domains and their owners genuinely differ. Absence of optional knowledge is normal.
- Inspect README, CI and manifests/scripts for real validation commands. Determine actually loaded Skill names, sources and relevant capabilities. Separate missing optional tools from onboarding blockers; don't provision unrelated software.

Done when you can distinguish **present / missing / conflicting / unknown**, with paths, and describe what stays untouched.

## 2. Present findings; confirm and edit

Show the proposed file/block changes (created, amended, preserved), target Git boundary and any meaningful original wording in conflict. Lead with the recommendation. Settle one material choice at a time. Explicit choices already made, including a request to apply standard setup, need no second confirmation. Stop before writing across unresolved conflicts.

Choose one substantive instructions file: retain an existing include or internal link to it; resolve conflicting independent files with the user; when absent, prefer AGENTS.md for shared use unless the user or host has chosen another. Select the actual domain layout, document root and tracker. Default work content is the CE plan. A configured remote is not evidence that the team wants issue synchronization; external trackers are for links and coordination. Do not initialize labels.

In `check`, return locations, evidence, impact and next action here. If preview-only, return proposed changes. Otherwise continue with the accepted scope.

## 3. Write using the bundled seeds

Read [domain.md](./domain.md), [workflow.md](./workflow.md), [status.md](./status.md), and [gitignore.md](./gitignore.md) **before** editing. Read [issue-tracker-local.md](./issue-tracker-local.md) or [issue-tracker-github.md](./issue-tracker-github.md) only when a distinct tracker note is useful. For an existing other tracker use its verified project instructions. Write real paths, confirmed constraints and actual status in the project's language. Templates guide edits; they are not evidence.

At the resolved root create/merge agents/domain.md, agents/workflow.md and status.md. When Matt already consumes a different domain pointer, maintain that substantive file and record its actual location in the shared entry; don't start a parallel tree. Only create agents/issue-tracker.md when needed. Use targeted edits: missing → add; equivalent → keep; nonconflicting new information → merge; conflicting → surface original vs proposal. Preserve comments, includes, user text and parallel work. For v1.0 use known BW-generated passages/provenance to retire its Python layout/test mandates, local-only Git policy, forced return-to-caller and obsolete generation calls; retain independent project requirements even if similar. Mixed or unattributed wording needs a decision.

If an `## Agent skills` block already exists in the chosen file, update its contents in-place rather than appending a duplicate. Use the following **semantics** with concrete project-relative paths (example for the default root):

    ## Agent skills
    - Domain language and ADRs: read docs/agents/domain.md before relevant design or diagnosis.
    - Workflow and document ownership: read docs/agents/workflow.md for routing, knowledge changes or completion.
    - Resume current work via docs/status.md and the linked active plan.
    - docs/solutions/ holds past solutions by category and YAML metadata (module, tags, problem_type); search it for relevant implementation or debugging work.
    - Plans and Git delivery follow CE and the project's existing configuration.

For CE config creation when needed read the installed [CE config template](../ce-setup/references/config-template.yaml); retain unrelated existing settings and comments. Read [CE repo fixes](../ce-setup/references/repo-fixes.md) Step 9 before merging the store pointer and directive. For a tracked store or an accepted store mention, use **Run automatically**, verbatim from the [CE compounding directive](../ce-setup/assets/compounding-directive.md), at the approved placement. Keep a semantically equivalent existing directive; respect an explicit project preference, flag conflicts. No second trigger in workflow or governance. Do not run full CE onboarding or start optional installation or standards interviews. Create no empty glossary, ADR, plan, research or solution. Mixed legacy knowledge goes to governance, not a wholesale rename.

## 4. Git readiness and verification

For an intended standalone project without a checkout, initialize Git once. Within an existing checkout preserve its history, remote, identity and WIP. Merge applicable ignore rules per the seed. Check identity and HEAD; when an initial commit is needed for a usable checkout and in scope, stage only named new baseline files after checking the index and diff. Never include pre-staged user changes in a baseline. If no identity, no approved boundary, or unrelated staged changes, report precisely rather than changing global config or sweeping changes into a commit. Remote creation is separate from local readiness.

Re-read the resulting authority/links, config resolution, and status. Verify ignore/exception samples and tracked-sensitive paths using Git; distinguish tracked risks from future ignores. Inspect the actual diff against the proposal (new files too). Verify repeat setup would edit the same block, not append another. Run only applicable project validation in the agreed scope; report the actual command/result or why not run. A project without business tests does not need a new toolchain. Do not replace application code or remove unique evidence to make a check pass.

## 5. Done

Return **Created / Updated / Preserved / Blockers / Checks / Next**, naming real paths, the consumer of each new entry, actual Git readiness, pending migrations and a usable next action in this host. Distinguish setup completion from application validation and remote delivery. No setup report file.
