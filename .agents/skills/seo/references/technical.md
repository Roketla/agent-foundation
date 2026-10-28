# SEO tècnic

Revisat el 2026-10-28. Aplica només els controls rellevants a les URL de l'encàrrec.
Els enllaços són fonts per verificar polítiques, no lectures obligatòries en bloc.

## Accés i indexació

- Distingeix producció, preview i pàgines privades abans de tocar directives.
  Verifica status HTTP, redireccions, `robots.txt`, meta robots i `X-Robots-Tag`
  efectius. Un estat 200 no prova que una URL estigui indexada.
- `robots.txt` controla rastreig, no és autenticació ni una garantia de desindexació.
  Si el robot no pot rastrejar, pot no veure el `noindex`. Preserva el control
  d'accés de les pàgines privades i comprova la combinació de directives.
  [Google: robots.txt](https://developers.google.com/search/docs/crawling-indexing/robots/intro).
- Revisa HTML rebut i DOM renderitzat: contingut principal, títol, enllaços i
  recursos necessaris. No prescriguis una migració de framework per una advertència
  sense reproduir el problema del renderitzat.

## Identitat de les URL

- Comprova que el canonical apunti a la versió pública preferida i accessible;
  no canonicalitzis totes les pàgines a la home. Revisa coherència amb redireccions,
  enllaços interns i sitemap. El canonical és un senyal, no una ordre garantida.
  [Google: canonicalització](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls).
- Si hi ha sitemap, inclou només URL canòniques destinades a indexació; exclou
  preview, duplicats, errors i redireccions. No inventis dates de modificació.
- Per variants reals d'idioma/regió, verifica `hreflang` vàlid, autoreferència,
  reciprocitat i URL absolutes. Usa `x-default` només si hi ha una pàgina de
  reserva adequada. No inventis variants inexistents.
  [Google: versions localitzades](https://developers.google.com/search/docs/specialty/international/localized-versions).

## Metadades i dades estructurades

Revisa títols descriptius, descripcions coherents, encapçalaments i enllaços HTML
rastrejables. Mantén les previsualitzacions socials separades dels senyals d'indexació.
No converteixis longituds de text orientatives en criteris absoluts d'aprovat.

Tria el tipus de schema segons la realitat visible, no pel nom del projecte.
Un directori no converteix el propietari del web en totes les botigues que llista.
No inventis `LocalBusiness`, adreces, valoracions ni preus. Valida la sintaxi i
els requisits de la funcionalitat vigent; passar el validador no garanteix un
resultat enriquit. [Google: dades estructurades](https://developers.google.com/search/docs/appearance/structured-data/sd-policies).

El resultat enriquit de FAQ va ser retirat el 2026; no proposis `FAQPage` com a
mecanisme per obtenir-lo. Una secció de preguntes útil continua sent contingut.
Revisa [les actualitzacions oficials](https://developers.google.com/search/updates)
abans de recomanar funcionalitats de cerca que poden canviar.

## Evidència

Per cada incidència conserva URL/fitxer, entorn, comportament observat i prova de
correcció. Usa el build i les proves disponibles; afegeix comprovacions només quan
protegeixin un comportament real. No confonguis Lighthouse amb una auditoria SEO
completa, ni el rendiment de laboratori amb dades de camp.
