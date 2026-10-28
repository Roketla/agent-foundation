# Accés dels cercadors d'IA

Revisat el 2026-10-28. Les identitats i polítiques poden canviar: comprova la font
del proveïdor abans d'editar robots, CDN o WAF. No extrapolis una plataforma a totes.

## Google

Per ser elegible com a enllaç en AI Overviews o AI Mode, la pàgina ha d'estar
indexada i poder mostrar snippet a Search. Google no exigeix fitxers d'IA ni
schema especial. Revisa accés, text visible, enllaços i coherència del marcatge.
Els controls de snippet condicionen què pot mostrar-se; avalua'n l'efecte abans
de modificar-los. Elegibilitat no garanteix aparició.
[Font: Google Search Central](https://developers.google.com/search/docs/appearance/ai-features).

## OpenAI

| Agent | Finalitat | Implicació |
|---|---|---|
| `OAI-SearchBot` | Cerca de ChatGPT | Comprova robots i accés des de la infraestructura pública documentada |
| `GPTBot` | Contingut que pot utilitzar-se per entrenar models | Preferència independent de la cerca; no l'obris per defecte |
| `ChatGPT-User` | Accions iniciades per l'usuari | No determina la inclusió a Search; robots pot no aplicar-se de la mateixa manera |

Es pot permetre cerca i bloquejar entrenament. No copiïs IP ni versions de
user-agent d'una llista antiga. Un header d'user-agent simulat només prova com
respon el servidor a aquella petició, no acredita una visita del robot real.
[Font: documentació oficial d'OpenAI](https://developers.openai.com/api/docs/bots).

## Aplicació al projecte

Inspecciona les regles completes i la ruta efectiva, incloent redireccions,
autenticació, challenges del CDN i recursos necessaris. Conserva els bloquejos
de preview. Proposa una correcció concreta i acotada a l'objectiu autoritzat;
no afegeixis `Allow: /` global sense revisar les exclusions existents.

Per altres motors, consulta la documentació oficial del proveïdor concret.
Si no estableix el comportament, marca'l com a desconegut. `llms.txt` només
s'avalua si hi ha un consumidor o experiment concret; no és un requisit universal
ni substitueix el contingut HTML accessible.
