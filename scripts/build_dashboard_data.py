#!/usr/bin/env python3
"""Convert the Context Flow sync CSVs (dir given as argv[1]) into public/data/*.json (schemaVersion 3)."""
import csv, json, os, sys

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public", "data")
PLANTS = ["HZL_DEMO_0%d" % i for i in range(1, 7)]


def rd(name):
    with open(os.path.join(SRC, name), newline="") as f:
        return list(csv.DictReader(f))


def num(v):
    if v is None or v == "":
        return None
    x = float(v)
    return int(x) if x == int(x) and abs(x) < 1e15 else x


def txt(v):
    return v if v not in (None, "") else None


def dump(name, obj):
    with open(os.path.join(OUT, name), "w") as f:
        json.dump(obj, f, separators=(",", ":"))
    print("wrote", name)


# ---- kpis.json (ALL_PLANTS kept, per contract) ----
CATALOG = {
 "BACKORDER_VALUE_INR": ("Backorder value", "INR", "lower_is_better", "Value of material demand that could not be fulfilled from stock."),
 "CONSUMPTION_VALUE_INR": ("Consumption value", "INR", "neutral", "Value of stores and spares issued to consumption in the month."),
 "CRITICAL_SPARE_AVAILABILITY_PCT": ("Critical spare availability", "PCT", "higher_is_better", "Share of critical spares available when needed."),
 "DAYS_ON_HAND": ("Days on hand", "DAYS", "lower_is_better", "Inventory value expressed as days of average consumption."),
 "DELAYED_PO_COUNT": ("Delayed purchase orders", "COUNT", "lower_is_better", "Number of open purchase orders past their delivery date."),
 "DUPLICATE_SKU_OPPORTUNITY_INR": ("Duplicate SKU opportunity", "INR", "higher_is_better", "Modelled value that could be released by consolidating duplicate SKUs."),
 "EXCESS_INVENTORY_VALUE_INR": ("Excess inventory value", "INR", "lower_is_better", "Value of stock above the maximum stock level."),
 "GROSS_INVENTORY_VALUE_INR": ("Gross inventory value", "INR", "lower_is_better", "Total value of stores and spares stock on hand."),
 "INVENTORY_TURNOVER_RATIO": ("Inventory turnover", "RATIO", "higher_is_better", "Annualised consumption value divided by inventory value."),
 "NON_MOVING_VALUE_INR": ("Non-moving inventory value", "INR", "lower_is_better", "Value of stock with no recent consumption."),
 "OBSOLETE_VALUE_INR": ("Obsolete inventory value", "INR", "lower_is_better", "Value of stock classed as obsolete."),
 "OPEN_PO_QTY": ("Open PO quantity", "QTY", "neutral", "Quantity on purchase orders not yet received."),
 "OPEN_PO_VALUE_INR": ("Open PO value", "INR", "neutral", "Value of purchase orders not yet received."),
 "OPEN_PR_COUNT": ("Open purchase requisitions", "COUNT", "neutral", "Number of purchase requisitions not yet converted to orders."),
 "OPEN_PR_QTY": ("Open PR quantity", "QTY", "neutral", "Quantity on purchase requisitions not yet ordered."),
 "PO_COUNT": ("Purchase orders", "COUNT", "neutral", "Number of purchase orders raised in the month."),
 "PO_VALUE_INR": ("PO value", "INR", "neutral", "Value of purchase orders raised in the month."),
 "POTENTIAL_INVENTORY_REDUCTION_INR": ("Potential inventory reduction", "INR", "higher_is_better", "Modelled inventory value that could be reduced."),
 "POTENTIAL_INVENTORY_REDUCTION_PCT": ("Potential inventory reduction %", "PCT", "higher_is_better", "Modelled inventory reduction as a share of inventory value."),
 "PR_COUNT": ("Purchase requisitions", "COUNT", "neutral", "Number of purchase requisitions raised in the month."),
 "SLOW_MOVING_VALUE_INR": ("Slow-moving inventory value", "INR", "lower_is_better", "Value of stock with low consumption frequency."),
 "STOCKOUT_MATERIAL_COUNT": ("Stockout materials", "COUNT", "lower_is_better", "Number of materials with zero available stock."),
 "TARGET_INVENTORY_REDUCTION_PCT": ("Target inventory reduction %", "PCT", "higher_is_better", "Scenario target for inventory reduction as a share of inventory value."),
 "UNDERSTOCK_MATERIAL_COUNT": ("Understock materials", "COUNT", "lower_is_better", "Number of materials below their safety stock."),
 "WORKING_CAPITAL_OPPORTUNITY_INR": ("Working capital opportunity", "INR", "higher_is_better", "Modelled working capital that could be released."),
}
k = rd("kpis.csv")
codes = sorted({r["KPI_CODE"] for r in k})
assert set(codes) == set(CATALOG), set(codes) ^ set(CATALOG)
uom = {r["KPI_CODE"]: r["KPI_UOM"] for r in k}
assert all(uom[c] == CATALOG[c][1] for c in codes)
dump("kpis.json", {
 "catalog": [{"code": c, "label": CATALOG[c][0], "uom": uom[c], "direction": CATALOG[c][2], "definition": CATALOG[c][3]} for c in codes],
 "rows": [{"month": r["MONTH"], "plantId": r["PLANT_ID"], "kpiCode": r["KPI_CODE"], "value": num(r["KPI_VALUE"]), "scenario": r["SCENARIO"]} for r in k],
})

