# Arquitectura de repositoris preparats per a agents

Investigació i proposta per a Andreu · 19 de setembre de 2026 · Estat: proposta, pendent de pilot.

L'objectiu és crear una base reutilitzable per a webs corporatives, ecommerce i SaaS, amb Pi, instruccions d'agents, skills, documentació i ADR. El criteri d'optimització serà el cost total d'obtenir un canvi correcte i mantenible, incloent-hi reintents, verificació i intervenció humana.

**Conclusió principal.** Proposo un repositori de plataforma petit, un generador amb actualitzacions, una capa d'execució controlada i un catàleg limitat de skills avaluades. Un agent principal serà suficient per defecte. Els subagents s'activaran per independència de treball o necessitat de revisió. Les regles crítiques es comprovaran amb codi i permisos reals.

**Abast i qualitat de l'evidència.** S'han consultat fonts primàries: relats d'equips d'enginyeria, documentació oficial i recerca. Els relats de les empreses descriuen sistemes o equips concrets; no demostren una arquitectura única adoptada a tota la companyia. Les mètriques dels blogs són declaracions dels seus autors, habitualment sense dades suficients per reproduir-les. Les recomanacions següents són una síntesi pròpia, no una certificació de les empreses. No s'ha inspeccionat el repositori privat `Roketla/opos`, perquè l'accés disponible retorna 404. Tampoc s'han executat benchmarks ni instal·lat eines en aquesta investigació.

**1. Què han construït els equips estudiats i què podem aprofitar.**

| Equip i font | Evidència publicada | Aplicació proposada | Límit de transferència |
|---|---|---|---|
| OpenAI, experiment amb Codex | Entrada curta, coneixement versionat, comprovacions arquitectòniques i entorns per canvi | Repositori llegible i regles verificables | És un producte experimental concret |
| Stripe, Minions | Fluxos que combinen codi determinista amb passos d'agent | Executor amb passos obligatoris | Parteixen d'una infraestructura de desenvolupament molt madura |
| Spotify, Honk | Verificadors especialitzats i comprovació de l'abast | Interfície única de validació | Manteniment i migracions no equivalen a dissenyar un producte nou |
| Google, Agent Skills | Avaluacions amb i sense skill, propietaris i controls automàtics | Catàleg petit amb criteris d'entrada | Les seves proves internes no són totes públiques |
| Google Research | Comparació controlada d'arquitectures d'agents | Delegació condicionada al tipus de tasca | Els benchmarks no representen tots els nostres projectes |
| Meta, pipelines de dades | Context sobre convencions internes difícils d'inferir | Documentar coneixement específic i punts delicats | Resultats preliminars en un domini molt concret |
| Cloudflare, auditoria | Estat persistent i validació separada dels candidats | Auditoria especialitzada amb evidències | Una plataforma d'auditoria té necessitats diferents del desenvolupament diari |

