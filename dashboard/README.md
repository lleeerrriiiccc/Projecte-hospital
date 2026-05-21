# Dashboard Power BI

Aquest directori recull els fitxers i les instruccions del dashboard de Power BI del projecte.

## Fitxers del dashboard

- `theme.json`: tema visual recomanat per a Power BI, alineat amb la paleta de l'aplicacio.
- `dashboard_powerbi.pbix`: fitxer actual del dashboard de Power BI del projecte.

## Vistes que consumeix Power BI

El dashboard esta pensat per llegir directament aquestes vistes de PostgreSQL:

- `vw_dashboard_visites_area_dia`
- `vw_dashboard_visites_metge_dia`
- `vw_dashboard_visites_franja_dia`
- `vw_dashboard_ocupacio_habitacions_dia`
- `vw_dashboard_quirofans_dia`
- `vw_dashboard_malalties_dia`
- `vw_dashboard_planta_recursos`
- `vw_dashboard_visites_detall`

## Ordre recomanat de preparacio

1. Executa `database/sql/implementacio.sql`.
2. Executa `database/sql/dashboard_views.sql`.
3. Executa `database/sql/esquemadeseguretat.sql` per crear `powerbi_reader` i aplicar els grants sobre les vistes.
4. Executa `database/sql/test_data.sql` si vols carregar dades de prova.

Aquest repositori no inclou cap script automatitzat per fer aquesta seqüència; si treballes des d'una base ja creada, executa manualment els fitxers SQL en l'ordre indicat més amunt.

Si la base ja existia i `esquemadeseguretat.sql` s'havia executat abans de crear les vistes del dashboard, torna'l a executar per aplicar els permisos de `powerbi_reader`.

## Connexio des de Power BI Desktop

1. Obre Power BI Desktop.
2. Selecciona PostgreSQL com a font de dades.
3. Introdueix el servidor i la base de dades del projecte.
4. Fes login amb `powerbi_reader`.
5. Importa les vistes del dashboard.
6. Carrega `theme.json` com a tema del report.

En aquest entorn no hi ha Power BI Desktop ni `pbi-tools`, aixi que el `.pbix` s'ha de generar en una maquina que si disposi d'aquestes eines.

## Pagines recomanades

1. Resum executiu: visites avui, visites per area, operacions avui i ocupacio actual.
2. Activitat assistencial: ranking de metges, franges horaries i tendencia de visites.
3. Recursos hospitalaris: ocupacio per planta i activitat de quirofans.
4. Vista clinica: malalties mes frequents i pacients afectats.

## Ajustos visuals recomanats

Perque el report sembli un dashboard real i no nomes una pagina amb visuals solts, convé tocar aquests punts directament a Power BI Desktop:

1. Usa format de pagina 16:9 i deixa marges amples, amb fons clar i visuals en targetes blanques.
2. Reserva la primera fila per a 3 o 4 KPI cards grans: visites del dia, ocupacio, operacions i una metrica d'alerta.
3. Col·loca els filtres principals a dalt en format slicer horitzontal: data, area i planta.
4. No barregis massa visuals en una sola pagina; 4 o 5 visuals ben agrupats funcionen millor que 9 petits.
5. Mantén els titols curts i consistents: mateix estil, mateixa mida i alineacio a l'esquerra.
6. Oculta capçaleres de visual i evita marcs gruixuts; el pes visual ha d'estar en les dades, no en el contenidor.
7. Fes servir una jerarquia simple de colors: blau per volum/activitat, verd per correcte, vermell per incidencies i taronja per avisos.
8. Afegeix una pagina inicial de resum executiu i deixa els detalls per a pagines posteriors, no tot a la portada.

Amb el `theme.json` actualitzat ja tens una base de colors coherent amb l'aplicacio, pero l'efecte de "dashboard real" dependrà sobretot del layout, de la mida dels visuals i de reduir soroll visual dins del report.