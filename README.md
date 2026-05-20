# Projecte-hospital

Aplicació de gestió hospitalària feta amb Python, Flask, HTML, CSS i PostgreSQL.

## Estructura del projecte

- `iniciar.py`: script per arrencar el servidor i el client d'un sol cop.
- `server/main.py`: punt d'entrada de l'aplicació web (Flask).
- `server/tools/db_driver.py`: connexió a PostgreSQL i funcions bàsiques de base de dades.
- `server/tools/manager.py`: lògica de login, registre i gestió d'usuaris i dades.
- `server/tools/crypt.py`: funcions per xifrar i verificar contrasenyes amb bcrypt.
- `server/tools/masking.py`: emmascarament de dades sensibles segons el rol de l'usuari.
- `server/html/`: plantilles HTML.
- `server/css/`: fitxers CSS.
- `server/uploads/`: fitxers pujats pel backend (CV de metges).
- `server/sql/`: consultes SQL dels informes.
- `client/desktop_main.py`: punt d'entrada del client d'escriptori.
- `client/desktop/app.py`: bootstrap de la finestra Tkinter i navegació entre pantalles.
- `client/desktop/api_client.py`: funcions per fer peticions HTTP al backend Flask.
- `client/desktop/config.py`: configuració del client (URL del servidor, mida de finestra).
- `client/desktop/theme.py`: paleta de colors i estils visuals de la interfície.
- `client/desktop/views/`: pantalles de la interfície Tkinter.
- `database/sql/implementacio.sql`: esquema principal de la base de dades.
- `database/sql/esquemadeseguretat.sql`: esquema de seguretat i permisos.
- `database/sql/dashboard_views.sql`: vistes analítiques per al dashboard de Power BI.
- `database/sql/test_data.sql`: dades de prova per fer consultes i comprovacions.
- `scripts/apply_dashboard_setup.py`: aplica les vistes del dashboard, actualitza `powerbi_reader` i valida l'accés de Power BI.
- `dashboard/`: documentació i tema visual del dashboard Power BI.

## Base de dades

La base de dades està pensada per a PostgreSQL i modela l'entorn hospitalari.

### Taules principals

- `personal`
- `metge`
- `enfermer`
- `pacient`
- `planta`
- `habitacio`
- `medicament`
- `quirofan`
- `maquina`
- `visita`
- `recepta`
- `operacio`
- `assisteix`
- `inventari`
- `reserva_habitacio`
- `supervisio`
- `assignacio_infermer_planta`
- `usuaris`

### Relacions principals

- `metge` i `enfermer` depenen de `personal`.
- `visita` relaciona un pacient amb un metge.
- `recepta` relaciona una visita amb un medicament.
- `operacio` relaciona un pacient amb un quiròfan.
- `assisteix` relaciona personal amb operacions.
- `inventari` relaciona quiròfans amb màquines.
- `reserva_habitacio` relaciona pacients amb habitacions.
- `supervisio` relaciona personal amb metges.
- `assignacio_infermer_planta` relaciona els infermers amb la planta on treballen per poder fer informes per planta.
- `usuaris` guarda les credencials de l'aplicació i el vincle amb personal.

### Dades de prova

El fitxer `database/sql/test_data.sql` conté dades de prova per omplir totes les taules i poder fer consultes i comprovacions sense dades reals.
També inclou exemples d'assignació d'infermers a plantes per poder provar el bloc de consultes i informes.

### Canvi de model per als informes

Per poder calcular quants infermers treballen a cada planta s'ha afegit la taula de relació `assignacio_infermer_planta` entre `enfermer` i `planta`.

Si la base de dades ja tenia la versió anterior de l'esquema, només cal executar el bloc de migració afegit al final de `database/sql/implementacio.sql` per crear aquesta relació nova sense reconstruir tota la base de dades.

## Esquema de seguretat

L'esquema de seguretat s'ha plantejat amb rols de login i rols de grup.

### Rols de PostgreSQL

- `hosp_admin`: usuari tècnic amb administració completa de la base de dades.
- `hosp_app`: usuari tècnic que farà servir el backend de l'aplicació.
- `administrador`, `personal`, `sanitari`, `gestio`, `serveis` i `pacient`: rols de grup.
- `rol_administrador`, `rol_metge`, `rol_infermer`, `rol_administratiu`, `rol_tecnic`, `rol_personal_neteja`, `rol_personal_seguretat`, `rol_personal_cuina` i `rol_pacient`: rols de login amb contrasenya d'exemple `P@ssw0rd`.

### Criteri de permisos

- `hosp_admin` té permisos totals sobre les taules i les seqüències.
- `hosp_app` pot llegir, inserir i actualitzar les taules necessàries per al funcionament de l'aplicació.
- `administrador` manté el control total.
- `personal` dona accés base de lectura a dades comunes.
- `sanitari`, `gestio` i `serveis` agrupen els perfils específics de la plantilla.
- `pacient` queda preparat per a un accés restringit amb vistes o RLS.
- Les operacions de DDL no es fan des de l'aplicació, sinó des del compte d'administració.

