# Projecte-hospital

Aplicació de gestió hospitalària feta amb Python, Flask, HTML, CSS i PostgreSQL.

## Estructura del projecte

- `app/main.py`: punt d'entrada de l'aplicació web.
- `app/tools/db_driver.py`: connexió a PostgreSQL i funcions bàsiques de base de dades.
- `app/tools/manager.py`: lògica de login, registre i gestió d'usuaris.
- `app/tools/masking.py`: utilitats previstes per emmascarar dades sensibles.
- `app/html/`: plantilles HTML.
- `app/css/`: fitxers CSS.
- `base_de_dades/implementacio.sql`: esquema principal de la base de dades.
- `base_de_dades/esquemadeseguretat.sql`: esquema de seguretat i permisos.
- `proves/data_prova.sql`: dades de prova per fer consultes i comprovacions.

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
- `usuaris` guarda les credencials de l'aplicació i el vincle amb personal.

### Dades de prova

En un futur es generara la dummy data per omplir tota la base de dades amb informació necessaria.

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

Per protegir les dades personals de grau alt, més endavant s'implementarà un sistema d'emmascarament al backend.

### Com es faria

- Es determinarien els camps de caràcter personal de grau alt, com ara `dni`, `telefon`, `telefon2`, `email`, `email_intern` i `data_naixement`.
- Es definiria quins rols poden veure la informació completa i quins només la versió parcialment amagada.
- L'emmascarament es faria a l'aplicació, abans de mostrar les dades a pantalla o retornar-les per API.
- A la base de dades es mantindrien les dades originals, sense modificar-les.

### Criteri proposat

- L'usuari amb accés complet veuria les dades senceres.
- La resta d'usuaris veurien els camps sensibles amb una màscara parcial.
- Si més endavant es volgués reforçar la seguretat, es podrien afegir vistes o consultes específiques per a cada rol.

## Migracio inicial a Tkinter

S'ha iniciat la migracio de la interfície web cap a una aplicacio d'escriptori amb Tkinter mantenint el backend Flask.

Estat actual: migracio funcional completada (web i desktop poden conviure).

### Estat actual

- Es manté el frontend web existent.
- S'ha afegit un client desktop en `app/desktop/`.
- Ja hi ha aquestes pantalles en Tkinter:
	- Login
	- Home
	- Alta de pacient
	- Alta de personal
	- Informe de visites
	- Informe de quirofans
	- Informe d'aparells
	- Informe de supervisio
	- Informe d'habitacions
	- Informe de metge
	- Informe de pacient

### Nous endpoints JSON per a desktop

- `POST /api/login`
- `POST /api/logout`
- `POST /api/register`
- `POST /api/pacients`
- `POST /api/personal`

Els endpoints API de consultes ja existents (`/api/informes/*`, `/api/metges`, `/api/habitacions`, `/api/pacients`) es mantenen.

### Variables d'entorn utiles

- `FLASK_USE_SSL`: `true` o `false` per activar/desactivar SSL al backend.
- `FLASK_HOST`: host de Flask (per defecte `0.0.0.0`).
- `FLASK_PORT`: port de Flask (per defecte `443`).
- `DESKTOP_API_BASE_URL`: URL base que usa Tkinter (per defecte `http://127.0.0.1:443`).
- `DESKTOP_API_VERIFY_TLS`: `true` o `false` per verificar certificat TLS al client desktop.

### Execucio en local (web + desktop)

1. Arrenca el backend:

```bash
cd app
FLASK_USE_SSL=false FLASK_PORT=443 python3 main.py
```

2. En una altra terminal, arrenca la GUI Tkinter:

```bash
cd app
DESKTOP_API_BASE_URL=http://127.0.0.1:443 python3 desktop_main.py
```

### Millores opcionals pendents

- Ajustos visuals pixel-perfect respecte HTML/CSS original.
- Carrega en segon pla de crides API per evitar bloqueig temporal de la UI en consultes pesades.

