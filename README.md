# Projecte Intermodular — Gestió Hospitalària

**Base de Dades · Programació · XML/JSON**  
ASIX M372 · M377 · M0003 · M0373 — Curs 25/26

**Autors:** Eric Lopez, Nil Parra  
**Cicle:** 1r ASIX

---

Aplicació de gestió hospitalària feta amb Python, Flask, HTML, CSS i PostgreSQL.

El projecte té tres capes principals: un backend Flask que exposa una API REST, un client d'escriptori Tkinter que la consumeix, i un dashboard de Power BI connectat directament a vistes SQL de PostgreSQL.

## Estructura del projecte

```
Projecte-hospital/
├── iniciar.py                          # Script per arrencar el servidor i el client d'un sol cop
├── requirements.txt                    # Dependències Python del projecte
├── server/
│   ├── main.py                         # Punt d'entrada del backend Flask
│   ├── tools/
│   │   ├── db_driver.py                # Connexió a PostgreSQL i funcions bàsiques de BD
│   │   ├── manager.py                  # Lògica de login, registre i gestió de dades
│   │   ├── crypt.py                    # Xifratge i verificació de contrasenyes amb bcrypt
│   │   ├── masking.py                  # Emmascarament de dades sensibles per rol
│   │   └── dummydata.py                # Generació de dades de prova per als informes
│   ├── html/                           # Plantilles HTML del frontend web
│   ├── css/                            # Fitxers CSS del frontend web
│   ├── sql/                            # Consultes SQL dels informes i exportacions
│   ├── schemas/
│   │   ├── visites_export.schema.json  # JSON Schema de l'exportació de visites
│   │   └── visites_export.xsd          # XSD de l'exportació de visites en XML
│   └── uploads/                        # Fitxers pujats pel backend (CV de metges)
├── client/
│   ├── desktop_main.py                 # Punt d'entrada del client d'escriptori
│   └── desktop/
│       ├── app.py                      # Bootstrap de la finestra Tkinter i navegació
│       ├── api_client.py               # Peticions HTTP al backend Flask
│       ├── config.py                   # Configuració del client (URL, mida de finestra)
│       ├── theme.py                    # Paleta de colors i estils de la interfície
│       └── views/                      # Pantalles del client Tkinter
├── database/
│   ├── design/
│   │   ├── diagrama_ER_hospital.drawio # Diagrama ER editable
│   │   ├── diagrama_ER_hospital.pdf    # Diagrama ER en PDF
│   │   └── diagrama_ER_hospital.png    # Diagrama ER en PNG
│   └── sql/
│       ├── implementacio.sql           # Esquema principal de la base de dades
│       ├── funcions_metge_infermer.sql # Funcions SQL per donar d'alta metges i infermers
│       ├── trigger_usuari.sql          # Trigger que crea el rol PostgreSQL en registrar usuari
│       ├── dashboard_views.sql         # Vistes analítiques per al dashboard de Power BI
│       ├── esquemadeseguretat.sql      # Rols, permisos i usuari powerbi_reader
│       └── test_data.sql               # Dades de prova per a consultes i comprovacions
├── scripts/
│   ├── backups/
│   │   ├── full_backup.py              # Backup complet de la BD amb pg_dumpall i pujada a Drive
│   │   ├── wal_backup.py               # Backup incremental WAL amb pg_basebackup
│   │   ├── drive_manager.py            # Gestió de la pujada a Google Drive
│   │   └── utils.py                    # Utilitats de logging per als scripts de backup
│   └── crash/
│       ├── crash_auto.sh               # Script de vigilància que detecta la caiguda del primari
│       └── failover.sh                 # Script de promoció del servidor de rèplica a primari
├── dashboard/
│   ├── README.md                       # Instruccions de connexió i construcció del report
│   ├── theme.json                      # Tema visual per a Power BI
│   └── dashboard_powerbi.pbix          # Fitxer del dashboard de Power BI
└── extras/
    ├── tailscale_doc.md                # Documentació de la instal·lació de Tailscale
    └── tailscale_installation.md       # Resum de la instal·lació de Tailscale
```

## Base de dades

La base de dades s'ha dissenyat per a PostgreSQL i modela l'entorn d'un hospital.

### Diagrama ER

El diagrama entitat-relació del projecte es troba a `database/design/`:

- `diagrama_ER_hospital.drawio` — versió editable amb draw.io
- `diagrama_ER_hospital.pdf` — versió en PDF per a lliurament
- `diagrama_ER_hospital.png` — versió en imatge per a previsualització ràpida

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
- `supervisio` relaciona personal amb metges supervisors.
- `assignacio_infermer_planta` relaciona els infermers amb la planta on treballen, per poder fer informes de plantilla per planta.
- `usuaris` guarda les credencials de l'aplicació i el vincle amb el registre de `personal`.

