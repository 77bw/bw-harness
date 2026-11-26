# Merge and verify ignore rules

Inspect existing rules and exceptions, including later overrides and nested files. Insert only missing applicable patterns, preserving user-specific exceptions and precedence. Common starting set:

```gitignore
.local/
.context/compound-engineering/
.compound-engineering/*.local.yaml
.env
.env.*
!.env.example
*.log
*.har
*.pcap
*.pcapng
.DS_Store
Thumbs.db
```

Recognized Python/Node projects may need their actual cache, environment or dependency directories ignored; do not blacklist data or all fixtures. Keep required redacted examples and tracked team CE config eligible for version control.

With `git check-ignore -v --no-index -- <path>` inspect the **winning pattern** on sample paths (including nested scratch, local config, .env, .env.example and any retained fixture); a winning negation is an exception. Verify positive/negative results with the nonverbose syntax and exit status. Use `git ls-files --cached -- <pathspecs>` to find already tracked sensitive or local material: ignore rules do not untrack it. Report paths, not contents. Neither silently untrack nor rewrite history. Preserve evidence.
