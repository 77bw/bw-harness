# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase. Use the project's actual locations when adapting these rules.

## Before exploring, read these

- **`GLOSSARY.md`** at the repo root, or
- **`GLOSSARY-MAP.md`** at the repo root if it exists: it points at one glossary per context. Read each one relevant to the topic.
- **ADRs**: read decisions that touch the area you're about to work in. Use the project’s existing decision directory and, in multi-context repos, the mapped domain's scoped decisions. The default single-context layout is root glossary + `docs/adr/`; multiple domains can each have their own glossary and decisions without sharing a source layout.

If any of these files don't exist, **proceed silently**. Domain modeling creates them lazily when terms or decisions actually get resolved. Do not leave an empty glossary or a placeholder decision.

## Use the glossary's vocabulary

When naming a domain concept in a plan, hypothesis, test, or review, use the canonical term and respect its disambiguated scope and avoided synonyms. A missing word may be an invented synonym or a real modeling question. Distinguish them using domain evidence. CONTEXT, CONTEXT-MAP and CONCEPTS are historical inputs for classification; two conflicting definitions do not both become current.

For planning or debugging a researched topic, consult its research note and relevant solutions. An experimental result is not itself a domain definition. Keep conditions, negative results and unknowns with the research.

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> Contradicts ADR-0007 (event-sourced orders); the newly observed constraint is … .