### Dades de prova

El fitxer `database/sql/test_data.sql` conté dades de prova per omplir totes les taules i poder fer consultes i comprovacions sense dades reals. Inclou exemples d'assignació d'infermers a plantes per provar el bloc de consultes i informes.

### Funcions i trigger SQL

**`database/sql/funcions_metge_infermer.sql`** defineix dues funcions PL/pgSQL:

- `afegir_metge(...)` — insereix una fila a `personal` i una a `metge` en una sola transacció.
- `afegir_infermer(...)` — insereix una fila a `personal`, una a `enfermer` i una a `supervisio`.

Aquestes funcions garanteixen que les dues insercions es fan sempre juntes i simplifiquen la lògica del backend.

**`database/sql/trigger_usuari.sql`** defineix el trigger `trigger_create_con_rol`:

- S'executa automàticament a l'`INSERT` sobre la taula `usuaris`.
- Llegeix el camp `tipus_feina` del registre de `personal` associat.
- Crea un rol de PostgreSQL per a l'usuari nou i li assigna el rol funcional corresponent (`rol_metge`, `rol_infermer`, `rol_administrador`, etc.).
- Garanteix que cada usuari de l'aplicació té un rol de base de dades assignat sense intervenció manual.

## Esquema de seguretat

L'esquema de seguretat es troba a `database/sql/esquemadeseguretat.sql` i es planteja amb rols de login i rols de grup.

### Rols de PostgreSQL

- `hosp_admin`: usuari tècnic amb administració completa de la base de dades.
- `hosp_app`: usuari tècnic que fa servir el backend de l'aplicació.
- `administrador`, `personal`, `sanitari`, `gestio`, `serveis` i `pacient`: rols de grup.
- `rol_administrador`, `rol_metge`, `rol_infermer`, `rol_administratiu`, `rol_tecnic`, `rol_personal_neteja`, `rol_personal_seguretat`, `rol_personal_cuina` i `rol_pacient`: rols de login amb contrasenya d'exemple `P@ssw0rd`.
- `powerbi_reader`: usuari de només lectura per al dashboard de Power BI.

### Criteri de permisos

- `hosp_admin` té permisos totals sobre les taules i les seqüències.
- `hosp_app` pot llegir, inserir i actualitzar les taules necessàries per al funcionament de l'aplicació.
- `administrador` manté el control total.
- `personal` dona accés base de lectura a dades comunes.
- `sanitari`, `gestio` i `serveis` agrupen els perfils específics de la plantilla.
- `pacient` queda preparat per a un accés restringit amb vistes o RLS.
- `powerbi_reader` té accés de només lectura sobre les vistes `vw_dashboard_*`.
- Les operacions DDL no es fan des de l'aplicació, sinó des del compte d'administració.

### Usuaris de l'aplicació

- Els usuaris reals de la web es desen a la taula `usuaris`.
- En inserir un usuari, el trigger `trigger_create_con_rol` crea automàticament el rol PostgreSQL corresponent i el vincula a `hosp_app`.
- El backend controla la lògica de negoci i el filtratge funcional.

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

## Client d'escriptori Tkinter

La interfície principal de l'aplicació és un client d'escriptori fet amb Tkinter que es connecta al backend Flask per HTTP.

### Pantalles disponibles

- Login
- Home
- Alta de pacient
- Alta de personal
- Informe per planta
- Informe de personal
- Visites per dia
- Informe de visites (amb exportació JSON/XML)
- Informe de quiròfans
- Informe d'aparells
- Informe de supervisió
- Informe d'habitacions
- Informe de metge
- Malalties més comunes
- Ranking de metges
- Informe de pacient

L'informe de visites incorpora un bloc d'exportació de dades que permet descarregar el rang seleccionat en format JSON o XML, i baixar el JSON Schema i l'XSD corresponents. Els esquemes es troben a `server/schemas/`.

## Frontend web

A més del client Tkinter, el backend Flask serveix un frontend web accessible des del navegador. Les pantalles web disponibles són:

- `/login` — formulari d'autenticació
- `/register` — registre d'un nou usuari (vinculat a un `id_intern` de `personal`)
- `/home` — pantalla principal
- `/alta_pacient` — formulari d'alta de pacient
- `/alta_personal` — formulari d'alta de personal

Els informes del frontend web s'accedeixen via les mateixes rutes API que usa el client Tkinter.

