# 0004 — L'orquestrador a Cursor tria models Grok

- Estat: acceptat per a la implementació d'aquest producte
- Data: 2026-10-14
- Substitueix: cap
- Abast: selecció de models quan el motor és Cursor

## Context

agent-foundation neix amb correspondència nativa per a Codex (Luna, Terra, Astra).
Aquest producte es treballa a Cursor, i l'encàrrec demana que l'orquestrador pugui
triar models Grok. El router ja separa el nivell (light, standard, deep) del motor.

## Opcions

Deixar Cursor com a `other` i escriure els models a cada sessió. És portable, però
l'orquestrador no té una decisió revisada i pot improvisar un model.

Substituir els models de Codex pels de Grok. Trenca la configuració nativa de Codex
i els tests que comproven Luna, Terra i Astra.

Afegir un bloc `cursor` a la mateixa política, amb una capacitat revisada i fitxers
generats, i conservar Codex. El motor actiu tria el bloc.

## Decisió

S'afegeix `policy.cursor` i `engine: cursor`. Els slugs són els de subagents Grok
observats a Cursor en aquesta sessió: `cursor-grok-4.6-high-fast` per light i
standard, i `grok-4.7-xhigh` per deep. No es rebaixa un nivell si el model no hi és,
ni es canvia a un proveïdor que no sigui Grok des d'aquest bloc.

## Conseqüències i verificació

Cal regenerar `.cursor/` amb `render-cursor` quan canviï la política. `validate` i
els tests de `tests/test_routing.py` comproven la selecció, el bloqueig si falta el
Grok profund, i que el runtime no sobreescrigui els nivells. Si Cursor exposa un
Grok més lleuger o un esforç separable del slug, s'ha de revisar `CURSOR_CAPACITY`
abans de canviar light.
