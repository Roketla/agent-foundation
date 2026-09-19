# 0003 — Pla persistent, memòria verificable i avaluació

Estat: acceptat. Data: 2026-09-19.

Les sessions noves necessiten recuperar la següent acció sense carregar tot
l'historial. Les promeses d'estalvi també necessiten observacions comparables.

Conservem un increment petit i notes amb citacions i SHA-256 en un JSON local,
gestionat amb Python estàndard. Un únic escriptor, revisió i bloqueig protegeixen
el pla. Un resum limitat omet memòria obsoleta; els ADRs segueixen sent la font de
decisions. No afegim cercadors vectorials, serveis de memòria ni indexació global.

L'avaluador separa model demanat i observat, mètriques desconegudes, errors i
reintents. Només compara casos amb el mateix entorn; els tokens no es converteixen
en diners sense preus verificats. Un pilot no permet generalitzar estalvis.

Conseqüències: l'agent ha de mantenir el pla i validar les afirmacions; els hashes
no proven correcció semàntica. Els límits obliguen a dividir increments grans.
La CI és determinista i no consumeix crèdits de models. Els pilots reals són manuals.