## Endpoints del backend

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
- `GET /api/informes/malalties`
- `GET /api/informes/ranking_metges`
- `GET /api/informes/visites_dia?date=YYYY-MM-DD`
- `GET /api/informes/supervisio`
- `GET /api/informes/visites?date=YYYY-MM-DD` o `?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
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

El fitxer del dashboard `dashboard/dashboard_powerbi.pbix` es connecta directament a PostgreSQL i usa aquestes vistes com a font de dades.

## Alta disponibilitat i còpies de seguretat

El projecte inclou scripts d'infraestructura per garantir la continuïtat del servei. Aquests scripts s'executen als servidors i les còpies d'aquí al repositori són de referència.

### Scripts de backup (`scripts/backups/`)

- `full_backup.py` — fa un backup complet de la base de dades amb `pg_dumpall`, el comprimeix i el puja a Google Drive.
- `wal_backup.py` — fa un backup incremental WAL amb `pg_basebackup` i el puja a Google Drive.
- `drive_manager.py` — gestiona l'autenticació i la pujada de fitxers a Google Drive via l'API de Google.
- `utils.py` — funcions de logging comunes per als scripts de backup.

### Scripts de failover (`scripts/crash/`)

L'arquitectura contempla un servidor primari i un servidor de rèplica en streaming (PostgreSQL hot standby).

- `crash_auto.sh` — script de vigilància que s'executa periòdicament al servidor primari. Si detecta que PostgreSQL ha caigut, executa el failover al servidor de rèplica via SSH i crea un fitxer de bloqueig per no fer-ho dues vegades.
- `failover.sh` — script que s'executa al servidor de rèplica per promoure'l a primari: atura PostgreSQL, elimina el fitxer `standby.signal` i el torna a arrencar com a primari.

### Tailscale

La comunicació entre el servidor local i el servidor cloud per a la replicació de streaming es fa a través d'una VPN Tailscale. La documentació de la instal·lació es troba a `extras/tailscale_doc.md`.

## Certificat SSL

El backend suporta connexió SSL. S'activa amb la variable d'entorn `FLASK_USE_SSL=true`. Per a entorns de producció, el certificat s'hauria de generar amb certbot i gestionar-ne la renovació automàtica amb un cron al servidor. En entorn local és habitual usar `FLASK_USE_SSL=false`.

## Variables d'entorn

Cal un fitxer `.env` a l'arrel del projecte (o a `server/`) amb les variables següents:

| Variable | Descripció | Valor per defecte |
|---|---|---|
| `FLASK_USE_SSL` | Activa SSL al backend | `false` |
| `FLASK_HOST` | Host de Flask | `127.0.0.1` |
| `FLASK_PORT` | Port de Flask | `5000` |
| `FLASK_SECRET` | Clau secreta per a les sessions Flask | — |
| `DESKTOP_API_BASE_URL` | URL base del client desktop | `http://127.0.0.1:5000` |
| `DESKTOP_API_VERIFY_TLS` | Verifica certificat TLS al client desktop | `false` |
| `DB_HOST` | Adreça del servidor PostgreSQL | — |
| `DB_PORT` | Port de PostgreSQL o PgBouncer | `5432` |
| `DB_DATABASE` | Nom de la base de dades | `hosp_blanes` |
| `DB_USER` | Usuari de connexió a PostgreSQL | — |
| `DB_PASSWORD` | Contrasenya de l'usuari de PostgreSQL | — |
| `DB_SSLMODE` | Mode SSL de PostgreSQL | `prefer` |

## Dependències Python

Les dependències es troben a `requirements.txt`:

- `Flask` — backend web i API REST
- `psycopg2-binary` — connexió a PostgreSQL
- `python-dotenv` — lectura del fitxer `.env`
- `requests` — peticions HTTP del client Tkinter al backend
- `gunicorn` — servidor WSGI per a desplegament en producció
- `bcrypt` — xifratge de contrasenyes
- `Faker` — generació de dades falses per a proves

## Requisits per executar-ho

- Python 3.10 o superior.
- PostgreSQL instal·lat i en marxa.
- La base de dades ha d'existir i tenir l'esquema carregat abans de fer login o carregar dades.
- Fitxer `.env` amb les variables d'entorn configurades.

## Preparació de la base de dades (primera vegada)

Cal executar els fitxers SQL en aquest ordre:

```bash
psql -U hosp_admin -d hosp_blanes -f database/sql/implementacio.sql
psql -U hosp_admin -d hosp_blanes -f database/sql/funcions_metge_infermer.sql
psql -U hosp_admin -d hosp_blanes -f database/sql/trigger_usuari.sql
psql -U hosp_admin -d hosp_blanes -f database/sql/dashboard_views.sql
psql -U hosp_admin -d hosp_blanes -f database/sql/esquemadeseguretat.sql
psql -U hosp_admin -d hosp_blanes -f database/sql/test_data.sql
```

Si la base ja existia i `esquemadeseguretat.sql` s'havia executat abans de crear les vistes del dashboard, torna'l a executar per aplicar els permisos de `powerbi_reader`.

## Execució en local

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
