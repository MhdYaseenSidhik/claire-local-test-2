# Dashboard data contract (schemaVersion 3)

The dashboard reads static JSON files from `public/data/`. `manifest.json` is written last and describes what is present. Numbers are JSON numbers, dates are `YYYY-MM-DD`, months are `YYYY-MM`, missing values are `null`.

## Contract

- manifest.json: {schemaVersion: 3, generatedAt: ISO timestamp of this run, asOf: YYYY-MM-DD (the latest date the source data describes: INVENTORY_CLASSIFICATION.AS_OF_DATE, else the last day of the last month in kpis.json; never the run date), disclaimer: string (the DISCLAIMER text from INVENTORY_KPI_MONTHLY), backcastIncluded: boolean, files: [{name, rows, generatedAt, source: {integrationId, syncId, assetId, sql}}], forecast: null or {experimentId, experimentCreatedAt, problemType, predictionLength, seriesCount, bestModel, metric: {name, value}, backtestError: {mae, wape}, verdict, verdictReasons: [string], forecastAssetId, forecastFrom: YYYY-MM, forecastTo: YYYY-MM}}.
- dims.json: {plants: [{plantId, name, type, region}] (real plants only, never ALL_PLANTS), materialGroups: [{code, name}], materialTypes: [{code, name}] (the material types in scope, e.g. ZSPR and ZSPN; name from the data dictionary or a reference table, else the code), criticality: [{code, name}], movementClasses: [string], inventoryStatuses: [string]}. Sources: DIM_PLANT, REF_MATERIAL_GROUP, REF_CRITICALITY, the distinct DIM_MATERIAL.MATERIAL_TYPE values in scope and the distinct values in INVENTORY_CLASSIFICATION.
- kpis.json: {catalog: [{code, label, uom, direction: "higher_is_better" | "lower_is_better" | "neutral", definition}], rows: [{month, plantId, kpiCode, value, scenario}]}. Source: INVENTORY_KPI_MONTHLY (POSTING_MONTH, PLANT_ID, KPI_CODE, KPI_VALUE, KPI_UOM, SCENARIO_LABEL), every KPI code and month. Here ALL_PLANTS IS kept: it is the portfolio value published by the source, and the dashboard shows it for the all-plants view instead of summing plants (ratios, percentages and days cannot be summed). catalog has one entry per KPI_CODE; label is a readable title; definition is one plain sentence; direction is lower_is_better for values, counts and days of excess, non-moving, slow-moving, obsolete, backorder, stockout, understock, delayed and days on hand, higher_is_better for turnover, critical spare availability, potential or target reduction and working-capital opportunity, neutral for volumes such as PO, PR and consumption counts and values.
- inventory_summary.json: {asOf, rows: [{plantId, materialGroup, materialType, criticality, movementClass, inventoryStatus, abcClass, materials, availableQty, valueInr}]}. Source: INVENTORY_CLASSIFICATION joined to DIM_MATERIAL, grouped by those dimensions; materials is a count, the others are sums. Real plants only.
- materials.json: {asOf, rows: [{materialId, plantId, description, materialGroup, materialType, criticality, abcClass, xyzClass, movementClass, inventoryStatus, availableQty, valueInr, daysOnHand, daysSinceLastConsumption, safetyStockQty, reorderPointQty, maxStockQty, trailing12mDemandQty}]}. Source: INVENTORY_CLASSIFICATION (one row per material x plant; sum storage locations) joined to DIM_MATERIAL for description, group and type. Real plants only.
- reorder.json: {asOf, rows: [{recommendationId, materialId, plantId, materialGroup, materialType, criticality, priority, recommendedPrDate, recommendedQty, estimatedValueInr, availableQty, openPrQty, openPoQty, safetyStockQty, reorderPointQty, reason, shutdownId}]}. Source: REORDER_RECOMMENDATION joined to DIM_MATERIAL for group, type and criticality. Real plants only.
- plan_vs_actual.json: {rows: [{month, plantId, materialGroup, materialType, shutdownDriven, planValueInr, actualPoValueInr, actualGrValueInr, varianceInr, variancePct}]}. Source: BUSINESS_PLAN_VS_ACTUAL (CALENDAR_MONTH as month). Real plants only.
- forecast_holdout.json: {kind: "backtest", note: "Predictions for held-out months the model did not see; not a forecast of future months.", experimentId, predictionLength, metric: {name, value}, error: {mae, wape}, leaderboard: [{model, metric}], byPlantMonth: [{plantId, month, actual, predicted}], series: [{seriesId, materialId, plantId, materialGroup, materialType, month, actual, predicted, lower, upper}]}. lower/upper are null when the file has no intervals. If series would exceed 15 MB, keep the 2,000 series with the largest actual volume, state that in note, and keep byPlantMonth complete.
- forecast.json: {available: boolean, reason: string or null, kind: "forecast", experimentId, assetId, predictionLength, forecastFrom: YYYY-MM, forecastTo: YYYY-MM, horizons: [3, 6, 12] (only those up to predictionLength), note: string, byPlantMonth: [{plantId, month, horizon, predicted}], rows: [{seriesId, materialId, plantId, materialGroup, materialType, month, horizon, predicted, lower, upper}]}. horizon is the month's step after the last history month (1 for the first forecast month, up to predictionLength); the dashboard's 3 / 6 / 12-month view shows rows with horizon up to 3, 6 or 12. predicted is the mean; lower and upper are the 0.1 and 0.9 quantiles. byPlantMonth sums predicted over every series of a plant and month; it has no interval, because quantiles cannot be summed. Values are not clipped: a negative value means more reversals than issues are expected. If rows would exceed 15 MB, keep the 2,000 series with the largest total predicted, state that in note, and keep byPlantMonth complete. With no forecast: {available: false, reason: "<why>", kind: "forecast", horizons: [3, 6, 12], byPlantMonth: [], rows: []}.

