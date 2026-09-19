# Selecció de models i subagents

La política comuna és `routing/policy.json`. El rol (investigador, implementador o
revisor) és independent del nivell de capacitat. `scripts/routing.py` comprova el
pla de delegació; el motor l'executa. El script no crida models ni transmet dades.

| Nivell | Codex | Esforç | Treball |
|---|---|---|---|
| light | gpt-5.6-luna | low | Cerca delimitada, extracció, documentació i petits canvis verificables |
| standard | gpt-5.6-terra | medium | Funcionalitats, integracions, tests i depuració habitual |
| deep | gpt-6-astra | high | Arquitectura, risc elevat, ambigüitat i problemes entre components |

Terra és el valor inicial del principal. Una sessió existent o selecció explícita
del client pot prevaler; el repositori no canvia retroactivament el model actiu.
Les tasques no passen obligatòriament per tres models. Risc o incertesa alta porten
directament a deep. Un intent fallit escala almenys un nivell, fins a deep; després
de dos intents fallits cal revisar causa i abast. Permisos, manca d'eines o requisits
contradictoris no es resolen automàticament amb un model més potent.

## Codex: configuració nativa

`.codex/config.toml` defineix el principal, el subagent per defecte i un màxim de dos
subagents simultanis. `.codex/agents/` defineix foundation_light, foundation_standard
i foundation_deep amb model i esforç explícits. No altera permisos, credencials ni
proveïdors globals. Els agents hereten les polítiques de la sessió: un rol de lectura
és una instrucció de treball, no una sandbox addicional.

La configuració deriva de policy. `python3 scripts/routing.py validate` detecta
divergències. Per canviar models/límits, modifica policy, executa `render-codex`,
revisa el JSON retornat i actualitza els quatre fitxers amb l'autorització d'escriptura
del teu entorn. No es sobreescriuen configuracions automàticament.

En un checkout de confiança, comprova la fila config de `codex --strict-config
doctor --summary`. El diagnòstic també comprova serveis externs: un error de xarxa
no és necessàriament un error de configuració. `codex debug models` mostra el catàleg, però no garanteix accés
per al compte ni model efectiu: comprova les eines/metadades de la sessió. Obre una
tasca nova si la sessió existent encara no veu els nous agents.

Fonts: [subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[configuració](https://learn.chatgpt.com/docs/config-file/config-reference).

## Contracte portable

L'agent prepara `.local/runtime.json` amb capacitats observades en cada sessió.
`.local/` està ignorat per Git. `routing/runtime.example.json` només és un esquelet:
la disponibilitat és desconeguda i no autoritza delegació.

- `engine`: codex, pi o other.
- `inventory_source`: session només si s'ha observat accés real en aquesta sessió;
  catalog si només hi ha un catàleg; unverified si es desconeix.
- `available_models`: IDs exactes i `efforts`, una llista d'esforços suportats.
- `current_model`: model efectiu; buit si es desconeix.
- `current_effort`: esforç efectiu; buit si es desconeix. Poder suportar high no
  demostra que la sessió l'estigui utilitzant.
- `can_spawn` / `can_select_model` / `can_select_effort`: capacitats observades.
- `max_parallel_subagents`: capacitat observada del motor; es pren el mínim amb
  el límit de policy. Usa zero si no es poden iniciar subagents.
- `tiers`: per Pi/altres, llistes ordenades de `{model, effort}` per nivell. L'ordre
  és la preferència de cost/qualitat revisada pel projecte. A Codex, omet aquest
  camp: es deriva de policy i es rebutgen sobreescriptures dins de runtime.

Els nivells natius es contrasten amb CODEX_CAPACITY a scripts/routing.py, una
classificació revisada, no un catàleg viu. Un model nou requereix revisar aquesta
classificació i els tests, no només canviar-ne el nom al JSON. Els mínims d'esforç
natius són low/medium/high. Altres motors normalitzen els seus esforços a les
etiquetes admeses només quan n'han comprovat l'equivalència; sense aquesta evidència
han d'indicar que la selecció no està disponible.

No dedueixis equivalències dels noms comercials. Classifica amb documentació,
capacitats i proves del projecte. Sense model o esforç compatible, es bloqueja
la delegació: no es rebaixa silenciosament el nivell necessari.

```sh
python3 scripts/routing.py doctor --runtime .local/runtime.json
python3 scripts/routing.py route --runtime .local/runtime.json --task .local/task.json
```

`doctor` valida declaracions i mostra correspondències; no verifica credencials
ni accés remot. `route` retorna JSON i codi 0 per spawn/current, 2 per
wait/handoff/blocked/stop i 1 per dades invàlides. Mai executa el pla.

La tasca segueix `routing/task.example.json`. Actualitza comptadors i intents abans
de consultar. El handoff només conté objectiu, rol, rutes, acceptació i context:
no copiïs transcripcions, secrets o fitxers sencers sense necessitat. El coordinador
aplica la decisió amb les eines reals i comprova el resultat de l'execució.

## Pi i altres motors

Pi comparteix AGENTS.md i les skills, però no incorpora subagents. Per defecte,
`can_spawn` és false. Observa l'inventari amb les eines del motor i `pi --list-models`.
Declara delegació només si hi ha una extensió instal·lada i operativa.

Amb handoff, selecciona el model en una sessió adequada. A Pi, la CLI admet
`pi --model provider/model --thinking nivell`: inicia una sessió nova, no una
col·laboració amb el principal. Aquesta versió no instal·la una extensió de subagents
Pi ni inicia processos d'IA automàticament. Vegeu la
[documentació de Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/README.md).

Altres motors consumeixen el mateix contracte. Si no poden canviar model o delegar,
retornen current/handoff segons la capacitat del model actual. Escriure el nom d'un
model al prompt no significa executar-lo.

## Pressupostos i evidència

| Control | Aplicació real |
|---|---|
| Dos subagents oberts | Configuració nativa Codex; router amb comptador observat als altres motors |
| Una generació de delegació | Router i instruccions als fills; no és un bloqueig global del motor |
| Dos intents fallits | Router amb historial proporcionat pel coordinador |
| 8.000 caràcters de handoff | Router rebutja context excessiu |
| 6.000 caràcters de resposta | Instrucció al fill; no trunca resultats executats |
| Tokens/euros | Sense límit dur; token_budget és null i es rebutgen límits ficticis |

El router no és un servei de reserves concurrent i no intercepta qui se'l salta.
El coordinador serialitza decisions de spawn i usa l'estat real. Per imposar despesa
caldria un executor que interceptés totes les crides i mesurés ús del proveïdor;
aquesta plantilla reutilitza l'execució nativa del motor.

Mesura resultat acceptat, reintents, tokens quan hi siguin, durada i intervenció
humana en tasques equivalents. No converteixis quotes de subscripció en preus API.
Els tests comproven decisions i límits, no qualitat dels models o percentatges d'estalvi.
