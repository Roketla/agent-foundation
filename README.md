# agent-foundation

Plantilla privada per començar webs corporatives, ecommerce i SaaS amb agents d'IA.
Inclou una entrevista inicial que es pot reprendre, skills seleccionades, perfils,
ADRs i validació automàtica. No imposa framework ni proveïdor; proposa una
configuració editable de models per a Codex.

## Com començar un projecte

1. A GitHub, usa **Use this template → Create a new repository** i tria la visibilitat
   del nou projecte. Clona **el repositori nou**, no treballis el producte sobre
   `agent-foundation`. També pots clonar manualment i canviar `origin` al nou repo.
2. Obre'l a Codex o Pi, accepta la confiança del projecte si el motor la demana i escriu:

   > Inicia aquest projecte. Llegeix AGENTS.md, pregunta'm què vull desenvolupar
   > i completa la configuració inicial abans de començar a implementar.

3. L'agent preguntarà objectiu, públic, MVP, acceptació i idiomes. Segons el perfil,
   completarà integracions, dades, restriccions i decisions pendents.
4. Les respostes es desen a `project/brief.json`. En completar-les es generen
   quatre documents a `docs/project/`. En sessions següents, l'agent reprèn el
   treball sense repetir l'entrevista.

A Pi també pots escriure `/init`: el prompt local ja inclou aquestes instruccions.
La descoberta de prompts requereix un projecte de confiança i que no estigui
desactivada; vegeu la [documentació de Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/prompt-templates.md).

**Clonar no executa cap IA.** L'entrevista comença en la primera interacció amb un
agent que llegeixi `AGENTS.md`. Si el motor no el descobreix, demana-li explícitament
que el llegeixi. `CLAUDE.md` és un enllaç d'instruccions per a motors que usin aquest
fitxer. Les versions actuals de Codex i Pi poden descobrir `.agents/skills/`;
altres eines poden requerir obrir el `SKILL.md` manualment.

## Requisits i comprovació local

Python 3.10 o superior, sense paquets addicionals per a l'onboarding. Git per al
control de versions. El motor d'IA s'instal·la i s'autentica fora del repositori.

```sh
python3 scripts/foundation.py status
python3 scripts/foundation.py validate
python3 scripts/routing.py validate
python3 -m unittest discover -s tests -v
```

La plantilla ha de romandre `uninitialized`. Per assajar sense convertir-la en un
projecte, usa els tests: treballen en directoris temporals. `ready` només indica
que la definició inicial és vàlida i s'han generat els documents.

## Què inclou

| Peça | Ubicació | Funció |
|---|---|---|
| Instruccions comunes | `AGENTS.md` | Entrada curta i lectura selectiva |
| Entrevista | `.agents/skills/project-intake/` | Preguntes, represa i generació |
| Perfils | `profiles/` | Corporate, ecommerce i SaaS |
| Skills | `.agents/skills/` | 7 adaptadors, activats segons la tasca |
| Fonts originals | `vendor/` | Versions fixades, dependències i llicències disponibles |
| Catàleg i integritat | `skills/catalog.json`, `skills/lock.json` | Procedència, opcions i SHA-256 |
| Rols d'agent | `agents/` | Coordinació, implementació i revisió sota demanda |
| Selecció de models | `routing/`, `scripts/routing.py` | Nivells, capacitats i decisions portables |
| Subagents de Codex | `.codex/` | Luna, Terra i Astra; màxim dos subagents simultanis |
| Decisions | `docs/adr/` | ADRs breus amb context i conseqüències |
| Operativa | `docs/templates/`, `docs/foundation/` | Specs, verificació, desplegament i actualitzacions |
| CI | `.github/workflows/foundation.yml` | Tests de la base i integritat del material vendored |

Les skills incloses són Clean Code, Frontend Design, Web Design Guidelines,
UX Heuristics, Security Audit de Cloudflare, Webapp Testing i Systematic Debugging.
Dues referències de Superpowers resolen les dependències de depuració. React Best
Practices i Web Performance consten com a opcionals, **no instal·lades**.

## Límits d'aquesta primera versió

- Els perfils orienten la definició i els controls; no són aplicacions ja implementades.
- Els rols són instruccions portables. El motor aporta execució, permisos i subagents.
  Codex té configuració nativa de models i concurrència; el router portable comprova
  les decisions abans de delegar. No hi ha un límit de tokens imposat per codi.
- La CI comprova foundation. Cada producte ha d'afegir els seus tests, compilació,
  secrets scanning i controls de dependències segons el stack escollit.
- No s'ha executat una auditoria de Cloudflare. La reproducció de vulnerabilitats
  necessita les capacitats d'aïllament que exigeix aquella skill.
- Les fonts de tercers conserven les seves condicions; consulta
  `THIRD_PARTY_NOTICES.md`. Les adaptacions locals són explícites als adaptadors.

Consulta [l'arquitectura](docs/foundation/architecture.md),
[la selecció de models](docs/foundation/model-routing.md),
[el manteniment de skills](docs/foundation/skills.md) i
[les actualitzacions de la plantilla](docs/foundation/updating.md).
