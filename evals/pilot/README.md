# Pilot real de la v0.3 — 2026-09-19

S'ha creat un repositori Git local independent a partir dels fitxers de la plantilla
en desenvolupament, basada en `d1a5d10`. No s'ha inicialitzat el brief de la plantilla.
El projecte fictici Estudi Blau ofereix serveis i prepara un resum de contacte local,
sense enviar missatges, desar dades ni carregar recursos externs.

## Què s'ha executat

1. Sessió nova de Codex CLI `0.155.0-alpha.9.2`, Terra/medium: onboarding amb dades
   fictícies completes, generació de documents, Frontend Design, implementació HTML,
   comprovacions bàsiques i desament de pla/memòria. Pausa deliberada abans del navegador.
2. Una altra sessió nova, Luna/low: només se li demana reprendre el projecte, validar
   foundation/continuïtat i retornar l'acció pendent i una convenció amb font. No se
   li passa l'historial ni el text esperat. Recupera exactament la següent acció i
   distingeix onboarding complet de verificació de navegador pendent.
3. L'orquestrador aplica Webapp Testing amb Playwright instal·lat i Chromium
   `151.0.7922.34`. Primera passada: 8 de 9 comprovacions correctes; el nom amb només
   espais s'acceptava. Correcció local: `setCustomValidity` rebutja el nom buit després
   de `trim()`. Segona passada: 9 de 9 correctes. Revisió visual de captures de
   1280 px i 390 px, sense desbordament horitzontal ni contingut tallat observat.
4. La correcció invalida automàticament la memòria i les tasques que citaven el codi.
   Després de verificar de nou, es refresquen explícitament les fonts i el pla queda
   `complete`. [Estat intermedi obsolet](stale-after-fix.json),
   [pla final](corporate/project/work.json).

La represa de Luna és una prova de recuperació i validació de context en lectura,
no una implementació autònoma de tot el segon increment. L'orquestrador executa
la verificació al navegador i la correcció. No s'ha provat Pi en execució real.

## Observacions del runtime

| Sessió | Model registrat | Esforç | Durada CLI (s) | Tokens entrada | Entrada en memòria cau | Tokens sortida |
|---|---|---|---:|---:|---:|---:|
| Construcció | gpt-5.6-terra | medium | 198,855 | 426.513 | 391.168 | 9.548 |
| Represa | gpt-5.6-luna | low | 16,124 | 44.743 | 33.024 | 411 |

Models observats a `turn_context` dels rollouts propis, vinculats als IDs de
`thread.started`. Ús procedent de `turn.completed.usage`; durada mesurada pel procés
que llança el CLI. [Extracte revisat](runtime.json) amb hashes dels logs originals.
La sortida JSONL està documentada al [mode no interactiu de Codex](https://learn.chatgpt.com/docs/non-interactive-mode).

Els tokens d'entrada són acumulats al llarg de les crides de cada sessió: inclouen
instruccions, eines, resultats i context repetit. El límit de 10.000 caràcters afecta
només el resum de continuïtat. La memòria cau és un subconjunt de l'entrada i no se
suma una altra vegada. Les sessions usen `--ignore-user-config`, models explícits,
`workspace-write` i cap subdelegació; la prova de represa porta instrucció de només
lectura. No s'han desactivat regles ni permisos per executar el pilot.

No hi ha baseline aparellada, ni mostres suficients per atribuir estalvi a les skills
o comparar Terra amb Luna: fan tasques diferents. La correcció de l'orquestrador té
ús i durada desconeguts; el report els conserva com `null`. Aquest pilot tampoc
mesura el consum total de desenvolupar foundation. No prova que el sistema sigui
l'òptim ni constitueix una auditoria de seguretat.

## Evidències i reproducció

- [Primera verificació, amb fallada](first-verification.json).
- [Verificació final](final-verification.json) amb hash de l'HTML comprovat.
- [Resposta de la sessió nova](resume-answer.json).
- [Registres d'avaluació](records.json) i [report generat](report.json): conserven
  l'intent fallit, la correcció i els casos sense baseline.
- [Fitxers del producte](corporate/site/index.html), brief, documents i pla final
  són una instantània revisada; no s'inclouen logs ni historial de conversa.
  `docs/project/checks.md` conserva les comprovacions bàsiques de la primera sessió;
  `browser-verification.json` documenta la verificació posterior que les completa.
- [Manifest de la plantilla usada](template-manifest.json): hashes de la còpia
  executada abans dels darrers enduriments de validació d'entrada de la v0.3.

Sense serveis ni models:

```sh
python3 scripts/evaluate.py report --input evals/pilot/records.json
python3 scripts/continuity.py --root evals/pilot/corporate validate
```

Amb Node, Playwright i el seu Chromium ja instal·lats (no s'instal·len a CI):

```sh
node evals/pilot/verify.cjs evals/pilot/corporate/site/index.html .local/pilot-check
```

Si Playwright és a una instal·lació compartida, configura `NODE_PATH` amb la seva
ruta de paquets. Les captures es desen al directori de sortida local. Aquesta prova
usa `file://` perquè el pilot és estàtic; no valida servidors, desplegaments, correu
real, totes les combinacions de navegador ni una auditoria WCAG completa.

Per repetir l'experiment d'agents, crea un nou repo des de la plantilla, usa el brief
fictici d'aquí i demana implementar deixant la verificació pendent. Inicia després
un `codex exec` nou sense `resume` ni historial i demana recuperar l'acció pendent.
Recull els events amb `--json`, comprova el model del rollout d'aquella mateixa
sessió i executa independentment les comprovacions. Això consumeix quota i és manual.
