# Dashboard Power BI

Aquest directori conté els fitxers i les instruccions del dashboard de Power BI del projecte.

## Fitxers del dashboard

- `dashboard_powerbi.pbix` — fitxer del dashboard de Power BI del projecte.
- `theme.json` — tema visual recomanat per a Power BI, alineat amb la paleta de l'aplicació.

## Vistes que consumeix Power BI

El dashboard es connecta directament a PostgreSQL i llegeix aquestes vistes, definides a `database/sql/dashboard_views.sql`:

- `vw_dashboard_visites_area_dia` — visites agrupades per àrea i dia
- `vw_dashboard_visites_metge_dia` — visites per metge i dia
- `vw_dashboard_visites_franja_dia` — visites per franja horària i dia
- `vw_dashboard_ocupacio_habitacions_dia` — ocupació d'habitacions per dia
- `vw_dashboard_quirofans_dia` — activitat de quiròfans per dia
- `vw_dashboard_malalties_dia` — malalties diagnosticades per dia
- `vw_dashboard_planta_recursos` — recursos humans per planta
- `vw_dashboard_visites_detall` — detall de cada visita

## Usuari de Power BI

`database/sql/esquemadeseguretat.sql` crea l'usuari `powerbi_reader`, pensat exclusivament per llegir les vistes del dashboard:

- Té `CONNECT` a la base de dades.
- Té `USAGE` sobre l'esquema `public`.
- Té `SELECT` només sobre les vistes `vw_dashboard_*`.

## Ordre recomanat de preparació

1. Executa `database/sql/implementacio.sql`.
2. Executa `database/sql/funcions_metge_infermer.sql`.
3. Executa `database/sql/trigger_usuari.sql`.
4. Executa `database/sql/dashboard_views.sql`.
5. Executa `database/sql/esquemadeseguretat.sql` per crear `powerbi_reader` i aplicar els permisos sobre les vistes.
6. Executa `database/sql/test_data.sql` si vols carregar dades de prova.

Si `esquemadeseguretat.sql` s'havia executat abans de crear les vistes del dashboard, torna'l a executar per aplicar els permisos de `powerbi_reader`.

## Connexió des de Power BI Desktop

1. Obre Power BI Desktop.
2. Selecciona **PostgreSQL** com a font de dades.
3. Introdueix el servidor i la base de dades del projecte.
4. Fes login amb l'usuari `powerbi_reader`.
5. Importa les vistes del dashboard (`vw_dashboard_*`).
6. Carrega `theme.json` com a tema del report.

## Pàgines del dashboard

1. **Resum executiu** — visites avui, visites per àrea, operacions avui i ocupació actual.
2. **Activitat assistencial** — ranking de metges, franges horàries i tendència de visites.
3. **Recursos hospitalaris** — ocupació per planta i activitat de quiròfans.
4. **Vista clínica** — malalties més freqüents i pacients afectats.

## Ajustos visuals recomanats

- Usa format de pàgina 16:9 amb fons clar i visuals en targetes blanques.
- Reserva la primera fila per a KPI cards grans: visites del dia, ocupació, operacions i una mètrica d'alerta.
- Col·loca els filtres principals a dalt en format slicer horitzontal: data, àrea i planta.
- No barregis massa visuals en una sola pàgina; 4 o 5 ben agrupats funcionen millor que 9 petits.
- Mantén els títols curts i consistents: mateix estil, mateixa mida i alineació a l'esquerra.
- Oculta capçaleres de visual i evita marcs gruixuts; el pes visual ha d'estar en les dades.
- Jerarquia de colors: blau per volum/activitat, verd per correcte, vermell per incidències i taronja per avisos.

El `theme.json` ja proporciona una base de colors coherent amb l'aplicació.
