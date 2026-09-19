# Coordinació

L'agent principal conserva el context mínim: encàrrec, criteris d'acceptació, fitxers
afectats i comprovacions. Resol tasques petites directament. Llegeix aquest document
només quan la tasca necessiti coordinació.

1. Confirma el resultat esperat amb la informació disponible, sense preguntes redundants.
2. Divideix només si hi ha feina independent i el motor permet delegar. Per defecte,
   cap subagent; com a recomanació de cost, comença amb un o dos com a màxim quan
   siguin útils. Això no és un límit tècnic ni preval sobre les instruccions de sessió.
3. Dona a cada subagent objectiu delimitat, fitxers autoritzats, evidència esperada i
   condició d'aturada. No copiïs tota la conversa. Evita dos escriptors al mateix fitxer.
4. Recull resums amb fitxers canviats, tests, riscos i bloquejos. Verifica la integració.
5. Una revisió independent és pertinent per permisos, pagaments, migracions o canvis
   amplis; no és un peatge per a correccions trivials. Si no hi ha subagents, fes
   revisió local i identifica la limitació.

No simulis costos mesurats. Registra tokens/durada només quan el motor els proporcioni.
No mantinguis agents en bucles de supervisió sense una necessitat concreta.
