#!/usr/bin/env python3
"""Convert the Context Flow asset CSV (sync hzl01-netconsump-s2-*) into
public/data/hzl01_net_consumption.json. Usage: build_hzl01_data.py <dataset.csv> <out_dir>"""
import csv, json, sys, collections

src, out = sys.argv[1], sys.argv[2]
COLS = ["seriesId", "materialId", "plantId", "materialGroup", "materialType", "month",
        "netConsumptionQty", "plannedMaintenanceQty", "plannedShutdownQty",
        "plantShutdownMonthFlag", "seasonIndex", "monthOfYear"]
rows, per_month = [], collections.defaultdict(float)
with open(src, newline="") as f:
    for r in csv.DictReader(f):
        month = r["PERIOD_START_DATE"][:7]
        q = float(r["NET_CONSUMPTION_QTY"])
        per_month[month] += q
        si = r["SEASON_INDEX"]
        rows.append([r["SERIES_ID"], r["MATERIAL_ID"], r["PLANT_ID"], r["MATERIAL_GROUP"],
                     r["MATERIAL_TYPE"], month, q, float(r["PLANNED_MAINTENANCE_QTY"]),
                     float(r["PLANNED_SHUTDOWN_QTY"]), int(r["PLANT_SHUTDOWN_MONTH_FLAG"]),
                     float(si) if si != "" else None, int(r["MONTH_OF_YEAR"])])
doc = {"kind": "training_set", "grain": "material x plant x month",
       "target": "netConsumptionQty", "plantId": "HZL_DEMO_01",
       "columns": COLS, "rows": rows}
with open(out + "/hzl01_net_consumption.json", "w") as f:
    json.dump(doc, f, separators=(",", ":"))
print(len(rows), "rows;", len({r[0] for r in rows}), "series;", len(per_month), "months;",
      min(per_month), "..", max(per_month), "; total", round(sum(per_month.values()), 3))
print("first", round(per_month[min(per_month)], 3), "last", round(per_month[max(per_month)], 3))
