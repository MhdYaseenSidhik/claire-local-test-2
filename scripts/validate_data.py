#!/usr/bin/env python3
"""Validate public/data against the contract. Exit 1 on any problem. Used locally and by CI."""
import json, os, sys, collections

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public", "data")
errs = []
def bad(m): errs.append(m)

for n in ("SCHEMA.md", "manifest.json"):
    if not os.path.exists(os.path.join(D, n)):
        bad("missing " + n)
if errs:
    print("\n".join(errs)); sys.exit(1)

m = json.load(open(os.path.join(D, "manifest.json")))
for k in ("schemaVersion", "generatedAt", "asOf", "disclaimer", "backcastIncluded", "files", "forecast"):
    if k not in m: bad("manifest missing " + k)
if m.get("schemaVersion") != 3: bad("schemaVersion must be 3")
if not isinstance(m.get("asOf"), str) or len(m["asOf"]) != 10: bad("asOf must be YYYY-MM-DD")

for f in m.get("files", []):
    for k in ("name", "rows", "generatedAt", "source"):
        if k not in f: bad("file entry missing " + k)
    for k in ("integrationId", "syncId", "assetId", "sql"):
        if k not in f.get("source", {}): bad("source missing " + k)
    p = os.path.join(D, f["name"])
    if not os.path.exists(p): bad("listed file missing: " + f["name"]); continue
    doc = json.load(open(p))
    if f["name"] == "hzl01_net_consumption.json":
        cols, rows = doc["columns"], doc["rows"]
        if len(rows) != f["rows"]: bad("row count differs from manifest")
        if any(len(r) != len(cols) for r in rows): bad("row width differs from columns")
        i = {c: cols.index(c) for c in cols}
        if {r[i["plantId"]] for r in rows} != {"HZL_DEMO_01"}: bad("plantId outside HZL_DEMO_01")
        if {r[i["materialType"]] for r in rows} - {"ZSPR", "ZSPN"}: bad("material type outside ZSPR/ZSPN")
        months = sorted({r[i["month"]] for r in rows})
        series = {r[i["seriesId"]] for r in rows}
        if len(rows) != len(series) * len(months): bad("rows != series x months (spine not dense)")
        c = collections.Counter((r[i["seriesId"]], r[i["month"]]) for r in rows)
        if max(c.values()) != 1: bad("duplicate series/month")
        if months[0] != "2023-01" or months[-1] != "2025-12" or len(months) != 36: bad("month range")
        print("ok", f["name"], len(rows), "rows", len(series), "series", months[0], months[-1])
if m.get("forecast") is not None and not isinstance(m["forecast"], dict): bad("forecast must be null or object")

if errs:
    print("\n".join(errs)); sys.exit(1)
print("data validation passed")