**OpenAI: preparar el repositori perquè l'agent pugui navegar, executar i verificar.** El seu equip explica que un `AGENTS.md` monolític va resultar difícil de mantenir i consumir. Va passar a una entrada breu, documents indexats i controls mecànics de l'arquitectura. També va donar als agents accés a la UI i a observabilitat per canvi. L'autonomia descrita depèn d'aquest entorn. No extrapolaria al nostre cas la seva política de poques barreres de merge ni les xifres de productivitat. [Cas publicat el 11-02-2026](https://openai.com/index/harness-engineering/).

**Stripe: passos deterministes al voltant del treball del model.** Minions combina passos d'agent amb operacions codificades, com executar linters. Treballa en devboxes aïllades i reutilitza infraestructura interna. Selecciona un subconjunt d'eines i limita les rondes de CI abans del retorn a una persona. La lliçó transferible és que les obligacions conegudes pertanyen al flux d'execució. No necessitem replicar la seva flota de màquines preescalfades. [Minions, part 2, 19-02-2026](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2).

**Spotify: verificar el resultat i contenir l'abast.** Honk exposa verificadors que trien les comprovacions segons el projecte i retornen resultats compactes. Afegeix un jutge sobre la petició i el diff per detectar desviacions. L'article també reconeix que llavors no havien invertit en avaluacions d'aquest jutge: és una limitació rellevant. Adoptaria verificació estructurada i revisió d'abast, calibrant qualsevol jutge amb casos revisats per persones. [Honk, part 3, 09-12-2025](https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3).

**Google: les skills tenen propietari, proves i manteniment.** El procés publicat comprova estructura i enllaços, exigeix casos d'avaluació i compara agents amb i sense cada skill, mesurant qualitat, tokens i temps. Proposo que cada incorporació al catàleg superi aquesta comparació. La publicació exposa el procés; no permet auditar tots els resultats interns. [Google Agent Skills, 03-08-2026](https://cloud.google.com/blog/topics/developers-practitioners/behind-the-scenes-how-we-build-test-and-scale-google-agent-skills).

**Meta: capturar allò que el codi no explica fàcilment.** L'equip de pipelines va documentar convencions internes i dependències poc evidents en fitxers consultables sota demanda. Comunica aproximadament un 40% menys de crides i tokens en proves preliminars de sis tasques. Aquesta mostra és massa petita per convertir-la en una promesa d'estalvi. Per nosaltres, la prioritat són les excepcions i decisions locals que eviten investigacions repetides. [Cas de Meta, 06-04-2026](https://engineering.fb.com/2026/04/06/developer-tools/how-meta-used-ai-to-map-tribal-knowledge-in-large-scale-data-pipelines/).

**Cloudflare: conservar estat abans d'ampliar concurrència.** La seva auditoria va evolucionar d'una skill a una canalització amb persistència i comprovacions independents. Recomanen començar amb un sistema mínim i ampliar-lo quan hi hagi un coll d'ampolla real. Per nosaltres, una interrupció hauria de permetre recuperar les evidències ja obtingudes. La recerca de vulnerabilitats tindria un flux propi. [Vulnerability harness, 18-06-2026](https://blog.cloudflare.com/build-your-own-vulnerability-harness/).

**2. Evidències que obliguen a matisar la primera arquitectura.**

**Més context pot augmentar el cost sense millorar el resultat.** La versió revisada de l'estudi *Evaluating AGENTS.md* no troba una millora general en la resolució de tasques i observa més d'un 20% d'increment mitjà de cost d'inferència en les seves condicions. Destaca la utilitat per explicar pràctiques no estàndard. No prova que qualsevol `AGENTS.md` sigui perjudicial. Justifica comparar instruccions mínimes, context selectiu i variants més extenses en tasques pròpies. [Estudi, revisió del 23-06-2026](https://arxiv.org/abs/2602.11988v2).

**Més agents no asseguren millor rendiment.** Google Research estudia 180 configuracions i observa que la coordinació pot ajudar en tasques paral·lelitzables i perjudicar el raonament seqüencial. És una prova controlada en determinats benchmarks, no una mesura directa d'ecommerce o SaaS. La nostra política haurà de considerar dependències entre subtasques i cost de coordinació. [Google Research, 28-01-2026](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/).

**Una millora de recerca no implica una millora de programació.** Anthropic descriu un sistema multiagent útil per explorar línies independents de recerca, amb un consum elevat. La comparació publicada d'aproximadament 15 vegades més tokens és respecte a xats, no respecte a un agent programador equivalent. No s'ha d'utilitzar per estimar el pressupost del nostre sistema. [Sistema multiagent d'Anthropic, 13-06-2025](https://www.anthropic.com/engineering/multi-agent-research-system).

**Hi ha decisions contextuals, no consens universal.** Spotify descriu avantatges de prompts estàtics i eines limitades per a migracions conegudes; Google prioritza MCP remot en les seves skills de serveis cloud. Proposo scripts locals per operar sobre el repositori i connectors quan calgui identitat, governança o dades externes. L'adaptador haurà de deixar clares les diferències. [Spotify, context engineering](https://engineering.atspotify.com/2025/11/context-engineering-background-coding-agents-part-2), [Google, procés de skills](https://cloud.google.com/blog/topics/developers-practitioners/behind-the-scenes-how-we-build-test-and-scale-google-agent-skills).

**3. Arquitectura recomanada: sis responsabilitats separades.**

La proposta següent és pròpia. Les fonts anteriors informen els principis; els noms, límits i contractes s'hauran de validar al pilot.

| Responsabilitat | Contingut | On s'aplica |
|---|---|---|
| Definició del projecte | Perfil, stack, mòduls, marca, criteris d'acceptació | Manifest versionat |
| Coneixement | Instruccions essencials, arquitectura, decisions, skills | Repositori i càrrega selectiva |
| Control d'execució | Estat, pressupost, permisos, reintents, assignacions | Executor de confiança |
| Treball del model | Implementar, investigar, dissenyar, revisar | Pi inicialment |
| Verificació | Proves, comprovacions arquitectòniques, UI, seguretat | Scripts, navegador i CI |
| Distribució | Generar, fixar versions, actualitzar, resoldre conflictes | Plantilla i PR d'actualització |

Flux orientatiu: petició → criteris verificables → selecció de context i eines → execució aïllada → verificació → correcció limitada → resultat revisable.

El control d'execució decideix què es pot fer. El model proposa i treballa dins d'aquest límit. La llista de permisos efectiva, els verificadors crítics i els límits pressupostaris no poden quedar a disposició de l'agent que està sent verificat.

No faria serveis separats per cadascuna d'aquestes responsabilitats. Inicialment poden ser mòduls del mateix programa i fitxers locals. La separació és de responsabilitats i confiança; només es convertirà en desplegaments separats quan ho exigeixi l'ús.

**4. Nucli, perfils, stacks i mòduls: evitar combinacions impossibles.**

Composició proposada: versió de la base + perfil de producte + stack admès + mòduls compatibles + configuració de projecte.

| Element | Exemples | Responsabilitat |
|---|---|---|
| Nucli | Qualitat, documentació, operativa, metadades | Contracte comú |
| Perfil | Corporativa, ecommerce, SaaS | Necessitats i casos d'acceptació |
| Stack | Opció tècnica aprovada per a cada perfil | Estructura i eines executables |
| Mòdul | CMS, idiomes, identitat, pagaments | Capacitat amb dependències |
| Projecte | Marca, continguts, domini, decisions | Personalització local |

La independència conceptual entre perfil i stack no implica suportar qualsevol combinació. La v0.1 només tindria una combinació corporativa validada. Els mòduls declararien requeriments, incompatibilitats, fitxers que gestionen, comprovacions i migracions. Afegir pagaments a una corporativa no la converteix automàticament en un ecommerce complet.

La funció de generar esquelets amb paràmetres està ben representada per Backstage Software Templates. Adoptaria aquest patró amb una interfície local; un portal Backstage complet pot esperar fins que hi hagi una necessitat real de catàleg i autoservei. [Documentació oficial](https://backstage.io/docs/features/software-templates/).

```text
agent-foundation/
├── AGENTS.md
├── README.md
├── core/                 # Contractes, regles i plantilles comunes
├── profiles/             # Corporativa; SaaS i ecommerce quan es validin
├── stacks/               # Combinacions tècniques realment suportades
├── modules/              # Capacitats amb dependències explícites
├── skills/               # Fonts canòniques de skills internes
├── adapters/pi/          # Traducció a descobriment i execució de Pi
├── workflows/            # Passos d'execució, sense obligar a usar un LLM
├── checks/               # Verificadors i contractes de resultats
├── evals/                # Fixtures i tasques de regressió del sistema
├── templates/            # Esquelet del projecte generat
├── migrations/           # Actualitzacions de versions anteriors
└── docs/                 # Decisions i manteniment de la plataforma
```

El projecte generat rebria només els fitxers i skills actius. El catàleg complet i l'executor viurien a la plataforma. Això limita duplicació, dependències i càrrega inicial.

**5. Pi: començar amb un adaptador i comprovar-ne les capacitats.**

Pi documenta extensions, skills i execució interactiva o programàtica. No incorpora subagents ni un sistema complet de permisos per defecte. L'extensió o executor escollit ha de proporcionar les capacitats que exigim. [Pi](https://pi.dev/).

Abans d'adoptar una extensió de subagents, provaríem:

- Inici i cancel·lació d'una tasca sense processos orfes.
- Context explícit per al fill i retorn estructurat al principal.
- Captura de consum, errors, timeout i límits de concurrència.
- Entorn i credencials delimitats per tasca.
- Compatibilitat amb la versió de Pi fixada.

Conservaria el format portàtil de les skills, però no prometria que Pi i Codex interpreten igual totes les carpetes i prioritats d'instruccions. Cada adaptador hauria de superar proves de descobriment, precedència i permisos. Codex documenta les seves regles de càrrega d'`AGENTS.md`; aquesta semàntica no s'ha d'assumir per a tots els motors. [AGENTS.md a Codex](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

L'adaptador Codex quedaria previst com a interfície. S'implementaria després de validar el primer motor, amb excepcions documentades per a les funcions que no siguin equivalents.

**6. Política d'agents i contracte de tasca.**

Els rols expressen responsabilitats. No obliguen a crear processos independents: el principal pot aplicar la skill UX i després implementar en una tasca petita.

| Situació | Política inicial proposada |
|---|---|
| Canvi petit amb dependències seqüencials | Un agent, context local i verificació afectada |
| Dues parts realment independents | Principal més fins a dos treballadors |
| Autorització, pagaments o migració sensible | Implementació i revisió separades |
| Auditoria profunda | Workflow especialitzat, amb cobertura i pressupost propis |

Un nivell de delegació i dos fills simultanis serien valors inicials experimentals. El límit de concurrència no substitueix el límit de fills totals: un procés podria generar-ne molts de manera successiva. Cal limitar també el total, els reintents i la despesa agregada.

Cada tasca declararia: identificador; commit base; objectiu; criteris d'acceptació; abast de lectura i escriptura; permisos; eines; pressupost; dependències; verificadors exigits; responsable d'integració; i ubicació d'evidències. El retorn separaria resultat, fitxers afectats, comprovacions executades, consum i bloquejos.

L'estat utilitzaria transicions explícites: pendent, executant, verificant, validada, pendent de revisió, fallida o cancel·lada. La publicació i la integració serien operacions diferenciades. Una resposta textual de l'agent no seria suficient per declarar èxit.

Per a paral·lelisme d'escriptura, utilitzaríem worktrees o còpies separades, propietat clara dels fitxers i un integrador únic. Un worktree aïlla canvis Git; no és una barrera de seguretat del sistema operatiu.

**7. Context, memòria i ADR.**

Separaria quatre tipus d'informació:

| Tipus | Exemples | Vida útil i tractament |
|---|---|---|
| Regles estables | Com validar, convencions locals imprescindibles | Entrada breu, revisada |
| Coneixement de projecte | Arquitectura, components, ADR, patrons no evidents | Versionat i carregat segons tasca |
| Estat d'execució | Etapa, fitxers, evidències, consum | Persistent localment, fora del prompt habitual |
| Dades externes | Issues, pàgines, sortides d'eines | Informació no fiable com a instruccions |

El `AGENTS.md` inicial apuntaria a unes 60–100 línies com a límit orientatiu, amb mètrica real de tokens segons motor. El millor contingut és el que redueix errors observats: ordres no estàndard, dependències delicades o restriccions de negoci que no s'infereixen fàcilment. No copiaria manuals genèrics dels frameworks.

La càrrega incremental i l'ús de notes persistents són tècniques descrites per Anthropic per gestionar sessions llargues. La nostra implementació hauria de mantenir l'origen i la vigència de cada nota i poder invalidar-la després de canvis. [Context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).

Per als ADR, seguiria un registre breu de context, alternatives, decisió i conseqüències. AWS recomana conservar les decisions acceptades i substituir-les amb nous registres quan canviïn, mantenint el vincle de substitució. Adoptaria aquest cicle per decisions significatives, evitant crear un ADR per cada detall rutinari. [Procés ADR d'AWS](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html).

El manteniment de documents tindria un propietari i una referència al codi corresponent. CI comprovaria enllaços locals, fitxers inexistents i metadades. La revisió semàntica es faria quan canviés l'àrea afectada. Les comprovacions mecàniques detecten inconsistències; no certifiquen que tota la documentació sigui correcta.

**8. Skills: catàleg controlat i validació del valor real.**

Cada skill tindria `SKILL.md` i, quan fos necessari, scripts, referències i assets, seguint Agent Skills. En metadades pròpies del nostre catàleg afegiríem propietari, origen, llicència, commit fixat, riscos, dependències i última avaluació. Aquestes metadades addicionals no són totes camps estàndard. [Especificació Agent Skills](https://agentskills.io/specification).

Proves d'entrada proposades per skill:

1. Una tasca on s'hauria d'activar i una on no.
2. Un cas típic i un cas límit amb resultat comprovable.
3. Comparació de qualitat, cost i temps amb la configuració sense skill.
4. Revisió de scripts, recursos remots i permisos requerits.
5. Verificació de les instruccions de fallada i d'aturada.

Classificació: experimental, validada per un stack, retirada o pendent d'actualització. Si una skill millora qualitat a un cost més elevat, podria continuar sent adequada per a tasques de risc. Una skill sense benefici mesurable ni funció normativa necessària no entraria al conjunt predeterminat.

La v0.1 tindria UX, UI, accessibilitat i revisió de seguretat focalitzada. ADR podria començar com una plantilla; només es convertiria en skill si el flux repetit ho justifica. Això simplifica la proposta inicial.

**9. UX i UI: vincular les instruccions a un sistema de disseny verificable.**

Carbon publica l'estat de comprovacions d'accessibilitat per component, incloent variants i navegació amb teclat. És una referència útil sobre evidències de qualitat d'un sistema de disseny; no és una prova que un agent produeixi per si sol una bona experiència d'usuari. [Carbon, estat d'accessibilitat](https://preview.carbondesignsystem.com/building-blocks/core/components/overview/accessibility-status).

La proposta és tenir una biblioteca de components escollida per stack, tokens versionats i criteris de marca locals. Les skills consumirien aquestes fonts. L'objectiu és obtenir consistència sense convertir tots els projectes en la mateixa web.

| Capa | Entrada | Evidència de sortida |
|---|---|---|
| UX | Públic, objectiu, continguts i tasques prioritàries | Fluxos, estructura i criteris d'èxit |
| UI | Marca, tokens i components disponibles | Pantalles i estats coherents |
| Accessibilitat | Components i fluxos interactius | Proves automàtiques i revisió de teclat/focus |
| Validació visual | Pantalles de referència i viewports acordats | Captures i comparació revisada |
| Validació funcional | Dades i escenaris realistes | Recorregut complet en navegador |

Es provarien estats buits, càrrega, error, èxit, permisos insuficients i contingut llarg. Per ecommerce s'afegirien preus, estoc i errors de checkout; per SaaS, permisos i dades de diferents organitzacions. Les proves automatitzades d'accessibilitat i els jutges visuals serien evidències parcials, complementades amb revisió humana dels recorreguts crítics.

**10. Seguretat del producte i de l'executor.**

La skill pública d'auditoria de Cloudflare combina exploració, validació dels candidats i comprovació independent dels registres finals. El repositori actual documenta requisits d'agents i sandbox. Fixaríem una versió revisada i comprovaríem aquests requisits abans d'executar-la. La publicació inicial del blog i el README actual descriuen versions amb fases diferents; la versió fixada governaria el flux real. [Skill oficial](https://github.com/cloudflare/security-audit-skill).

Proposta per al producte: comprovacions de secrets i dependències, validació d'entrades, proves d'autorització i verificació dels fluxos sensibles. L'abast exacte dependria del perfil, de les dades i dels serveis que utilitzi.

Proposta per a l'executor:

- Workspace de tasca separat; entorn amb límits de CPU, memòria, temps i xarxa segons risc.
- Cap credencial de producció disponible per defecte; permisos mínims per connector.
- Configuració de control fora de l'escriptura de l'agent de la tasca.
- Logs amb minimització de dades, redacció de secrets i termini de retenció.
- Instruccions de documents, issues i resultats d'eines tractades com a dades externes.
- Canvis de CI, scripts de validació i permisos sotmesos a revisió diferenciada.

Per evitar que l'agent validi un canvi eliminant la prova que el detecta, el paquet de verificació crític s'executaria des d'una versió de confiança. Si la tasca exigeix actualitzar proves, el canvi es podria fer, però no alteraria silenciosament la base de validació independent.

L'auditoria profunda es llançaria abans de fites o després de canvis sensibles. La revisió diària seria acotada al canvi. No activaria una auditoria multiagent completa en cada correcció de text o estil.

**11. Cost i fiabilitat: pressupost al nivell de tota la tasca.**

El cost a registrar inclouria tokens d'entrada i sortida, ús de memòria cau quan el proveïdor l'informi, eines de pagament, sandbox, CI, reintents i revisió humana. Les subscripcions poden no oferir un cost exacte per petició: en aquest cas separaríem consum observat i cost estimat, amb tarifa i data de referència.

Mètrica principal proposada: cost total de les execucions, també les fallides, dividit pel nombre de tasques que compleixen els criteris d'acceptació. La taxa d'èxit s'ha de mostrar al costat; un cost baix amb moltes tasques abandonades pot ser un resultat dolent.

| Control | Com s'aplicaria |
|---|---|
| Pressupost agregat | Inclou principal, fills, verificació i reintents |
| Reserva abans de delegar | El fill rep una part del pressupost restant |
| Límits de peticions | Nombre de crides, temps i sortida màxima |
| Reintents segons causa | Separar xarxa, límit temporal i error funcional |
| Sortides compactes | Resultat, error útil i ruta del log complet |
| Comprovacions reutilitzables | Memòria cau invalidada segons entrades i configuració |
| Aturada amb evidència | Retornar treball parcial i motiu, sense declarar èxit |

Una comptabilitat exacta en temps real pot ser impossible si el proveïdor informa del consum al final. El controlador ha de reservar un marge, limitar la petició següent i reconèixer aquesta incertesa. Si falta telemetria, no tractaria el consum com a zero.

Cloudflare mostra una tècnica de descoberta i execució que evita carregar totes les definicions d'una API al context. Adoptaria el principi de consultar només les eines necessàries. L'estalvi que publica és sobre la superfície d'eines d'aquella API; no és una reducció equivalent de tot el cost d'una tasca. [Code Mode](https://blog.cloudflare.com/code-mode-mcp/).

**12. Avaluacions que permetin afirmar que el sistema millora.**

Anthropic proposa combinar verificadors deterministes, judicis del model i revisió humana segons el resultat a comprovar, repetint intents perquè els agents són variables. També diferencia capacitat i regressió. Adoptaria aquesta separació i mantindria entorns nets entre proves. [Guia d'avaluacions, 09-01-2026](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).

Pla propi de pilot: començar amb 12 tasques representatives i ampliar a unes 30 quan existeixin els tres perfils. La mida inicial detectarà errors grans, però no permetrà afirmar millores petites amb confiança estadística.

| Família | Exemples |
|---|---|
| Corporativa | Formulari, navegació, continguts llargs, correcció responsive |
| Ecommerce | Preu manipulat, webhook repetit, estoc i pagament fallit |
| SaaS | Permís insuficient, separació d'organitzacions, migració |
| Operativa | Represa després d'error, timeout i pressupost esgotat |
| Plataforma | Actualitzar la base mantenint personalitzacions |
| Context i skills | Activació correcta, absència d'activació i instruccions contradictòries |

Les variants serien: motor amb instruccions mínimes; context selectiu; skills afegides individualment; delegació quan sigui aplicable. Compararíem tasques aparellades sobre el mateix commit, entorn i versió del model, amb diversos intents i ordre alternat. Cada canvi experimental tindria una hipòtesi.

Mètriques: acceptació funcional, regressions, canvis fora d'abast, falsos positius de revisió, tokens, temps mitjà i de cua, cost, intervenció humana i capacitat de represa. Un subconjunt de tasques quedaria reservat per a validació, separat dels exemples emprats per ajustar les skills.

Els criteris de seguretat serien obligatoris. La qualitat visual requeriria una rúbrica i mostres revisades per una persona. El jutge automàtic es calibraria amb aquestes mostres abans d'usar-lo com a barrera.

**13. Generar projectes i mantenir-los actualitzats són dos problemes diferents.**

Proposo començar amb Copier com a candidat de generació i actualització, pendent de pilot. La seva documentació explica com reaplica diferències locals i assenyala els casos de conflicte. No promet actualitzacions sense conflictes. El fitxer de respostes gestionat per Copier s'ha de conservar segons el seu mecanisme. [Actualització de projectes](https://copier.readthedocs.io/en/stable/updating/).

El repartiment de fitxers quedaria explícit:

| Categoria | Exemples | Política |
|---|---|---|
| Generats | Adaptadors i índexs derivats | Regenerar des de la font canònica |
| Compartits i editables | Configuració CI i instruccions del projecte | Actualització amb diff i conflictes visibles |
| Propis del projecte | Producte, marca, ADR i codi funcional | No sobreescriure amb la plantilla |
| Distribuïts com a paquet | Verificadors estables | Versió fixada i actualització de dependència |

El registre de procedència inclouria versió de plantilla, perfil, stack, mòduls i commits de skills externes. Si creem `foundation.lock`, seria una convenció nostra, amb esquema i comprovador. No substituiria el lockfile de dependències del projecte.

La primera prova crítica seria: generar v0.1, personalitzar-la, aplicar una millora de v0.2, mostrar conflictes, conservar el producte i passar les comprovacions. El flux es provaria en una branca o còpia temporal abans de proposar el diff d'actualització.

**14. Canvis concrets respecte a la primera proposta.**

| Primera idea | Ajust després de la investigació |
|---|---|
| Repositori principal per clonar | Plataforma versionada amb prova d'actualització |
| Orquestrador com a rol | Executor que imposa estat, permisos i límits |
| Nombre fix de subagents | Valors inicials experimentals i delegació segons dependències |
| Catàleg inicial de skills | Entrada subjecta a proves i propietari |
| ADR com a skill necessària | Plantilla primer; skill si aporta valor repetit |
| Base independent del stack | Matriu petita de combinacions compatibles i provades |
| `AGENTS.md` curt per convenció | Curt, específic i contrastat amb una configuració mínima |
| Compatibilitat amb diversos motors | Pi primer; altres adaptadors amb proves explícites |

**15. Ordre d'implementació i criteris per avançar.**

| Etapa | Resultat concret | Condició per avançar |
|---|---|---|
| 0. Delimitar pilot | Un perfil, un stack, 12 tasques i criteris | Resultats avaluables i entorn conegut |
| 1. Base mínima | Instruccions, docs, generació i verificadors | Projecte nou arrenca i passa comprovacions |
| 2. Execució amb Pi | Tasques acotades, consum i errors registrats | Fallades i cancel·lacions no es confonen amb èxit |
| 3. Skills UX/UI | Tokens, components i evidències visuals | Millora observada en tasques del pilot |
| 4. Actualització | Migració de v0.1 a v0.2 personalitzada | Sense pèrdua silenciosa de canvis |
| 5. Delegació | Subtasques delimitades i revisió independent | Benefici mesurat respecte a agent únic |
| 6. Nous perfils | SaaS i ecommerce amb verificacions pròpies | Fluxos sensibles provats abans d'ampliar ús |

Els ADR inicials quedarien com a propostes: composició del projecte; executor de confiança; Pi i contracte d'adaptador; tractament de dades i permisos; pressupost; catàleg de skills; verificació; distribució i migració. Només es marcarien acceptats després de la decisió corresponent.

**16. Decisions que podem prendre ara i decisions que necessiten proves.**

Podem fixar ara la separació de responsabilitats, l'existència de comprovacions objectives, la procedència de skills, la conservació de decisions i la necessitat d'actualitzar projectes generats. També podem començar amb una base mínima sense serveis permanents.

Necessiten proves: models concrets, quantitat òptima de context, pressupost numèric, nombre de subagents, generador definitiu, llibreria visual i extensió de Pi. El repositori privat pot aportar implementacions que modifiquin aquestes eleccions.

No construiria encara una xarxa permanent d'agents, una base vectorial, un portal intern, una cua distribuïda ni una auditoria contínua de tota la flota. Cadascun d'aquests components tindria un criteri d'entrada: un problema recurrent observat, volum suficient i una prova que demostri que el resol a un cost assumible.

El primer resultat operatiu a perseguir és un repositori corporatiu generat, modificat amb Pi, verificat i actualitzat preservant la personalització. Aquest recorregut permet validar la base abans d'augmentar-ne l'abast.
