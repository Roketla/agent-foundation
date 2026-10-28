# Càrrega de context

Revisió: 2026-10-28. Aquesta guia és de consulta; no s'ha de llegir a cada torn.

## Contracte local

`AGENTS.md` conté l'entrada mínima. Llegeix el brief només per treballar en el
producte; les tasques de manteniment no han d'obrir una entrevista. Cerca rutes
abans d'obrir documents sencers. Usa `--help` abans d'inspeccionar un CLI.

Les descripcions de skills serveixen per seleccionar-les. Després es llegeix el
`SKILL.md` escollit i, només si la tasca ho exigeix, una referència concreta.
Les dues skills de cerca mantenen el detall a `references/`; una tasca SEO no
carrega GEO automàticament, ni a l'inrevés.

## Descoberta per motor

| Motor | Entrada i descoberta del projecte | Decisió local |
|---|---|---|
| Codex | Cadena d'`AGENTS.md` de l'arrel al directori actiu; noms, descripcions i rutes de `.agents/skills/` | Una sola entrada arrel i un sol directori de skills |
| Claude Code | `CLAUDE.md`; skills natives sota `.claude/skills/`. El suport directe d'`AGENTS.md` depèn de versió/configuració | `CLAUDE.md` importa només `AGENTS.md`. Les skills compartides s'obren per ruta quan no apareixen al selector |
| Cursor | Skills a `.agents/skills/` i `.cursor/skills/`, amb compatibilitat per altres rutes | No crear còpies a `.cursor/skills/` ni `.codex/skills/` |
| Pi | Noms, descripcions i rutes de les skills; també admet `.agents/skills/` | Una sola font. Els prompts de `.pi/prompts/` s'invoquen quan calen |

No s'han executat sessions de Claude, Cursor ni Pi per provar-ne la càrrega.
La taula combina inspecció dels fitxers de la plantilla amb la documentació oficial;
la configuració personal i les versions instal·lades poden canviar el resultat.

No hi ha còpies de skills en altres directoris de descoberta ni regles locals
`alwaysApply`. Els rols de `.codex/agents/`, `.claude/agents/` i `.cursor/agents/`
conserven la configuració generada: no se n'importa el contingut a `AGENTS.md`.
No afegim hooks que imprimeixin documents ni imports en cadena de manuals.

## Fonts de detall

| Necessitat | Font única |
|---|---|
| Dades i preguntes de producte | `project/brief.json` |
| Context manual durador | `docs/project/notes.md` |
| Selecció de models | `routing/policy.json` i `docs/foundation/model-routing.md` |
| Protocol de delegació | `agents/orchestrator.md` |
| Pla i memòria verificable | `docs/foundation/continuity.md` i `project/work.json` quan existeixi |
| Versió i actualitzacions | `foundation.json` i `docs/foundation/updating.md` |
| Fonts, referències i llicències | `vendor/` i `skills/lock.json` |

`docs/research/` i `evals/` són consulta històrica, no context del producte. No s'eliminen ni s'oculten del control de versions.
Els manuals detallats no es dupliquen en les instruccions d'entrada.

La reducció és del context aportat per aquest repositori, no del total de la
conversa: eines, plugins, instruccions globals i historial són capes separades.
Editar fitxers tampoc elimina el text ja llegit en aquest xat. Una sessió nova
aprofita l'entrada reduïda des de l'inici. Les mesures en bytes no són tokens.

## Fonts de descoberta

- [Codex: instruccions](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
  i [skills](https://learn.chatgpt.com/docs/build-skills): metadades inicials,
  cos de la skill quan se selecciona; les rutes duplicades poden afegir entrades.
- [Claude: memòria](https://code.claude.com/docs/en/memory) i
  [skills](https://code.claude.com/docs/en/skills): un import `@AGENTS.md` comparteix
  les instruccions; importar manuals amb `@` també els carregaria.
- [Cursor: skills](https://cursor.com/docs/skills).
- [Pi: skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md).
