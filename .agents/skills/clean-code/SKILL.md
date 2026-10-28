---
name: clean-code
description: Improve maintainability in changed code or a requested review; avoid unrelated repository-wide audits.
---

Read `vendor/skills/clean-code/SKILL.md` on demand; resolve supporting paths there.
Project instructions and user scope take priority. Keep checks proportional to the
diff. Do not automatically add architecture layers, audit the whole repo or install
dependencies. Use existing lint/type checks for mechanical rules; focus reasoning
on naming, boundaries, duplication and error behavior.