# ---- inventory_summary.json ----
ASOF = "2025-12-31"  # INVENTORY_CLASSIFICATION.AS_OF_DATE (min = max = 2025-12-31)
s = rd("summary.csv")
dump("inventory_summary.json", {"asOf": ASOF, "rows": [{
 "plantId": r["PLANT_ID"], "materialGroup": r["MATERIAL_GROUP"], "materialType": r["MATERIAL_TYPE"],
 "criticality": r["CRITICALITY"], "movementClass": r["MOVEMENT_CLASS"], "inventoryStatus": r["INVENTORY_STATUS"],
 "abcClass": r["ABC_CLASS"], "materials": num(r["MATERIALS"]), "availableQty": num(r["AVAILABLE_QTY"]),
 "valueInr": num(r["VALUE_INR"])} for r in s]})

# ---- materials.json ----
m = rd("materials.csv")
dump("materials.json", {"asOf": ASOF, "rows": [{
 "materialId": r["MATERIAL_ID"], "plantId": r["PLANT_ID"], "description": r["DESCRIPTION"],
 "materialGroup": r["MATERIAL_GROUP"], "materialType": r["MATERIAL_TYPE"], "criticality": r["CRITICALITY"],
 "abcClass": r["ABC_CLASS"], "xyzClass": txt(r["XYZ_CLASS"]), "movementClass": r["MOVEMENT_CLASS"],
 "inventoryStatus": r["INVENTORY_STATUS"], "availableQty": num(r["AVAILABLE_QTY"]), "valueInr": num(r["VALUE_INR"]),
 "daysOnHand": num(r["DAYS_ON_HAND"]), "daysSinceLastConsumption": num(r["DAYS_SINCE_LAST_CONSUMPTION"]),
 "safetyStockQty": num(r["SAFETY_STOCK_QTY"]), "reorderPointQty": num(r["REORDER_POINT_QTY"]),
 "maxStockQty": num(r["MAX_STOCK_QTY"]), "trailing12mDemandQty": num(r["TRAILING_12M_DEMAND_QTY"])} for r in m]})

