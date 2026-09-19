# Dades d'inici

`brief.json` conté respostes confirmades, sense secrets. La plantilla es distribueix
buida: no hi defineixis el primer producte real abans de crear-ne un repositori.

L'agent pot passar respostes parcials en un JSON a:

```sh
python3 scripts/foundation.py configure --answers /tmp/project-answers.json
python3 scripts/foundation.py plan
python3 scripts/foundation.py init
```

`configure` fusiona camps de primer nivell; les llistes es reemplacen senceres.
`state.json` es crea en finalitzar i registra el resum de continguts generats.
`ready` vol dir **brief inicial vàlid i documents generats**, no producte implementat,
segur, desplegat o aprovat per producció.

Per revisar una configuració, actualitza les respostes i usa `init --refresh`.
Només regenera fitxers encara idèntics a l'última versió generada. Si un document
té canvis manuals, atura't i reconcilia'ls amb la persona; no esborres el fitxer
ni canviïs els hashes per esquivar aquesta protecció. Conserva notes manuals a
`docs/project/notes.md`, fora dels documents generats.
