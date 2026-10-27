# 0004 — Perfils library i service

Estat: proposat. Data: 2026-10-27.

Els perfils corporate, ecommerce i SaaS suposen una web o una aplicació amb usuaris.
Roketla també manté paquets compartits (`@roketla/square-shared`, consumit per tres
botigues) i serveis o integracions (API de l'editor, funcions de Cloudflare, webhooks).
Aquests projectes no tenen públic final: tenen consumidors, un contracte i un cicle de
versions, i els errors que més costen són canvis silenciosos de comportament, secrets
exposats i efectes duplicats per reintents.

Afegim dos perfils, `library` i `service`, amb les mateixes quatre peces que els
existents (preguntes, comprovacions, riscos, etiqueta). `foundation.py` n'obté la llista
d'una sola constant, `PROFILES`, i el test de la base falla si un `profiles/*.json` no hi
és. No hi afegim camps nous ni lògica específica de perfil.

Alternatives descartades: usar `corporate` o `saas` per a aquests projectes (genera
comprovacions d'SEO o de multitenència que no s'apliquen) i un perfil genèric
«altres» (no concreta riscos ni comprovacions).

Conseqüències: projectes nous i existents poden triar-los en l'entrevista. Un projecte
híbrid continua escollint el perfil dominant. La versió de la base puja a 0.4.0 perquè
els projectes derivats puguin saber quan els hi apareixen. Els perfils són una base
editable: cal revisar-los amb el primer projecte real que els faci servir.