# ---- reorder.json ----
o = rd("reorder.csv")
dump("reorder.json", {"asOf": ASOF, "rows": [{
 "recommendationId": r["RECOMMENDATION_ID"], "materialId": r["MATERIAL_ID"], "plantId": r["PLANT_ID"],
 "materialGroup": r["MATERIAL_GROUP"], "materialType": r["MATERIAL_TYPE"], "criticality": r["CRITICALITY"],
 "priority": r["PRIORITY"], "recommendedPrDate": txt(r["RECOMMENDED_PR_DATE"]), "recommendedQty": num(r["RECOMMENDED_QTY"]),
 "estimatedValueInr": num(r["ESTIMATED_VALUE_INR"]), "availableQty": num(r["AVAILABLE_QTY"]),
 "openPrQty": num(r["OPEN_PR_QTY"]), "openPoQty": num(r["OPEN_PO_QTY"]), "safetyStockQty": num(r["SAFETY_STOCK_QTY"]),
 "reorderPointQty": num(r["REORDER_POINT_QTY"]), "reason": txt(r["REASON"]), "shutdownId": txt(r["SHUTDOWN_ID"])} for r in o]})

# ---- plan_vs_actual.json ----
p = rd("planvsactual.csv")
dump("plan_vs_actual.json", {"rows": [{
 "month": r["MONTH"], "plantId": r["PLANT_ID"], "materialGroup": r["MATERIAL_GROUP"], "materialType": r["MATERIAL_TYPE"],
 "shutdownDriven": r["SHUTDOWN_DRIVEN"], "planValueInr": num(r["PLAN_VALUE_INR"]),
 "actualPoValueInr": num(r["ACTUAL_PO_VALUE_INR"]), "actualGrValueInr": num(r["ACTUAL_GR_VALUE_INR"]),
 "varianceInr": num(r["VARIANCE_INR"]), "variancePct": num(r["VARIANCE_PCT"])} for r in p]})

# ---- dims.json (plants/groups/criticality/types from the queries shown in scripts/sql/dims.sql) ----
PLANT_ROWS = [
 ("HZL_DEMO_01", "Hindustan Zinc Demo Plant 01", "MINE", "North Demo Cluster"),
 ("HZL_DEMO_02", "Hindustan Zinc Demo Plant 02", "SMELTER", "North Demo Cluster"),
 ("HZL_DEMO_03", "Hindustan Zinc Demo Plant 03", "MINE", "South Demo Cluster"),
 ("HZL_DEMO_04", "Hindustan Zinc Demo Plant 04", "CONCENTRATOR", "South Demo Cluster"),
 ("HZL_DEMO_05", "Hindustan Zinc Demo Plant 05", "SMELTER", "West Demo Cluster"),
 ("HZL_DEMO_06", "Hindustan Zinc Demo Plant 06", "CAPTIVE_POWER_PLANT", "East Demo Cluster")]
GROUPS = ["MECHANICAL", "SAFETY", "CONVEYOR_COMPONENTS", "VALVES_AND_FITTINGS", "FILTERS", "ELECTRICAL",
          "PUMP_COMPONENTS", "INSTRUMENTATION", "BEARING_COMPONENTS", "FASTENERS", "LUBRICANTS", "CONSUMABLES"]
title = lambda c: c.replace("_AND_", "_and_").replace("_", " ").title().replace(" And ", " and ")
dump("dims.json", {
 "plants": [{"plantId": a, "name": b, "type": c, "region": d} for a, b, c, d in PLANT_ROWS],
 "materialGroups": [{"code": g, "name": title(g)} for g in GROUPS],
 "materialTypes": [{"code": "ZSPR", "name": "ZSPR"}, {"code": "ZSPN", "name": "ZSPN"}],
 "criticality": [{"code": c, "name": c.title()} for c in ("DESIRABLE", "ESSENTIAL", "VITAL")],
 "movementClasses": sorted({r["MOVEMENT_CLASS"] for r in m}),
 "inventoryStatuses": sorted({r["INVENTORY_STATUS"] for r in m})})