### Usuaris de l'aplicació

- Els usuaris reals de la web es desen a la taula `usuaris`.
- Els rols funcionals de l'aplicació també existeixen com a rols de PostgreSQL i tambe es guarden a la base de dades per poder identificar a cada usuari correctament.
- El backend continua controlant la lògica de negoci i el filtratge funcional.
- La relació `assignacio_infermer_planta` s'ha afegit per poder fer informes de plantilla per planta de manera clara i senzilla.

### Accés del pacient

- De moment no és obligatori fer servir vistes per a pacient.
- L'opció més simple és que el backend faci consultes filtrades amb l'identificador del pacient autenticat.
- Si més endavant cal més aïllament a nivell de base de dades, es poden afegir vistes de només lectura.

## Certificat SSL

Per garantir una connexió segura, més endavant s'implementarà l'ús d'un certificat SSL al servidor.

### Com es faria

- Es generaria o s'obtindria un certificat vàlid per al domini o entorn de proves amb certbot.
- El servidor web s'encarregaria de fer servir HTTPS i de redirigir el trànsit HTTP cap a HTTPS.
- La renovació del certificat es faria de manera automàtica quan el certificat ho requereixi amb un cron dintre del servidor.
- La configuració de seguretat es mantindria fora del codi de l'aplicació, a nivell de servidor.

## Emmascarament de dades

El backend disposa d'un sistema d'emmascarament implementat a `server/tools/masking.py` que protegeix les dades personals de grau alt.

### Com funciona

- Els camps sensibles són: `dni`, `telefon`, `telefon2`, `email`, `email_intern` i `data_naixement`.
- Cada camp té la seva pròpia funció de màscara: `mask_dni`, `mask_phone`, `mask_email`, `mask_date`.
- La funció `mask_payload` recorre totes les files retornades per la base de dades i aplica les màscares necessàries.
- L'emmascarament es fa al backend, just abans de retornar les dades per API. La base de dades guarda sempre les dades originals.

### Criteri d'accés

- Els rols `hosp_admin`, `administrador` i `rol_administrador` veuen les dades senceres.
- La resta d'usuaris veuen els camps sensibles amb una màscara parcial.
- Si més endavant cal més aïllament, es poden afegir vistes o consultes específiques per a cada rol.

## Client d'escriptori Tkinter

La interfície principal de l'aplicació és un client d'escriptori fet amb Tkinter que es connecta al backend Flask per HTTP.

Estat actual: client completament funcional, conviu amb el frontend web original.

### Pantalles disponibles

- Login
- Home
- Alta de pacient
- Alta de personal
- Informe per planta
- Informe de personal
- Visites per dia
- Informe de visites
- Informe de quiròfans
- Informe d'aparells
- Informe de supervisió
- Informe d'habitacions
- Informe de metge
- Informe de pacient

L'informe de visites, tant al frontend web com al client Tkinter, incorpora ara un bloc d'exportació de dades. Aquest bloc permet descarregar el rang seleccionat en format JSON o XML, i també baixar el JSON Schema i l'XSD corresponents.

### Endpoints del backend

**Autenticació:**
- `POST /api/login`
- `POST /api/logout`
- `POST /api/register`
- `GET /me`

**Alta de dades:**
- `POST /api/pacients`
- `POST /api/personal`

**Consultes:**
- `GET /api/metges`
- `GET /api/pacients`
- `GET /api/habitacions`
- `GET /api/informes/planta`
- `GET /api/informes/personal`
- `GET /api/informes/visites_dia?date=YYYY-MM-DD`
- `GET /api/informes/supervisio`
- `GET /api/informes/visites?date=YYYY-MM-DD` o `GET /api/informes/visites?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /api/informes/quirofans?date=YYYY-MM-DD`
- `GET /api/informes/habitacions?habitacio=NUM`
- `GET /api/informes/metge?metge=ID&date=YYYY-MM-DD`
- `GET /api/informes/aparells`
- `GET /api/informes/pacient?pacient=ID`

**Exportació de visites:**
- `GET /api/exportacions/visites/json?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /api/exportacions/visites/xml?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /api/exportacions/visites/schema/json`
- `GET /api/exportacions/visites/schema/xml`

Els fitxers d'exportació inclouen el rang de dates i, per a cada visita, `id_visita`, `dia`, `metge` i un bloc `pacient` amb `id_pacient`, `nom`, `cognom` i `cognom2`. Tant el JSON com l'XML es generen indentats amb tabulacions.

### Variables d'entorn

