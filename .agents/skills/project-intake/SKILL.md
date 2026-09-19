---
name: project-intake
description: Define a new product from this template or resume incomplete onboarding. Use when project status is uninitialized or in_progress; do not use for maintenance of agent-foundation itself.
---

# Inici del projecte

1. Llegeix AGENTS.md. Executa `python3 scripts/foundation.py status` i llegeix
   `project/brief.json`. Si és ready, continua la tasca sense repetir l'entrevista.
2. Recupera dades ja conegudes. Pregunta com a màxim 2–3 coses per torn, en l'idioma
   de l'usuari: què vol desenvolupar i per a qui; MVP i límits; criteris d'acceptació
   i idiomes. No tornis a preguntar res resolt a la conversa.
3. Proposa corporate, ecommerce o saas i llegeix només el perfil triat a profiles/.
   Per a un híbrid, escull el dominant i registra extensions al MVP/restriccions.
4. Pregunta només detalls del perfil que afectin el primer increment. Identifica
   stack/hosting existents, integracions, dades sensibles i restriccions. Stack i
   hosting desconeguts poden quedar undecided: proposa'ls abans d'implementar.
   Desa incògnites no bloquejants a open_questions. Mai demanis credencials.
5. Desa respostes parcials en un JSON temporal amb el format de project/brief.json.
   Executa `python3 scripts/foundation.py configure --answers /ruta/respostes.json`.
   Les llistes es reemplacen senceres. Desa fets confirmats o propostes acceptades,
   sense secrets. Elimina el temporal creat per tu en acabar. No editis state.json.
6. Executa `plan` i resumeix MVP, perfil, acceptació i decisions pendents. Resol
   contradiccions o decisions que necessitin l'usuari; no afegeixis confirmacions
   rutinàries quan ja hi ha autorització. Amb els camps obligatoris complets,
   executa `init` i després `validate`.
7. Si ja existien documents, revisa plan abans d'usar `init --refresh`. Davant d'un
   conflicte, preserva els canvis manuals: no esborris documents ni canviïs hashes
   per esquivar la protecció. Notes manuals a docs/project/notes.md.
8. Resumeix què s'ha creat i el primer increment. Continua implementant si l'encàrrec
   ho inclou. L'onboarding no crea serveis, secrets o desplegaments.

No carreguis altres skills durant l'entrevista. ready significa definició inicial
vàlida i documents generats, no producte acabat. Identifica hipòtesis com a tals.
