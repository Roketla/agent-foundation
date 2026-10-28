# Claude Code, OpenAI Codex i Cursor

Guia de consulta revisada el 2026-10-28. Els tres motors treballen sobre el mateix
repositori i estat; no cal mantenir tres variants de la plantilla.

## Primera sessió

Crea un repositori a partir de la plantilla i obre'n l'arrel al motor escollit.
Python 3.10+ i Git són els requisits de la base. Instal·la i autentica el motor
amb el teu compte i accepta la confiança del projecte quan ho demani.

Escriu:

> Inicia aquest projecte. Llegeix AGENTS.md i la skill
> .agents/skills/project-intake/SKILL.md. Reutilitza les dades conegudes i pregunta
> només el que falta abans de desenvolupar.

Per mantenir la plantilla mateixa, indica que és una tasca de manteniment:
el seu brief ha de continuar `uninitialized`.

## Entrades i agents

| Motor | Instruccions | Agents natius | Principal |
|---|---|---|---|
| Claude Code | `CLAUDE.md` importa `AGENTS.md` | `.claude/agents/*.md` | Standard a `.claude/settings.json` |
| OpenAI Codex | `AGENTS.md` | `.codex/agents/*.toml` | Standard a `.codex/config.toml` |
| Cursor | `AGENTS.md` | `.cursor/agents/*.md` | Selecció de la sessió de Cursor |

Cada motor té `foundation-light`, `foundation-standard` i `foundation-deep`.
Els rols d'investigació, implementació i revisió es passen a l'encàrrec; els seus
mínims i models viuen a `routing/policy.json`. La generació és offline i no
inicia agents ni concedeix permisos. La [política de models](model-routing.md)
explica com observar capacitats i decidir si cal delegar.

Cursor també llegeix definicions compatibles d'altres motors. Els noms comuns
fan que la definició de `.cursor/agents/` prevalgui sobre la de Claude/Codex.
El manifest `.cursor/model-routing.json` és per al router de la base.

## Skills compartides i context

Hi ha una sola font a `.agents/skills/`: SEO, GEO, intake i els adaptadors de
qualitat. Codex i Cursor descobreixen les seves metadades; les instruccions i
referències es llegeixen quan calen. A Claude, si la skill no apareix al selector,
demana-la per ruta, per exemple:

> Revisa el SEO d'aquesta pàgina amb .agents/skills/seo/SKILL.md.

> Revisa la descoberta en cerca d'IA amb .agents/skills/geo/SKILL.md.

La càrrega per ruta permet compartir-les sense duplicar directoris de descoberta.
No s'importen totes les skills a `CLAUDE.md`. Consulta els detalls i límits a
[càrrega de context](context-loading.md).

## Represa amb un altre motor

Desa el progrés amb `scripts/continuity.py save` segons la
[guia de continuïtat](continuity.md), i confirma els canvis en Git. A la sessió
següent demana «Reprèn el projecte»: l'agent llegeix el mateix brief i executa
`scripts/continuity.py resume`. Les evidències modificades es tornen a validar.
Els comptes, la conversa privada i les credencials pertanyen a cada motor.

## Verificació

Executa `sh scripts/check-foundation.sh` amb Python compatible. Comprova el brief,
els perfils, la integritat de vendor, la continuïtat i que les configuracions dels
tres motors coincideixin amb la política. `render-codex`, `render-claude` i
`render-cursor` emeten les configuracions proposades com a JSON per revisar-les.

Obre una sessió nova per comprovar la descoberta dels tres agents i d'una skill
concreta. A Claude, `/agents` permet veure els agents carregats. A Codex, consulta
el diagnòstic del client i les metadades de la sessió. A Cursor, comprova els agents
descoberts i, si delegues, el model a la targeta de la tasca. Una configuració vàlida
no demostra accés al model: la subscripció, la versió i les regles de l'organització
poden alterar-lo. No declaris una execució remota només perquè un test local passa.

## Fonts

- [Codex: agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Claude Code: agents](https://code.claude.com/docs/en/sub-agents)
  i [skills](https://code.claude.com/docs/en/skills)
- [Cursor: agents](https://cursor.com/docs/subagents)
  i [skills](https://cursor.com/docs/skills); [AGENTS.md](https://cursor.com/docs/rules#agentsmd)
