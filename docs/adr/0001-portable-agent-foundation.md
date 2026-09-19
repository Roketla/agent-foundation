# 0001 — Base portable amb inicialització explícita

- Estat: acceptat per a la implementació de la plantilla
- Data: 2026-09-19
- Abast: foundation; no escull el stack dels productes

## Context

Cal reutilitzar processos entre webs corporatives, ecommerce i SaaS, amb poc context
inicial i sense lligar la plantilla a un sol motor o framework.

## Decisió

AGENTS.md és l'entrada comuna; skills curtes remeten a fonts fixades. Python estàndard
valida respostes i genera documents amb control de sobrescriptures. L'entrevista
s'inicia en conversar amb l'agent, mai mitjançant un hook de clone. El motor extern
aporta execució, permisos i delegació; la plantilla no n'implementa un de nou.

## Alternatives i conseqüències

Un runtime propi i un scaffolder per cada stack afegirien dependències abans de
conèixer els primers productes. Copiar totes les instruccions a AGENTS.md augmentaria
el context de cada tasca. Fonts vendored permeten treballar offline i revisar les
versions, amb el cost de mantenir-les i conservar-ne atribucions.

Els tests comproven inicialització, represa, validació, idempotència i preservació
de canvis manuals. Cal un primer projecte real per avaluar la qualitat de l'entrevista
i l'estalvi de recursos; els tests deterministes no proven el comportament d'un LLM.
