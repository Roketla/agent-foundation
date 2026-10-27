# Coordinació

L'agent principal conserva l'encàrrec, criteris d'acceptació, fitxers afectats i
comprovacions. Resol tasques petites directament. Llegeix aquest document quan
la tasca necessiti coordinació.

1. Classifica complexitat, risc i incertesa. Permisos, pagaments, aïllament de clients
   o migracions irreversibles tenen risc alt encara que el diff sigui petit. No
   rebaixes el risc per aconseguir un model barat.
2. Si delegar té sentit, llegeix `docs/foundation/model-routing.md`. Observa models,
   esforços i eines de la sessió. Desa només informació no secreta a
   `.local/runtime.json` amb el format de `routing/runtime.example.json`.
   `inventory_source: session` exigeix observació real en aquesta sessió. Un catàleg
   no demostra accés; no reutilitzis inventaris d'altres sessions sense verificar-los.
3. Prepara `.local/task.json` com a `routing/task.example.json`, amb comptadors
   actuals i intents fallits reals. Executa:
   `python3 scripts/routing.py route --runtime .local/runtime.json --task .local/task.json`.
   Conserva el mateix registre d'intents en reintentar. No canviïs el nom de la
   tasca per esquivar el pressupost: cada intent fallit compta encara que canviï el model.
4. Segueix l'acció retornada: `spawn`, `current`, `wait`, `handoff`, `blocked` o `stop`.
   `spawn` és un pla: invoca l'eina real i espera'n el resultat. A Codex selecciona
   l'agent natiu retornat, o model/esforç explícits si l'eina no ofereix rols. A
   Cursor, amb `engine: cursor`, usa el `model` Grok de `selection` (els slugs de
   `policy.cursor` i `.cursor/model-routing.json`). No canviïs a un model que no
   sigui Grok si la política d'aquest projecte ha demanat Grok. No
   copiïs tot l'historial si això impedeix seleccionar el model. Comprova la selecció
   efectiva a la resposta de l'eina; si no la pots verificar, indica-ho.
5. Màxim dos subagents simultanis i una generació: els fills no creen més agents.
   Actualitza l'estat dels que hi ha abans d'obrir-ne un altre. Evita dos escriptors
   al mateix fitxer. Els revisors i investigadors no editen.
6. Una fallada justificada pot escalar de nivell; dues temptatives fallides aturen
   els reintents automàtics i requereixen revisar la causa. Un error de permisos,
   una API caiguda o requisits contradictoris no es resolen canviant de model.
7. Recull resums amb evidència, fitxers, tests i bloquejos, i verifica la integració.
   No repeteixis tot l'anàlisi del fill. Demana revisió independent per canvis de
   risc elevat quan sigui útil i possible, no per a cada correcció trivial.

Codex imposa la concurrència configurada quan es carrega la configuració del projecte.
El router comprova intents, profunditat i context amb les dades que li passes; el
protocol exigeix usar-lo, però no intercepta crides que el saltin. No hi ha un límit
dur de tokens, euros o subscripció. Les polítiques del motor i les instruccions
explícites de l'usuari prevalen.

Registra tokens/durada només quan el motor els proporcioni. No simulis costos ni
mantinguis agents en bucles de supervisió sense una necessitat concreta.

Per reprendre feina entre sessions, consulta `scripts/continuity.py resume`; el pla
té un únic escriptor i els fills retornen evidències. Abans de cedir feina inacabada,
desa estat, bloquejos i següent acció segons `docs/foundation/continuity.md`. Els
experiments comparatius segueixen `evals/README.md`; no confonguis selecció recomanada
amb model observat ni desconegut amb consum zero.
