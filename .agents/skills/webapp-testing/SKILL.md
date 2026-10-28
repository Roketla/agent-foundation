---
name: webapp-testing
description: Verify local web journeys and error states, or reproduce a browser bug.
---

Read `vendor/skills/webapp-testing/SKILL.md`; helpers/examples are relative there.
Prefer the project's existing test framework and installed tooling. Vendoring this
skill does not install Playwright. Local adaptations: inspect unfamiliar helpers
before execution, avoid secrets in logs, and use observable UI conditions/assertions
instead of mandatory networkidle or arbitrary sleeps. Do not submit real transactions
or test production without applicable authorization. Report actual executed checks.
