---
name: security-audit
description: Review security-sensitive changes or perform an explicitly requested defensive audit using Cloudflare methodology. Use focused guidance by default.
---

Read `vendor/skills/security-audit/SKILL.md`; companions live in that directory.
Preserve its guidance/full-audit distinction. Loading a skill does not authorize
execution, delegation, external access or a complete audit. Follow the platform's
permissions and delegation rules. Verify every upstream sandbox requirement before
executing target-controlled code. If unavailable, continue safe source inspection,
mark affected conclusions needs_validation and do not claim a complete audit.
Docker defaults and prompt instructions are not proof of enforced isolation.
