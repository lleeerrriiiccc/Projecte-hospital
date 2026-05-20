# Dashboard Power BI

Aquest directori recull els fitxers i les instruccions del dashboard de Power BI del projecte.

## Fitxers del dashboard

- `theme.json`: tema visual recomanat per a Power BI, alineat amb la paleta de l'aplicacio.
- `hospital_dashboard.pbix`: guarda aqui el fitxer de Power BI quan el construeixis des d'una maquina amb Power BI Desktop.

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

Com a alternativa, pots executar `python scripts/apply_dashboard_setup.py` per aplicar `dashboard_views.sql`, actualitzar `powerbi_reader` i verificar que pot llegir les vistes principals.

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