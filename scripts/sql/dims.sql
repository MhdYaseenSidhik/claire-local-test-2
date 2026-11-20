-- dims.json is assembled from five read-only query_preview statements (limit 5..50 rows each):
SELECT * FROM VEDANTA_POC.DIM_PLANT WHERE PLANT_ID <> 'ALL_PLANTS' ORDER BY PLANT_ID
SELECT * FROM VEDANTA_POC.REF_MATERIAL_GROUP
SELECT * FROM VEDANTA_POC.REF_CRITICALITY
SELECT MATERIAL_TYPE, COUNT(*) AS N FROM VEDANTA_POC.DIM_MATERIAL GROUP BY MATERIAL_TYPE
-- distinct movementClasses / inventoryStatuses come from the materials.json sync (INVENTORY_CLASSIFICATION).
