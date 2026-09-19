# 0002 — Models per capacitat amb adaptació al motor

- Estat: acceptat per a la implementació de la plantilla
- Data: 2026-09-19
- Abast: selecció de models i subagents

## Context i decisió

Cal assignar feina senzilla a models econòmics i reservar anàlisi profunda per als
problemes que la requereixen. Definim light/standard/deep separats dels rols.
Codex els implementa amb Luna/Terra/Astra i un principal Terra. Un script offline
comprova el pla amb inventari observat, risc, incertesa i pressupostos operatius.

## Alternatives

Un únic model potent simplifica operativa però pot gastar més en tasques petites.
Una cascada fixa afegeix cost encara que no calgui. Un executor propi imposaria
pressupostos globals, amb més manteniment, autenticació i superfície de seguretat.
Reutilitzem l'execució nativa i documentem quins límits són reals o de protocol.

## Conseqüències i verificació

La configuració nativa deriva d'una font comuna i la CI comprova divergències.
Un model no disponible no es substitueix silenciosament per un nivell inferior.
Pi/altres motors tenen un contracte explícit, sense suposar que poden delegar.
Els tests cobreixen selecció, escalada, falta de capacitats i límits. Cal un pilot
real per mesurar qualitat/cost: els tests deterministes no ho demostren.
