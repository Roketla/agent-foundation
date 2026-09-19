# Comprovacions bàsiques de l'MVP

Data: 2026-09-19

- `HTMLParser` de Python ha analitzat `site/index.html` correctament.
- `node --check` ha validat el JavaScript incrustat a `site/index.html` sense errors de sintaxi.
- Una exploració estàtica ha confirmat que el fitxer no conté `fetch(`, `XMLHttpRequest`, enllaços de recursos externs ni `url(http`.
- Una exploració estàtica ha confirmat la presència de `aria-live="polite"`, `:focus-visible` i la regla mòbil `@media (max-width: 620px)`.
- `git diff --check` no ha informat d'errors d'espais en blanc.

No s'ha obert un navegador ni s'han verificat visualment el formulari, el teclat o la vista a 390 px. Aquesta comprovació continua pendent expressament.
