# Skills: selecció, confiança i manteniment

Els adaptadors locals de `.agents/skills/` tenen descripcions curtes i un abast
concret. Les fonts originals s'han incorporat sense modificar a `vendor/skills/`
a partir de commits fixats. `skills/catalog.json` descriu la procedència i
`skills/lock.json` fixa SHA-256 de tots els fitxers vendored i les llicències.

Les adaptacions són deliberades: UI fa servir una referència fixada en lloc de
descarregar main cada vegada; tests respecten el framework existent i esperes per
condicions observables; depuració no copia exemples que mostren secrets; disseny
no assumeix com a fet el client fictici del prompt original.

No carreguis totes les fonts en iniciar una sessió. Les dependències de Superpowers
són lectures locals quan les demani la depuració. Les skills opcionals del catàleg
no estan instal·lades i no són ordres disponibles fins que s'incorporin.

## Skills locals i context

`seo` i `geo` són skills pròpies a `.agents/skills/`, registrades al catàleg com
a `role: base`. Les seves referències es carreguen per necessitat i incorporen
fonts oficials i data de revisió. No són fonts vendored i no entren al lock de
tercers. Cal revalidar les polítiques dels cercadors abans de recomanacions noves.

Mantén una sola còpia descobrible de cada skill. L’entrada mínima i la descoberta
per motor es documenten a `docs/foundation/context-loading.md`.

## Actualització d'una font

1. Revisa canvis upstream, llicència, scripts i dependències. Tria un SHA de commit
   complet; evita seguir automàticament main o instal·lar un catàleg sencer.
2. Descarrega a un directori temporal amb una eina fiable, sense executar scripts
   de la font. Compara amb vendor i revisa qualsevol canvi de permisos o trànsit.
3. Substitueix només la font aprovada i actualitza commit i llicències del catàleg.
4. Regenera `skills/lock.json` calculant SHA-256 de cada fitxer de vendor, ordenat
   per ruta. Inclou només schema_version, algorithm i files, com el lock existent.
5. Executa validate i tests, i revisa el diff en un PR. Canviar hashes no és una
   comprovació de confiança: el control és la revisió del nou contingut.

Les llicències i atribucions s'inventarien a THIRD_PARTY_NOTICES.md. El repositori
agent-skills de Vercel declara MIT al README però no inclou un fitxer LICENSE a
la revisió consultada; conservem aquella declaració. La referència separada
web-interface-guidelines sí que inclou LICENSE, conservat al seu directori.

## Security Audit

Cloudflare distingeix consulta/revisió focalitzada d'auditoria completa. L'adaptador
manté aquesta distinció. Instal·lar la skill no executa una auditoria ni crea la
sandbox requerida. Llegeix els requisits originals abans d'executar codi objectiu;
si no es compleixen, documenta needs_validation i limita't a inspecció segura.