- `FLASK_USE_SSL`: `true` o `false` per activar/desactivar SSL al backend.
- `FLASK_HOST`: host de Flask (per defecte `127.0.0.1`).
- `FLASK_PORT`: port de Flask (per defecte `5000`).
- `FLASK_SECRET`: clau secreta de Flask per a les sessions.
- `DESKTOP_API_BASE_URL`: URL base que usa el client desktop (per defecte `http://127.0.0.1:5000`).
- `DESKTOP_API_VERIFY_TLS`: `true` o `false` per verificar certificat TLS al client desktop.
- `DB_HOST`: adreça del servidor PostgreSQL.
- `DB_PORT`: port del servidor PostgreSQL o de PgBouncer. Per defecte `5432`.
- `DB_DATABASE`: nom de la base de dades (per exemple `hosp_blanes`).
- `DB_USER`: usuari de connexió a PostgreSQL.
- `DB_PASSWORD`: contrasenya de l'usuari de PostgreSQL.
- `DB_SSLMODE`: mode SSL de PostgreSQL. Per treballar en local és recomanable `prefer`.

### Requisits per executar-ho

- Cal tenir PostgreSQL instal·lat i en marxa.
- La base de dades ha d'existir i tenir l'esquema carregat abans de fer login o carregar dades.
- Si PostgreSQL no està arrencat, el backend i el client s'obriran igualment, però les accions que depenen de base de dades retornaran error.
- Cal un fitxer `.env` a l'arrel del projecte (o a `server/`) amb les variables d'entorn.

### Execució en local

**Opció 1 — script d'inici ràpid (recomanat):**

```bash
python iniciar.py
```

Aquesta ordre arrenca el servidor Flask i el client Tkinter d'un sol cop. Quan es tanca la finestra del client, el servidor s'atura automàticament.

**Opció 2 — arrencada manual en dues terminals:**

1. Arrenca el backend:

```bash
cd server
python main.py
```

2. En una altra terminal, arrenca el client:

```bash
cd client
python desktop_main.py
```

**Preparació de la base de dades (primera vegada):**

```bash
psql -U hosp_admin -d hosp_blanes -f database/sql/implementacio.sql
psql -U hosp_admin -d hosp_blanes -f database/sql/dashboard_views.sql
psql -U hosp_admin -d hosp_blanes -f database/sql/esquemadeseguretat.sql
psql -U hosp_admin -d hosp_blanes -f database/sql/test_data.sql
```

**Aplicació ràpida del paquet Power BI sobre una base ja existent:**

```bash
python scripts/apply_dashboard_setup.py
```

Aquest script reaplica les vistes analítiques, ajusta el login `powerbi_reader` i comprova que pot llegir com a minim `vw_dashboard_visites_area_dia` i `vw_dashboard_quirofans_dia`.

### Millores opcionals pendents

- Ajustos visuals pixel-perfect respecte HTML/CSS original.
- Carrega en segon pla de crides API per evitar bloqueig temporal de la UI en consultes pesades.

## Dashboard Power BI

El projecte incorpora una capa de vistes SQL pensada per alimentar un dashboard extern fet amb Power BI, sense dependre del backend Flask ni del client Tkinter.

### Vistes del dashboard

El fitxer `database/sql/dashboard_views.sql` crea aquestes vistes en `public`:

- `vw_dashboard_visites_area_dia`
- `vw_dashboard_visites_metge_dia`
- `vw_dashboard_visites_franja_dia`
- `vw_dashboard_ocupacio_habitacions_dia`
- `vw_dashboard_quirofans_dia`
- `vw_dashboard_malalties_dia`
- `vw_dashboard_planta_recursos`
- `vw_dashboard_visites_detall`

Aquestes vistes cobreixen el minim demanat per al quadre de comandament i amplien el dashboard a ocupacio, quirofans i vista clinica.

### Usuari de Power BI

`database/sql/esquemadeseguretat.sql` crea l'usuari `powerbi_reader`, pensat exclusivament per llegir les vistes del dashboard.

- `powerbi_reader` te `CONNECT` a la base.
- `powerbi_reader` te `USAGE` sobre `public`.
- `powerbi_reader` te `SELECT` nomes sobre les vistes `vw_dashboard_*` quan aquestes existeixen.

Si executes `esquemadeseguretat.sql` abans de crear les vistes del dashboard, cal tornar-lo a executar despres per aplicar els grants.

### Ordre recomanat d'execucio

Per deixar la base preparada per al dashboard:

```bash
psql -U hosp_admin -d hosp_blanes -f database/sql/implementacio.sql
psql -U hosp_admin -d hosp_blanes -f database/sql/dashboard_views.sql
psql -U hosp_admin -d hosp_blanes -f database/sql/esquemadeseguretat.sql
psql -U hosp_admin -d hosp_blanes -f database/sql/test_data.sql
```

### Entregable Power BI

La carpeta `dashboard/` inclou:

- `README.md` amb els passos de connexio i construccio del report.
- `theme.json` amb el tema visual recomanat.
- espai per guardar el fitxer `hospital_dashboard.pbix`.

