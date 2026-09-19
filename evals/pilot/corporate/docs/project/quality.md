<!-- Generat des de project/brief.json. Notes manuals a docs/project/notes.md. -->

# Qualitat del projecte

## Criteris del negoci

- La navegació porta de serveis a contacte.
- Els camps buits o invàlids no poden mostrar un estat d'èxit.
- Un nom, correu i servei vàlids mostren un resum visible amb el servei seleccionat, sense peticions de xarxa.
- El focus de teclat és visible.
- No hi ha desbordament horitzontal a 390 px.
- La interfície explica explícitament que és una demostració i que no envia res.

## Comprovacions proposades pel perfil

- Navegació i contingut accessibles amb teclat
- Metadades, sitemap i indexació coherents
- Formularis amb validació, protecció antiabús i estats d'error
- Objectius de rendiment definits per les pàgines principals

## Skills disponibles

Les set skills de base són a skills/catalog.json; activa-les per tasca, no totes a cada torn. Les de React i rendiment són opcionals i encara no estan instal·lades.

## Verificació

Quan existeixi codi, afegeix les ordres reals de lint, tipus i tests a la CI del producte. La CI de foundation només valida aquesta base. Defineix proves del flux crític i dels permisos. Una auditoria pendent no és una auditoria superada.
