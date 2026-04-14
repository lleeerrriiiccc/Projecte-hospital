# Projecte-hospital

Aplicació de gestió hospitalària feta amb Python, Flask, HTML, CSS i PostgreSQL.

## Estructura del projecte

- `app/main.py`: punt d'entrada de l'aplicació web.
- `app/tools/db_driver.py`: connexió a PostgreSQL i funcions bàsiques de base de dades.
- `app/tools/manager.py`: lògica de login, registre i gestió d'usuaris.
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

L'esquema de seguretat s'ha plantejat de manera senzilla, pensant en un projecte d'ASIX1.

### Usuaris tècnics de PostgreSQL

- `hosp_admin`: usuari tècnic amb administració completa de la base de dades.
- `hosp_app`: usuari tècnic que farà servir el backend de l'aplicació.

### Criteri de permisos

- `hosp_admin` té permisos totals sobre les taules i les seqüències.
- `hosp_app` pot llegir, inserir i actualitzar les taules necessàries per al funcionament de l'aplicació.
- Les operacions de DDL no es fan des de l'aplicació, sinó des del compte d'administració.

### Usuaris de l'aplicació

- Els usuaris reals de la web es desen a la taula `usuaris`.
- Els rols funcionals de l'aplicació són: administrador, personal i pacient.
- El control d'aquests rols es fa des del backend, no com a rols de PostgreSQL.

### Accés del pacient

- De moment no és obligatori fer servir vistes per a pacient.
- L'opció més simple és que el backend faci consultes filtrades amb l'identificador del pacient autenticat.
- Si més endavant cal més aïllament a nivell de base de dades, es poden afegir vistes de només lectura.
