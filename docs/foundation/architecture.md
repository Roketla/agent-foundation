# Arquitectura de la base

La capa comuna conté instruccions, processos i eines petites. El perfil afegeix
preguntes i controls de producte. El stack es decideix segons cada projecte; les
skills especialitzades s'afegeixen quan hi ha una necessitat real.

```text
Primera interacció amb l'agent
  AGENTS.md → status → project-intake → project/brief.json
                                      ↓
                            perfil + plan + init
                                      ↓
                       docs/project/* + state.json

Treball habitual
  AGENTS.md → status ready → brief + tasca → skill pertinent → verificació
```

## Estat i protecció de documents

`status` calcula l'estat a partir de les respostes, la seva empremta i l'existència
dels documents. No hi ha cap hook executat per Git en clonar ni daemon en segon pla.

- `uninitialized`: no hi ha cap resposta essencial.
- `in_progress`: hi ha respostes parcials o el brief ha canviat després de generar.
- `ready`: brief complet i documents inicials existents per aquella versió de dades.

`configure` valida tipus i camps abans de desar. `plan` mostra el contingut previst
sense escriure. `init` comprova totes les destinacions abans d'escriure, és repetible
amb les mateixes respostes i desa cada fitxer amb substitució atòmica. El conjunt de
fitxers no és una transacció: si el procés s'interromp, els documents parcials idèntics
es poden reprendre. Una interrupció a mig refresh pot requerir reconciliació manual.
No executis dos processos de configuració simultanis al mateix checkout.

Els hashes de state protegeixen contra sobrescriptures accidentals en un refresh;
no impedeixen editar documents després de l'inici ni són una defensa contra un
atacant amb accés d'escriptura al repositori. Els canvis manuals es conserven.

## Portabilitat i recursos

El motor d'IA proporciona conversa, model, eines i permisos. Codex i Pi comparteixen
les instruccions i les skills descobertes a `.agents/skills/`. No es forcen models,
proveïdors ni configuracions de confiança globals. Amb altres motors, l'entrada
explícita és llegir AGENTS.md i el SKILL.md necessari.

Només les metadades dels adaptadors han de ser descobertes inicialment; fonts i
referències es llegeixen sota demanda. No s'han definit promeses percentuals
d'estalvi. Per mesurar-lo, compara tasques semblants, tokens, temps i correccions
necessàries amb dades del motor, no amb una estimació de la longitud dels fitxers.

## Separació de responsabilitats

La plantilla genera definicions, no codi de producte. Les especificacions i ADRs
guiaran la implementació. Abans de producció, cada producte necessita CI real,
autorització, gestió de secrets, observabilitat i un procediment de restauració.
Les eines de foundation funcionen offline i no instal·len frameworks ni criden APIs.

Referències de compatibilitat: [AGENTS.md](https://agents.md/),
[skills de Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md).
