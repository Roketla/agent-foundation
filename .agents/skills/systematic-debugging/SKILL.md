---
name: systematic-debugging
description: Diagnose a failure or unexpected behavior before changing code, with investigation proportional to the bug.
---

Read `vendor/skills/systematic-debugging/SKILL.md` and relevant companions.
Resolve cross-skill dependencies locally:
- superpowers:test-driven-development → vendor/skills/test-driven-development/SKILL.md
- superpowers:verification-before-completion → vendor/skills/verification-before-completion/SKILL.md

Do not execute examples verbatim: never dump environment variables, signing identities
or secret values from diagnostic examples. Log only necessary safe fields. Establish
a cause, make a bounded fix and verify it. Avoid unrelated changes or unnecessary
test frameworks. Dependencies are references, not always active skills.
