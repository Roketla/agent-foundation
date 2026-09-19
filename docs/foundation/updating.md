# Evolució de la plantilla

`foundation.json` identifica la versió de partida. Els repositoris creats amb una
plantilla GitHub són independents: no reben automàticament actualitzacions.

Mantén agent-foundation com a plantilla buida i prova l'onboarding en còpies o
directoris temporals. Publica canvis agrupats amb notes de versió i instruccions de
migració quan canviïn esquema, scripts o skills.

Per actualitzar un projecte existent, compara la versió d'origen, prepara un PR
amb els canvis comuns pertinents i conserva el brief, els ADRs i el codi del projecte.
No copiïs la plantilla sencera a sobre del producte. Valida integritat de skills i
executa també els tests del producte. Registra la versió adoptada a foundation.json.

La versió inicial no inclou sincronització automàtica entre repositoris ni un bot
d'actualització. Afegir-los tindrà sentit quan hi hagi diversos projectes reals i
una política d'actualitzacions demostrada.