## Files in this refresh (dashboard data refresh, schemaVersion 3)

All files cover material types ZSPR and ZSPN and plants HZL_DEMO_01..06 (ALL_PLANTS only in `kpis.json`), and include the fabricated 2023 backcast year (`manifest.backcastIncluded = true`). `manifest.asOf` is 2025-12-31 (INVENTORY_CLASSIFICATION.AS_OF_DATE). Every figure is a simulated POC figure; show `manifest.disclaimer` with it.

| file | grain | rows key |
|---|---|---|
| dims.json | plants, material groups, material types, criticality, movement classes, inventory statuses | n/a (dimension lists) |
| kpis.json | month x plant (incl. ALL_PLANTS) x KPI code x scenario, plus a 25-entry catalog | rows |
| inventory_summary.json | plant x material group x material type x criticality x movement class x inventory status x ABC class | rows |
| materials.json | material x plant (storage locations summed) | rows |
| reorder.json | one reorder recommendation | rows |
| plan_vs_actual.json | month x plant x material group x material type x shutdownDriven | rows |
| hzl01_net_consumption.json | HZL_DEMO_01 forecast training set, material x month (columnar, described below) | rows |
| forecast_holdout.json, forecast.json | written by the forecast task; absent until it runs (`manifest.forecast` is `null`) | n/a |

`manifest.files[].rows` is the length of the file's `rows` array (for `dims.json`, the number of plants). Each manifest entry carries the integrationId, syncId, assetId and exact SQL of the Context Flow sync it came from; the SQL is also in `scripts/sql/`. `scripts/build_dashboard_data.py` converts the synced CSVs to JSON and `scripts/validate_data.py` checks the contract.

### hzl01_net_consumption.json

Columnar layout to keep the file small: `{kind: "training_set", grain, target, plantId, columns: [...], rows: [[...], ...]}`. Each row follows `columns` in order.

| column | meaning |
|---|---|
| seriesId | `MATERIAL_ID\|PLANT_ID`, the AutoML item id |
| materialId, plantId | plantId is HZL_DEMO_01 only |
| materialGroup, materialType | from DIM_MATERIAL (type is ZSPR or ZSPN) |
| month | `YYYY-MM`, period start month |
| netConsumptionQty | target: movement 261 (issue) minus 262 (reversal) per material and month; empty months are 0 |
| plannedMaintenanceQty | covariate: FACT_MAINTENANCE_REQUIREMENT.REQUIRED_QTY by planned start month |
| plannedShutdownQty | covariate: FACT_SHUTDOWN_SCHEDULE.REQUIRED_QTY by planned start month |
| plantShutdownMonthFlag | covariate: 1 when a HZL_DEMO_01 shutdown event overlaps the month |
| seasonIndex | covariate: SEASONALITY_INPUT manual override, else derived index, by plant, material group and calendar month |
| monthOfYear | covariate: 1-12 |

Range 2023-01 to 2025-12 (36 months, the first and last months with source records). 2023 is the fabricated backcast year and is included. No columns computed over the full history are included.
