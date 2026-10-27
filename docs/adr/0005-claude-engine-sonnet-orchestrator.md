# 0005 — Motor Claude amb Sonnet com a orquestrador

- Estat: acceptat
- Data: 2026-10-26
- Substitueix: cap (complementa 0002 i 0004)
- Abast: selecció de models quan el motor és Claude Code

## Context

El router ja separa nivell (light, standard, deep) i motor, amb blocs per a Codex i
Cursor. Aquest producte es treballa amb Claude Code i vol Sonnet com a orquestrador,
amb models més barats o més potents segons la tasca.

## Decisió

S'afegeix `policy.claude`: light = claude-haiku-5-5 (low), standard = claude-sonnet-5-5
(medium) i deep = claude-opus-5-5 (high). Sonnet és el model per defecte del projecte
(`.claude/settings.json`) i per tant l'orquestrador. S'afegeix `policy.role_floors`
(implementer light, researcher standard, reviewer deep) per a tots els motors, de
manera que una revisió no la fa mai el model barat. Es conserven Codex i Cursor.

## Conseqüències i verificació

Cal regenerar `.claude/` amb `render-claude` quan canviï la política. `validate` i
`tests/test_routing.py` comproven la selecció per nivell, el bloqueig si falta Opus,
el mínim per rol i que el runtime no sobreescrigui els nivells. Opus és més car:
si el cost dels revisors esdevé un problema, es revisa `role_floors` amb dades de les
mesures d'`evals/`, no a ull.
